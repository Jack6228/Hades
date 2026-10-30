"""Defines styling configurations for Hades plots and visualisations.

Configures the visual appearance of plots, including colors, markers, and line styles for different minerals and phases, as well as some helper functions.
"""

# Dependencies
import os, sys
from matplotlib import rcParams, font_manager

from .logger import log_meta

# Dynamically locate the directory where THIS current file lives
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# %% ---- Formatting Variables ----

size: int = 7
mineralstyles = {
    # TODO: Fix names?
    'olivine': {'color': 'forestgreen', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 5, 'label': 'Olivine', 'markeredgecolor': 'black', 'markeredgewidth': 0.5, 'clip_on': True},
    'spinel': {'color': '#FF0000', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Spinel', 'markeredgecolor': 'none', 'markeredgewidth': 0, 'clip_on': True},
    'clinopyroxene': {'color': 'crimson', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Clinopyroxene', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'orthopyroxene': {'color': 'orange', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Orthopyroxene', 'markeredgecolor': 'brown', 'markeredgewidth': 0.5, 'clip_on': True},
    'plagioclase': {'color': 'tan', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Plagioclase', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'amphibole': {'color': 'darkgreen', 'alpha': 0.75, 'marker': 'd', 'markersize': size, 'zorder': 2, 'label': 'Amphibole', 'markeredgecolor': 'brown', 'markeredgewidth': 0.5, 'clip_on': True},
    'magnetite': {'color': 'k', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Magnetite', 'markeredgecolor': 'none', 'markeredgewidth': 0, 'clip_on': True},
    'ilmenite': {'color': '#FF00FF', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Ilmenite', 'markeredgecolor': 'none', 'markeredgewidth': 0, 'clip_on': True},
    'kfeldspar': {'color': 'r', 'alpha': 0.75, 'marker': 'd', 'markersize': size, 'zorder': 2, 'label': 'Biotite', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'biotite': {'color': 'r', 'alpha': 0.75, 'marker': 'd', 'markersize': size, 'zorder': 2, 'label': 'Biotite', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'quartz': {'color': 'tan', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Quartz', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'titanaugite': {'color': 'purple', 'alpha': 0.75, 'marker': 's', 'markersize': size, 'zorder': 2, 'label': 'Titanaugite', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'nepheline': {'color': 'blue', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Nepheline', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},   
    'leucite': {'color': 'cyan', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Leucite', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'nosean_hauyne': {'color': 'magenta', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Nosean', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'alkali_amphibole': {'color': 'grey', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 2, 'label': 'Alkali-amph.', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    # Other data
    'bulk': {'color': 'hotpink', 'alpha': 0.75, 'marker': '*', 'markersize': size*2, 'zorder': 3, 'label': 'Quartz', 'markeredgecolor': 'k', 'markeredgewidth': 0.5, 'clip_on': True},
    'datasuite': {'color': 'goldenrod', 'alpha': 0.75, 'marker': 'o', 'markersize': 20, 'zorder': 1, 'label': 'Data Suite', 'markeredgecolor': 'none', 'markeredgewidth': 0, 'alpha': 0.5},
    'assimilant': {'color': 'goldenrod', 'alpha': 0.75, 'marker': 'o', 'markersize': size, 'zorder': 1, 'label': 'Assimilant', 'markeredgecolor': 'none', 'markeredgewidth': 0, 'alpha': 0.5},
}
phase_colours = {
    'Primary': '#FFE600',#'yellow',
    'Primitive': '#FF6600',#'gold',
    'Basic': '#D00000',#'orange',
    'Intermediate': '#7B1FA2',#'darkorange',
    'Evolved': '#4E2A1E',#'orangered',
    'End': '#1E1E24',#'darkmagenta',
} 
phase_markerstyle = {
    'marker': 'o',
    'color': 'none',
    's': 60,
    'zorder': 10,
    'linewidth': 2,
}
initial_phase_line_properties = {
    'c': 'k',
    'ls': '--',
    'alpha': 0.5,
    'linewidth': 1.5,
    'zorder': 3,
    'label': 'Initial/Input'
}
computed_phase_line_properties = {
    'c': 'r',
    'linewidth': 2,
    'zorder': 3,
    'label': 'Computed'
}
trace_phase_line_properties = {
    'c': 'dodgerblue',
    'linewidth': 2,
    'zorder': 3,
    'label': 'Traces'
}
data_suite_style = {
    'color': 'goldenrod',
    'marker': 'o',
    'markeredgecolor': 'k',
    'markersize': 4,          # Approximates s=15; adjust visually if needed
    'zorder': 1,
    'alpha': 0.5,
    'markeredgewidth': 0.0,   # Equivalent to linewidth=0.
    'linestyle': 'none',      # CRITICAL: Prevents lines connecting the points
}

# %% ---- Font Helper ----

def setup_fonts():
    """Call this once at startup to register custom fonts."""
    try:
        from .utils import get_asset_path
        fontfile = 'Figtree-VariableFont_wght.ttf'
        font_path = get_asset_path('hades_plouton.assets', fontfile)
        
        font_manager.fontManager.addfont(font_path)
        rcParams.update({'font.family': 'Figtree'})
        log_meta("Figtree font loaded successfully.")
    except FileNotFoundError:
        log_meta("Warning: Figtree font not found. Using system default.")
    except Exception as e:
        log_meta(f"Warning: Could not load custom font: {e}")


# Auto-setup when module is imported (optional but convenient)
setup_fonts()