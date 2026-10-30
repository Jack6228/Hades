"""hades-obol: 

The Python engine for the Hades software.

Documentation: https://hades-obol.readthedocs.io/en/latest/
GitHub: https://github.com/Jack6228/Hades

Authors: 
    Jack Lee Smith, Alan Hastie, Lindsay Young, 
    Isobel Nash, Sally Law, Godfrey Fitton
"""

from __future__ import annotations
from typing import TYPE_CHECKING

# ---- Metadata ----

__version__ = "0.9.0"
__author__ = 'Jack Lee Smith, Alan Hastie, Lindsay Young, Isobel Nash, Godfrey Fitton, Sally Law'
__license__ = 'BSD 3-Clause License'
__copyright__ = 'Copyright (c) 2026 Jack Lee Smith'
__description__ = 'Fractional crystallisation modelling and solving for petrology'
__url__ = 'https://hades-obol.readthedocs.io/en/latest/'

# ---- Imports ----

# Visible to type checkers and IDEs at analysis time, but not imported at runtime, keeping initial load fast and memory usage low.
if TYPE_CHECKING:
    from .model import Obol
    from .visuals import Visuals

def __getattr__(name: str) -> object:
    """
    Lazily import public objects on first attribute access.
    """
    if name == "Obol":
        from .model import Obol
        return Obol
    if name == "Visuals":
        from .visuals import Visuals
        return Visuals
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# Expose the check for updates
from .updates import check_for_updates

__all__ = [
    "Obol", 
    "Visuals",
    "check_for_updates"
]

print(f"hades-obol v{__version__}. This is a pre-release version. Check for updates using hades.check_for_updates()")