"""Pop-up window which has trace element functionality for the Hades GUI application.

This module defines the TraceElementVisualiser class, which provides a GUI interface for trace element analysis within the Hades application. It allows users to input accessory mineral weights, view and edit Kd values, and visualize trace element evolution through plots. The visualiser is designed to be integrated into the main Hades GUI and interacts with the underlying model to perform calculations and update results in real-time.
"""

# Dependencies
import tkinter as tk
from tkinter import ttk, StringVar, messagebox
import threading
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tksheet import Sheet

from hades.visuals import format_label
from hades_plouton.visuals_GUI import BivariateVisualiser

class TraceElementVisualiser:
    """
    Pop-up window for trace element analysis with custom-styled tab navigation.
    """

    # Which trace elements can form structural components of the melt
    TRACES_FIXED = ["P", "Zr", "La", "Ce", "Nd", "Y", "Th"]

    def __init__(self, parent, style, model) -> None:
        """Set up the trace element visualiser window with tabs, tables, and plots."""
        self.styler = style
        self.parent_root = parent
        self.model = model

        # Shorthand reference to the model data - edits in place 
        self.Kd_3D = self.model.minerals.trace_KDs

        self.Nphases, self.Nminerals, self.Ntraces = self.Kd_3D.shape
        self.phases = self.model.namespace.phases[:-1]
        self.minerals = self.model.meta.minerals_ + self.model.namespace.accessory_minerals
        self.traces = self.model.namespace.traces

        # Theme attributes from the parent GUI window
        self.style = getattr(self.styler, "style", None)
        self.palette = getattr(self.styler, "palette", {})
        self.font_main = getattr(self.styler, "font_main", ("TkDefaultFont", 10))
        self.font_bold = getattr(self.styler, "font_bold", ("TkDefaultFont", 10, "bold"))

        # Single visualiser for all 8 subplots
        self.viz = BivariateVisualiser(
            x_order=['SiO2'],
            y_order=self.TRACES_FIXED + ['Ba'],  # 'Ba' is default for slot 7
        )

        self.phase_idx = [
            p for p in range(self.Nphases)
            if getattr(self.model.trace_results[p], 'isrun', False)
        ] if hasattr(self.model, 'trace_results') else []

        # Window setup
        self.win = tk.Toplevel(parent)
        self.win.transient(parent)
        self.win.grab_set()
        self.win.title("Trace Element Analysis")
        self.win.geometry("1400x900")
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.win.update_idletasks()
        self.win.minsize(1000, 700)

        # Store Kd values
        self.kd_values = [
            [
                [
                    tk.DoubleVar(value=self.Kd_3D[phase_idx][row_idx][col_idx])
                    for col_idx in range(self.Ntraces)
                ] for row_idx in range(self.Nminerals)
            ] for phase_idx in range(self.Nphases)
        ]

        # Structure to store FloatVars for entry grid: list of dicts per stage
        self.mineral_vars = []

        # Build Main Structure using custom tab bar styling
        self._build_main_structure()

        # Setup Analysis Page components
        self.setup_top_panel()
        self.setup_bottom_panel()

        # Setup Tables Page components
        self.setup_tables_page()

        # Select initial main tab
        self.select_main_tab(0)

        # Initial render & button initialisation
        self._redraw_all()
        isrun = [self.model.results[i].isrun for i in range(self.Nphases)]
        self._apply_button_states([i for i, run in enumerate(isrun) if run])

    # Main Layout with Custom Styled Tab Bar 

    def _build_main_structure(self) -> None:
        """Create the main window layout with a custom tab bar and content area."""
        p = self.palette

        # Top-level Tab Bar
        main_tab_bar = ttk.Frame(self.win)
        main_tab_bar.pack(fill="x", padx=15, pady=(15, 0))

        # Content container frame
        self.main_content = tk.Frame(
            self.win, 
            bg=p.get("surface", "#ffffff"),
            highlightbackground=p.get("border", "#cccccc"),
            highlightthickness=1
        )
        self.main_content.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        # Main Pages: Analysis & Tables
        self.analysis_tab = ttk.Frame(self.main_content)
        self.analysis_tab.grid_rowconfigure(0, weight=1, minsize=200)
        self.analysis_tab.grid_rowconfigure(1, weight=3, minsize=400)
        self.analysis_tab.grid_columnconfigure(0, weight=1)

        self.tables_tab = ttk.Frame(self.main_content)

        self.main_panels = [self.analysis_tab, self.tables_tab]

        # Main Tab Headers
        self.main_tab_headers = []
        names = ["Analysis", "KD Values"]
        for idx, name in enumerate(names):
            hf = ttk.Frame(main_tab_bar, width=150, height=34, style="TabInactive.TFrame")
            hf.pack_propagate(False)
            hf.pack(side="left", padx=(0, 4))

            hl = ttk.Label(hf, text=name, style="TabInactive.TLabel")
            hl.pack(expand=True)

            hf.bind("<Button-1>", lambda e, i=idx: self.select_main_tab(i))
            hl.bind("<Button-1>", lambda e, i=idx: self.select_main_tab(i))
            self.main_tab_headers.append((hf, hl))

    def select_main_tab(self, index: int) -> None:
        """Switch between the Analysis and Tables main pages."""
        for panel in self.main_panels:
            panel.pack_forget()

        self.main_panels[index].pack(fill="both", expand=True, padx=10, pady=10)

        for i, (hf, hl) in enumerate(self.main_tab_headers):
            if i == index:
                hf.configure(style="TabActive.TFrame")
                hl.configure(style="TabActive.TLabel")
            else:
                hf.configure(style="TabInactive.TFrame")
                hl.configure(style="TabInactive.TLabel")

    def setup_top_panel(self) -> None:
        """Mineral weight entry grid and analysis controls."""
        top_frame = ttk.Frame(self.analysis_tab, padding=10)
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.grid_columnconfigure(0, weight=1, uniform="top_halves")
        top_frame.grid_columnconfigure(1, weight=1, uniform="top_halves")
        top_frame.grid_rowconfigure(0, weight=1)

        # Top-Left: Mineral weight entry grid
        table_border = ttk.LabelFrame(top_frame, text=" Accessory Mineral Weights (0 - 100 wt.%) ", padding=10)
        table_border.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        table_border.grid_rowconfigure(0, weight=1)
        table_border.grid_columnconfigure(0, weight=1)

        headers = self.model.namespace.accessory_minerals

        grid_frame = ttk.Frame(table_border)
        grid_frame.grid(row=0, column=0, sticky="nsew")

        # Column headers
        grid_frame.columnconfigure(0, weight=1)  # Stage names column
        for col_idx, header in enumerate(headers):
            lbl = ttk.Label(grid_frame, text=header, font=self.font_bold, anchor="center")
            lbl.grid(row=0, column=col_idx + 1, padx=4, pady=(0, 5), sticky="ew")
            grid_frame.columnconfigure(col_idx + 1, weight=1)
        grid_frame.columnconfigure(len(headers) + 1, weight=0)  # Buttons column

        self.buttons = []
        self.mineral_vars = []

        # Validate function for floating-point values
        vcmd = (self.win.register(self._validate_float_input), '%P')

        for stage_idx, stage_name in enumerate(self.phases):
            # Row title
            stage_lbl = ttk.Label(grid_frame, text=stage_name, anchor="w", font=self.font_main)
            stage_lbl.grid(row=stage_idx + 1, column=0, padx=(0, 5), pady=4, sticky="w")

            stage_vars = {}
            for col_idx, mineral in enumerate(headers):
                var = tk.DoubleVar(value=0.0)
                stage_vars[mineral] = var

                entry = ttk.Entry(
                    grid_frame, 
                    textvariable=var, 
                    width=8, 
                    justify="right",
                    validate="key",
                    validatecommand=vcmd
                )
                entry.grid(row=stage_idx + 1, column=col_idx + 1, padx=2, pady=4, sticky="ew")

            self.mineral_vars.append(stage_vars)

            # Row Action Buttons (perfectly aligned with row)
            btn_box = ttk.Frame(grid_frame)
            btn_box.grid(row=stage_idx + 1, column=len(headers) + 1, padx=(8, 0), pady=2, sticky="ew")

            btn_view = ttk.Button(btn_box, text="View", width=6, command=lambda idx=stage_idx: self.on_run(idx))
            btn_rst = ttk.Button(btn_box, text="Reset", width=6, command=lambda idx=stage_idx: self.reset_phase(idx))
            
            btn_view.pack(side="left", padx=2)
            btn_rst.pack(side="left", padx=2)
            self.buttons.append([btn_view, btn_rst])

        # Top-Right: Controls
        ctrl = ttk.LabelFrame(top_frame, text=" Analysis Controls ", padding=10)
        ctrl.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ctrl.grid_columnconfigure(1, weight=1)
        ctrl.grid_rowconfigure(0, weight=1)

        tk.Label(
            ctrl,
            text=(
                "Trace element optimisation works by perturbing the optimal solution "
                "found for the major oxide elements with up to four accessory minerals. "
                "This is re-modelled with adjusted mineral weights to compute trace element evolution.\n\n"
                "Enter weight fraction values for each accessory mineral in the entries "
                "on the left (0-100). The 'View' button for each row re-computes the trace "
                "element evolution for that stage and updates the plots below.\n\n"
                "Once run, close the window to save or export results."
            ),
            justify="left", anchor="nw", wraplength=550, font=("TkDefaultFont", 10)
            , bg=self.palette.get("surface", None), fg=self.palette.get("fg", None)
        ).grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        ttk.Label(ctrl, text="Bottom-Right Plot Y-Axis:").grid(row=1, column=0, sticky="w", pady=5)
        self.br_y_var = StringVar(value="Ba")
        combo = ttk.Combobox(
            ctrl, textvariable=self.br_y_var,
            values=getattr(self.model.namespace, "traces", []), state="readonly",
        )
        combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        combo.bind("<<ComboboxSelected>>", lambda e: self._on_y_element_change())

        btn_frame = ttk.Frame(ctrl)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="Save & Close", command=self.on_close).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def setup_bottom_panel(self) -> None:
        """Build shared 2x4 Harker figure."""
        plot_frame = ttk.LabelFrame(self.analysis_tab, text=" Trace Element Evolution Plots ", padding=5)
        plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        plot_frame.grid_rowconfigure(1, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        controls = ttk.Frame(plot_frame)
        controls.grid(row=0, column=0, sticky="ew")

        self.fig = Figure(figsize=(12, 5), dpi=100)
        raw_axs = self.fig.subplots(2, 4)
        axs_flat = np.array(raw_axs).flatten()

        all_elements = self.TRACES_FIXED + [self.br_y_var.get()]
        for ax, y_elem in zip(axs_flat, all_elements):
            ax.minorticks_on()
            ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
            ax.set_xlabel(f"{format_label('SiO2')} (wt.%)", fontsize=10)
            ax.set_ylabel(f"{format_label(y_elem)} (ppm)", fontsize=10)
            ax.grid(True, linestyle=':', alpha=0.4)

        self.fig.tight_layout(pad=3.0)
        self.viz.fig = self.fig
        self.viz.ax = axs_flat.reshape(8, 1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        self.viz.canvas = self.canvas

        self.toolbar = NavigationToolbar2Tk(self.canvas, controls, pack_toolbar=False)
        self.toolbar.grid(row=0, column=0, sticky="w")
        self.toolbar.update()

    # Variable Access & Validation Helpers 

    def _validate_float_input(self, P: str) -> bool:
        """Validate live keystrokes to ensure entry values are numeric floats."""
        if P == "" or P == "-":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def get_stage_mineral_weights(self, stage_idx: int) -> list[float]:
        """Extract float values for all mineral entries in a given stage index."""
        weights = []
        for var in self.mineral_vars[stage_idx].values():
            try:
                weights.append(float(var.get()))
            except (ValueError, tk.TclError):
                weights.append(0.0)
        return weights

    def set_stage_mineral_weights(self, stage_idx: int, values: list[float]) -> None:
        """Set float values for all entries in a given stage index."""
        for (min_name, var), val in zip(self.mineral_vars[stage_idx].items(), values):
            var.set(float(val))

    # Tables Tab UI Setup with Custom Subtabs 

    def setup_tables_page(self) -> None:
        """Nested 5-subtab view built with styled custom tab headers."""
        p = self.palette

        # Subtab bar
        sub_tab_bar = ttk.Frame(self.tables_tab)
        sub_tab_bar.pack(fill="x", padx=10, pady=(10, 0))

        # Subtab content container
        sub_content = tk.Frame(
            self.tables_tab,
            bg=p.get("surface", "#ffffff"),
            highlightbackground=p.get("border", "#cccccc"),
            highlightthickness=1
        )
        sub_content.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.sub_panels = []
        self.table_sheets = []
        self.sub_tab_headers = []

        for i in range(5):
            tab_frame = ttk.Frame(sub_content, padding=10)
            self.sub_panels.append(tab_frame)

            tab_frame.grid_rowconfigure(0, weight=1)
            tab_frame.grid_columnconfigure(0, weight=1)

            # Container for sheet
            sheet_container = ttk.Frame(tab_frame)
            sheet_container.grid(row=0, column=0, sticky="nsew")

            sheet = Sheet(sheet_container, 
                          data=self.Kd_3D[i].tolist(), 
                          headers=self.traces, 
                          row_index=[m for m in self.minerals],
                        )

            sheet.table_align('centre')
            sheet.align_rows('center')
            sheet.row_index_align('left')
            sheet.set_all_column_widths(60)
            # sheet.set_row_heights([50] * 5)
            sheet.set_index_width(160)
            self._apply_sheet_theme(sheet)

            sheet.enable_bindings("single_select", "drag_select", "edit_cell", "copy", "cut", "paste")
            # Real-time auto-save using save_table_data via sheet_data_to_array
            # tksheet structural events (cell commits, paste, delete, undo/redo)
            sheet.extra_bindings("end_edit_cell", lambda e, idx=i: self.save_table_data(idx))
            sheet.extra_bindings("post_paste", lambda e, idx=i: self.save_table_data(idx))
            sheet.extra_bindings("end_delete_rows", lambda e, idx=i: self.save_table_data(idx))
            sheet.extra_bindings("end_undo", lambda e, idx=i: self.save_table_data(idx))
            sheet.extra_bindings("end_redo", lambda e, idx=i: self.save_table_data(idx))

            # Live keypress auto-save (triggers instantly as values are typed)
            sheet.bind("<KeyRelease>", lambda e, idx=i: self.save_table_data(idx))

            sheet.pack(fill="both", expand=True)
            self.table_sheets.append(sheet)

            # Control row per subtab with Save Button
            ctrl_bar = ttk.Frame(tab_frame)
            ctrl_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
            btn_save = ttk.Button(
                ctrl_bar, 
                text=f"Save {self.phases[i]} Table Data", 
                command=lambda idx=i: self.save_table_data(idx)
            )
            btn_save.pack(side="right")

            # Create Subtab Header Widget
            hf = ttk.Frame(sub_tab_bar, width=130, height=30, style="TabInactive.TFrame")
            hf.pack_propagate(False)
            hf.pack(side="left", padx=(0, 4))

            hl = ttk.Label(hf, text=self.phases[i], style="TabInactive.TLabel")
            hl.pack(expand=True)

            hf.bind("<Button-1>", lambda e, idx=i: self.select_sub_tab(idx))
            hl.bind("<Button-1>", lambda e, idx=i: self.select_sub_tab(idx))
            self.sub_tab_headers.append((hf, hl))

        # Default to first subtab
        self.select_sub_tab(0)

    def select_sub_tab(self, index: int) -> None:
        """Switch between subtabs on the Tables page."""
        for panel in self.sub_panels:
            panel.pack_forget()

        self.sub_panels[index].pack(fill="both", expand=True, padx=5, pady=5)

        for i, (hf, hl) in enumerate(self.sub_tab_headers):
            if i == index:
                hf.configure(style="TabActive.TFrame")
                hl.configure(style="TabActive.TLabel")
            else:
                hf.configure(style="TabInactive.TFrame")
                hl.configure(style="TabInactive.TLabel")

    def sheet_data_to_array(self, raw_data: list[list],  expected_shape: tuple[int, int] = None,  default_val: float = 0.0, parent=None) -> tuple[np.ndarray, bool]:
        """
        Safely converts tksheet list-of-lists into a clean float64 NumPy array.

        Returns (array, had_errors): The converted array and a boolean indicating if unparseable values were encountered and replaced.
        """
        rows = len(raw_data)
        cols = len(raw_data[0]) if rows > 0 else 0
        clean_arr = np.full((rows, cols), default_val, dtype=np.float64)
        had_errors = False

        for r in range(rows):
            for c in range(cols):
                val = raw_data[r][c]
                if val is None or str(val).strip() == "":
                    clean_arr[r, c] = default_val
                else:
                    try:
                        clean_arr[r, c] = float(val)
                    except (ValueError, TypeError):
                        clean_arr[r, c] = default_val
                        had_errors = True

        if expected_shape and clean_arr.shape != expected_shape:
            raise ValueError(f"Shape mismatch: expected {expected_shape}, got {clean_arr.shape}")

        if had_errors and parent:
            messagebox.showwarning(
                "Validation Warning", 
                "Some cells contained non-numeric text or invalid characters.\n"
                f"They were automatically replaced with {default_val}.",
                parent=parent
            )

        return clean_arr, had_errors

    def save_table_data(self, subtab_index: int, *args) -> None:
        """
        Safely validate sheet inputs and update model KDs in-place.
        
        *args absorbs any event dict passed by tksheet bindings without throwing a TypeError.
        """
        raw_data = self.table_sheets[subtab_index].get_sheet_data()
        expected_shape = (self.Nminerals, self.Ntraces)

        # print(f"{self.phases[subtab_index]} table original data sum:     {np.nansum(self.Kd_3D[subtab_index, :, :]):.4f}")
        
        # Validate and convert raw table data
        clean_matrix, had_errors = self.sheet_data_to_array(
            raw_data, 
            expected_shape=expected_shape, 
            default_val=0.0, 
            parent=None # Set to None to prevent annoying popups while typing
        )

        # In-place write to model array
        self.Kd_3D[subtab_index, :, :] = clean_matrix
        # print(f" > adjusted sum for phase '{self.phases[subtab_index]}': {clean_matrix.sum():.4f}")
   
    # Helpers & Events 

    def _apply_sheet_theme(self, sheet) -> None:
        """Tint tksheet instance using palette properties."""
        p = self.palette
        if not p:
            return
        try:
            sheet.set_options(
                table_bg=p.get("surface", "#ffffff"), 
                table_fg=p.get("fg", "#000000"),
                table_grid_fg=p.get("border", "#cccccc"),
                header_bg=p.get("side_bg", "#f0f0f0"), 
                header_fg=p.get("fg", "#000000"),
                index_bg=p.get("side_bg", "#f0f0f0"), 
                index_fg=p.get("fg", "#000000"),
                top_left_bg=p.get("side_bg", "#f0f0f0"),
                table_selected_cells_bg=p.get("tab_active_bg", "#e1e1e1"),
                table_selected_cells_border_fg=p.get("primary", "#007acc"),
            )
            sheet.refresh()
        except Exception as exc:
            print(f"[sheet theme error] {exc}")

    def on_close(self) -> None:
        """Close the trace element visualiser window."""
        self.win.destroy()

    def _apply_button_states(self, enabled_rows=None) -> None:
        """Enable or disable the 'View' buttons based on whether the corresponding trace results are valid."""
        isrun_valid = [self.model.results[i].isrun for i in range(5)]
        samples = self.model.magma.magma_samples
        transitions_valid = [
            (samples[i] is not None and samples[i + 1] is not None)
            for i in range(len(samples) - 1)
        ]

        default_rows = np.arange(len(transitions_valid))[transitions_valid]
        default_rows = [r for r in default_rows if isrun_valid[r]]

        enabled_rows = default_rows if enabled_rows is None else [r for r in enabled_rows if r in default_rows]
        enabled = set(enabled_rows)
        for r_idx, row_of_buttons in enumerate(self.buttons):
            state = "normal" if r_idx in enabled else "disabled"
            row_of_buttons[0].config(state=state)

    def _on_y_element_change(self) -> None:
        """Update the bottom-right plot's Y-axis element based on the combobox selection."""
        y_elem = self.br_y_var.get()
        self.viz.y_order[7] = y_elem
        self.viz.ax[7, 0].set_ylabel(f"{format_label(y_elem)} (ppm)", fontsize=10)
        self._redraw_all()

    def _redraw_all(self) -> None:
        """Redraw all plots based on the current model state and selected phase indices."""
        if self.model is None:
            return

        run_trace_idxs = list(range(self.phase_idx + 1)) if isinstance(self.phase_idx, int) else self.phase_idx

        try:
            self.viz.plot_data_suite(self.model)
            self.viz.plot_magma(self.model, mode='initial')
            self.viz.clear_magma(mode='traces')

            if run_trace_idxs:
                self.viz.plot_magma(
                    self.model,
                    mode='traces',
                    transition_idxs=run_trace_idxs,
                )
        except Exception as e:
            print(f"Plot generation skip: {e}")

        self.viz.rescale_axes()

    def on_run(self, stage_idx=None) -> None:
        """Run trace element calculations for a specific stage index through the backend."""
        idx = stage_idx if stage_idx is not None else 0
        self.phase_idx = idx

        # Extract floats directly from entry variables
        Wacc = self.get_stage_mineral_weights(idx)

        target_win = self.win
        target_win.config(cursor="starting")

        print(f"Using accessory mineral weights for phase '{self.phases[idx]}': {Wacc}")
        print(f" > sum of KD table for this phase: {self.Kd_3D[idx].sum():.4f}")

        blocker = tk.Frame(target_win, bg="", highlightthickness=0, bd=0)
        blocker.place(relx=0, rely=0, relwidth=1, relheight=1)
        blocker.configure(cursor="starting")
        blocker.grab_set()

        result = {"error": None}

        def worker():
            try:
                self.model.runTraces(idx + 1, Wacc)
            except Exception as e:
                result["error"] = e

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        def check_thread() -> None:
            """Check if the worker thread has finished and update the GUI accordingly."""
            if not target_win.winfo_exists():
                return

            if thread.is_alive():
                target_win.after(50, check_thread)
                return

            blocker.grab_release()
            blocker.destroy()
            target_win.config(cursor="")

            if self.parent_root is not None:
                target_win.grab_set()

            if result["error"]:
                messagebox.showerror(
                    "Model Error",
                    f"Trace compute failed: {result['error']}",
                    parent=target_win,
                )
                return

            self._apply_button_states(range(idx + 2))
            self._redraw_all()

        check_thread()

    def reset_phase(self, idx : int) -> None:
        """Reset the trace element results for a specific phase index."""
        if hasattr(self.model, 'trace_results'):
            for p in range(idx, len(self.model.namespace.phase_transitions)):
                self.model.trace_results[p].isrun = False

        # Reset row entry variables back to 0.0
        self.set_stage_mineral_weights(idx, [0.0] * 4)

        self._apply_button_states(range(idx, len(self.buttons)))
        self._redraw_all()


def show_trace_window(model, parent, style) -> tk.Toplevel:
    """Create and display the trace element visualiser window."""
    app = TraceElementVisualiser(parent, style, model)
    return app.win