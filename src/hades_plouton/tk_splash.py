"""A borderless Tkinter splash window used during local runs / testing.

This module defines the TkSplash class, which creates a simple splash screen with a title, status text, and a progress bar. The splash window is displayed during the initialisation of the Hades application.
"""

# Dependencies
import tkinter as tk
from tkinter import ttk

class TkSplash:
    def __init__(self, master, BASE_DIR='', title="HADES", text="Loading...", size=(420, 300), bg="#1e1e1e") -> None:
        """Initialise the splash window with a title, status text, and progress bar."""

        # Use relative path to compile assets
        image_path = BASE_DIR / "hades_plouton" / "assets" / "HadesLogo_Dark_Icon_Transparent_120px.png"

        w, h = size
        sw, sh = master.winfo_screenwidth(), master.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2

        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)                 # borderless
        self.win.wm_attributes("-topmost", True)        # stay above during load

        frame = tk.Frame(self.win, bg=bg, bd=1, relief="solid", width=w, height=h)
        frame.pack(fill="both", expand=True)
        frame.pack_propagate(False)                     # lock size, no shrink-to-fit

        # Image below the title (ignored gracefully if missing)
        self._img = None
        if image_path:
            try:
                self._img = tk.PhotoImage(file=image_path)
                tk.Label(frame, image=self._img, bg=bg).pack(pady=(24, 0))
            except Exception:
                self._img = None

        # Title text ("Loading" area / app name)
        tk.Label(frame, text=title, fg="white", bg=bg, font=("Century Gothic Bold", 24, "")).pack(pady=(6, 8))

        # Status text
        self._status = tk.Label(frame, text=text, fg="#aaaaaa", bg=bg, font=("Segoe UI", 10))
        self._status.pack(pady=(4, 8))

        # Determinate bar we advance manually
        self._bar = ttk.Progressbar(frame, mode="determinate", style="Splash.Horizontal.TProgressbar", length=w - 80, maximum=100)
        self._bar.pack(pady=(0, 20))
        self._progress = 0

        # Lock geometry AFTER building, so nothing recalculates it later
        self.win.update_idletasks()
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.update()

    def text(self, msg: str, step: int = 12) -> None:
        """Update status + nudge the bar forward, then repaint."""
        self._status.config(text=msg)
        self._progress = min(self._progress + step, 100)
        self._bar["value"] = self._progress
        self.win.update()          # forces an immediate repaint


    def close(self) -> None:
        """Close the splash window."""
        try:
            self._bar.stop()
        except Exception:
            pass
        self.win.destroy()
