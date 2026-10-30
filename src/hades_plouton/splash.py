"""Helpers for PyInstaller's native (bootloader) splash screen.

This module provides functions to update the text on the native splash screen and to close it when the application is ready. It checks for the presence of PyInstaller's splash screen support and handles cases where it is not available.
"""

# Dependencies
import os, sys

HAS_PYI_SPLASH = False
pyi_splash = None

# Only attempt to import if frozen by PyInstaller and the bootloader IPC exists
if getattr(sys, 'frozen', False) and '_PYI_SPLASH_IPC' in os.environ:
    try:
        import pyi_splash  # noqa: F401
        HAS_PYI_SPLASH = True
    except (ImportError, KeyError, RuntimeError):
        pyi_splash = None
        HAS_PYI_SPLASH = False

# print(f"pyi_splash: HAS_PYI_SPLASH={HAS_PYI_SPLASH}, pyi_splash={pyi_splash}")

def update_text(msg: str = '') -> None:
    """Update the native splash progress text (no-op if unsupported)."""
    if HAS_PYI_SPLASH and pyi_splash:
        try:
            pyi_splash.update_text(msg)
        except Exception:
            pass

def close() -> None:
    """Close the native splash if it is showing (no-op if unsupported)."""
    if HAS_PYI_SPLASH and pyi_splash:
        try:
            pyi_splash.close()
        except Exception:
            pass