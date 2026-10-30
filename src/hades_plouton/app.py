"""Main entry point for the Hades GUI application.

This module defines the HadesGUI class, which encapsulates the entire GUI application. It manages the layout, styling, and interaction with the underlying Hades model (Obol). The GUI allows users to input parameters, run simulations, and visualize results. It also handles theme switching, documentation access, and other user interface functionalities.
"""

# Dependencies (lazy-loaded)
from __future__ import annotations
from typing import TYPE_CHECKING, Any

# Use type checking to avoid circular imports and heavy dependencies at runtime
if TYPE_CHECKING:
    import numpy as np
    from tkinter import ttk
    from hades.model import Obol
    from hades_plouton.asset_manager import get_asset_path
    from hades.utils import (
        sanity_check,
        nice_display,
        get_nested_attr,
        set_nested_attr,
        convert_to_serialisable,
        sort_geochem,
        _deserialise,
        from_dict
    )
    from hades.logger import (
        setup_logger,
        log_gui,
        pause_logging,
        resume_logging,
    )   

# C-based imports (fast)
import time
t0 = time.time()
import sys, os, time, ctypes
from pathlib import Path
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import StringVar, BOTH, X, W, BOTTOM, HORIZONTAL, DISABLED, NORMAL

# Global module placeholders
np: Any = None
ttk : Any = None
Obol: Any = None
get_asset_path: Any = None
sanity_check: Any = None
nice_display: Any = None
get_nested_attr: Any = None
set_nested_attr: Any = None
convert_to_serialisable: Any = None
sort_geochem: Any = None
_deserialise: Any = None
from_dict: Any = None
setup_logger: Any = None
log_gui: Any = None
pause_logging: Any = None
resume_logging: Any = None

def format_axis_labels(label: str) -> str:
    """Placeholder for the original oxide/axis label formatter."""
    return label

def add_tooltip(widget, text: str) -> None:
    """Show a small tooltip while the pointer is over a widget."""
    tooltip = None
    show_after_id = None

    def show(_event=None) -> None:
        """Display the tooltip."""
        nonlocal tooltip, show_after_id
        if tooltip is not None:
            return
        show_after_id = None
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(
            f"+{widget.winfo_rootx() + 12}+"
            f"{widget.winfo_rooty() + widget.winfo_height() + 4}"
        )
        tk.Label(
            tooltip, text=text, background="#ffffe0", relief="solid",
            borderwidth=1, padx=5, pady=2,
        ).pack()

    def hide(_event=None) -> None:
        """Hide the tooltip."""
        nonlocal tooltip, show_after_id
        if show_after_id is not None:
            widget.after_cancel(show_after_id)
            show_after_id = None
        if tooltip is not None:
            tooltip.destroy()
            tooltip = None

    def schedule_show(_event=None) -> None:
        """Schedule the tooltip to be shown after a delay."""
        nonlocal show_after_id
        if show_after_id is None and tooltip is None:
            show_after_id = widget.after(500, show)

    widget.bind("<Enter>", schedule_show, add="+")
    widget.bind("<Leave>", hide, add="+")

class HadesGUI:
    """Hades GUI, wired to the modular styling & asset engines + backend Model"""
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialise the Hades GUI application."""
        self.root = root
        self.root.title("Hades")

        # key -> (VarType, model_path, default)
        self.VARIABLE_SPEC = {
            "mode":                (tk.StringVar, "meta.mode",               "subalkaline"),
            "submode":             (tk.StringVar, "meta.submode",            None),
            "iterations":          (tk.IntVar,    "optimising.max_iter",     500),
            "popsize":             (tk.IntVar,    "optimising.pop_size",     50),
            "FeO_Fe2pO_Ratio":     (tk.DoubleVar, "meta.FeO_Fe2pO_Ratio",    0.9),
            "data_suite_filepath": (tk.StringVar, "datasuite.filepath", "Click Browse... to load a data suite"),
        }
        
        N_MIN, N_OX = 16, 8
        # key -> (shape, VarType, model_path, dtype)
        self.ARRAY_SPEC = {
            "kd_values":               ((5, 11),        tk.DoubleVar,  "minerals.KD_vals",              np.float64),
            "usage":                   ((5, 16),        tk.BooleanVar, "minerals.usage",                np.bool_),
            "assimilant_composition":  ((32, 1),        tk.DoubleVar,  "assimilant.composition",        np.float64),
            "assimilant_pct":          ((5, 1),         tk.DoubleVar,  "assimilant.percentages",        np.float64),
            "custom_mineralogies":     ((5, N_MIN, N_OX), tk.DoubleVar, "minerals.custom_mineralogies", np.float64),
        }

        from hades_plouton.asset_manager import AssetManager
        from hades_plouton.styling import StyleManager

        # Call Assets (icons, logos, images)
        self.assets = AssetManager()

        # Geometry constraints (used as a fallback if maximise fails)
        self.root.minsize(950, 600)
        self.root.geometry("1100x600")

        # Styling engine
        self.styler = StyleManager(self.root, initial="light")
        self.style = self.styler.style
        self.current_theme = self.styler.current_theme
        self.palette = self.styler.palette
        for attr in ("font_main", "font_bold", "font_heading", "font_title", "font_subtitle", "font_authors"):
            setattr(self, attr, getattr(self.styler, attr))

        self.status_var = StringVar(value="Ready")
        self.vars = {}
        self.array_vars = {}
        self.short_filename = StringVar(value="Click Browse... to load a data suite")

        self.init_vars()                    # create scalar tk vars (hard-coded defaults)
        self.init_array_vars()              # 1b. create array tk vars (hard-coded defaults)
        self.init_aux_vars()                # vars that survive rebuilds
        self.reset_model()                # build the model FROM those default tk values

        # Load logos
        self.logos = {
            "light": self.assets.load_image("logo_light"),
            "dark": self.assets.load_image("logo_dark"),
        }

        # Build layout and paint theme
        self._create_layout()
        self.apply_theme("light")

        # Auto-maximise once everything is built
        self._maximise_window()

        print("GUI built in {:.3f} seconds.".format(time.time() - t0))

        # Intercept the OS window 'X' close button
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    # %% ---- Variable Set-up ----
    
    def init_vars(self) -> None:
        """
        Create all tkinter variable objects (StringVar, IntVar, etc.) based on self.VARIABLE_SPEC which are also found in the hades.model.Model instance
        """
        for key, (VarType, _path, default) in self.VARIABLE_SPEC.items():
            self.vars[key] = VarType(self.root, value=default)

    def _fresh_model(self, mode=None, submode=None, FeO_Fe2pO_Ratio=None) -> "hades.model.Obol":
        """
        Initialises and directly returns a new hades.model.Obol instance based on the current values of the relevant tk variables (mode, submode, FeO_Fe2pO_Ratio).

        In the event a new model should be created independent of the current GUI state, variables can be passed directly
        """
        if mode is None:
            mode = self.vars["mode"].get()
        if submode is None:
            submode = self.vars["submode"].get()
        if FeO_Fe2pO_Ratio is None:
            FeO_Fe2pO_Ratio = self.vars["FeO_Fe2pO_Ratio"].get()
            
        print(f"----\n## Initialising new Model with mode={mode}, submode={submode}, FeO_Fe2pO_Ratio={FeO_Fe2pO_Ratio}\n----")
        return Obol.newModel(
            mode=mode,
            submode=submode,
            FeO_Fe2pO_Ratio=FeO_Fe2pO_Ratio,
        )

    def reset_model(self) -> None:
        """
        Creates a new model using the GUI settings and updates tk variables from it
        """
        self.model = self._fresh_model()   # rebind; old one is GC'd
        self.model_to_vars()               # pull clean state into the GUI

    def init_aux_vars(self) -> None:
        """
        Initialise other tkinter variables which are only used for GUI display and/or depend on the model 
        """
        self.vars["Nsamples"] = StringVar(value="0")
        # TODO Remove hard-coded numbers
        n_cols = 12 if self.vars["mode"].get() == "subalkaline" else 13
        self.mineral_weights_table = [ [StringVar(value="") for _ in range(n_cols)] for _ in range(5) ]
        self.phase_total_vars = [StringVar(value="") for _ in range(n_cols)]

    def update_phase_totals(self) -> None:
        """
        Update the phase-total labels from the model without writing to the model."""
        totals = self.model.crystallisation_dict.get("total_minerals_wt", [None]*len(self.model.meta.minerals_))
        f_pct = self.model.crystallisation_dict.get("delta_S", None)
        totals = np.concatenate([totals, [100*f_pct.sum() if f_pct is not None else None]])

        for i, var in enumerate(self.phase_total_vars):
            if i < len(totals) and totals[i] is not None:
                var.set(f"{float(totals[i]):.2f}")
            else:
                var.set("")

    def _mineral_weights_sync(self, direction: str) -> None:
        """
        Sync the mineral-weights grid with the model results.

        Columns 0 .. len(minerals_)-1  <->  model.results[i].weights  (np.ndarray)
        Last column                    <->  model.results[i].F        (np.float64)

        Row i of self.mineral_weights_table maps to phase index i (0-4 inclusive).
        Results that don't exist yet (phase not run) are skipped/cleared.

        Directions: 
            "from_model"  ->  model.results -> tk vars
            "to_model"    ->  tk vars -> model.results
            "variable"   ->  return a 2D np.ndarray of the current tk var values (ignores model)
        """
        n_phases = len(self.mineral_weights_table)

        if direction == "variable":
            arr = np.array(
                [
                    [
                        float(var.get()) if var.get() != "" else 0
                        for var in row
                    ]
                    for row in self.mineral_weights_table
                ],
                dtype=float,
            ) / 100
            # Move the last column (F) to the first column
            arr = np.hstack((arr[:, -1][:, np.newaxis], arr[:, :-1]))
            return arr

        for i in range(n_phases):
            row_vars = self.mineral_weights_table[i]
            mineral_vars, f_var = row_vars[:-1], row_vars[-1]

            # Guard: the result for this phase may not exist yet
            try:
                result = self.model.results[i]
            except (IndexError, KeyError, TypeError):
                result = None

            # model -> vars
            if direction == "from_model":
                if result is None:
                    for var in row_vars:
                        var.set("")
                    continue

                # weights (minerals)
                weights = getattr(result, "weights", None)
                if weights is None:
                    for var in mineral_vars:
                        var.set("")
                else:
                    flat = np.ravel(weights)
                    for j, var in enumerate(mineral_vars):
                        if j < flat.size:
                            val = flat[j]
                            # Display percentages rounded to 2dp; model values remain 0-1.
                            var.set(
                                ""
                                if val is None or np.isnan(val)
                                else round(val * 100, 2)
                            )
                        else:
                            var.set("")

                # F (np.float64 scalar)
                F = getattr(result, "F", None)
                f_var.set(
                    ""
                    if F is None or np.isnan(F) or F == 0
                    else round(F * 100, 2)
                )

            # vars -> model 
            elif direction == "to_model":
                if result is None:
                    continue   # nothing computed yet to write into

                # weights (minerals)
                weights = getattr(result, "weights", None)
                if weights is not None:
                    orig = np.asarray(weights)
                    flat = np.ravel(orig).astype(float, copy=True)
                    for j in range(flat.size):
                        raw = mineral_vars[j].get() if j < len(mineral_vars) else ""
                        try:
                            if raw != "":
                                value = float(raw) / 100
                                if not np.isnan(value):
                                    flat[j] = value
                        except ValueError:
                            pass  # leave the existing value unchanged
                    result.weights = flat.reshape(orig.shape)

                # F (write back as np.float64)
                raw = f_var.get()
                if raw != "":
                    try:
                        result.F = np.float64(raw) / 100
                    except ValueError:
                        pass  # leave F unchanged on bad input

            else:
                raise ValueError(f"Unknown direction: {direction!r}")

    def _clear_mineral_table(self, phase_idx: int) -> None:
        """
        Clear the mineral weights table for a specific phase index and all downstream phases.
        """
        n_phases = len(self.mineral_weights_table)
        for i in range(phase_idx, n_phases):
            for var in self.mineral_weights_table[i]:
                var.set("")

    def _clear_totals_row(self) -> None:
        """
        Clear the phase totals row in the mineral weights table.
        """
        for var in self.phase_total_vars:
            var.set("")

    def init_array_vars(self) -> None:
        """Create nested tkinter variable objects (DoubleVar, BooleanVar, etc.) based on self.ARRAY_SPEC which are also found in the hades.model.Model instance."""
        self.array_vars = {}
        for key, (shape, VarType, _path, _dtype) in self.ARRAY_SPEC.items():
            self.array_vars[key] = self._make_nested_vars(shape, VarType, self.root)

    def _make_nested_vars(self, shape, VarType, root) -> list:
        """Build a nested list of tk vars matching `shape`."""
        if len(shape) == 1:
            return [VarType(root) for _ in range(shape[0])]
        return [self._make_nested_vars(shape[1:], VarType, root) for _ in range(shape[0])]

    def _nested_set(self, nested, arr) -> None:
        """model ndarray -> nested tk vars."""
        arr = np.asarray(arr)
        # leaf level: `nested` is a list of Variables
        if isinstance(nested[0], tk.Variable):
            for i, var in enumerate(nested):
                val = arr[i]
                if hasattr(val, "item"):            # numpy scalar -> python scalar
                    val = val.item()
                var.set(round(val, 2) if isinstance(val, float) else val)
        else:
            for i, sub in enumerate(nested):
                self._nested_set(sub, arr[i])

    def _nested_get(self, nested, dtype) -> np.ndarray:
        """nested tk vars -> ndarray."""
        if isinstance(nested[0], tk.Variable):
            return np.array([v.get() for v in nested], dtype=dtype)
        return np.array([self._nested_get(sub, dtype) for sub in nested], dtype=dtype)

    def _arrays_from_model(self) -> None:
        """model ndarray -> nested tk vars."""
        for key, (shape, _VT, path, _dtype) in self.ARRAY_SPEC.items():
            try:
                arr = get_nested_attr(self.model, path)
            except AttributeError:
                log_gui(f"Warning: array path '{path}' not found", level=14)
                continue

            arr = np.asarray(arr)
            if arr.shape != tuple(shape):
                try:
                    arr = arr.reshape(shape)
                except ValueError:
                    log_gui(f"Warning: '{path}' shape {arr.shape} != {shape}; skipping", level=14)
                    continue

            old_arr = self._nested_get(self.array_vars[key], arr.dtype)
            self._nested_set(self.array_vars[key], arr)
            if not np.array_equal(old_arr, arr):
                log_gui(f"[#] {path}: (shape {old_arr.shape}; sum={np.nansum(old_arr):.3f} -> {arr.shape}; sum={np.nansum(arr):.3f})", level=14)
            else:
                log_gui(f"[ ] {path}: (shape {arr.shape}; sum={np.nansum(arr):.3f})", level=14)

    def _arrays_to_model(self) -> None:
        """nested tk vars -> model ndarray."""
        for key, (shape, _VT, path, dtype) in self.ARRAY_SPEC.items():
            new = self._nested_get(self.array_vars[key], dtype)      # grid-shaped

            # Match whatever shape the model currently uses (e.g. (32,) not (32,1))
            try:
                target = np.asarray(get_nested_attr(self.model, path)).shape
            except AttributeError:
                target = tuple(shape)

            orig = np.asarray(get_nested_attr(self.model, path))

            if not np.array_equal(orig, new.reshape(target)):
                log_gui(f"[#] {path}: (shape {orig.shape}; sum={np.nansum(orig):.3f}) -> (shape {new.reshape(target).shape}; sum={np.nansum(new):.3f})", level=14)
            else:
                log_gui(f"[ ] {path}: (shape {orig.shape}; sum={np.nansum(orig):.3f})", level=14)

            set_nested_attr(self.model, path, new.reshape(target))

    def model_to_vars(self) -> None:
        """model (scalars + arrays) -> tk variables."""
        log_gui(f"Syncing Hades Model --> GUI", level=7)

        # arrays
        self._arrays_from_model()
        # mineral weights table
        self._mineral_weights_sync("from_model")
        # assimilant traces count
        self._update_assimilant_traces()
        # Crystallisation totals are display-only and flow from model -> GUI.
        self.update_phase_totals()

        # scalars
        for key, (_VarType, path, default) in self.VARIABLE_SPEC.items():
            try:
                value = get_nested_attr(self.model, path)
            except AttributeError as exc:
                # print(f"Warning: could not get {path}: {exc}. Using default '{default}'")
                log_gui(f"Warning: could not get {path}: {exc}. Using default '{default}'", level=14)
                value = default
            if hasattr(value, "item"):          # numpy scalar -> python scalar
                value = value.item()
            current = self.vars[key].get()
            if current != value:
                # print(f"model_to_vars: {path}: {current!r} -> {value!r}")
                log_gui(f"[#] {path}: {current!r} -> {value!r}", level=14)
            else:
                # print(f"model_to_vars: {path}: {current!r} [no change]")
                log_gui(f"[ ] {path}: {current!r}", level=14)
            self.vars[key].set("" if value is None else round(value, 2) if isinstance(value, float) else value)

        log_gui(f"", level=6)

    def vars_to_model(self):
        """tk variables -> model (scalars + arrays)."""
        log_gui(f"Syncing GUI --> Hades Model", level=7)

        # arrays
        self._arrays_to_model()
        # mineral weights table
        self._mineral_weights_sync("to_model")

        # scalars
        for key, (_VarType, path, _default) in self.VARIABLE_SPEC.items():
            try:
                orig = get_nested_attr(self.model, path)
                new = self.vars[key].get()
                set_nested_attr(self.model, path, new)
                if orig != new:
                    # print(f"vars_to_model: {path}: {orig!r} -> {new!r}")
                    log_gui(f"[#] {path}: {orig!r} -> {new!r}", level=14)
                else:
                    # print(f"vars_to_model: {path}: {orig!r} [no change]")
                    log_gui(f"[ ] {path}: {orig!r}", level=14)
            except Exception as exc:  # noqa: BLE001
                # print(f"Warning: could not set {path}: {exc}")
                log_gui(f"Warning: could not set {path}: {exc}", level=14)

        log_gui(f"", level=6)

    def _reset_vars_to_defaults(self):
        """GUI-only: reset ALL editable tk vars to their declared/natural defaults.
        Does NOT touch the model."""

        print("Resetting all tk vars to their declared/natural defaults...", end='')

        # scalar vars (preserve mode/submode)
        for key, (_VarType, _path, default) in self.VARIABLE_SPEC.items():
            if key not in ("mode", "submode"):
                self.vars[key].set(default)

        # array vars (reset to VarType's natural zero)
        for key, (rows, cols, VarType, _path, _dtype) in self.ARRAY_SPEC.items():
            default = False if VarType is tk.BooleanVar else 0.0
            for i in range(rows):
                for j in range(cols):
                    self.array_vars[key][i][j].set(default)

        # mineral weights table
        for row in self.mineral_weights_table:
            for var in row:
                var.set("")

        # aux / derived display vars
        self.vars["Nsamples"].set("0")

        # repaint dependent widgets
        self._update_assimilant_traces()

    # %% ---- GUI Construction ----

    def _maximise_window(self) -> None:
        """Attempt to maximise the window using platform-specific methods."""
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                w = self.root.winfo_screenwidth()
                h = self.root.winfo_screenheight()
                self.root.geometry(f"{w}x{h}+0+0")

    def apply_theme(self, name: str) -> None:
        """Apply a theme to the GUI."""
        self.styler.apply(name)
        self.current_theme = name
        self.palette = self.styler.palette
        if hasattr(self, "logo_label"):
            logo = self.logos.get(name)
            if logo:
                self.logo_label.configure(image=logo)

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes [obsolete]."""
        new = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new)
        self._log(f"Toggled theme.")

    def _create_layout(self) -> None:
        """Create the main layout of the GUI."""
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        status_bar = ttk.Frame(self.root)
        status_bar.pack(side=BOTTOM, fill=X)
        from tkinter import LEFT, RIGHT

        status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var,
            anchor=W,
            style="StatusBar.TLabel",
            padding=6,
        )
        status_label.pack(side=LEFT, fill=X, expand=True)

        # Display the version and update link at the right end of the status bar.
        update_link_font = tkfont.Font(root=self.root, font=self.font_main)
        update_link_font.configure(underline=True)
        status_info = ttk.Frame(status_bar)
        status_info.pack(side=RIGHT, padx=(0, 10))
        from hades import __version__ as hades_version
        ttk.Label(
            status_info,
            text=f"Hades v{hades_version}",
            style="StatusBar.TLabel",
            padding=2,
        ).pack(side=LEFT)
        ttk.Label(
            status_info,
            text=f" | ",
            style="StatusBar.TLabel",
            padding=2,
        ).pack(side=LEFT)
        update_link = ttk.Label(
            status_info,
            text="Check for updates",
            font=update_link_font,
            cursor="hand2",
            style="StatusBar.TLabel",
            padding=2,
        )
        update_link.pack(side=LEFT)
        update_link.bind("<Button-1>", lambda _event: self.handle_update_check())

        self.main_pane = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        self.main_pane.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.control_frame = self._create_control_panel(self.main_pane)
        self.main_pane.add(self.control_frame, weight=1)

        self.viz_frame = self._create_graph_panel(self.main_pane)
        self.main_pane.add(self.viz_frame, weight=3)

    def _create_control_panel(self, parent) -> ttk.Frame:
        """Create the control panel frame with all input widgets."""
        panel = ttk.Frame(parent, padding=10)
        panel.columnconfigure(0, weight=1)
        self.create_title_section(panel, 0)
        self._CP_initial_magma(panel, 1)
        self._CP_assimilant_input(panel, 2)
        self._CP_main_inputs(panel, 3)
        self._CP_button_panel(panel, 4)
        return panel

    def rebuild_control_panel(self) -> None:
        """Tear down and rebuild the model-dependent control panel."""
        # Destroy existing widgets inside the control frame
        for child in self.control_frame.winfo_children():
            child.destroy()

        # Recreate aux vars (dimensions may have changed)
        self.init_aux_vars()

        # Rebuild the sub-panels from the current model
        self.control_frame.columnconfigure(0, weight=1)
        self.create_title_section(self.control_frame, 0)
        self._CP_initial_magma(self.control_frame, 1)
        self._CP_assimilant_input(self.control_frame, 2)   # rereads oxides/phases
        self._CP_main_inputs(self.control_frame, 3)         # rereads minerals
        self._CP_button_panel(self.control_frame, 4)

    def refresh_gui(self) -> None:
        """Call after reset_model() so the GUI matches the new model shape."""
        self.rebuild_control_panel()

    def get_docs_path(self) -> Path:
        """Resolves the local path to docs, handling PyInstaller environment."""
        if getattr(sys, 'frozen', False):
            # Running inside PyInstaller bundle
            if hasattr(sys, '_MEIPASS'):
                # Built with --onefile
                base_path = Path(sys._MEIPASS)
            else:
                # Built with --onedir
                base_path = Path(sys.executable).parent
        else:
            # Running from source code (project root)
            base_path = Path(__file__).resolve().parent.parent.parent

        # Path to Sphinx build output relative to base_path
        print(f"docs base path: {base_path}")
        print(f"docs path: {base_path / 'docs' / '_build' / 'html' / 'index.html'}")
        return base_path / "docs" / "_build" / "html" / "index.html"

    def open_documentation(self, local=False) -> None:
        """Open online documentation when available, otherwise use local docs."""
        import webbrowser

        if local:
            local_docs = self.get_docs_path()
            if local_docs.exists():
                # pathlib's as_uri() correctly formats file:/// C:/... for web browsers
                webbrowser.open(local_docs.as_uri())
            else:
                self._log(f"Local documentation not found at {local_docs}. Attempting to open online docs.")
                return 

        else:

            docs_url = "https://hades-obol.readthedocs.io/en/latest/"
            try:
                webbrowser.open(docs_url)
                self._log("Documentation opened")
            except Exception as e:
                print(f"Error: Could not open online documentation at {docs_url}: {e}") 
                self._log("Documentation not reachable - search online")

    def handle_update_check(self) -> None:
        from hades.updates import check_for_updates
        from tkinter import messagebox
        
        available, latest_version = check_for_updates(gui=True)
        
        if available:
            messagebox.showinfo(
                "Update Available", 
                f"A new version of Hades is available: {latest_version}. Please visit the Hades GitHub page to download the latest version."
            )
            self._log(f"Update available: {latest_version}.")
        else:
            if latest_version is not None:
                # ADDED: Show a popup so the user knows they are up-to-date
                messagebox.showinfo(
                    "Up to Date", 
                    f"You are using the latest version of Hades (v{latest_version})."
                )
                self._log("You are using the latest version of Hades.")
            else:
                messagebox.showinfo(
                    "Update Check", 
                    "Could not check for updates. Note that this function requires an internet connection.\nCheck manually at https://github.com/Jack6228/Hades."
                )
                self._log("Could not check for updates.")

    def create_title_section(self, parent, row) -> None:
        """Create the title section of the GUI with logo, title, subtitle, and setup options."""
        title_frame = ttk.Frame(parent, padding=(10, 10))
        title_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        title_frame.columnconfigure(0, weight=1)
        title_frame.columnconfigure(1, weight=0)

        left = ttk.Frame(title_frame)
        left.grid(row=0, column=0, sticky="w")
        left.columnconfigure(1, weight=1)

        active_logo = self.logos.get(self.current_theme)
        if active_logo:
            self.logo_label = ttk.Label(left, image=active_logo)
        else:
            print(f"Warning: no logo found for theme '{self.current_theme}'; using placeholder")
            self.logo_label = ttk.Label(left, text="◆", font=("Segoe UI", 28))
        self.logo_label.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky="nw")

        ttk.Label(left, text="Hades", style="Title.TLabel").grid(
            row=0, column=1, sticky="w", padx=5, pady=(5, 0))
        ttk.Label(left, text="Mass Balance Fractional Crystallisation Modelling",
                  style="Subtitle.TLabel").grid(row=1, column=1, sticky="w", padx=5, pady=(0, 5))

        # add link to launch docs
        # docs_button = ttk.Button(left, text="Documentation", command=lambda: self.open_documentation(local=True))
        # docs_button.grid(row=3, column=1, sticky="w", padx=5, pady=(0, 5))

        setup = ttk.LabelFrame(title_frame, text="Setup", padding=10)
        setup.grid(row=0, column=1, sticky="ne", padx=(20, 0))

        ttk.Label(setup, text="Data Suite Rock Type:", font=("", 9, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=(5, 2), pady=5)

        self.subalk_radio = ttk.Radiobutton(
            setup, text="Subalkaline", variable=self.vars["mode"],
            value="subalkaline", command=self.on_mode_change)
        self.subalk_radio.grid(row=1, column=0, sticky="w", padx=2, pady=5)
        self.alk_radio = ttk.Radiobutton(
            setup, text="Alkaline", variable=self.vars["mode"],
            value="alkaline", command=self.on_mode_change)
        self.alk_radio.grid(row=1, column=1, sticky="w", padx=2, pady=5)

        self.tholeiitic_radio = ttk.Radiobutton(
            setup, text="Tholeiitic", variable=self.vars["submode"],
            value="tholeiitic", command=self.on_submode_change)
        self.tholeiitic_radio.grid(row=2, column=0, sticky="w", padx=2, pady=5)
        self.calcalk_radio = ttk.Radiobutton(
            setup, text="Calc-alkaline", variable=self.vars["submode"],
            value="calcalkaline", command=self.on_submode_change)
        self.calcalk_radio.grid(row=2, column=1, sticky="w", padx=2, pady=5)

        self._sync_submode_state()   # set initial enabled/disabled state


    def _CP_initial_magma(self, parent, row) -> None:
        """Create the initial magma data input section."""
        frame = ttk.LabelFrame(parent, text=" Magmatic Data ", padding=10)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        # Give column 1 weight so the Entry expands to fill available width
        frame.columnconfigure(1, weight=1)
        # Give column 6 weight to push the right-aligned buttons to the far right edge
        frame.columnconfigure(6, weight=1)

        # Column 0: Label
        ttk.Label(frame, text="Data Suite", font=("", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(5, 2), pady=5)
        
        # Column 1: Entry (Wider and stretching)
        # Set a larger width base value and let weight=1 handle horizontal expansion
        ttk.Entry(frame, textvariable=self.short_filename, width=25).grid(
            row=0, column=1, sticky="ew", padx=(2, 10), pady=5
        )

        # Columns 2 & 3: Action Buttons (Left-aligned area)
        b1 = ttk.Button(frame, text="Browse...", command=self.browse_data_suite)
        b1.grid(row=0, column=2, padx=3, pady=5)
        add_tooltip(b1, "Browse and load geochemical data from a file")

        b2 = ttk.Button(frame, text="Set Samples", command=self.edit_data_suite)
        b2.grid(row=0, column=3, padx=3, pady=5)
        add_tooltip(b2, "Select magma compositions")

        # Column 4 & 5: Sample Count Labels
        # Column 4: "No. samples:" aligned to the right (e) of its cell
        ttk.Label(frame, text="No. samples:", font=("", 9, "bold")).grid(row=0, column=4, sticky="e", padx=(10, 2), pady=5)
        
        # Column 5: Sample count value aligned to the left (w) of its cell
        ttk.Label(frame, width=4, anchor="w", textvariable=self.vars["Nsamples"], font=("", 9, "bold")).grid(
            row=0, column=5, sticky="w", padx=(0, 10), pady=5
        )

        # Columns 6 & 7: Configuration Buttons (Aligned to the Right)
        # Adding sticky="e" inside column 6/7 pushes these buttons to the far right edge
        configure_button = ttk.Button(frame, text="Configure", command=self.open_advanced_config_window)
        configure_button.grid(row=0, column=6, sticky="e", padx=3, pady=5)

        load_config_button = ttk.Button(frame, text="Load Config File", command=self.load_config_file)
        load_config_button.grid(row=0, column=7, sticky="e", padx=(3, 5), pady=5)

        add_tooltip(configure_button, "Open parameter configuration")
        add_tooltip(load_config_button, "Load a configuration file")  

    def _CP_assimilant_input(self, parent, row) -> None:
        """Create the assimilant input section with composition and phase percentages."""
        frame = ttk.LabelFrame(parent, text=" Assimilant Input ", padding=10)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        # Allow both primary sides (Left: Composition/Traces, Right: Phase %) to share space
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # ==================== LEFT PANEL: COMPOSITION & TRACES ====================
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_frame.columnconfigure(0, weight=1)

        # Composition Header & Load Button Bar
        comp_header_frame = ttk.Frame(left_frame)
        comp_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        comp_header_frame.columnconfigure(0, weight=1)

        ttk.Label(comp_header_frame, text="Assimilant Composition (wt%)", font=("", 9, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        load_btn = ttk.Button(comp_header_frame, text="Load Assimilant", command=self._load_assimilant_file)
        load_btn.grid(row=0, column=1, sticky="e")
        add_tooltip(load_btn, "Load assimilant composition from file")

        # Oxide Composition Table
        oxide_labels = self.model.namespace.oxides[:8]
        table = ttk.Frame(left_frame)
        table.grid(row=1, column=0, sticky="ew")

        self.assimilant_entries = []
        for j, label in enumerate(oxide_labels):
            table.columnconfigure(j, weight=1)

            ttk.Label(
                table,
                text=format_axis_labels(label),
                style="TableHead.TLabel",
                anchor="center",
                relief="solid",
                borderwidth=1,
            ).grid(row=0, column=j, sticky="nsew")

            entry = ttk.Entry(
                table,
                textvariable=self.array_vars["assimilant_composition"][j],
                width=6,
                justify="center",
            )
            entry.grid(row=1, column=j, sticky="nsew")
            # entry.bind("<Control-v>", self._assimilant_paste_handler)
            self.assimilant_entries.append(entry)

        # Trace Elements Display Row
        _base = tkfont.nametofont("TkDefaultFont")
        self._trace_font_off = tkfont.Font(
            family=_base.actual("family"), size=_base.actual("size"), weight="normal"
        )
        self._trace_font_on = tkfont.Font(
            family=_base.actual("family"), size=_base.actual("size"), weight="bold"
        )

        trace_frame = ttk.Frame(left_frame)
        trace_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.assimilant_trace_labels = []
        trace_symbols = self.model.namespace.traces

        ttk.Label(trace_frame, text="Traces:", font=("", 8, "italic")).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )

        for k, sym in enumerate(trace_symbols):
            lbl = ttk.Label(
                trace_frame,
                text=format_axis_labels(sym),
                font=self._trace_font_off,
                foreground="grey",
            )
            lbl.grid(row=0, column=k + 1, sticky="w", padx=3)
            self.assimilant_trace_labels.append(lbl)

        self._update_assimilant_traces()

        # Right panel: Phase % Input
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        right_frame.columnconfigure(0, weight=1)

        # Phase % Header
        ttk.Label(
            right_frame, text="Assimilant % added per phase (0–100):", font=("", 9, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        # Phase Grid
        pct_frame = ttk.Frame(right_frame)
        pct_frame.grid(row=1, column=0, sticky="ew")

        phases_short = self.model.namespace.phases_short[:5]
        self.assimilant_pct_entries = []

        for i, phase_name in enumerate(phases_short):
            pct_frame.columnconfigure(i, weight=1)

            ttk.Label(
                pct_frame,
                text=phase_name,
                style="TableHead.TLabel",
                anchor="center",
                relief="solid",
                borderwidth=1,
            ).grid(row=0, column=i, sticky="nsew")

            e = ttk.Entry(
                pct_frame,
                textvariable=self.array_vars["assimilant_pct"][i],
                width=6,
                justify="center",
            )
            e.grid(row=1, column=i, sticky="nsew")
            self.assimilant_pct_entries.append(e)

    def _CP_main_inputs(self, parent, row) -> None:
        """Create the main inputs section for mineral modal abundances and related controls."""
        frame = ttk.LabelFrame(parent, text=" Mineral Modal Abundances ", padding=10)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        self.buttons = []
        names = ["Primary", "Primitive", "Basic", "Intermed.", "Evolved"]
        minerals = self.model.namespace.minerals_short
        minerals = [m for i, m in enumerate(minerals) if self.model.namespace.minerals[i] in self.model.meta.minerals_]
        cols = minerals + ["FC%"]
        Nminerals = len(self.model.meta.minerals_)

        for i in range(len(cols)):
            ttk.Label(frame, text=cols[i], anchor="center").grid(
                row=0, column=i + 1, sticky="ew", padx=2, pady=2)

        for i in range(len(names)):
            ttk.Label(frame, text=names[i], font=("", 9, "bold")).grid(row=i + 1, column=0, sticky="w", padx=5, pady=5)
            button_row = []
            for j in range(len(cols)):
                # Ensure FC% is the last column, even if the number of minerals is less than the max columns
                target_col = (len(cols) - 1) if (j == Nminerals) else j
                ttk.Entry(frame, textvariable=self.mineral_weights_table[i][target_col],
                          width=6, justify="center").grid(
                    row=i + 1, column=target_col + 1, sticky="ew", padx=2, pady=2)

            btn_view = ttk.Button(frame, text="View", command=lambda idx=i: self.view_phase(idx))
            btn_run = ttk.Button(frame, text="Run", command=lambda idx=i: self.run_phase(idx))
            btn_reset = ttk.Button(frame, text="Reset", command=lambda idx=i: self.reset_phase(idx))
            btn_view.grid(row=i + 1, column=len(cols) + 1, sticky="ew", padx=5, pady=5)
            btn_run.grid(row=i + 1, column=len(cols) + 2, sticky="ew", padx=5, pady=5)
            btn_reset.grid(row=i + 1, column=len(cols) + 3, sticky="ew", padx=5, pady=5)

            add_tooltip(btn_view, f"Model values in the table")
            add_tooltip(btn_run, f"Find optimal mineral solution")
            add_tooltip(btn_reset, f"Reset to this phase")

            button_row.extend([btn_view, btn_run, btn_reset])
            self.buttons.append(button_row)

        # Add text labels for dynamic updating numbers on the bottom row
        ttk.Label(frame, text='Totals', font=("", 9)).grid(row=len(names) + 1, column=0, sticky="e", padx=5, pady=5)
        for j in range(len(cols)):
            ttk.Label(frame, textvariable=self.phase_total_vars[j], anchor="center", font=("", 9)).grid(row=len(names) + 1, column=j + 1, sticky="ew", padx=2, pady=2)

        # Sequential gating: only the first phase is runnable at startup
        self._apply_button_states()

        frame.grid_columnconfigure(tuple(range(len(cols) + 4)), weight=1)

    def _CP_button_panel(self, parent, row) -> None:
        """Create the bottom button panel with action buttons for TAS, mineralogy, export, and reset."""
        frame = ttk.LabelFrame(parent, text=" Optimisation & Controls ", padding=10)
        frame.grid(row=row, column=0, sticky="ew")

        # Configure weight on ALL columns containing buttons so they expand equally
        # Columns 2 through 6 contain the 5 button pairs
        for col in range(2, 7):
            frame.columnconfigure(col, weight=1)

        # ROW 0: Max Iterations
        ttk.Label(frame, text="Max. iterations:", font=("", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(5, 2), pady=5)
        ttk.Spinbox(frame, from_=10, to=1000, increment=10,
                    textvariable=self.vars["iterations"], width=5).grid(
            row=0, column=1, sticky="w", padx=(0, 15), pady=5)

        # ROW 1: Population Size
        ttk.Label(frame, text="Population size:", font=("", 9, "bold")).grid(row=1, column=0, sticky="w", padx=(5, 2), pady=5)
        ttk.Spinbox(frame, from_=10, to=100, increment=2,
                    textvariable=self.vars["popsize"], width=5).grid(
            row=1, column=1, sticky="w", padx=(0, 15), pady=5)

        # ACTION BUTTONS
        b1 = ttk.Button(frame, text="TAS Diagram", command=self.make_TAS)
        b2 = ttk.Button(frame, text="View Mineralogy", command=self.make_bulk_min_wdw)
        b3 = ttk.Button(frame, text="Export Config", command=self.save_config_file)
        b4 = ttk.Button(frame, text="Export PDF", command=self.export_pdf)
        b5 = ttk.Button(frame, text="Export Data", command=self.export_data)
        b6 = ttk.Button(frame, text="Trace Elements", command=self.trace_window)
        b7 = ttk.Button(frame, text="Reset Defaults", command=self.reset_all_fields)
        b8 = ttk.Button(frame, text="Reset Plot", command=self.reset_plot)
        b19 = ttk.Button(frame, text="Help", command=self.open_documentation)
        b10 = ttk.Button(frame, text="Quit", command=self.quit_app)

        buttons = [b1, b2, b3, b4, b5, b6, b7, b8, b19, b10]
        tooltips = [
            "Generate TAS diagram from current data",
            "View bulk mineralogy of current data",
            "Export current configuration to a file",
            "Export results to a PDF file",
            "Export results to a CSV file",
            "Model trace elements",
            "Completely reset Hades",
            "Reset the visualisation panel",
            "Open the Hades documentation",
            "Quit Hades"
        ]

        # Grid buttons starting at Column 2 (leaving 0 & 1 for labels/spinboxes)
        for i, btn in enumerate(buttons):
            col_idx = 2 + (i // 2)
            row_idx = i % 2
            btn.grid(row=row_idx, column=col_idx, sticky="ew", padx=3, pady=3)
            add_tooltip(btn, tooltips[i])

    # %% ---- GUI Update Functions ----

    def _update_assimilant_traces(self) -> None:
        """
        Bold + colour each trace-element symbol if its value is non-zero,
        otherwise show it greyed / non-bold to indicate absence.
        """
        if not getattr(self, "assimilant_trace_labels", None):
            return

        data = self.model.assimilant.composition
        for k, lbl in enumerate(self.assimilant_trace_labels):
            idx = 8 + k                      # traces live after the first 8 oxides
            val = ""
            if data is not None and idx < len(data):
                try:
                    v = float(data[idx])
                    val = "" if np.isnan(v) else v
                except (TypeError, ValueError):
                    val = ""

            if val != "" and val != 0:
                lbl.configure(font=self._trace_font_on, foreground="black")
            else:
                lbl.configure(font=self._trace_font_off, foreground="grey")

    def _load_assimilant_file(self) -> None:
        """
        use the model's function to set assimilation
        """
        from tkinter import filedialog, messagebox
        filepath = filedialog.askopenfilename(
            title="Select Assimilant Data File",
            filetypes=[("Data Files", "*.txt *.csv *.xlsx"), ("All Files", "*.*")]
        )
        if not filepath:
            return  # User cancelled

        try:
            self.model.set_assimilant(filepath=filepath)
            # Update vars with model
            self.model_to_vars()
        except Exception as e:
            messagebox.showerror("Error Loading File", f"An error occurred while loading the assimilant data file:\n{e}")

    def _create_axis_controls(self, parent, oxides) -> None:
        """
        Build the X / Y axis Combobox row inside *parent* (the controls frame).
        Stores StringVars as self.x_axis_vars / self.y_axis_vars.
        """
        from hades.visuals import format_axis_labels, format_label

        axes_frame = ttk.Frame(parent)
        axes_frame.grid(row=1, column=0, sticky="ew", pady=8)
        axes_frame.grid_columnconfigure(tuple(range(10)), weight=1)

        oxide_labels = format_axis_labels(oxides)   # pass the full list — not one string at a time

        # Xxaxes (2 selectors) 
        ttk.Label(axes_frame, text="X-axes:").grid(row=0, column=0, padx=5, sticky="e")

        # Cleaner loop that keeps the widget reference for gridding:
        self.x_axis_vars = []
        for i in range(2):
            val = (format_label(self.bivar_plot.x_order[i])
                if i < len(self.bivar_plot.x_order) else oxide_labels[i])
            var = StringVar(value=val)
            self.x_axis_vars.append(var)
            cb = ttk.Combobox(axes_frame, textvariable=var, values=oxide_labels,
                            state="readonly", width=7, style="Axis.TCombobox")
            cb.bind("<<ComboboxSelected>>", lambda e: self._on_axes_change())
            cb.grid(row=0, column=i + 1, padx=2)

        # Y-axes (up to 6 selectors) 
        ttk.Label(axes_frame, text="Y-axes:").grid(row=0, column=3, padx=5, sticky="e")

        self.y_axis_vars = []
        for i in range(6):
            val = (format_label(self.bivar_plot.y_order[i])
                if i < len(self.bivar_plot.y_order) else "None")
            var = StringVar(value=val)
            self.y_axis_vars.append(var)
            cb = ttk.Combobox(axes_frame, textvariable=var,
                            values=["None"] + oxide_labels,
                            state="readonly", width=7, style="Axis.TCombobox")
            cb.bind("<<ComboboxSelected>>", lambda e: self._on_axes_change())
            cb.grid(row=0, column=i + 4, padx=2)

    def _on_axes_change(self) -> None:
        """
        Called whenever any axis Combobox changes.
        Converts formatted labels back to raw oxide names, then asks the
        visualiser to rebuild itself and replot.
        """
        from hades.visuals import format_axis_labels

        oxides = self.model.namespace.oxides
        label_to_raw = dict(zip(format_axis_labels(oxides), oxides))

        x_order = [label_to_raw.get(v.get(), v.get()) for v in self.x_axis_vars]
        y_order = [label_to_raw.get(v.get(), v.get()) for v in self.y_axis_vars if v.get() not in ('', 'None')]

        if not x_order or not y_order:
            return

        # rebuild() tears down the old canvas/toolbar, creates a new figure with the updated axis grid, and remounts everything.
        self.bivar_plot.rebuild(x_order=x_order, y_order=y_order)

        self.bivar_plot.plot_data_suite(model=self.model)
        self.bivar_plot.plot_magma(self.model, mode='initial')
        self.bivar_plot.plot_magma(self.model, mode='computed')

    def _create_graph_panel(self, parent) -> ttk.Frame:
        """
        Build the bivariate plot panel: canvas, toolbar, and axis selectors.
        Stores the visualiser as self.bivar_plot for use by other methods.
        Returns the outer ttk.Frame so the caller can grid/pack it.
        """
        from hades_plouton.visuals_GUI import BivariateVisualiser

        # Outer frame
        frame = ttk.Frame(parent, padding=10)
        frame.grid_rowconfigure(0, weight=1)    # canvas expands
        frame.grid_rowconfigure(1, weight=0)    # controls stay fixed
        frame.grid_columnconfigure(0, weight=1)

        # Controls strip (toolbar + axis selectors)
        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=1, column=0, sticky="ew")
        controls_frame.columnconfigure(0, weight=1)

        # Visualiser
        self.bivar_plot = BivariateVisualiser(
            x_order=['SiO2', 'MgO'],
            y_order=['TiO2', 'Fe2O3', 'Al2O3'],
        )
        self.bivar_plot.init_bivariate_plot()
        # mount() creates the FigureCanvasTkAgg, the NavigationToolbar, and stores both frame references for later calls to rebuild().
        self.bivar_plot.mount(frame, toolbar_parent=controls_frame)

        # Axis selector combos (row 1 of controls_frame) 
        oxides = self.model.namespace.oxides
        self._create_axis_controls(controls_frame, oxides)

        return frame

    def _validate(self, function, popup_title='', popup_msg='', status_on_error=None, *args, **kwargs) -> bool:
        """
        Function wrapper to validate and handle exceptions for GUI operations, displaying appropriate pop-up messages.
        Returns True if the function executed successfully, False otherwise.
        """
        from tkinter import messagebox
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Capture all warnings
            try:
                function(*args, **kwargs)
            except Exception as e:
                # Log full error
                import traceback
                log_gui(
                    "Error occurred while loading the data suite:\n"
                    f"{traceback.format_exc()}"
                )
                # messagebox.showerror("Error Loading Data Suite", f"An error occurred while loading the data suite:\n{str(e)}")
                messagebox.showerror(f"Error {popup_title}", f"{popup_msg or 'An error occurred'}:\n{str(e)}")
                if status_on_error:
                    self.status_var.set(status_on_error)
                return False
            else:
                if w:
                    # Log full error
                    log_gui(f"Warning occurred while loading the data suite: {str(w[-1].message)}")
                    # messagebox.showinfo("Warning Loading Data Suite", f"Warnings occurred while loading the data suite:\n{str(w[-1].message)}")
                    messagebox.showwarning(f"Warning {popup_title}", f"{popup_msg or 'Warnings occurred'}:\n{str(w[-1].message)}")
                return True

    def load_config_file(self) -> None:
        """Load a configuration file and update the model and GUI accordingly."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Load Configuration File",
            filetypes=[("Hades Files", "*.hades"), ("All Files", "*.*")]
        )
        if not filepath:
            return  # User cancelled

        # Save the current model params
        prev = {
            'mode': self.model.meta.mode,
            'submode': self.model.meta.submode,
        }

        # To validate config in a new state before committing in case of error, create a trial model instance
        # This doesn't use the _fresh_model method since we don't want to update the existing method or the GUI

        pause_logging()
        trial = Obol.newModel()     # Init with defaults as load_config will update
        resume_logging()

        log_gui(f"Loading configuration", level=7)
        log_gui(f"{filepath}", level=9)
            
        success = self._validate(trial.load_config, filepath=filepath)          # may raise -> nothing committed

        if not success:
            return  # Validation failed, do not commit changes

        # print(f"Current settings:  mode={self.model.meta.mode}, submode={self.model.meta.submode}, FeO_Fe2pO_Ratio={self.model.meta.FeO_Fe2pO_Ratio}")
        log_gui("Loaded configuration settings, applying to GUI", level=16)
        log_gui(f"mode      = {trial.meta.mode}", level=15)
        log_gui(f"submode   = {trial.meta.submode}", level=15)
        log_gui(f"Fe3+/Fe2+ = {trial.meta.FeO_Fe2pO_Ratio}", level=15)

        # If success, overwrite model and sync GUI
        self.model = trial       # commit only on success

        # If the mode or submode changed, we need to reset the GUI to match the new model state
        if self.model.meta.mode != prev['mode']:# or self.model.meta.submode != prev['submode']:
            log_gui(f"GUI mode changed, resetting GUI", level=8)
            # print(f"Mode or submode changed: resetting GUI. New mode: {trial.meta.mode}, New submode: {trial.meta.submode}")
            self._sync_submode_state()  # ensure GUI reflects the new mode/submode
            self.root.after_idle(self.refresh_gui) # then rebuild GUI safely
        
        del trial           # free memory

        log_gui(f"Configuration loading complete", level=6)

        # Reset buttons - only to the the stages which have initial data (e.g. sample name is not None)
        samples = self.model.magma.magma_samples
        transitions_valid = [
            (samples[i] is not None and samples[i + 1] is not None)
            for i in range(len(samples) - 1)
        ]
        available_stages = np.arange(len(transitions_valid))[transitions_valid].tolist()
        self._apply_button_states(available_stages)
        # Send new data to new GUI state (after refresh_gui() to avoid overwriting)
        self.model_to_vars()  

        # Clear the plot and replot with the new model's data
        self.empty_plot()
        self.bivar_plot.plot_data_suite(model=self.model)
        self.bivar_plot.plot_magma(model=self.model, mode='initial')

        self.vars["Nsamples"].set(str(self.model.datasuite.data.shape[0]))  

        self._log(f"Configuration loaded from '{os.path.basename(filepath)}'")

    def save_config_file(self) -> None:
        """Save the current configuration to a file."""
        from tkinter import filedialog, messagebox
        filepath = filedialog.asksaveasfilename(
            title="Save Configuration File",
            defaultextension=".hades",
            filetypes=[("Hades Files", "*.hades"), ("All Files", "*.*")]
        )
        if not filepath:
            return  # User cancelled

        try:
            self.model.save_config(filepath=filepath)
            self._log(f"Configuration saved to '{os.path.basename(filepath)}'")
        except Exception as e:
            messagebox.showerror("Error Saving Configuration", f"An error occurred while saving the configuration:\n{str(e)}")
            self._log(f"Error saving configuration: {str(e)}")

    def open_single_bivariate_window(self) -> None:
        """Pop-up: one bivariate plot (with axis selectors) + a single
        mineral-composition table with a phase-transition selector."""

        from hades_plouton.windows.mineralogy import show_bivariate_window
        # print("Launching window framework layout verification shell...")
        show_bivariate_window(self.model, self.root, self.styler)
        return 

    def open_advanced_config_window(self) -> None:
        """Open the advanced parameter configuration dialog."""
        from hades_plouton.windows.parameter_config import ParameterConfigWindow

        # Build the seed dict from the current model/vars.
        initial = {
            'FeO_Fe2pO_Ratio': self.vars["FeO_Fe2pO_Ratio"].get(),
            'kd_values': [[var.get() for var in row] for row in self.array_vars["kd_values"]],
            'usage': [[var.get() for var in row] for row in self.array_vars["usage"]],
            'custom_mineralogies': self._nested_get(self.array_vars["custom_mineralogies"], np.float64).tolist(),
        }

        # Extract the whole rock ratios for the KD minerals
        WHR_comps = [self.model.minerals.whole_rock_ratios[m] for m in self.model.minerals.KD_minerals]

        dlg = ParameterConfigWindow(
            self.root,
            self.styler,                       # <-- shared theme
            initial_values=initial,
            used_minerals=self.model.meta.minerals_,
            all_minerals=self.model.namespace.minerals,
            formal_minerals=self.model.namespace.minerals_title,
            phases=self.model.namespace.phase_transitions,
            oxides=self.model.namespace.oxides,
            Kd_minerals=self.model.minerals.KD_minerals_short,
            Kd_min_WRs=WHR_comps,
            icon_path=self.assets.icon(),
            on_apply=self._apply_param_config, # callback below
        )
        dlg.transient(self.root)               # keep above main window
        dlg.grab_set()                         # modal
        self.root.wait_window(dlg)             # block until closed

        # Reset all phases
        self.reset_phase(0)

        self._log("Parameter changes applied.")

    def _apply_param_config(self, result: dict) -> None:
        """Push the dialog's result into the tk vars, then sync to the model."""

        # scalars
        self.vars["FeO_Fe2pO_Ratio"].set(result["FeO_Fe2pO_Ratio"])

        # arrays: result key -> array_vars key
        array_updates = {
            "kd_values":            result["kd_values"],
            "usage":                result["usage"],
            "custom_mineralogies":  result["custom_mineralogies"],
        }
        for key, values in array_updates.items():
            self._nested_set(self.array_vars[key], np.asarray(values))

        # Single sync point: vars -> model
        self.vars_to_model()
        self._log("Applied parameter configuration.")

    # %% ---- Helper Functions ----

    def _log(self, msg: str) -> None:
        """Log a message to the status bar and optionally to the console."""
        self.status_var.set(f"{msg}")

    def _sync_submode_state(self) -> None:
        """Enable/disable submode radios based on the current mode."""
        print(f"Syncing submode radios for mode '{self.vars['mode'].get()}' and submode '{self.vars['submode'].get()}'")
        if self.vars["mode"].get() == "alkaline":
            self.tholeiitic_radio.config(state=DISABLED)
            self.calcalk_radio.config(state=DISABLED)
            self.vars["submode"].set("")
        else:
            self.tholeiitic_radio.config(state=NORMAL)
            self.calcalk_radio.config(state=NORMAL)
            if self.vars["submode"].get() not in ("tholeiitic", "calcalk"):
                self.vars["submode"].set("tholeiitic")
        print(f"Submode radios updated:\n  > tholeiitic={self.tholeiitic_radio['state']}, calcalkaline={self.calcalk_radio['state']}, current submode={self.vars['submode'].get()}")

    # %% ---- Additional Event Handlers ----

    def on_mode_change(self) -> None:
        """Handle changes to the mode radio buttons."""
        self._sync_submode_state()   # enable/disable + fix submode value
        self.reset_model()         # <-- re-initialise with new mode/submode
        self.reset_plot()              # <-- clear the plot
        self.empty_plot()              # <-- clear the plot
        self.root.after_idle(self.refresh_gui) # then rebuild GUI safely
        self._log(f"Mode set to '{self.vars['mode'].get()}'.")

    def on_submode_change(self) -> None:
        """Handle changes to the submode radio buttons."""
        self.reset_model()         # <-- re-initialise with new submode
        self._log(f"Submode set to '{self.vars['submode'].get()}'.")

    def browse_data_suite(self) -> None:
        """[Browse...] Pick and load a data-suite file."""
        # Open a file dialog to select a data suite file (CSV, TXT, XLSX, or any file)
        from tkinter import filedialog
        # Always show CSV, TXT, XLSX, and All Files together by default
        filetypes = [
            ("CSV, TXT, XLSX files", "*.csv *.txt *.xlsx"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(title="Select a File", filetypes=filetypes)
        if filepath:
            self.vars["data_suite_filepath"].set(filepath)
            self.status_var.set(f"File selected: {filepath.split('/')[-1]}")
            self.short_filename.set(filepath.split('/')[-1])  # Update the short filename display
        else:
            self.status_var.set("No file selected.")
            return
        
        self.load_data_suite()  # Load the data suite after a file is selected

    def load_data_suite(self) -> None:
        """Load the data suite from the selected file and update the model and GUI."""
        # If a file was selected, attempt to load it into the model
        self.model.load_data_suite(self.vars["data_suite_filepath"].get())
        self.vars['Nsamples'].set(str(self.model.datasuite.data.shape[0]))  # Update the number of samples in the GUI
        self._log(f"Loaded data suite from '{os.path.basename(self.model.datasuite.filepath)}' with {self.vars['Nsamples'].get()} samples.")

        # Update the plot
        self.bivar_plot.plot_data_suite(model=self.model)
        self.bivar_plot.plot_magma(model=self.model, mode='initial')

        # Update button availability
        self._apply_button_states(range(len(self.buttons)))

    def edit_data_suite(self) -> None:
        """[Edit] Edit the currently loaded data suite."""
        from hades_plouton.windows.edit_magmas import EditMagmasWindow
        from tkinter import messagebox

        # Continue only if data has been loaded
        if self.model.datasuite.data.size == 0:
            messagebox.showwarning("No Data Loaded", "Please load a data suite before attempting to edit.")
            return  

        dlg = EditMagmasWindow(
            self.root,
            self.styler,                       # shared theme (StyleManager)
            self.model,
            icon_path=self.assets.icon(),
            on_apply=self._apply_edit_magma_config,
        )

        dlg.transient(self.root)               # keep above main window
        dlg.grab_set()                         # modal
        self.root.wait_window(dlg)             # block until closed

        # Update button availability
        self._apply_button_states(range(len(self.buttons)))

        self._log("Custom magma compositions selected.")

    def _apply_edit_magma_config(self, selected_labels: list) -> None:
        """Takes the six selected samples and pushes to the model, then syncs to GUI"""

        print(f"Applying selected magma compositions: {selected_labels}")
        self.model.select_initial_composition(selected_labels) 
        # Single sync point: vars -> model
        self.model_to_vars()
        # Reset plot and buttons
        self.refresh_plot()
        # Update button availability
        self._apply_button_states(range(len(self.buttons)))
        self._log("Applied parameter configuration.")

    def _apply_button_states(self, enabled_rows=None) -> None:
        """
        Enable the rows whose index is in `enabled_rows`; disable all others.
        Defaults to all enabled if `enabled_rows` is None.
        """
        # TODO: this is written twice in this file - could be a class method or variable of the model?
        samples = self.model.magma.magma_samples
        transitions_valid = [
            (samples[i] not in (None, "None") and samples[i + 1] not in (None, "None"))
            for i in range(len(samples) - 1)
        ]
        default_rows = np.arange(len(transitions_valid))[transitions_valid].tolist()

        if enabled_rows is None:
            # Default not to all buttons, but those which have initial data (e.g. sample name is not None)
            enabled_rows = default_rows
        else:
            # Ensure that the enabled_rows are valid indices based on the available transitions
            enabled_rows = [r for r in enabled_rows if r in default_rows]
            
        enabled = set(enabled_rows)
        for r_idx, row_of_buttons in enumerate(self.buttons):
            state = "normal" if r_idx in enabled else "disabled"
            # Only for the Run & View buttons - 0, 1, 2 is View, Run, Reset
            # for button in row_of_buttons[1:]:
            row_of_buttons[0].config(state=state)
            row_of_buttons[1].config(state=state)

    def normalise_assimilant(self) -> None:
        """
        Ensure that the assimilant major composition sums to 100 if any of the first 8 oxides are non-zero. 
        If all are zero, leave as is.
        """
        # Ensure assimilation major composition is either all 0 or normalised to 100
        assim_comp = self._nested_get(self.array_vars["assimilant_composition"], np.float64)
        assim_mjr = assim_comp[:8]
        if np.any(assim_mjr) and not np.isclose(np.sum(assim_mjr), 100.0):
            print(f"Normalising assimilant major composition to sum to 100.")
            assim_mjr = 100.0 * assim_mjr / np.sum(assim_mjr)
            assim_comp[:8] = assim_mjr
            self._nested_set(self.array_vars["assimilant_composition"], assim_comp)

    def view_phase(self, idx: int) -> None:
        """[View] Inspect phase results for a given row."""
        self.normalise_assimilant()  # Ensure assimilation major composition is either all 0 or normalised to 100

        self._log(f"Viewing phase {self.model.namespace.phase_transitions[idx]}.")
        # Sync the current GUI variables to the model before running the view
        self.vars_to_model()  

        # Run with validation and pass self.results[idx].weights
        params = np.concat([np.array([self.model.results[idx].F]), self.model.results[idx].weights])

        # If params is length 1, it means user is only viewing, not optimising, so read directly from the mineral table
        if len(params) == 1:
            # Read the weights directly from the GUI table for this phase
            params = self._mineral_weights_sync("variable")
            params = params[idx, :]  # Get the weights for the specific phase

        # If the amount of FC% (first value) is 0, throw warning and return
        if params[0] < 0.01:
            import tkinter.messagebox as mb
            mb.showwarning("Fractional Crystallisation Warning", "Amount of fractional crystallisation must be greater than 0 to model results.")
            self._log(f"Model error. Ready.")
            return

        log_gui(f"Viewing phase {idx+1} with params: {params}")
        success = self._validate(self.model.run, phase=idx+1, params=params)

        self._log(f"{self.model.namespace.phase_transitions[idx]} viewed with cost {self.model.results[idx].cost:.2f}.")

        # Clear previous computed magmas for this phase and those above
        self.bivar_plot.clear_magma('computed', phase_idxs=[p for p in range(idx, len(self.model.namespace.phase_transitions))])

        self.bivar_plot.plot_magma(model=self.model, mode='computed', transition_idxs=[idx])

        # Update vars from model after view
        self.model_to_vars() 

    def run_phase(self, idx : int) -> None:
        """[Run] Optimise a single phase row and update the GUI accordingly."""

        self.normalise_assimilant()  # Ensure assimilation major composition is either all 0 or normalised to 100

        self._log(f"Running phase {self.model.namespace.phase_transitions[idx]}...")
        self.vars_to_model()

        # Set global busy cursor
        self.root.config(cursor="starting")

        # Create an invisible overlay frame to grab all clicks
        # We define no background, no highlightthickness, no relief.
        blocker = tk.Frame(self.root, bg="", highlightthickness=0, bd=0)
        
        blocker.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # We must explicitly set the watch cursor on the blocker frame too
        blocker.configure(cursor="starting")
        
        blocker.grab_set()  # Intercepts ALL mouse and keyboard inputs to the main window

        result = {"success": False, "error": None}

        # Worker Thread
        def worker():
            try:
                result["success"] = self._validate(self.model.run, phase=idx + 1)
            except Exception as e:
                result["error"] = e

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        # Polling loop on main thread
        def check_thread():
            if thread.is_alive():
                self.root.after(50, check_thread)
                return

            # Restore input state & cursor
            blocker.grab_release()
            blocker.destroy()
            self.root.config(cursor="")

            if result["error"]:
                self._log(f"Error during phase {idx}: {result['error']}")
                return

            success = result["success"]

            self._log(
                f"{self.model.namespace.phase_transitions[idx]} completed with cost {self.model.results[idx].cost:.2f}."
            )

            # Plotting & Tkinter UI updates on main thread
            self.bivar_plot.plot_magma(model=self.model, mode='computed', transition_idxs=[idx])

            if success:
                self._apply_button_states({idx, idx + 1})

            self.model_to_vars()

        check_thread()


    def reset_phase(self, idx: int) -> None:
        """[Reset] Clear a single phase row and re-open it plus all downstream phases."""
        for i in range(idx, len(self.model.namespace.phase_transitions)):
            self.bivar_plot.clear_magma('computed', phase_idxs=[i])   # int, not [i]

        # Rescale axis 
        self.bivar_plot.rescale_axes()

        # Plot all the initial magmas
        # self.bivar_plot.plot_magma(self.ax, mode='initial')
        self._log(f"Reset phases {self.model.namespace.phases[idx]} to {self.model.namespace.phases[-1]}.")

        # Sequential gating: unlock this row and everything below it
        self._apply_button_states(range(idx, len(self.buttons)))

        # Clear the mineral table for this phase and all downstream phases
        for i in range(idx, len(self.model.namespace.phase_transitions)):
            self._clear_mineral_table(i)

        # Reset the results for the phase and all downstream phases
        for i in range(idx, len(self.model.namespace.phase_transitions)):
            self.model.results[i].reset()

        # Recompute the crystallisation dict
        if idx > 0:
            self.model.crystallisation_dict = self.model.calculate_mineral_proportions(idx-1)
            self.update_phase_totals()
        # If the reset phase is the first one, clear the totals row
        else:
            self._clear_totals_row()


    def make_TAS(self) -> None:
        """Spawns an independent pop-up window containing the static TAS diagram."""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        from tkinter import messagebox

        # If the data suite is empty, don't plot
        if self.model.datasuite.data.size == 0:
            self._log("Cannot generate TAS diagram: data suite is empty.")
            messagebox.showwarning("TAS Diagram", "Cannot generate TAS diagram: data suite is empty.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("TAS Diagram")
        
        # Make popup modal relative to the main window
        popup.transient(self.root)
        popup.grab_set()

        popup.geometry("1000x600") 
        popup.minsize(600, 450)

        # CRITICAL: Pack the toolbar frame FIRST at the bottom. 
        toolbar_frame = ttk.Frame(popup)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add padding to the plot frame so the canvas isn't touching the window edges.
        plot_frame = ttk.Frame(popup, padding=(15, 15, 15, 0))
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot
        from hades.visuals import tas
        fig, ax = tas(self.model, return_fig_ax=True)

        # Embed Canvas into the padded plot frame
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Initialise the Toolbar inside its dedicated frame
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame, pack_toolbar=True)
        toolbar.update()

        # Initial render push
        canvas.draw()

        # Clean up the matplotlib figure when the window closes
        def _on_close():
            import matplotlib.pyplot as plt
            plt.close(fig)
            popup.destroy()
            
        popup.protocol("WM_DELETE_WINDOW", _on_close)

        # Halt execution of main window thread until popup is destroyed
        self.root.wait_window(popup)

    def make_bulk_min_wdw(self) -> None:
        """[Minerology Info] Open the mineralogy window."""
        self.open_single_bivariate_window()  # <-- reuse the single bivariate window for now
        self._log("Mineralogy window opened.")

    def export_pdf(self) -> None:
        """[Export PDF] Export a results report as PDF."""
        from tkinter import messagebox

        # Sync GUI to model
        self.vars_to_model()

        # Quick check to see if any phases have been run; if not, warn the user and abort
        if not any(result.isrun for result in self.model.results):
            messagebox.showwarning("Export PDF", "No phases have been run yet. Please run at least one phase before exporting a PDF report.")
            self._log("Export PDF aborted: no phases have been run.")
            return

        from hades_plouton.windows.export import HadesPDFGenerator
        pdf_worker = HadesPDFGenerator(self.root, self.model, self.styler)

        try:
            filepath, _result = pdf_worker.generate_pdf()
        except Exception as e:
            log_gui(f"Error exporting data: {e}", level=1)
            messagebox.showerror("Export Data Error", f"An error occurred while exporting data:\n{str(e)}")
            self._log(f"Results PDF could not be exported. Check logs for details.")
        # else:
        #     if _result:
        #         messagebox.showinfo("Export Data", "Data export completed successfully.")
        #         self._log(f"Results PDF exported to {os.path.basename(filepath)}")

    def export_data(self) -> None:
        """[Export Data] Export numerical results (xlsx)."""
        from tkinter import messagebox
        from hades_plouton.windows.export import saveExcel

        try:
            filepath, _result = saveExcel(self.model)
        except Exception as e:
            log_gui(f"Error exporting data: {e}", level=1)
            messagebox.showerror("Export Data Error", f"An error occurred while exporting data:\n{str(e)}")
        else:
            if _result:
                messagebox.showinfo("Export Data", "Data export completed successfully.")

        # messagebox.showinfo("Export Data", "This feature is not yet implemented.")
        self._log(f"Results data exported to {os.path.basename(filepath)}")

    def trace_window(self) -> None:
        """[Trace] Open the trace window."""
        # Only enable this window to be opened if any of the normal phases have been run 
        isrun = [self.model.results[i].isrun for i in range(len(self.model.namespace.phase_transitions))]
        if not any(isrun):
            from tkinter import messagebox
            messagebox.showwarning("Trace Window", "Run at least one stage of evolution before analysing trace elements.")
            self._log("Run at least one phase before opening the trace window.")
            return

        from hades_plouton.windows.newtraces import show_trace_window
        self._log("Trace window opened...")
        win = show_trace_window(self.model, self.root, self.styler)

        # Pause execution of this method until `win` is destroyed
        self.root.wait_window(win)
        
        # Executed immediately after the trace window closes
        self._log("Trace analyses complete")

        # Sync model to GUI after trace window closes, in case any changes were made
        self.model_to_vars()

    def reset_all_fields(self) -> None:
        """Reset all fields in the GUI to their default values, except for mode and submode selection."""
        # Prompt user
        from tkinter import messagebox
        if not messagebox.askyesno("Reset All Fields", "Are you sure you want to reset all fields to default values? This will clear all data and results."):
            return  # User cancelled
        
        # Reset model to fresh defaults
        self.reset_model() 

        # Reset button states to all enabled
        self._apply_button_states()  # Enable all rows

        # Clear plot
        self.empty_plot()
        self._log("Interface reset.")

    def empty_plot(self) -> None:
        """
        Removes all artists from the plots
        """
        self.bivar_plot.clear_data_suite()
        self.bivar_plot.clear_magma('initial')
        self.bivar_plot.clear_magma('computed')
        # Rescale axes
        self.bivar_plot.rescale_axes()
        self._log("Plot elements cleared.")

    def refresh_plot(self) -> None:
        """
        Removes all artists and replots the data suite and initial magmas
        """
        self.empty_plot()
        self.bivar_plot.plot_data_suite(model=self.model)
        self.bivar_plot.plot_magma(model=self.model, mode='initial')
        self._apply_button_states()
        self._log("Plot refreshed.")

    def reset_plot(self) -> None:
        """
        Resets the plot by clearing all computed magmas
        """
        # Clear artist collections internally from memory
        self.bivar_plot.clear_magma('computed')
        
        # Replot using whatever self.model points to right now
        self.bivar_plot.plot_data_suite(model=self.model)

        # Rescale axis 
        self.bivar_plot.rescale_axes()
        self._log("Magmas removed.")

    def quit_app(self, event=None) -> None:
        """Safe shutdown that cleanly unbinds Tcl callbacks."""
        try:
            # Stop accepting any new user events immediately
            self.root.withdraw()
            
            # Break the main loop cleanly (stops event processing safely)
            self.root.quit()
        except Exception:
            pass

def load_dependencies() -> None:
    """Imports heavy C-extensions & backend models, assigning them to module globals."""
    global np, ttk, Obol, get_asset_path, sanity_check, nice_display
    global get_nested_attr, set_nested_attr, convert_to_serialisable
    global sort_geochem, _deserialise, from_dict
    global setup_logger, log_gui, pause_logging, resume_logging

    from tkinter import ttk

    import numpy as np

    from hades import Obol
    from hades.utils import (
        _deserialise,
        convert_to_serialisable,
        from_dict,
        get_asset_path,
        get_nested_attr,
        nice_display,
        sanity_check,
        set_nested_attr,
        sort_geochem,
    )

    from hades.logger import (
        log_gui,
        pause_logging,
        resume_logging,
        setup_logger,
    )

def main() -> None:
    """Main entry point for the Hades Plouton GUI application."""

    try:
        myappid = f'hades.plouton.app.{"0.9.1"}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    root = tk.Tk()
    root.withdraw()

    # Initialise splash screen immediately
    from hades_plouton import splash
    from hades_plouton.tk_splash import TkSplash

    # Close the native PyInstaller splash screen if it exists, then open our own Tkinter splash screen
    if splash.HAS_PYI_SPLASH:
        # Since this indicates a built version, get BASE_DIR

        # Absolute path to the directory containing this script (app.py)
        #  - Using relative paths avoid loading hades.utils
        BASE_DIR = Path(__file__).resolve().parent
        splash.close()
    else:
        # Else, will be running in dev mode, so get BASE_DIR normally
        BASE_DIR = Path(__file__).resolve().parent.parent

    # Build the splash image path relative to app.py
    tk_splash = TkSplash(root, BASE_DIR=BASE_DIR, title="HADES", text="Initialising modules...")

    def status(msg: str, step: int):
        if tk_splash:
            tk_splash.text(msg, step=step)

    messages = [
        'Waiting for Charon to finish his coffee break...',
        'Feeding the three-headed dog...',
        'Polishing Hades\' bident...',
        'Sorting feldspars by personality type...',
        'Asking Persephone if she packed the pomegranate snacks...',
        'Topping off the ambrosia supply...',
        'Poseidon likes the hydrous amphiboles and micas the most',
        'Woof, woof, woof, Grrrrrrrrrrrrrr!!! - Cerberus',
        'Tartarus is full of many a failed petrological model',
        'Make amphibole great again!',
        'Where we\'re going, we don\'t need thermodynamics',
        'Hades is a great place to work, but the commute is hell',
        'Nobody likes a calc-alkaline, but they\'re still welcome here',
        'Eat well, for tonight we dine in Hades',
    ]
    # Pick a random message to display during the splash screen
    random_message = messages[id(object()) % len(messages)]

    status(random_message, 20)
    
    load_dependencies()

    status(random_message, 20)

    icon_path = str(get_asset_path('hades_plouton.assets', 'hades_icon_dark.ico'))
    if icon_path:
        try:
            root.iconbitmap(default=icon_path)
        except Exception:
            pass

    status(random_message, 30)

    setup_logger()
    
    status("Launching Hades...", 15)

    import traceback
    try:
        # Initialise the main application GUI
        app = HadesGUI(root)                       

        # Close splash
        if tk_splash:
            tk_splash.close()

        root.deiconify()
        root.mainloop()

    except Exception as e:
        # Capture the full traceback as a string
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        
        # Log it using your custom logging functionality
        log_gui(f"CRITICAL: Application crashed unexpectedly:\n{error_msg}")
        
        # Optional: Show a popup error box to the user so they know why it failed
        try:
            from tkinter import messagebox
            messagebox.showerror("Fatal Error", f"Hades encountered a fatal error, see the log files for more details:\n{e}")
        except Exception:
            pass
            
        sys.exit(1)

    # Cleanup -> root.quit leads here
    try:
        root.destroy()
    except Exception:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
