"""Visualisation functions for Hades.

Functions and setup for creating bivariate plots, Harker diagrams, TAS diagrams, and other geochemical visualisations, both directly from Python, and for use in the Hades GUI application.
"""

# Dependencies
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from . import styles

# %% ---- Constants ---- 

_LABEL_MAP = {
    'SiO2':  'SiO₂',    'TiO2':  'TiO₂',
    'Al2O3': 'Al₂O₃',   'Fe2O3': 'Fe₂O₃',
    'MgO':   'MgO',     'CaO':   'CaO',
    'Na2O':  'Na₂O',    'K2O':   'K₂O',
}
_ALKALI = {'na2o+k2o', 'k2o+na2o'}

# %% ---- Utilities ---- 

def format_axis_labels(names: list) -> list:
    """Format a list of oxide names to their LaTeX labels."""
    return [_LABEL_MAP.get(n, n) for n in names]

def _is_alkali(comp: str) -> bool:
    """Check if a composition string represents the sum of Na₂O and K₂O."""
    return comp.lower().replace(' ', '') in _ALKALI

def _xy(arr : np.ndarray, geochem : list, x_comp : str, y_comp : str, rows=slice(None)) -> tuple[np.ndarray, np.ndarray]:
    """Extract (x, y) columns from a 2-D composition array."""
    x = arr[rows, geochem.index(x_comp)]
    if _is_alkali(y_comp):
        y = (arr[rows, geochem.index('Na2O')] +
             arr[rows, geochem.index('K2O')])
    else:
        y = arr[rows, geochem.index(y_comp)]
    return x, y

def _2d(ax : np.ndarray) -> np.ndarray:
    """Guarantee ax is a 2-D numpy array regardless of subplot shape."""
    return np.atleast_2d(ax)

def format_label(name: str) -> str:
    """Format a single oxide name to its LaTeX label."""
    return _LABEL_MAP.get(name, name)

def _save_figure(filename : str | None) -> None:
    """Save the current figure to a file, handling directory creation and extension."""
    if filename is None:
        return

    path = Path(filename)

    if path.suffix == "":
        path = path.with_suffix(".png")

    if not path.parent.exists():
        print(f"Warning: Not saving figure as directory does not exist: {path.parent}")
        return

    plt.savefig(path, dpi=300, bbox_inches='tight')

# ---- Initialisation ---- 

def init_bivariate_plot(x_order : tuple = ('SiO2',), y_order : tuple = ('TiO2', 'Fe2O3', 'Al2O3'), dpi : int = 100, figsize : tuple | None = None, sharex : str | bool = 'col', sharey : str | bool = 'row', darkmode : bool = False, **kwargs) -> tuple[plt.Figure, np.ndarray]:
    """
    Create a bivariate subplot grid for the given x and y compositions with various options for layout and appearance.

    Parameters
    ----------
    x_order : tuple of str
        The compositions to plot on the x-axis, in order of appearance.
    y_order : tuple of str
        The compositions to plot on the y-axis, in order of appearance.
    dpi : int
        The resolution of the figure in dots per inch.
    figsize : tuple of float or None
        The size of the figure in inches (width, height). If None, a default size is computed based on the number of rows and columns.
    sharex : str or bool
        If True or 'col', the x-axis is shared across columns. If False, each subplot has its own x-axis. Default is 'col'.
    sharey : str or bool
        If True or 'row', the y-axis is shared across rows. If False, each subplot has its own y-axis. Default is 'row'.
    darkmode : bool
        If True, the figure and axes are styled for dark mode with black backgrounds and white text. Default is False.
    kwargs : additional keyword arguments
        Additional keyword arguments are passed to plt.subplots().

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure object.
    axs : numpy.ndarray
        A 2-D array of Axes objects corresponding to the subplot grid, with shape (len(y_order), len(x_order)).
    """
    nrows, ncols = len(y_order), len(x_order)

    if figsize is None:
        figsize = (
            (10, 10 * 9 / 16) if (nrows == 1 and ncols == 1)
            else (5 * ncols, 4 * nrows)
        )

    # Remove layout manager so explicit gridspec margins are respected.
    gskw = kwargs.pop('gridspec_kw', {
        'hspace': 0.075, 'wspace': 0.05,
        'left': 0.08, 'right': 0.92, 'top': 0.93, 'bottom': 0.15,
    })

    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols,
        figsize=figsize, dpi=dpi,
        sharex=sharex, sharey=sharey,
        gridspec_kw=gskw,
        **kwargs,
    )
    axs = np.atleast_2d(axs)

    if darkmode:
        fig.patch.set_facecolor('black')
        for ax in axs.flat:
            ax.set_facecolor('black')
            for spine in ax.spines.values():
                spine.set_color('white')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')

    xlabels = format_axis_labels(list(x_order))
    ylabels = format_axis_labels(list(y_order))

    for i in range(nrows):
        for j in range(ncols):
            ax = axs[i, j]
            ax.minorticks_on()
            ax.tick_params(axis='x', which='both', top=True, bottom=True,
                           labeltop=(i == 0), labelbottom=(i == nrows - 1))
            ax.tick_params(axis='y', which='both', left=True, right=True,
                           labelleft=(j == 0), labelright=(j == ncols - 1))

    for j, label in enumerate(xlabels):
        if nrows > 1:
            axs[0, j].set_xlabel(label, fontsize=12, labelpad=10)
            axs[0, j].xaxis.set_label_position('top')
        axs[-1, j].set_xlabel(label, fontsize=12, labelpad=10)

    for i, label in enumerate(ylabels):
        axs[i, 0].set_ylabel(label, fontsize=12)
        if ncols > 1:
            axs[i, -1].set_ylabel(label, fontsize=12)
            axs[i, -1].yaxis.set_label_position('right')

    return fig, axs

def init_harker_plot(x_order : tuple = ('SiO2',), y_order : tuple = ('P', 'Zr', 'Ce'), nrows : int = 1, y_unit : str | None = 'ppm', dpi : int = 100, figsize : tuple | None = None, darkmode : bool = False, **kwargs) -> tuple[plt.Figure, np.ndarray]:
    """
    Initialise a Harker-style subplot grid.

    Each panel plots one element from *y_order* against *x_order[0]* (SiO₂). All panels are fully independent - no shared axes.

    By default produces 1 row x len(y_order) columns; pass nrows > 1 to wrap into a multi-row grid.

    Parameters
    ----------
    x_order : tuple of str
        The compositions to plot on the x-axis, in order of appearance. Default is ('SiO2',).
    y_order : tuple of str
        The compositions to plot on the y-axis, in order of appearance. Default is ('P', 'Zr', 'Ce').
    nrows : int
        The number of rows in the subplot grid. Default is 1.
    y_unit : str or None
        The unit to append to the y-axis labels. If None, no unit is appended. Default is 'ppm'.
    dpi : int
        The resolution of the figure in dots per inch. Default is 100.
    figsize : tuple of float or None
        The size of the figure in inches (width, height). If None, a default size is computed based on the number of rows and columns.
    darkmode : bool 
        If True, the figure and axes are styled for dark mode with black backgrounds and white text. Default is False.
    kwargs : additional keyword arguments
        Additional keyword arguments are passed to plt.subplots().

    Returns 
    -------
    fig : matplotlib.figure.Figure
        The created figure object.
    axs : numpy.ndarray
        A 2-D array of Axes objects corresponding to the subplot grid, with shape (len(y_order), 1).

    Examples
    --------
    >>> # Classic 1 x 3
    >>> fig, axs = init_harker_plot(y_order=['P', 'Zr', 'Ce'])

    >>> # 2 x 4 for 8 elements
    >>> fig, axs = init_harker_plot(
    ...     y_order=['P','Zr','Ce','Ba','Nb','La','Sm','Eu'], nrows=2
    ... )
    """
    x_order = list(x_order)
    y_order = list(y_order)
    n_y   = len(y_order)
    ncols = np.ceil(n_y / nrows).astype(int)

    xlabels = format_axis_labels(x_order)
    ylabels = format_axis_labels(y_order)

    if figsize is None:
        figsize = (4 * ncols, 4 * nrows)

    gskw = kwargs.pop('gridspec_kw', {
        'hspace': 0.30, 'wspace': 0.30,
        'left': 0.08, 'right': 0.95, 'top': 0.93, 'bottom': 0.12,
    })

    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols,
        figsize=figsize, dpi=dpi,
        sharex=False, sharey=False,   # every Harker panel is fully independent
        gridspec_kw=gskw,
        **kwargs,
    )
    # Guarantee 2-D so .flat works regardless of grid shape
    axs_2d = np.atleast_2d(axs)

    if darkmode:
        fig.patch.set_facecolor('black')
        for ax in axs_2d.flat:
            ax.set_facecolor('black')
            for spine in ax.spines.values():
                spine.set_color('white')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')

    ylabel_suffix = f' ({y_unit})' if y_unit else ''

    for k, ax in enumerate(axs_2d.flat):
        if k >= n_y:
            ax.set_visible(False)      # hide surplus slots in non-square grids
            continue
        ax.minorticks_on()
        ax.tick_params(
            axis='both', which='both',
            top=True, bottom=True, left=True, right=True,
            labelleft=True, labelbottom=True,
        )
        ax.set_xlabel(f'{xlabels[0]} wt.%', fontsize=12, labelpad=10)
        ax.set_ylabel(f'{ylabels[k]}{ylabel_suffix}', fontsize=12)

    # Reshape to (n_y, 1): downstream functions address panels as ax[j, i] where j = y_order index and i = x_order index (always 0 for Harker).
    # The visual layout (nrows x ncols) is preserved in the figure; this reshape is purely for indexing compatibility.
    axs_compat = np.array(list(axs_2d.flat)[:n_y]).reshape(n_y, 1)

    return fig, axs_compat

def make_tas_background(ax : plt.Axes | None = None, dpi : int = 120) -> tuple[plt.Figure, plt.Axes]:
    """
    Draw TAS (Total Alkali-Silica) classification boundaries and field labels.

    Creates a new figure when *ax* is None; otherwise populates the supplied
    Axes and returns its parent Figure.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or None   
        The Axes to populate with the TAS background. If None, a new figure and Axes are created.
    dpi : int
        The resolution of the figure in dots per inch. Only used when creating a new figure. Default is 120.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object containing the TAS plot.
    ax : matplotlib.axes.Axes
        The Axes object containing the TAS plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10 * 9 / 16), dpi=dpi, layout='constrained')
    else:
        fig = ax.get_figure()

    # Boundary polylines - each vertex is stored as (Na₂O+K₂O, SiO₂) so that zip(*verts) gives (alkali_vals, sio2_vals) directly.
    boundary_lines = [
        [(0.5,41),(3,41),(7,41),(9.4,45),(11.5,48.5),(14,52.5)],
        [(0.5,45),(3,45),(5,45),(7.3,49),(9.3,53),(11.7,57.8),(13.5,61),(15,63.8)],
        [(3,41),(3,45),(5,45),(5,52),(5.9,57),(7,63),(8,69)],
        [(0.5,52),(5,52),(7.3,49),(9.4,45)],
        [(0.7,57),(5.9,57),(9.3,53),(11.5,48.5)],
        [(1,63),(7,63),(11.7,57.8),(14,52.5),(15.083,50)],
        [(1,76),(8,69),(13,69)],
    ]
    for verts in boundary_lines:
        alkali, sio2 = zip(*verts)
        ax.plot(sio2, alkali, c='k', linewidth=1, zorder=0)

    # Field label positions - (SiO₂, Na₂O+K₂O)
    field_labels = {
        'Foidite':                    (44,   12.5),
        'Phonolite':                  (57,   14.0),
        'Tephriphonolite':            (53.4, 11.7),
        'Phonotephrite':              (49.2,  9.3),
        'Basanite':                   (45,    7.1),
        'Picro-\nBasalt':             (43,    1.8),
        'Basalt':                     (48.6,  2.5),
        'Trachybasalt':               (48.72, 5.4),
        'Basaltic\nTrachyandesite':   (53.2,  6.8),
        'Basaltic\nAndesite':         (54.5,  3.2),
        'Trachyandesite':             (58,    8.3),
        'Andesite':                   (60,    3.8),
        'Trachyte':                   (64.8, 10.0),
        'Rhyolite':                   (72,    9.5),
        'Dacite':                     (67,    4.3),
    }
    for label, (sio2, alkali) in field_labels.items():
        ax.text(sio2, alkali, label, fontsize=9, ha='center', va='center',
                color='grey', zorder=1)

    ax.set_xlim(40, 79)
    ax.set_ylim(0, 16)
    ax.set_xlabel(r'$\mathrm{SiO_2}$ wt.%')
    ax.set_ylabel(r'$\mathrm{Na_2O} + \mathrm{K_2O}$ wt.%')
    return fig, ax

def init_tas_plot(ax : plt.Axes, model : "hades.model.Obol", legend : bool = True) -> tuple[plt.Figure, plt.Axes]:
    """
    Populate *ax* with the data suite, initial magma path, and computed melt-evolution trends. *ax* should already carry the TAS background from :func:`make_tas_background`.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes to populate with TAS data. If None, a new figure and Axes are created.
    model : hades.model.Obol or None
        The Hades model object containing the data suite and magma paths. If None, only the TAS background is drawn.
    legend : bool
        If True, a legend is added to the plot. Default is True.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The Figure object containing the TAS plot.
    ax : matplotlib.axes.Axes   
        The Axes object containing the TAS plot.
    """
    geochem = model.namespace.geochem

    # Data suite - reuses _xy() which handles the alkali-sum column
    data = getattr(model.datasuite, 'data', None)
    if data is not None and data.size > 0:
        x, y = _xy(data, geochem, 'SiO2', 'Na2O+K2O')
        ax.plot(x, y, **styles.data_suite_style)

    # Magma paths - _magma_xy() replaces the old _get_tas_xy_data() because _xy() already handles 'Na2O+K2O' via _is_alkali().
    n_phases   = len(model.namespace.phase_transitions)
    run_phases = [p for p in range(n_phases) if model.results[p].isrun]

    for mode in ('initial', 'computed'):
        is_initial     = (mode == 'initial')
        line_props     = (styles.initial_phase_line_properties if is_initial
                          else styles.computed_phase_line_properties)
        phases_to_plot = list(range(n_phases)) if is_initial else run_phases
        alpha          = 0.6 if is_initial else 1.0

        start_marker_drawn = False  # drawn once for the first valid phase only

        for p in phases_to_plot:
            x, y = _magma_xy(model, p, mode, 'SiO2', 'Na2O+K2O')

            if x is None or np.isnan(x).any() or np.isnan(y).any():
                continue

            phase_name   = model.namespace.phases[p + 1]
            phase_colour = styles.phase_colours[phase_name]

            ax.plot(x, y, **line_props)
            ax.scatter(x[-1], y[-1],
                       edgecolors=phase_colour,
                       label=phase_name,
                       alpha=alpha,
                       **styles.phase_markerstyle)

            # Origin marker - same start_marker_drawn fix as plot_magma:
            # p_idx == 0 would fail when early phases contain NaN and are
            # skipped; the flag triggers on whichever phase plots first.
            if not start_marker_drawn:
                origin_name   = model.namespace.phases[p]
                origin_colour = styles.phase_colours[origin_name]
                ax.scatter(x[0], y[0],
                           edgecolors=origin_colour,
                           label=origin_name,
                           alpha=alpha,
                           **styles.phase_markerstyle)
                start_marker_drawn = True

    # Deduplicated legend (handles repeated phase labels across modes)
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        seen = {}
        for h, l in zip(handles, labels):
            if l and l not in seen:
                seen[l] = h
        if seen:
            ax.legend(seen.values(), seen.keys(), loc='upper left', fontsize=8, frameon=False)

# %% ---- Data Suite ---- 

def plot_datasuite(ax : plt.Axes | np.ndarray, model : "hades.model.Obol", x_order : tuple, y_order : tuple) -> list:
    """
    Plot the reference data suite on the bivariate grid.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray
        The Axes or 2-D array of Axes to populate with the data suite.
    model : hades.model.Obol
        The Hades model object containing the data suite.
    x_order : tuple of str
        The compositions to plot on the x-axis, in order of appearance.
    y_order : tuple of str
        The compositions to plot on the y-axis, in order of appearance.
    """
    ax = _2d(ax)
    artists = []

    data = getattr(model.datasuite, 'data', None)
    if data is None or data.size == 0:
        return artists          # ← always a list

    geochem = model.namespace.geochem
    for j, y_comp in enumerate(y_order):
        for i, x_comp in enumerate(x_order):
            x, y = _xy(data, geochem, x_comp, y_comp)
            artists.extend(ax[j, i].plot(x, y, **styles.data_suite_style))

    return artists

# %% ---- Magma ---- 

def _magma_xy(model : "hades.model.Obol", p : int, mode : str, x_comp : str, y_comp : str) -> tuple[np.ndarray | None, np.ndarray | None]:
    """
    Prepare (x, y) data for a given magma path phase and mode from the model object.

    Parameters
    ----------
    model : hades.model.Obol  
        The Hades model object containing the magma paths and results.
    p : int
        The index of the phase transition to extract data for.
    mode : str
        The mode of data to extract. Must be one of 'initial', 'computed', or 'traces'.
    x_comp : str
        The composition to plot on the x-axis.
    y_comp : str
        The composition to plot on the y-axis.

    Returns
    -------
    tuple of (x, y) arrays or (None, None) if data is unavailable or invalid.
    """
    if mode == 'computed':
        arr  = model.results[p].melt_evolution
        rows = slice(None)
    elif mode == 'traces':
        arr  = model.magma.traces
        rows = slice(p, p + 2)
    else:   # 'initial' or 'traces'
        arr  = model.magma.initial
        rows = slice(p, p + 2)

    if arr is None or arr.size == 0:
        return None, None

    return _xy(arr, model.namespace.geochem, x_comp, y_comp, rows)

def plot_magma(ax : plt.Axes | np.ndarray, model : "hades.model.Obol", x_order : tuple, y_order : tuple, transition_idxs : list[int] | None = None, mode : str = 'initial', phase_highlight : int | None = None) -> dict[str, list]:
    """
    Plot magma paths on the bivariate grid, with options for initial, computed, or trace modes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray
        The Axes or 2-D array of Axes to populate with the magma paths.
    model : hades.model.Obol
        The Hades model object containing the magma paths and results.
    x_order : tuple of str
        The compositions to plot on the x-axis, in order of appearance.
    y_order : tuple of str
        The compositions to plot on the y-axis, in order of appearance.
    transition_idxs : list of int or None
        Optional list of phase transition indices to plot. If None, all phases are considered.
    mode : str
        The mode of data to plot. Must be one of 'initial', 'computed', or 'traces'.
    phase_highlight : int or None
        Optional index of a phase to highlight. If None, no phase is highlighted.

    Returns
    -------
    dict
        A dictionary mapping phase keys to lists of matplotlib artists (lines and scatter points) created for each phase.
    """
    ax = _2d(ax)
    n_phases = len(model.namespace.phase_transitions)

    candidates = (list(range(n_phases)) if transition_idxs is None else [int(p) for p in transition_idxs])

    is_initial = (mode == 'initial')
    alpha      = 0.6 if is_initial else 1.0
    if is_initial:
        line_props = styles.initial_phase_line_properties
        phases_to_plot = candidates
    elif mode == 'traces':
        line_props = styles.trace_phase_line_properties
        phases_to_plot = [p for p in candidates if model.trace_results[p].isrun]
    elif mode == 'computed':
        line_props = styles.computed_phase_line_properties
        phases_to_plot = [p for p in candidates if model.results[p].isrun]

    new_artists: dict[str, list] = {}

    for j, y_comp in enumerate(y_order):
        for i, x_comp in enumerate(x_order):
            a = ax[j, i]

            # Reset per subplot so every panel gets its origin marker
            start_marker_drawn = False

            for p in phases_to_plot:
                x, y = _magma_xy(model, p, mode, x_comp, y_comp)

                # Skip entirely invalid / uncomputed phases
                if x is None or np.isnan(x).any() or np.isnan(y).any():
                    continue

                phase_key    = f"{mode}_phase_{p}"
                phase_name   = model.namespace.phases[p + 1]
                phase_colour = styles.phase_colours[phase_name]

                if phase_key not in new_artists:
                    new_artists[phase_key] = []

                # End-node marker 
                sc_end = a.scatter(
                    x[-1], y[-1],
                    edgecolors=phase_colour,
                    label=phase_name,
                    alpha=alpha,
                    **styles.phase_markerstyle,
                )

                # Connector line 
                if phase_highlight is not None and p != phase_highlight and not is_initial:
                    lp = {k: v for k, v in line_props.items() if k not in ('c', 'color')}
                    ln, = a.plot(x, y, c='darkslategrey', **lp)
                else:
                    ln, = a.plot(x, y, **line_props)

                new_artists[phase_key].extend([sc_end, ln])

                # Origin marker - first *valid* phase only 
                # Using a flag instead of p_idx == 0 so that phases skipped due to NaN (e.g. uncomputed earlier phases) don't prevent the marker from appearing on whichever phase IS first drawn.
                if not start_marker_drawn:
                    origin_name   = model.namespace.phases[p]   # node before this segment
                    origin_colour = styles.phase_colours[origin_name]
                    sc_start = a.scatter(
                        x[0], y[0],
                        edgecolors=origin_colour,
                        label=origin_name,
                        alpha=alpha,
                        **styles.phase_markerstyle,
                    )
                    new_artists[phase_key].append(sc_start)
                    start_marker_drawn = True               # ← only ever drawn once

    return new_artists

# %% ---- Minerals ---- 

def plot_minerals(ax : plt.Axes | np.ndarray, data_matrix : np.ndarray, geochem : list[str], labels : list[str], x_order : tuple, y_order : tuple) -> list:
    """
    Plot mineral end-member compositions across every subplot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray
        The Axes or 2-D array of Axes to populate with the mineral compositions.
    data_matrix : np.ndarray
        A 2-D array where each row corresponds to a mineral or bulk composition, and each column corresponds to a geochemical component.
    geochem : list of str   
        The list of geochemical components corresponding to the columns of *data_matrix*.
    labels : list of str
        The labels for each row in *data_matrix*, corresponding to mineral names or bulk compositions.
    x_order : tuple of str
        The compositions to plot on the x-axis, in order of appearance.
    y_order : tuple of str
        The compositions to plot on the y-axis, in order of appearance.

    Returns
    -------
    list
        A list of matplotlib artists (lines) created for each mineral composition across the subplots.
    """
    ax = _2d(ax)
    artists = []

    for j, y_comp in enumerate(y_order):
        for i, x_comp in enumerate(x_order):
            a = ax[j, i]
            x, y = _xy(data_matrix, geochem, x_comp, y_comp)
            for k, label in enumerate(labels):
                line, = a.plot(x[k], y[k], **styles.mineralstyles[label])
                artists.append(line)

    return artists

# %% ---- Legend ----

def make_legend(fig, minerals=False):
    """
    Makes a legend which can be added to a figure. Optional arguments control what is shown in the legend.
    """
    from matplotlib.lines import Line2D
    from hades.styles import mineralstyles, phase_colours

    # 2. Build explicit lists of Matplotlib proxy artists
    mineral_proxies = []
    seen_labels = set()
    system_proxies = []
    titles = []

    # Process System Paths & Trends
    system_proxies = [
        Line2D([0], [0], linestyle='--', color='k', linewidth=1.5, alpha=0.5, label='Initial LLOD'),
        Line2D([0], [0], linestyle='-', color='r', linewidth=2.0, label='Computed LLOD'),
        Line2D([0], [0], linestyle='-', color='dodgerblue', linewidth=2.0, label='Trace Element LLOD'),
        Line2D([0], [0], linestyle='', marker='o', markerfacecolor='goldenrod', markeredgecolor='none', markersize=7, alpha=0.5, label='Data Suite'),
    ]
    titles.append("Data & Magma")
    
    # Process Minerals (skipping system components like bulk, datasuite, assimilant for column 1)
    if minerals:

        system_proxies.extend([
            Line2D([0], [0], linestyle='', marker='*', markerfacecolor='hotpink', markeredgecolor='k', markersize=12, label='Bulk Comp.'),
            Line2D([0], [0], linestyle='', marker='^', markerfacecolor='teal', markeredgecolor='k', markersize=8, label='Assimilant')
        ])

        for k, v in mineralstyles.items():
            if k in ['bulk', 'datasuite', 'assimilant']:
                continue
            lbl = v.get('label', k)
            if lbl not in seen_labels:
                seen_labels.add(lbl)
                art = Line2D([0], [0], linestyle='', marker=v['marker'], markerfacecolor=v['color'],
                            markeredgecolor=v['markeredgecolor'], markeredgewidth=v['markeredgewidth'],
                            markersize=v['markersize'], alpha=v['alpha'], label=lbl)
                mineral_proxies.append(art)

        titles.append("Minerals")

    
    # Process Crystallisation Evolution Stages
    phase_proxies = []
    for name, color in phase_colours.items():
        # Represent liquidus differentiation fields using hollow circles
        phase_proxies.append(Line2D([0], [0], linestyle='', marker='o',
                                    markerfacecolor='none', markeredgecolor=color,
                                    label=name, linewidth=1.5, markersize=8))
    titles.append("Evolution Stages")
    
    if not minerals:
        proxy_groups = system_proxies + phase_proxies
    else:
        proxy_groups = mineral_proxies + system_proxies + phase_proxies
    
    handletextpad = 0.5

    # Call legend construction 
    fig.legend(
        handles=proxy_groups,
        labels=[h.get_label() for h in proxy_groups],
        loc='upper center',
        bbox_to_anchor=(0.5, 0.98),
        ncol=5,
        fontsize=9,
        frameon=False,
        handletextpad=handletextpad,
        columnspacing=1.8,
        labelspacing=1.2,
    )

# %% ---- Primary Visualisation Functions ---- 

def bivar(model : "hades.model.Obol", x_order : tuple = ('SiO2', 'MgO'), y_order : tuple = ('TiO2', 'Fe2O3', 'Al2O3'), legend : bool = False, phase_highlight : int | None = None, return_fig_ax : bool = False, mode : str = 'computed', cropped : bool = False, filename : str | None = None) -> tuple[plt.Figure, np.ndarray] | None:
    """
    Creates a panel of bivarate plots for a Hades `Obol` model, plotting the data suite, expected and modelled LLODs and optionally mineral compositions, for the desired major oxides.

    To save the figure, pass a valid *filename* (e.g. 'output.png').

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model instance to visualise.
    x_order : tuple of str, optional
        The major oxide(s) to plot on the x-axis. Default is ('SiO2', 'MgO').
    y_order : tuple of str, optional
        The major oxide(s) to plot on the y-axis. Default is ('TiO2', 'Fe2O3', 'Al2O3').
    legend : bool, optional
        If True, adds a legend to the plot. Default is False.
    phase_highlight : int or None, optional
        If specified, highlights the given phase transition index in the plots and plots the mineral compositions for that phase. Default is None (no highlight).
    return_fig_ax : bool, optional
        If True, returns the figure and axes objects instead of displaying the plot. Default is False.
    mode : str, optional
        The mode of magma path to plot. Can be 'initial', 'traces', or 'computed'. Default is 'computed'. 'initial' plots the preliminary LLOD as computed from the data suite, 'computed' plots preliminary and computed LLODs, and 'traces' plots the both LLODs, and that modelled with the addition of accessory minerals.
    cropped : bool, optional
        If True, keeps the viewport cropped to the data suite, ignoring the mineral compositions outwith this view.
    filename : str or None, optional
        If specified, saves the figure to the given filename as well as displaying it. Default is None (display the plot).

    Returns
    -------
    tuple of (matplotlib.figure.Figure, numpy.ndarray) or None
        If `return_fig_ax` is True, returns the figure and axes objects. Otherwise, displays the plot and returns None.

    Examples
    --------
    >>> from hades.visuals import bivar
    >>> bivar(model)

    >>> fig, ax = bivar(model, phase_highlight=2, return_fig_ax=True)
    """

    # mode is computed or traces; each plot initial and the selected mode

    if phase_highlight is not None:
        n = len(model.namespace.phase_transitions)
        if not isinstance(phase_highlight, int) or not 0 <= phase_highlight < n:
            raise ValueError(
                f"phase_highlight must be an int in [0, {n - 1}], "
                f"got {phase_highlight!r}."
            )

    fig, axs = init_bivariate_plot(x_order=x_order, y_order=y_order)

    plot_datasuite(axs, model, x_order=x_order, y_order=y_order)
    plot_magma(axs, model, x_order=x_order, y_order=y_order,
               mode='initial', phase_highlight=phase_highlight)
    if mode == 'traces':
        plot_magma(axs, model, x_order=x_order, y_order=y_order,
                   mode='traces', phase_highlight=phase_highlight)
        plot_magma(axs, model, x_order=x_order, y_order=y_order,
                mode='computed', phase_highlight=phase_highlight)
    else:
        plot_magma(axs, model, x_order=x_order, y_order=y_order,
                mode='computed', phase_highlight=phase_highlight)

    if cropped:
        xlims = [axs[0, i].get_xlim() for i in range(len(x_order))]
        ylims = [axs[j, 0].get_ylim() for j in range(len(y_order))]
        for j in range(len(y_order)):
            for i in range(len(x_order)):
                axs[j, i].set_xlim(xlims[i])
                axs[j, i].set_ylim(ylims[j])

    if phase_highlight is not None:
        data_matrix = np.vstack([
            model.results[phase_highlight].cotectics,
            model.results[phase_highlight].bulk_mineralogy,
            model.assimilant.composition[:8],
        ])
        plot_minerals(
            axs, data_matrix,
            geochem=model.namespace.geochem,
            labels=model.meta.minerals_ + ['bulk', 'assimilant'],
            x_order=x_order,
            y_order=y_order,
        )

    # Plot a legend above the figure
    if legend:
        make_legend(fig=fig)

    _save_figure(filename)
    
    if return_fig_ax:
        return fig, axs
    plt.show()

def tas(model : "hades.model.Obol", return_fig_ax : bool = False, fig_kw : dict | None = None, filename : str | None = None) -> tuple[plt.Figure, plt.Axes] | None:
    """
    Display a TAS (Total Alkali-Silica) diagram for the given Hades model. Displays the data suite and the preliminary and computed LLODs, if they exist.

    To save the figure, pass a valid *filename* (e.g. 'output.png').

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model instance to visualise.
    return_fig_ax : bool, optional
        If True, returns the figure and axes objects instead of displaying the plot. Default is False.
    fig_kw : dict, optional
        Keyword arguments passed directly to `plt.subplots()` (e.g., figsize, dpi).
    filename : str or None, optional
        If specified, saves the figure to the given filename as well as displaying it. Default is None (display the plot).

    Returns
    -------
    tuple of (matplotlib.figure.Figure, matplotlib.axes.Axes) or None
        If `return_fig_ax` is True, returns the figure and axes objects. Otherwise, displays the plot and returns None.

    Examples
    --------
    >>> from hades.visuals import tas
    >>> tas(model)

    >>> fig, ax = tas(model, return_fig_ax=True)
    """
    fig, ax = make_tas_background()
    init_tas_plot(ax, model)

    _save_figure(filename)

    if return_fig_ax:
        return fig, ax
    plt.show()

def mineral_usage(model : "hades.model.Obol", return_fig_ax : bool = False, fig_kw : dict | None = None, filename : str | None = None, **kwargs) -> tuple[plt.Figure, plt.Axes] | None:
    """
    Plots a heatmap of mineral usage (present / absent) across all phase transitions.

    To save the figure, pass a valid *filename* (e.g. 'output.png').

    Parameters
    ----------
    model : hades.model.Obol
        Hades model instance.
    return_fig_ax : bool, optional
        If True, returns (fig, ax) without calling plt.show(). Default is False.
    fig_kw : dict, optional
        Keyword arguments passed directly to `plt.subplots()` (e.g., figsize, dpi).
    filename : str or None, optional
        If specified, saves the figure to the given filename as well as displaying it. Default is None (display the plot).
    **kwargs
        Additional keyword arguments passed directly to `ax.imshow()` 
        (e.g., cmap, interpolation, aspect, vmin, vmax).

    Returns
    -------
    tuple of (matplotlib.figure.Figure, matplotlib.axes.Axes) or None
        If `return_fig_ax` is True, returns the figure and axes objects. Otherwise, displays the plot and returns None.

    Examples
    --------
    Using defaults
    >>> mineral_usage(model)
     
    Customising figure size/dpi AND heatmap color/aspect
    >>> mineral_usage(model, fig_kw={'figsize': (12, 8), 'dpi': 300}, cmap='viridis', aspect='equal')
    """
    # 1Set default figure arguments while allowing user overrides
    default_fig_kw = {'figsize': (10, 6), 'dpi': 120, 'layout': 'constrained'}
    if fig_kw is not None:
        default_fig_kw.update(fig_kw)

    # Set default imshow arguments while allowing user overrides
    default_imshow_kw = {'aspect': 'auto', 'cmap': 'PiYG', 'interpolation': 'none'}
    default_imshow_kw.update(kwargs)

    min_usage = model.minerals.usage.copy()
    # Force all values in places where no initial magma sample is present to False (i.e. these stages will not be run, so the mineral usage is irrelevant)
    ms = model.magma.magma_samples
    ms = np.logical_and(ms[:-1], ms[1:]).astype(bool)
    min_usage[~ms] = False

    # Create figure and plot
    fig, ax = plt.subplots(**default_fig_kw)

    ax.imshow(min_usage.T, **default_imshow_kw)

    ax.set_yticks(np.arange(len(model.namespace.minerals_title)), model.namespace.minerals_title)
    ax.set_xticks(np.arange(len(model.namespace.phases)) - 0.5, model.namespace.phases)
    ax.set_xlabel("Phase Transitions")
    ax.set_ylabel("Minerals")
    ax.set_title("Mineral Usage for Current Model")

    # Add faint grid lines above the imshow
    # TODO
    # print("www")
    # ax.axvline(np.arange(len(model.namespace.phases)) - 0.5, color='grey', alpha=0.3, linewidth=0.5)
    # ax.axhline(np.arange(len(model.namespace.minerals)) - 0.5, color='grey', alpha=0.3, linewidth=0.5)

    # Add grey text bottom right of the figure for extra info
    # fig.text(0.99, -0.02, f"Transitions with no initial magma compositions are automatically excluded", fontsize=8, color='grey', ha='right', va='bottom', transform=fig.transFigure)

    _save_figure(filename)
    
    if return_fig_ax:
        return fig, ax
    plt.show()

def harker(model : "hades.model.Obol", y_order=('P', 'Zr', 'Ce'), nrows=1, y_unit='ppm', return_fig_ax=False, filename : str | None = None) -> tuple[plt.Figure, np.ndarray] | None:
    """
    Plots a series of Harker diagrams for the given Hades model. Each panel displays one trace or minor element from *y_order* against SiO2. The initial magma path and trace-data magma path are also plotted for comparison.

    To save the figure, pass a valid *filename* (e.g. 'output.png').

    Parameters
    ----------
    y_order : sequence[str]
        Y-axis elements - one panel per entry.  All must be present in ``model.namespace.geochem``.
    nrows   : int
        Number of visual rows.  Default ``1`` → classic single-row layout.
        ``ncols`` is computed automatically from ``len(y_order) / nrows``.
    y_unit  : str | None
        Unit suffix for y-axis labels (``'ppm'``, ``'wt.%'``, etc.).
    return_fig_ax : bool
        If True, returns the figure and axes objects instead of displaying the plot. Default is False.
    filename : str or None, optional
        If specified, saves the figure to the given filename as well as displaying it. Default is None (display the plot).

    Returns
    -------
    tuple of (matplotlib.figure.Figure, numpy.ndarray) or None
        If `return_fig_ax` is True, returns the figure and axes objects. Otherwise, displays the plot and returns None.

    Examples
    --------
    >>> from hades.visuals import harker
    >>> # Classic 1 x 3 layout
    >>> harker(model)

    >>> # 2 x 4 grid for 8 trace elements
    >>> harker(model, y_order=['P','Zr','Ce','Ba','Nb','La','Sm','Eu'], nrows=2)
    """
    x_order = ['SiO2']
    y_order = list(y_order)

    fig, axs = init_harker_plot(
        x_order=x_order,
        y_order=y_order,
        nrows=nrows,
        y_unit=y_unit,
    )

    plot_datasuite(axs, model, x_order=x_order, y_order=y_order)
    plot_magma(axs, model, x_order=x_order, y_order=y_order, mode='initial')
    plot_magma(axs, model, x_order=x_order, y_order=y_order, mode='traces')

    _save_figure(filename)
    
    if return_fig_ax:
        return fig, axs
    plt.show()
