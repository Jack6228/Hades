"""Wrappers to the backend to export data to Excel and PDF formats."""

# Dependencies
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

# %% ---- Excel Data Exporting ---- 

class ExportData:

    def go(self, model : "hades.model.Obol", filename : str = None) -> tuple[str, bool]:
        """
        Exports the model data to an Excel file. If no filename is provided, prompts the user to select a save location.
        
        Parameters
        ----------
        model : hades.model.Obol
            The Hades model instance containing the data to be exported.
        filename : str, optional
            The desired filename for the exported Excel file. If None, a save dialog will be presented to the user.
            
        Returns
        -------
        tuple[str, bool]
            A tuple containing the filename of the saved Excel file and a boolean indicating success (True) or cancellation (False).
        """
        if filename is None:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Hades_{now_str}.xlsx"

        root = tk.Tk()
        root.withdraw()
        user_filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename,
            title="Save As"
        )
        root.destroy()

        if user_filename:
            filename = user_filename
        else:
            print("Export cancelled by user.")
            return "", False

        model.saveData(filename)
        return filename, True

def saveExcel(model : "hades.model.Obol", filename : str = None) -> tuple[str, bool]:
    """
    Saves the model data to an Excel file. If no filename is provided, prompts the user to select a save location.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model instance containing the data to be exported.
    filename : str, optional
        The desired filename for the exported Excel file. If None, a save dialog will be presented to the user.

    Returns
    -------
    tuple[str, bool]
        A tuple containing the filename of the saved Excel file and a boolean indicating success (True) or cancellation (False).
    """
    exporter = ExportData()
    return exporter.go(model, filename)

# %% ---- PDF Exporting ----

class HadesPDFGenerator:

    def __init__(self, root, model, style_manager) -> None:
        self.root = root
        self.model = model
        self.style_manager = style_manager

    def generate_pdf(self, **kwargs) -> tuple[str, bool]:
        """
        Generates a PDF from the model data using the specified template and options.

        Parameters
        ----------
        **kwargs : dict
            Options for PDF generation, such as whether to include headers, footers, images, and the theme.

        Returns
        -------
        tuple[str, bool]
            A tuple containing the filename of the saved PDF file and a boolean indicating success (True) or cancellation (False).
        """
        # When run the first time, open a dialog to ask for options. If the user cancels, return early. 
        # _open_options_dialog() will re-call this function with the selected options if the user confirms.

        # TEMP TODO: currently, ignore the option pop-up 
        # if not kwargs:
        #     opts = self._open_options_dialog()
        #     if not opts:  # User closed dialog via window 'X' button or cancelled
        #         return "", False
        #     kwargs = opts

        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"Hades_{now_str}.pdf"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            title="Save PDF As",
            initialfile=default_filename
        )

        if not file_path:
            print("PDF export cancelled by user.")
            return "", False

        self._show_progress_and_save(file_path, kwargs)

        return file_path, True

    def _open_options_dialog(self) -> dict:
        """
        Opens a modal dialog to allow the user to select PDF generation options.

        Returns
        -------
        dict
            A dictionary containing the selected options, or None if the user cancels.
        """
        p = self.style_manager.palette          # current colour tokens

        dialog = tk.Toplevel(self.root)
        dialog.title("PDF Options")
        dialog.geometry("320x250")
        dialog.configure(bg=p["bg"])           # ← fix: theme the Toplevel bg
        dialog.transient(self.root)

        # move to the center of the parent window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()

        var_include_header = tk.BooleanVar(value=True)
        var_include_footer = tk.BooleanVar(value=True)
        var_include_images = tk.BooleanVar(value=False)
        var_theme = tk.StringVar(value="Standard")

        ttk.Label(
            dialog, text="Configure PDF Options", font=("Helvetica", 11, "bold")
        ).pack(pady=10)

        ttk.Checkbutton(
            dialog, text="Include Header", variable=var_include_header
        ).pack(anchor="w", padx=20, pady=2)
        ttk.Checkbutton(
            dialog, text="Include Footer", variable=var_include_footer
        ).pack(anchor="w", padx=20, pady=2)
        ttk.Checkbutton(
            dialog, text="Include Images", variable=var_include_images
        ).pack(anchor="w", padx=20, pady=2)

        theme_frame = ttk.Frame(dialog)
        theme_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side="left")
        ttk.Radiobutton(
            theme_frame, text="Standard", variable=var_theme, value="Standard"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            theme_frame, text="Dark", variable=var_theme, value="Dark"
        ).pack(side="left")

        # Local storage for options upon confirmation
        result_holder = {}

        def on_confirm():
            result_holder["options"] = {
                "include_header": var_include_header.get(),
                "include_footer": var_include_footer.get(),
                "include_images": var_include_images.get(),
                "theme": var_theme.get(),
            }
            dialog.destroy()

        ttk.Button(dialog, text="Continue", command=on_confirm).pack(pady=15)

        # Pause main thread here while modal dialog is open
        dialog.wait_window()

        return result_holder.get("options", None)

    def _show_progress_and_save(self, file_path : str, options : dict) -> None:
        """
        Creates a progress window and starts the PDF generation in a background thread, updating the progress bar dynamically.

        Parameters
        ----------
        file_path : str
            The path where the PDF will be saved.
        options : dict
            A dictionary containing the PDF generation options.
        """
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Generating PDF...")
        progress_win.geometry("320x120")
        progress_win.transient(self.root)
        
        progress_win.update_idletasks()
        px = self.root.winfo_x() + (self.root.winfo_width() // 2) - (progress_win.winfo_width() // 2)
        py = self.root.winfo_y() + (self.root.winfo_height() // 2) - (progress_win.winfo_height() // 2)
        progress_win.geometry(f"+{px}+{py}")

        progress_win.grab_set()

        lbl_status = ttk.Label(progress_win, text="Initialising...", style="Status.TLabel")
        lbl_status.pack(pady=10)

        progress_bar = ttk.Progressbar(
            progress_win, orient="horizontal", length=250, mode="determinate",
             style="Saving.Horizontal.TProgressbar"
        )
        progress_bar.pack(pady=5)

        # State tracking
        save_state = {"done": False, "error": None}

        # Background worker function
        def worker():
            try:
                print(self.model.meta)
                self.model.savePDF(file_path)
            except Exception as e:
                save_state["error"] = e
            finally:
                save_state["done"] = True

        # Start saving immediately in the background
        threading.Thread(target=worker, daemon=True).start()

        # Dynamic progress animation loop
        def update_progress(current_val=0):
            # Handle error if thread caught an exception
            if save_state["error"]:
                progress_win.destroy()
                raise RuntimeError(f"Error during PDF generation: {save_state['error']}")

            # If file saving is finished, rush to 100%
            if save_state["done"]:
                progress_bar["value"] = 100
                lbl_status.config(text="Saved Successfully!")
                # Brief hold at 100% so user sees completion before closing
                self.root.after(200, progress_win.destroy)
                return

            # Smooth gradual progress while waiting (caps at 90% until done)
            time_increment_ms = 150
            loop_advance = 5  # increment per loop
            if current_val < 90:
                current_val += loop_advance
                progress_bar["value"] = current_val

                # Update status labels dynamically based on stage
                if current_val < 30:
                    lbl_status.config(text="Loading Template...")
                elif current_val < 60:
                    lbl_status.config(text="Injecting Variables...")
                else:
                    lbl_status.config(text="Compiling PDF...")

            # Poll every 50ms for high responsiveness
            self.root.after(time_increment_ms, lambda: update_progress(current_val))

        update_progress()

        # Block parent window until compilation and progress dialog finish
        progress_win.wait_window()