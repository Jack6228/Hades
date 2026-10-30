"""Edit the per-phase initial magma compositions in a spreadsheet-style table and bivariate plot.

Pop-up window for the main GUI. The user can assign samples to customise the automatically generated LLOD from the data suite.
"""

# Dependencies
import tkinter as tk
from tkinter import ttk, StringVar
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from hades.styles import phase_colours, initial_phase_line_properties, data_suite_style

# tksheet is required for the spreadsheet-style tables. Imported lazily so a # missing dependency produces a clear error at construction time.
try:
    from tksheet import Sheet
except ImportError:                      # pragma: no cover
    Sheet = None

def format_axis_labels(label: str) -> str:
    """Passthrough placeholder (kept consistent with the main GUI helper)."""
    return label

class EditMagmasWindow(tk.Toplevel):
    """Interactive editor for the per-phase initial magma compositions."""

    # Style forplot elements
    COMPOSITION_MARKER_STYLE = {
        "marker": "o",
        "s": 90,
        "facecolor": "none",
        "linewidth": 2.0,
        "zorder": 10,
    }
    COMPOSITION_LINE_STYLE = initial_phase_line_properties
    DATASUITE_MARKER_STYLE = data_suite_style

    def __init__(self, parent, styler, model, icon_path=None, on_apply=None) -> None:
        """Create the Edit Magmas window."""
        super().__init__(parent)

        if Sheet is None:
            raise ImportError("tksheet is required for EditMagmasWindow "
                            "(pip install tksheet).")

        self.styler = styler
        self._on_apply_cb = on_apply
        self.result = None

        self.title("Edit Magmatic Compositions")
        self.geometry("1400x820")
        self.minsize(1050, 620)

        if icon_path:
            try:
                self.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception:
                pass  # non-fatal icon issue

        # Extract values from the model
        self.init_comp       = np.array(model.magma.initial, dtype=float)    # (6 x N) copy
        self.init_samples    = list(model.magma.magma_samples)               # 6 labels
        # Auto-computed defaults + their labels (used by the "[auto]" option).
        self.default_comp    = np.array(model.magma.autocomp, dtype=float)   # (6 x N) copy
        self.default_samples = list(model.magma.autocomp_samples)            # 6 labels

        # Oxide names (first 8 are the majors we display / plot).
        self.oxides       = list(model.namespace.oxides)
        self.major_oxides = self.oxides[:8]
        self.n_major      = len(self.major_oxides)

        # Data suite (all samples) for the pickable scatter + table.
        ds = np.array(model.datasuite.data, dtype=float)
        if ds.ndim == 1:
            ds = ds.reshape(1, -1)
        self.main_data    = ds[:, :self.n_major].tolist()   # detached copy
        self.n_samples    = len(self.main_data)
        self.sample_names = list(model.datasuite.sample_names)

        self.PHASES = list(phase_colours.keys())
        self.phase_colours = phase_colours

        # Editable copies (tolist() detaches these from the numpy arrays above).
        self.phase_data = self.init_comp[:, :self.n_major].tolist()      # what the user edits
        self.autocomp   = self.default_comp[:, :self.n_major].tolist()   # majors for "[auto]"

        # Dropdown options + one preset selector var per phase.
        self.dropdown_options = ["[auto]", "None"] + self.sample_names
        self.column_selectors = [StringVar(value=self._initial_label(i)) for i in range(len(self.PHASES))]

        # Create the main horizontal pane: left = controls, right = plot.
        self.main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = self._create_control_panel(self.main_pane)
        self.main_pane.add(self.control_frame, weight=1)

        self.viz_frame = self._create_graph_panel(self.main_pane)
        self.main_pane.add(self.viz_frame, weight=2)

        self.update_plot()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _initial_label(self, i) -> str:
        """Return the label for the initial selection of phase `i`. If the initial sample is in the dropdown, return it; otherwise, return "[auto]".
        """
        if i < len(self.init_samples):
            lbl = self.init_samples[i]
            if lbl in self.dropdown_options:
                return lbl
        return "[auto]"

    def _phase_colour(self, phase_idx):
        """Colour for a phase index, from phase_colours (safe fallback)."""
        name = self.PHASES[phase_idx]
        return self.phase_colours.get(name, "black")

    def _create_control_panel(self, parent) -> ttk.Frame:
        """Left-hand control panel with the data suite table + phase assignment."""
        panel = ttk.Frame(parent, padding=10)
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)   # data table expands

        # Header 
        ttk.Label(panel, text="Edit Initial Magma Compositions",
                  style="Header.TLabel").grid(row=0, column=0, sticky="w",
                                              padx=2, pady=(0, 8))

        # Data-suite table (all samples) 
        data_lf = ttk.LabelFrame(panel, text=" Data Suite Samples ", padding=8)
        data_lf.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        data_lf.rowconfigure(0, weight=1)
        data_lf.columnconfigure(0, weight=1)

        self.main_sheet = Sheet(
            data_lf,
            data=self._fmt(self.main_data),
            headers=list(self.major_oxides),
            height=260,
        )
        # Read-only interactions: users assign via the plot / dropdowns.
        self.main_sheet.enable_bindings(
            ("single_select", "row_select", "arrowkeys", "drag_select", "copy"))
        self.main_sheet.grid(row=0, column=0, sticky="nsew")
        self.main_sheet.table_align("centre")
        self.main_sheet.row_index_align("left")
        self.main_sheet.row_index(self.sample_names)
        self.main_sheet.set_index_width(110)
        self.main_sheet.set_column_widths([55] * self.n_major)

        # Phase assignment (dropdowns + table) 
        phase_lf = ttk.LabelFrame(panel, text=" Phase Assignment ", padding=8)
        phase_lf.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        phase_lf.columnconfigure(0, weight=1)

        ttk.Label(phase_lf,
                  text="Assign a sample (or '[auto]' / 'None') to each phase:",
                  anchor="w", justify="left").grid(row=0, column=0, sticky="w",
                                                   pady=(0, 6))

        # Dropdown grid, one Combobox per phase (two columns to save space).
        sel_frame = ttk.Frame(phase_lf)
        sel_frame.grid(row=1, column=0, sticky="ew")
        for i, phase in enumerate(self.PHASES):
            r, c = divmod(i, 2)
            ttk.Label(sel_frame, text=f"{phase}:",
                      foreground=self._phase_colour(i)
                      ).grid(row=r, column=c * 2, sticky="e", padx=(4, 4), pady=3)
            # self.column_selectors[i].set(self.get_current_selector_label(i))
            cb = ttk.Combobox(sel_frame, textvariable=self.column_selectors[i],
                              values=self.dropdown_options, state="readonly",
                              width=16, style="Axis.TCombobox")
            cb.grid(row=r, column=c * 2 + 1, sticky="w", padx=(0, 12), pady=3)
            # Bind by index so the correct phase row is updated.
            cb.bind("<<ComboboxSelected>>",
                    lambda e, idx=i: self.on_select(
                        self.column_selectors[idx].get(), idx))

        # Phase composition table (majors only, mirrors phase_data).
        self.phase_sheet = Sheet(
            phase_lf,
            data=self._fmt(self.phase_data),
            headers=list(self.major_oxides),
            height=190,
        )
        self.phase_sheet.enable_bindings(
            ("single_select", "row_select", "arrowkeys", "drag_select", "copy"))
        self.phase_sheet.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.phase_sheet.table_align("centre")
        self.phase_sheet.row_index_align("left")
        self.phase_sheet.row_index(self.PHASES)
        self.phase_sheet.set_index_width(110)
        self.phase_sheet.set_column_widths([55] * self.n_major)

        # Action buttons 
        btn_frame = ttk.Frame(panel)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="Apply", command=self.on_apply).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(btn_frame, text="Cancel", command=self.on_close).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))

        return panel

    def _create_graph_panel(self, parent) -> ttk.Frame:
        """Single-plot bivariate panel with toolbar + X/Y axis selectors."""
        frame = ttk.Frame(parent, padding=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Figure / single Axes
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Artist tracking for the initial-magma overlay
        # We draw/remove these ourselves so styling stays local & editable.
        self.composition_markers = [None] * len(self.PHASES)
        self.composition_lines = []

        # Toolbar + controls container
        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=1, column=0, sticky="ew")
        controls_frame.columnconfigure(0, weight=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, controls_frame,
                                            pack_toolbar=False)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.toolbar.update()

        # Axis selection controls (defaults differ from main GUI)
        axes_frame = ttk.Frame(controls_frame)
        axes_frame.grid(row=1, column=0, sticky="ew", pady=6)

        default_x = "MgO" if "MgO" in self.major_oxides else self.major_oxides[0]
        default_y = ("Al2O3" if "Al2O3" in self.major_oxides
                     else self.major_oxides[min(1, self.n_major - 1)])
        self.x_axis_var = StringVar(value=format_axis_labels(default_x))
        self.y_axis_var = StringVar(value=format_axis_labels(default_y))

        oxide_labels = [format_axis_labels(o) for o in self.major_oxides]
        # Reverse map to recover raw oxide names from formatted combobox text.
        self._label_to_raw = {format_axis_labels(o): o for o in self.major_oxides}

        ttk.Label(axes_frame, text="X-axis:").grid(row=0, column=0, padx=5, sticky="e")
        x_menu = ttk.Combobox(axes_frame, textvariable=self.x_axis_var,
                              values=oxide_labels, state="readonly",
                              width=8, style="Axis.TCombobox")
        x_menu.grid(row=0, column=1, padx=2)
        x_menu.bind("<<ComboboxSelected>>", lambda e: self.update_plot())

        ttk.Label(axes_frame, text="Y-axis:").grid(row=0, column=2, padx=5, sticky="e")
        y_menu = ttk.Combobox(axes_frame, textvariable=self.y_axis_var,
                              values=oxide_labels, state="readonly",
                              width=8, style="Axis.TCombobox")
        y_menu.grid(row=0, column=3, padx=2)
        y_menu.bind("<<ComboboxSelected>>", lambda e: self.update_plot())

        # Hook the pick event for interactive phase assignment.
        self.fig.canvas.mpl_connect("pick_event", self.on_plot_pick)

        return frame

    # %% ---- Plotting Functions ----

    def _current_axes(self) -> tuple[str, str]:
        """Return the raw (x_oxide, y_oxide) currently selected."""
        x_raw = self._label_to_raw.get(self.x_axis_var.get(), self.x_axis_var.get())
        y_raw = self._label_to_raw.get(self.y_axis_var.get(), self.y_axis_var.get())
        return x_raw, y_raw

    def _val(self, row, oxide) -> float:
        """Safely pull a single oxide value from a majors row."""
        try:
            return row[self.major_oxides.index(oxide)]
        except (ValueError, IndexError):
            return np.nan   # unknown oxide / short row -> NaN

    def get_axis_values(self) -> tuple[list[float], list[float]]:
        """X/Y arrays for every data-suite sample under the current selection."""
        x_ox, y_ox = self._current_axes()
        x_vals = [self._val(self.main_data[i], x_ox) for i in range(self.n_samples)]
        y_vals = [self._val(self.main_data[i], y_ox) for i in range(self.n_samples)]
        return x_vals, y_vals

    def update_plot(self) -> None:
        """Redraw the data-suite scatter, rescale, then overlay initial magma."""
        x_ox, y_ox = self._current_axes()
        x_vals, y_vals = self.get_axis_values()

        # Full redraw keeps the axes clean between oxide switches.
        self.ax.clear()

        # Data-suite points (pickable), styled from DATASUITE_MARKER_STYLE
        # picker=True is required so on_plot_pick still fires for assignment.
        self.scatter = self.ax.plot(
            x_vals, y_vals, picker=True, **self.DATASUITE_MARKER_STYLE)

        self.ax.set_xlabel(format_axis_labels(x_ox), fontsize=12)
        self.ax.set_ylabel(format_axis_labels(y_ox), fontsize=12)
        self.ax.set_title("Click a sample to assign it to a phase")
        self.ax.minorticks_on()
        self.ax.tick_params(axis="both", which="both", direction="in", top=True, right=True)

        # Autoscale with padding (guard against all-NaN columns).
        try:
            xa, ya = np.asarray(x_vals, float), np.asarray(y_vals, float)
            if np.isfinite(xa).any():
                xmn, xmx = np.nanmin(xa), np.nanmax(xa)
                xp = (xmx - xmn) * 0.05 if xmx > xmn else 0.5
                self.ax.set_xlim(xmn - xp, xmx + xp)
            if np.isfinite(ya).any():
                ymn, ymx = np.nanmin(ya), np.nanmax(ya)
                yp = (ymx - ymn) * 0.05 if ymx > ymn else 0.5
                self.ax.set_ylim(ymn - yp, ymx + yp)
        except Exception:
            pass  # leave matplotlib defaults on any numeric edge case

        # ax.clear() detached our overlay artists — reset the trackers so we # don't try to .remove() stale references in update_plot_highlights.
        self.composition_markers = [None] * len(self.PHASES)
        self.composition_lines = []

        # Draw the initial-magma composition overlay for the new axes.
        self.update_plot_highlights()
        self.canvas.draw_idle()

    def update_plot_highlights(self) -> None:
        """Add/remove the initial-magma markers + connecting line."""
        x_ox, y_ox = self._current_axes()

        # Remove any stale markers
        for idx, artist in enumerate(self.composition_markers):
            if artist is not None:
                try:
                    artist.remove()
                except Exception:
                    pass  # may already be detached after ax.clear()
                self.composition_markers[idx] = None

        # Remove any stale connecting lines
        for line in self.composition_lines:
            try:
                line.remove()
            except Exception:
                pass
        self.composition_lines = []

        # Draw one marker per phase; collect finite points for the line
        phase_points = []
        for p in range(len(self.PHASES)):
            xv = self._val(self.phase_data[p], x_ox)
            yv = self._val(self.phase_data[p], y_ox)
            phase_points.append((xv, yv))

            # Skip disabled (NaN) phases so we don't plant a marker at (0, 0).
            if not (np.isfinite(xv) and np.isfinite(yv)):
                continue

            marker = self.ax.scatter(
                [xv], [yv],
                edgecolor=self._phase_colour(p),   # per-phase outline colour
                label=self.PHASES[p],
                **self.COMPOSITION_MARKER_STYLE)
            self.composition_markers[p] = marker

        # Connect consecutive *finite* phase points
        finite = [(x, y) for (x, y) in phase_points if np.isfinite(x) and np.isfinite(y)]
        for i in range(len(finite) - 1):
            line, = self.ax.plot(
                [finite[i][0], finite[i + 1][0]],
                [finite[i][1], finite[i + 1][1]],
                **self.COMPOSITION_LINE_STYLE)
            self.composition_lines.append(line)

        self.canvas.draw_idle()

    def on_plot_pick(self, event) -> None:
        """Clicking a scatter point opens a phase-assignment dialog."""
        if not len(getattr(event, "ind", [])):
            return
        sample_idx = int(event.ind[0])   # first point under the cursor

        p = self.styler.palette

        dlg = tk.Toplevel(self)
        dlg.title(f"Assign {self.sample_names[sample_idx]}")
        dlg.geometry("300x320")
        dlg.configure(bg=p["bg"])
        dlg.attributes("-toolwindow", True)  # no taskbar icon on Windows
        dlg.transient(self)

        # move to the center of the parent window
        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2)
        dlg.geometry(f"+{x - dlg.winfo_width() // 2}+{y - dlg.winfo_height() // 2}")

        dlg.grab_set()

        ttk.Label(dlg, text=f"Assign '{self.sample_names[sample_idx]}' to:").pack(pady=(10, 5))
        radio_frame = ttk.Frame(dlg)
        radio_frame.pack(pady=(0, 10), padx=10, fill="x")

        phase_var = StringVar(value="None")
        ttk.Radiobutton(radio_frame, text="None", variable=phase_var,
                        value="None").pack(anchor="w", pady=2)
        for phase in self.PHASES:
            ttk.Radiobutton(radio_frame, text=phase, variable=phase_var,
                            value=phase).pack(anchor="w", pady=2)

        def assign() -> None:
            """Assign the selected sample to the chosen phase."""
            phase = phase_var.get()
            if phase in ("", "None"):
                dlg.destroy()
                return
            p_idx = self.PHASES.index(phase)
            # Copy the sample's majors into the phase row (explicit copy).
            self.phase_data[p_idx] = list(self.main_data[sample_idx])
            self.column_selectors[p_idx].set(self.sample_names[sample_idx])
            self._refresh_phase_sheet()
            self.update_plot_highlights()
            dlg.destroy()

        ttk.Button(dlg, text="Assign", command=assign).pack(pady=(5, 15))

    def on_select(self, label, i) -> None:
        """Handle a dropdown change for phase `i`."""
        if label == "[auto]":
            self.phase_data[i] = list(self.autocomp[i])       # copy
        elif label == "None":
            self.phase_data[i] = [np.nan] * self.n_major
        elif label in self.sample_names:
            idx = self.sample_names.index(label)
            self.phase_data[i] = list(self.main_data[idx])    # copy
        else:
            # Unknown label — leave the row unchanged (defensive).
            pass

        self.column_selectors[i].set(label)
        self._refresh_phase_sheet()
        self.update_plot_highlights()

    def _refresh_phase_sheet(self) -> None:
        """Push phase_data back into the phase composition table."""
        self.phase_sheet.set_sheet_data(self._fmt(self.phase_data))
        self.phase_sheet.set_column_widths([55] * self.n_major)
        self.phase_sheet.set_index_width(110)

    def on_apply(self) -> None:
        """
        Send the six selected sample labels to the caller and close.

        The callback receives a plain list, one entry per phase, each being
        one of: "[auto]", "None", or a sample name.
        """
        selected = [self.column_selectors[i].get()
                    for i in range(len(self.PHASES))]
        self.result = selected

        if callable(self._on_apply_cb):
            try:
                self._on_apply_cb(selected)
            except Exception as exc:
                # Surface callback errors instead of silently swallowing them.
                from tkinter import messagebox
                messagebox.showerror(
                    "Apply Failed",
                    f"Could not apply magma selection:\n{exc}")
                return
        self.destroy()

    def on_close(self) -> None:
        """
        Cancel: discard result and close.

        No model restore is needed — the model was never mutated.
        """
        self.result = None
        self.destroy()

    @staticmethod
    def _sample_label(idx):
        """Return a label for the sample at index `idx`."""
        return f"Sample {idx + 1}"

    @staticmethod
    def _fmt(data):
        """Format a 2D numeric list to 2-dp strings ('nan' where missing)."""
        return [ [f"{v:.2f}" if (v is not None and v == v) else "None" for v in row] for row in data ]
