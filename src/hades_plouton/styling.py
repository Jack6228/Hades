"""Styling and theming for the Hades GUI application.

This module defines the colour palettes, fonts, and ttk styles used throughout the Hades GUI. It provides a `StyleManager` class that encapsulates the application of light and dark themes, allowing for consistent styling of widgets such as frames, labels, buttons, entries, and comboboxes.
"""

# Dependencies
from tkinter import ttk

# %% ---- Base Variables ----

FONTS = {
    "main":     ("Segoe UI", 10),
    "bold":     ("Segoe UI", 10, "bold"),
    "heading":  ("Segoe UI", 13, "bold"),
    "title":    ("Figtree", 30, "bold"),
    "subtitle": ("Segoe UI", 14),
    "authors":  ("Segoe UI", 9, "italic"),
}

# Brand Reds & Interactive States
RED_PRIMARY = "#A32325"      # Red
RED_HOVER = "#BD2A2D"        # Lighter
RED_PRESSED = "#841B1D"      # Darker
RED_LIGHT_BORDER = "#D68C8E" # Muted
RED_DARK_MODE = "#C7383B"    # Contrast
RED_DARK_HOVER = "#E0484B"   # Hover

# Neutrals - Light Mode
NEUTRAL_LIGHT_BG = "#F9F9F9"
NEUTRAL_LIGHT_SIDE_BG = "#F0F0F0"
NEUTRAL_LIGHT_SURFACE = "#FFFFFF"
NEUTRAL_LIGHT_FG = "#1A1A1A"
NEUTRAL_LIGHT_FG_DIM = "#666666"
NEUTRAL_LIGHT_BORDER = "#E0E0E0"
NEUTRAL_LIGHT_TAB_ACTIVE = "#E5E5E5"
NEUTRAL_LIGHT_TOGGLE_HOV = "#404040"

# Neutrals - Dark Mode
NEUTRAL_DARK_BG = "#121212"
NEUTRAL_DARK_SIDE_BG = "#1A1A1A"
NEUTRAL_DARK_SURFACE = "#242424"
NEUTRAL_DARK_FG = "#E0E0E0"
NEUTRAL_DARK_FG_DIM = "#A0A0A0"
NEUTRAL_DARK_BORDER = "#333333"
NEUTRAL_DARK_TAB_ACTIVE = "#2D2D2D"
NEUTRAL_DARK_TOGGLE_HOV = "#FFFFFF"

# Palettes Dictionary
PALETTES = {
    "light": {
        "bg": NEUTRAL_LIGHT_BG,
        "side_bg": NEUTRAL_LIGHT_SIDE_BG,
        "surface": NEUTRAL_LIGHT_SURFACE,
        "fg": NEUTRAL_LIGHT_FG,
        "fg_dim": NEUTRAL_LIGHT_FG_DIM,
        "border": NEUTRAL_LIGHT_BORDER,
        "primary": RED_PRIMARY,
        "primary_hov": RED_HOVER,
        "button": RED_PRIMARY,
        "button_hover": RED_HOVER,
        "button_pressed": RED_PRESSED,
        "tab_active_bg": NEUTRAL_LIGHT_TAB_ACTIVE,
        "tab_active_border": RED_LIGHT_BORDER,
        "toggle_bg": NEUTRAL_LIGHT_FG,
        "toggle_fg": NEUTRAL_LIGHT_BG,
        "toggle_hov": NEUTRAL_LIGHT_TOGGLE_HOV,
    },
    "dark": {
        "bg": NEUTRAL_DARK_BG,
        "side_bg": NEUTRAL_DARK_SIDE_BG,
        "surface": NEUTRAL_DARK_SURFACE,
        "fg": NEUTRAL_DARK_FG,
        "fg_dim": NEUTRAL_DARK_FG_DIM,
        "border": NEUTRAL_DARK_BORDER,
        "primary": RED_DARK_MODE,
        "primary_hov": RED_DARK_HOVER,
        "button": RED_PRIMARY,
        "button_hover": RED_HOVER,
        "button_pressed": RED_PRESSED,
        "tab_active_bg": NEUTRAL_DARK_TAB_ACTIVE,
        "tab_active_border": RED_DARK_MODE,
        "toggle_bg": NEUTRAL_DARK_FG,
        "toggle_fg": NEUTRAL_DARK_BG,
        "toggle_hov": NEUTRAL_DARK_TOGGLE_HOV,
    },
}

# %% ---- Style Manager Class ----

class StyleManager:
    """
    Owns the ttk.Style object and applies theme profiles.

    Parameters
    ----------
    root : tk.Tk
        The root Tkinter window.
    initial : str, optional
        Name of the palette to load on startup, by default ``"light"``.

    Examples
    --------
    >>> style_mgr = StyleManager(root, initial="dark")
    >>> style_mgr.apply("light")  # Switch to light mode
    >>> style_mgr.apply("dark")   # Switch back to dark mode
    >>> style_mgr.palette  # Access the current palette dictionary
    >>> style_mgr.font_main  # Access the main font tuple

    To apply a style in a ttk widget, use the style name, e.g.::
    >>> ttk.Button(root, text="Click Me", style="TButton")
    """

    def __init__(self, root, initial: str = "light") -> None:
        """Initialise the StyleManager with the root window and initial theme."""
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Expose fonts as attributes for convenient access
        self.font_main = FONTS["main"]
        self.font_bold = FONTS["bold"]
        self.font_heading = FONTS["heading"]
        self.font_title = FONTS["title"]
        self.font_subtitle = FONTS["subtitle"]
        self.font_authors = FONTS["authors"]

        self.current_theme = initial
        self.palette = PALETTES[initial]

    def apply(self, name: str) -> None:
        """
        Apply a full flat style profile for the requested palette name.

        Parameters
        ----------
        name : str
            Key into ``PALETTES``; either ``"light"`` or ``"dark"``.
        """
        p = PALETTES[name]
        self.current_theme = name
        self.palette = p
        s = self.style

        self.root.configure(bg=p["bg"])

        # Splash / loading bar 
        s.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor=p["bg"],
            background="#1c1673",
            bordercolor=p["bg"],
            lightcolor="#2ecc71",
            darkcolor="#2ecc71",
        )
        s.configure(
            "Saving.Horizontal.TProgressbar",
            troughcolor=p["bg"],
            background="#2ecc71",
            bordercolor=p["bg"],
            lightcolor="#2ecc71",
            darkcolor="#2ecc71",
        )

        # Hyperlink Label
        s.configure("Hyperlink.TLabel", foreground="blue", font=("TkDefaultFont", 10, "underline"))

        # Frames 
        s.configure("TFrame", background=p["bg"])
        self.style.configure("TabActive.TFrame", background=p["bg"], bordercolor=p["primary"],
                             borderwidth=1, relief="solid")
        self.style.configure("TabInactive.TFrame", background=p["bg"],
                             borderwidth=1, relief="solid")
        self.style.configure("TabActive.TLabel", background=p["bg"],
                             foreground=p["primary"], font=self.font_bold)
        self.style.configure("TabInactive.TLabel", background=p["bg"],
                             foreground=p["fg"], font=self.font_main)
        
        s.configure("Card.TFrame", background=p["surface"])
        s.configure("TPanedwindow", background=p["bg"])

        # Labels 
        s.configure("TLabel", background=p["bg"], foreground=p["fg"], font=self.font_main)
        s.configure("Title.TLabel", background=p["bg"], foreground=p["fg"], font=self.font_title)
        s.configure("Subtitle.TLabel", background=p["bg"], foreground=p["fg_dim"], font=self.font_subtitle)
        s.configure("Authors.TLabel", background=p["bg"], foreground=p["fg_dim"], font=self.font_authors)
        s.configure("Header.TLabel", background=p["bg"], foreground=p["fg"], font=self.font_heading)
        s.configure("Card.TLabel", background=p["surface"], foreground=p["fg"], font=self.font_main)
        s.configure("StatusBar.TLabel", background=p["side_bg"], foreground=p["fg_dim"], font=self.font_main)
        s.configure("TableHead.TLabel", background=p["side_bg"], foreground=p["fg"], font=self.font_bold)

        # LabelFrames 
        s.configure("TLabelframe", background=p["bg"], bordercolor=p["border"],
                    borderwidth=1, relief="solid")
        s.configure("TLabelframe.Label", background=p["bg"], foreground=p["primary"],
                    font=self.font_bold)

        # Entries
        s.configure("TEntry", fieldbackground=p["surface"], foreground=p["fg"],
                    bordercolor=p["border"], borderwidth=1, relief="solid", font=self.font_main, padding=(4, 2))
        s.map("TEntry", bordercolor=[("focus", p["primary"])])

        # Spinbox 
        s.configure("TSpinbox", fieldbackground=p["surface"], foreground=p["fg"],
                    background=p["side_bg"], bordercolor=p["border"], borderwidth=1,
                    arrowcolor=p["fg"], relief="solid")

        # Buttons 
        s.configure("TButton", background=p["button"], foreground="#FFFFFF",
                    font=self.font_bold, borderwidth=0, relief="flat", padding=(10, 6))
        s.map("TButton", background=[
            ("pressed", p.get("button_pressed", p["button"])),
            ("active", p["button_hover"]),
        ])

        s.configure("Toggle.TButton", background=p["toggle_bg"], foreground=p["toggle_fg"],
                    font=self.font_bold, borderwidth=0, relief="flat", padding=(10, 6))
        s.map("Toggle.TButton",
              background=[("pressed", p.get("button_pressed", p["button"])),
                          ("active", p["button_hover"])],
              foreground=[("active", p["toggle_fg"])])

        # Remove focus ring from all TButtons
        s.layout("TButton", [
            ('Button.border', {'sticky': 'nswe', 'children': [
                ('Button.padding', {'sticky': 'nswe', 'children': [
                    ('Button.label', {'sticky': 'nswe'})
                ]})
            ]})
        ])
        s.layout("Toggle.TButton", s.layout("TButton"))

        # Radiobuttons / Checkbuttons 
        for widget in ("TRadiobutton", "TCheckbutton"):
            s.configure(widget, background=p["bg"], foreground=p["fg"],
                        font=self.font_main, indicatorcolor=p["surface"], focuscolor=p["bg"])
            s.map(widget,
                  background=[("active", p["bg"])],
                  foreground=[("disabled", p["fg_dim"])],
                  indicatorcolor=[("selected", p["primary"])])


        # Combobox (base + "Axis" variant) 
        for name in ("TCombobox", "Axis.TCombobox"):
            s.configure(
                name,
                fieldbackground=p["surface"],
                background=p["surface"],
                foreground=p["fg"],
                arrowcolor=p["primary"],           # coloured chevron
                bordercolor=p["border"],
                lightcolor=p["surface"],           # kills the clam bevel
                darkcolor=p["surface"],
                borderwidth=1,
                relief="flat",
                padding=(8, 5),                    
                selectbackground=p["surface"],     # no text highlight
                selectforeground=p["fg"],
            )
            s.map(
                name,
                fieldbackground=[("readonly", p["surface"]),
                                 ("hover", p["side_bg"]),
                                 ("focus", p["surface"])],
                bordercolor=[("focus", p["primary"]),
                             ("hover", p["primary"])],
                arrowcolor=[("pressed", p["primary_hov"]),
                            ("disabled", p["fg_dim"])],
                foreground=[("disabled", p["fg_dim"])],
            )

        # Dropdown list (classic Tk Listbox) 
        self.root.option_add("*TCombobox*Listbox.background", p["surface"])
        self.root.option_add("*TCombobox*Listbox.foreground", p["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", p["primary"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        self.root.option_add("*TCombobox*Listbox.font", self.font_main)
        self.root.option_add("*TCombobox*Listbox.borderWidth", 0)
        self.root.option_add("*TCombobox*Listbox.relief", "flat")
        self.root.option_add("*TCombobox*Listbox.highlightThickness", 1)
        self.root.option_add("*TCombobox*Listbox.highlightColor", p["border"])
