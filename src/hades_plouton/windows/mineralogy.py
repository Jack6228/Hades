"""Mineral assemblage pop-up viewer and explorer.

Displays a bivariate plot of oxide compositions alongside a table of mineral compositions for each phase transition. Users can select different oxides for the x and y axes, and choose which phase transition to view.
"""

# Dependencies
import tkinter as tk
from tkinter import ttk, StringVar
import numpy as np
from tksheet import Sheet

from hades.visuals import format_axis_labels, format_label
from hades_plouton.visuals_GUI import BivariateVisualiser

def show_bivariate_window(model, parent_root=None, styler=None) -> None:
    """
    Spawns a standalone GUI frame to display a single interactive bivariate plot alongside mineral compositions mapped by phase transitions.

    Parameters
    ----------
    model : Hades.model.Obol
        The Hades model instance containing the data to visualise.
    parent_root : tk.Tk or tk.Toplevel, optional
        The parent Tkinter root or Toplevel window. If None, a new Tk root is created.
    styler : object, optional   
        An optional styler object providing color palette and styling information.
    """
    p = styler.palette

    # Window 
    if parent_root is None:
        win = tk.Tk()
    else:
        win = tk.Toplevel(parent_root)
        win.transient(parent_root)

    win.title("Mineral Assemblage Explorer")
    win.geometry("1200x700")
    win.configure(bg=p["bg"])
    win.update_idletasks()
    win.minsize(1000, 600)

    win.grid_columnconfigure(0, weight=1, uniform="halves", minsize=500)
    win.grid_columnconfigure(1, weight=1, uniform="halves", minsize=400)
    win.grid_rowconfigure(0, weight=0)  # header — fixed height
    win.grid_rowconfigure(1, weight=1)  # panes  — expand to fill

    # Oxide label helpers
    oxides = model.namespace.oxides
    oxide_labels = format_axis_labels(oxides)           # LaTeX-formatted list
    label_to_raw = dict(zip(oxide_labels, oxides))      # formatted → raw lookup

    # GUI
    ttk.Label(
        win,
        text="Mineral Assemblage Explorer",
        font=("Arial", 16, "bold"),
    ).grid(row=0, column=0, columnspan=2, pady=(10, 5))

    plot_frame = ttk.LabelFrame(win, text=" Bivariate Plot ", padding=10)
    plot_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
    plot_frame.grid_rowconfigure(0, weight=1)   # canvas expands
    plot_frame.grid_rowconfigure(1, weight=0)   # controls strip stays fixed
    plot_frame.grid_columnconfigure(0, weight=1)

    # Controls strip: toolbar at row 0, axis selectors at row 1
    controls = ttk.Frame(plot_frame)
    controls.grid(row=1, column=0, sticky="ew")
    controls.columnconfigure(0, weight=1)

    viz = BivariateVisualiser(x_order=['SiO2'], y_order=['MgO'])
    viz.init_bivariate_plot()
    viz.mount(plot_frame, toolbar_parent=controls)

    # Axis Selector 
    axsel = ttk.Frame(controls)
    axsel.grid(row=1, column=0, sticky="ew", pady=6)

    x_var = StringVar(value=format_label('SiO2'))
    y_var = StringVar(value=format_label('MgO'))

    ttk.Label(axsel, text="X-axis:").grid(row=0, column=0, padx=5, sticky="e")
    x_menu = ttk.Combobox(axsel, textvariable=x_var, values=oxide_labels,
                           state="readonly", width=10)
    x_menu.grid(row=0, column=1, padx=2)

    ttk.Label(axsel, text="Y-axis:").grid(row=0, column=2, padx=5, sticky="e")
    y_menu = ttk.Combobox(axsel, textvariable=y_var, values=oxide_labels,
                           state="readonly", width=10)
    y_menu.grid(row=0, column=3, padx=2)

    def redraw(*_) -> None:
        """
        Draws the bivariate plot based on the selected x and y axes, and updates the mineral compositions table accordingly.
        """
        x_raw = label_to_raw.get(x_var.get(), x_var.get())
        y_raw = label_to_raw.get(y_var.get(), y_var.get())
        if not x_raw or not y_raw:
            return

        phase_idx = phases.index(phase_var.get()) if phase_var.get() in phases else 0

        # rebuild() tears down the old canvas + toolbar and creates a fresh figure
        viz.rebuild(x_order=[x_raw], y_order=[y_raw])

        try:
            viz.plot_data_suite(model)
            viz.plot_magma(model, mode='initial',  phase_highlight=phase_idx)
            viz.plot_magma(model, mode='computed', phase_highlight=phase_idx)
            viz.plot_minerals(model, phase_idx=phase_idx)
        except Exception as e:
            print(f"Plotting errors: {e}")

    x_menu.bind("<<ComboboxSelected>>", redraw)
    y_menu.bind("<<ComboboxSelected>>", redraw)

    right_pane = ttk.LabelFrame(win, text=" Mineral Compositions by Phase ",
                                 padding=10)
    right_pane.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
    right_pane.grid_columnconfigure(0, weight=1)
    right_pane.grid_rowconfigure(0, weight=11)  # ~55 sheet
    right_pane.grid_rowconfigure(1, weight=9)   # ~45 legend

    # Data Table 
    table_container = ttk.Frame(right_pane)
    table_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
    table_container.grid_rowconfigure(1, weight=1)
    table_container.grid_columnconfigure(0, weight=1)

    phases = model.namespace.phase_transitions

    phase_frame = ttk.Frame(table_container)
    phase_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    ttk.Label(phase_frame, text="Phase transition:").grid(row=0, column=0, padx=5)

    phase_var  = StringVar(value=phases[0])
    phase_menu = ttk.Combobox(phase_frame, textvariable=phase_var, values=phases,
                               state="readonly", width=22)
    phase_menu.grid(row=0, column=1, padx=2)

    sheet = Sheet(
        table_container,
        header=["wt.%"] + oxides,
        empty_vertical=0,
        empty_horizontal=0,
        row_index_width=90,
    )
    sheet.grid(row=1, column=0, sticky="nsew")
    sheet.enable_bindings((
        "drag_select", "select", "select_all",
        "row_select", "column_select",
        "ctrl_c", "copy", "arrowkeys",
    ))
    sheet.default_column_width(60)

    # Legend image
    legend_container = ttk.LabelFrame(right_pane, text=" Figure Legend ", padding=10)
    legend_container.grid(row=1, column=0, sticky="ew")  # 'ew' lets width fit container, height grows naturally
    legend_container.grid_rowconfigure(0, weight=1)
    legend_container.grid_columnconfigure(0, weight=1)
    # Remove grid_propagate(False) so height auto-adjusts to image height

    legend_label = ttk.Label(legend_container, anchor="center")
    legend_label.grid(row=0, column=0, sticky="nsew")

    try:
        from PIL import Image, ImageTk
        from hades.utils import get_asset_path

        legend_label.orig_img = Image.open(get_asset_path("hades_plouton.assets", "mineral_legend.png"))
        legend_label.last_width = 0  # Store last width to avoid infinite recursion loops

        def resize_legend(event):
            # Target width available inside padding
            target_w = event.width - 20
            if target_w <= 10 or target_w == legend_label.last_width:
                return

            legend_label.last_width = target_w

            # Calculate exact height to preserve aspect ratio
            orig_w, orig_h = legend_label.orig_img.size
            aspect_ratio = orig_h / orig_w
            target_h = int(target_w * aspect_ratio)

            # Resize to fill full width
            resized_img = legend_label.orig_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_img)
            
            legend_label.configure(image=photo)
            legend_label.image = photo  # Keep reference against garbage collection

        # Bind to right_pane or container width changes
        legend_container.bind("<Configure>", resize_legend)

    except Exception as e:
        print(f"Warning: could not load legend image: {e}")

    # Sheet refresh
    def refresh_table(*_):
        """
        Updates the mineral compositions table based on the selected phase transition.
        """
        phase_idx = phases.index(phase_var.get()) if phase_var.get() in phases else 0

        if not model.results[phase_idx].isrun:
            print(f"Phase {phase_idx} has not been run yet — no data to display.")
            return

        minerals = model.meta.minerals_

        cotectics = model.results[phase_idx].cotectics
        weights   = 100 * model.results[phase_idx].weights
        arr       = np.hstack([weights.reshape(-1, 1), cotectics])

        # Filter to minerals that are actually used in this phase
        usage    = model.results[phase_idx].usage
        minerals = [m for m, u in zip(minerals, usage) if u]
        arr      = arr[usage.astype(bool), :]

        sheet_data = []
        for m_idx in range(len(minerals)):
            row = []
            for o_idx in range(len(oxides)+1):
                try:
                    val = arr[m_idx, o_idx]
                    row.append("" if np.isnan(val) else round(float(val), 2))
                except Exception:
                    row.append("")
            sheet_data.append(row)

        sheet.row_index(minerals)
        sheet.set_sheet_data(sheet_data, redraw=True)

    # Phase change → refresh both table and plot
    phase_menu.bind("<<ComboboxSelected>>", lambda e: (refresh_table(), redraw()))

    # Initial Render
    redraw()
    refresh_table()

    if parent_root is None:
        win.mainloop()
