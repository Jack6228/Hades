"""GUI extension module (plouton) for Hades.

Provides the Tkinter-based graphical user interface and interactive components which use the hades-obol engine. 
"""

try:
    from hades_plouton.app import main
except ImportError as e:
    def main():
        raise ImportError(
            "GUI dependencies are missing. Please install them using:\n"
            "pip install hades-obol[plouton]"
        ) from e

__all__ = ["main"]