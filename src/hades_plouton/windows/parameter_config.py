"""Pop-up window for configuring parameters (Fe ratio, KD values, mineral compositions).

Creates a standalone Toplevel window with tabs for Fe ratio, KD values, and phase compositions.
"""

# Dependencies
import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np

class ParameterConfigWindow(tk.Toplevel):

    def __init__(self, master, styler, used_minerals, all_minerals, formal_minerals, phases, oxides, Kd_minerals, Kd_min_WRs, initial_values=None, icon_path=None, on_apply=None) -> None:
        """Initialise the parameter configuration window."""
        super().__init__(master)

        # Theme resources from the shared StyleManager
        self.styler = styler
        self.style = styler.style
        self.palette = styler.palette
        self.font_main = styler.font_main
        self.font_bold = styler.font_bold

        # Callbacks / result 
        self.on_apply_callback = on_apply
        self.result = None

        # Data 
        self.USED_MINERALS = used_minerals
        self.ALL_MINERALS = all_minerals
        self.FORMAL_MINERALS = formal_minerals
        self.PHASES = phases
        self.OXIDES = oxides
        self.KD_MINERALS = Kd_minerals
        self.KD_MIN_WRs = Kd_min_WRs

        # Window setup 
        self.title("Parameter Configuration")
        self.geometry("1200x900")
        self.resizable(True, True)
        if icon_path:
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        self.configure(bg=self.palette["bg"])

        self._constrain_to_screen()

        self._init_variables(initial_values)  # build all tk variables
        self._build_layout()                  # tab bar + content + panels

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # %% ---- Styling and Setup ----

    def _constrain_to_screen(self) -> None:
        """Ensure window fits within screen bounds, adjusting size and position as needed."""
        # Force geometry update to get accurate dimensions
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Get taskbar/reserved space (rough estimate; varies by OS)
        taskbar_height = 50
        usable_height = screen_height - taskbar_height
        
        # Requested size (from current geometry)
        req_width = 1200
        req_height = 900
        
        # Constrain to fit on screen with small margins
        margin = 20
        max_width = screen_width - (2 * margin)
        max_height = usable_height - (2 * margin)
        
        actual_width = min(req_width, max_width)
        actual_height = min(req_height, max_height)
        
        # Position: center horizontally, top-aligned vertically
        x_pos = (screen_width - actual_width) // 2
        y_pos = margin  # Near the top
        
        self.geometry(f"{actual_width}x{actual_height}+{x_pos}+{y_pos}")

    def _apply_sheet_theme(self, sheet) -> None:
        """Apply the current palette to a tksheet instance for consistent theming."""
        p = self.palette
        try:
            sheet.set_options(
                table_bg=p["surface"], table_fg=p["fg"],
                table_grid_fg=p["border"],
                header_bg=p["side_bg"], header_fg=p["fg"],
                index_bg=p["side_bg"], index_fg=p["fg"],
                top_left_bg=p["side_bg"],
                table_selected_cells_bg=p["tab_active_bg"],
                table_selected_cells_border_fg=p["primary"],
            )
            sheet.refresh()
        except Exception as exc:  # noqa: BLE001
            print(f"[sheet theme] {exc}")

    def _init_variables(self, initial_values) -> None:
        """Initialise all Tkinter variables for Fe ratio, KD values, and phase compositions."""
        initial_values = initial_values or {}

        print("Initial values received:")
        for key, val in initial_values.items():
            if isinstance(val, (list, np.ndarray)):
                print(f"  {key}: type={type(val)}, shape={np.asarray(val).shape}")
            else:
                print(f"  {key}: {val} - type={type(val)}")

        # Fe ratio
        self.FeRatio = tk.DoubleVar(value=initial_values.get('FeO_Fe2pO_Ratio'))
        self.FeRatio.trace_add("write", lambda *a: print(f"FeO_Fe2pO_Ratio updated: {self.FeRatio.get()}"))

        # KD values
        kd_init = initial_values.get('kd_values')
        self.kd_values = [[tk.DoubleVar(value=kd_init[i][j]) for j in range(11)] for i in range(5)]

        # Custom mineralogy and usage
        custom_mins = initial_values.get('custom_mineralogies')
        min_usage = initial_values.get('usage')

        # Store phase data and usage as dictionaries keyed by phase name
        self.phase_data = {}
        self.phase_usage = {}
        for p_idx, phase in enumerate(self.PHASES):
            data = []
            for i in range(len(self.ALL_MINERALS)):
                row = []
                for j in range(8):
                    try:
                        val = custom_mins[p_idx][i][j]
                        if val is None or (isinstance(val, float) and np.isnan(val)):
                            row.append("")
                        else:
                            row.append(str(val))
                    except Exception:
                        row.append("")
                data.append(row)
            self.phase_data[phase] = data

            usage = []
            for i in range(len(self.ALL_MINERALS)):
                try:
                    used = bool(min_usage[p_idx][i])
                except Exception:
                    used = True
                usage.append(tk.BooleanVar(value=used))
            self.phase_usage[phase] = usage

    # %% ---- Layout and Tabs ----

    def _build_layout(self) -> None:
        """Construct the main layout: tab bar, content area, and apply/cancel buttons."""
        p = self.palette

        # Tab bar
        tab_bar = ttk.Frame(self)
        tab_bar.pack(fill="x", padx=15, pady=(15, 0))

        # Content container (bordered surface, like Advanced Config)
        self.content = tk.Frame(self, bg=p["surface"],
                                highlightbackground=p["border"],
                                highlightthickness=1)
        self.content.pack(fill="both", expand=True, padx=15, pady=(10, 0))

        # Build the tabs
        self.panels = [
            self._build_fe_kds_panel(self.content),
            self._build_comp_panel(self.content),
        ]

        # Tab headers (fixed size => never shift)
        self.tab_headers = []
        names = ["Geochemistry", "Phase Compositions"]
        for idx, name in enumerate(names):
            hf = ttk.Frame(tab_bar, width=150, height=34, style="TabInactive.TFrame")
            hf.pack_propagate(False)
            hf.pack(side="left", padx=(0, 4))
            hl = ttk.Label(hf, text=name, style="TabInactive.TLabel")
            hl.pack(expand=True)
            hf.bind("<Button-1>", lambda e, i=idx: self.select_tab(i))
            hl.bind("<Button-1>", lambda e, i=idx: self.select_tab(i))
            self.tab_headers.append((hf, hl))

        # Apply / Cancel row
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=15, pady=15)
        ttk.Button(btn_row, text="Apply", command=self.on_apply).pack(side="right")
        ttk.Button(btn_row, text="Cancel", command=self.on_close).pack(side="right", padx=(0, 8))

        self.select_tab(0)

    def select_tab(self, index: int) -> None:
        """Switch to the specified tab index, updating the displayed panel and tab styles."""
        for panel in self.panels:
            panel.pack_forget()
        self.panels[index].pack(fill="both", expand=True, padx=10, pady=10)
        for i, (hf, hl) in enumerate(self.tab_headers):
            if i == index:
                hf.configure(style="TabActive.TFrame")
                hl.configure(style="TabActive.TLabel")
            else:
                hf.configure(style="TabInactive.TFrame")
                hl.configure(style="TabInactive.TLabel")

    def _build_fe_kds_panel(self, parent) -> ttk.Frame:
        """Build the panel containing Fe ratio controls and KD values table."""
        import tksheet
        
        # Main container card frame
        panel = ttk.Frame(parent, style="Card.TFrame", padding=20)
        
        # Top row: Fe Ratio Controls
        fe_frame = ttk.Frame(panel, style="Card.TFrame")
        fe_frame.pack(fill="x", side="top", pady=(0, 15))
        
        ttk.Label(
            fe_frame, 
            text="Feᵗ to Fe²⁺ Ratio:", 
            style="Card.TLabel", 
            font=self.font_bold
        ).pack(side="left", padx=(0, 10))
        
        ttk.Entry(
            fe_frame, 
            textvariable=self.FeRatio, 
            width=12
        ).pack(side="left")
        
        # Separator line to keep things looking modern and organized
        sep = ttk.Separator(panel, orient="horizontal")
        sep.pack(fill="x", side="top", pady=(0, 15))

        # Bottom row: KD Values Table
        kd_container = ttk.Frame(panel, style="Card.TFrame")
        kd_container.pack(fill="both", expand=True, side="top")
        
        ttk.Label(
            kd_container, 
            text="KD Values",
            style="Card.TLabel", 
            font=self.font_bold
        ).pack(anchor="w", pady=(0, 10))

        kd_data = [[self.kd_values[i][j].get() for j in range(11)] for i in range(5)]

        # Have headers display the composition
        HEADERS = [f"{min_short}\n({comp})" for min_short, comp in zip(self.KD_MINERALS, self.KD_MIN_WRs)]
        print(f"KD Table Headers: {HEADERS}")

        # Bind tksheet to the explicit container frame
        self.sheet = tksheet.Sheet(
            kd_container, 
            data=kd_data, 
            headers=HEADERS,
            row_index=[phase for phase in self.PHASES],
        )
        self.sheet.pack(fill="both", expand=True)
        
        # Keep your exact sheet configuration and styling
        self.sheet.enable_bindings((
            "single_select", "row_select", "column_select", "drag_select",
            "edit_cell", "arrowkeys", "copy", "cut", "paste", "undo", "redo",
            "cell_select",
        ))
        self.sheet.table_align('centre')
        self.sheet.align_rows('center')
        self.sheet.row_index_align('left')
        self.sheet.set_all_column_widths(70)
        self.sheet.set_row_heights([50] * 5)
        self.sheet.set_index_width(160)
        self.sheet.set_header_height_lines(2.5)
        self._apply_sheet_theme(self.sheet)
        
        return panel

    def _build_comp_panel(self, parent) -> ttk.Frame:
        """Build the panel for phase compositions, including dropdown and tksheet."""
        panel = ttk.Frame(parent, style="Card.TFrame", padding=20)
        panel.rowconfigure(3, weight=1)
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="Mineral Phase Compositions", style="Card.TLabel",
                  font=self.font_bold).grid(row=0, column=0, columnspan=2,
                                            sticky="w", pady=(0, 10))

        sel = ttk.Frame(panel, style="Card.TFrame")
        sel.grid(row=1, column=0, sticky="w")
        ttk.Label(sel, text="Select Phase:", style="Card.TLabel").grid(
            row=0, column=0, padx=(0, 8))
        self.phase_dropdown_var = tk.StringVar(value=self.PHASES[0])

        phase_menu = ttk.Combobox(sel, textvariable=self.phase_dropdown_var,
                                  values=self.PHASES, state="readonly", width=24)
        phase_menu.grid(row=0, column=1)
        phase_menu.bind("<<ComboboxSelected>>",
                        lambda e: self.show_phase_sheet(self.phase_dropdown_var.get()))

        ttk.Label(panel, style="Card.TLabel",
                  text="Note: compositions are wt% oxides, and are force normalised after input."
                  ).grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.phase_table_frame = ttk.Frame(panel, style="Card.TFrame")
        self.phase_table_frame.grid(row=3, column=0, columnspan=2,
                                    sticky="nsew", pady=(10, 0))

        self.current_sheet = None
        self.checkbox_widgets = []
        self.show_phase_sheet(self.PHASES[0])
        return panel

    def show_phase_sheet(self, phase) -> None:
        """Display the tksheet for the selected phase, along with checkboxes for mineral usage."""
        import tksheet
        for widget in self.phase_table_frame.winfo_children():
            widget.destroy()

        sheet = tksheet.Sheet(
            self.phase_table_frame, 
            data=self.phase_data[phase],
            headers=self.OXIDES, 
            row_index=self.FORMAL_MINERALS,
            show_table=True, 
            height=600, 
            width=850,
        )
        sheet.enable_bindings((
            "single_select", "row_select", "column_select", "drag_select",
            "column_resize", "row_resize", "edit_cell", "arrowkeys", "copy",
            "cut", "paste", "delete", "undo", "redo", "cell_select",
        ))
        sheet.table_align('centre')
        sheet.row_index_align('left')
        row_height = 30
        sheet.set_all_column_widths(80)
        sheet.set_row_heights([row_height] * len(self.ALL_MINERALS))
        sheet.set_index_width(160)      # BUGFIX: was self.sheet (the KD sheet)
        sheet.grid(row=0, column=0, sticky="n")
        self._apply_sheet_theme(sheet)
        self.current_sheet = sheet

        # Checkbox column
        cb_frame = ttk.Frame(self.phase_table_frame, style="Card.TFrame")
        cb_frame.grid(row=0, column=1, sticky="ns", padx=0)
        ttk.Label(cb_frame, text="Used?", anchor="center", style="Card.TLabel",
                  font=self.font_bold).grid(row=0, column=0, sticky="ew")

        self.checkbox_widgets = []
        for i, mineral in enumerate(self.ALL_MINERALS):
            cb = ttk.Checkbutton(cb_frame, variable=self.phase_usage[phase][i])
            cb.grid(row=i + 1, column=0, sticky="ew", ipadx=10)

            if mineral not in self.USED_MINERALS:
                self.phase_usage[phase][i].set(False)
                cb.state(['disabled'])
            else:
                cb.state(['!disabled'])

            cb_frame.grid_rowconfigure(i + 1, minsize=row_height)
            self.checkbox_widgets.append(cb)

    # %% ---- Event Handlers ----
   
    def _browse_file(self, mineral) -> None:
        """Open a file dialog to select a file for the given mineral and update the corresponding variable."""
        path = filedialog.askopenfilename(title=f"Select file for {mineral}", parent=self)
        if path:
            self.bank_filepaths[mineral].set(path)

    def parse_float(self, val) -> float:
        """Safely parse a string to float, returning NaN for empty or invalid inputs."""
        try:
            return float('nan') if val == "" else float(val)
        except Exception:
            return float('nan')

    def on_apply(self) -> None:
        """Gather all current values and invoke the callback with the result."""
        fe_ratio = self.FeRatio.get()
        kd_vals = self.sheet.get_sheet_data()

        # Persist the currently-shown phase before gathering
        phase = self.phase_dropdown_var.get()
        self.phase_data[phase] = self.current_sheet.get_sheet_data()

        custom_mineralogies, mineral_usage = [], []
        for phase in self.PHASES:
            phase_matrix = [[self.parse_float(v) for v in row]
                            for row in self.phase_data[phase]]
            custom_mineralogies.append(phase_matrix)
            mineral_usage.append([var.get() for var in self.phase_usage[phase]])

        custom_mineralogies = np.array(custom_mineralogies)
        mineral_usage = np.array(mineral_usage)

        # Normalise each mineral row to 100 wt%
        for p in range(custom_mineralogies.shape[0]):
            for m in range(custom_mineralogies.shape[1]):
                row = custom_mineralogies[p][m]
                if np.any(np.isnan(row)):
                    continue
                total = np.sum(row)
                if total > 0:
                    custom_mineralogies[p][m] = (row / total) * 100.0

        self.result = {
            'FeO_Fe2pO_Ratio': fe_ratio,
            'kd_values': kd_vals,
            'custom_mineralogies': custom_mineralogies,
            'usage': mineral_usage,
        }

        if self.on_apply_callback:
            self.on_apply_callback(self.result)
        self.destroy()

    def on_close(self) -> None:
        """Handle window close event, resetting result and destroying the window."""
        self.result = None
        self.destroy()
