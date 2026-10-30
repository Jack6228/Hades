"""Wrapper functions to the stateless hades.visuals plotting functions, providing a stateful GUI interface for interactive use.

Defines the BivariateVisualiser class, which manages a matplotlib figure and axes, tracks plotted artists, and provides methods to plot data suites, magma paths, and mineral compositions in a bivariate plot. It also handles embedding the plot in a tkinter GUI with optional navigation toolbar support.
"""

# Dependencies
import numpy as np

from hades.visuals import (
    init_bivariate_plot,
    plot_datasuite,
    plot_magma,
    plot_minerals,
)

class BivariateVisualiser:
    """
    Stateful GUI wrapper around the stateless hades.visuals plotting functions.

    Parameters
    ----------
    x_order : list[str]
        The oxides to display on the x-axis (ordered).
    y_order : list[str]
        The oxides to display on the y-axis (ordered).
    """

    def __init__(self, x_order : list[str] = ('SiO2', 'MgO'), y_order : list[str] = ('TiO2', 'Fe2O3', 'Al2O3')) -> None:
        """Store the axis orders and initialise empty figure/axes/canvas references."""

        # matplotlib state
        self.fig    = None
        self.ax     = None
        self.canvas = None

        self.x_order = list(x_order)
        self.y_order = list(y_order)

        # Artist buckets: generic and magma-specific
        self._artists: dict[str, list] = {'datasuite': [], 'minerals': []}
        self._magma:   dict[str, list] = {}

        # tkinter state (populated by mount()) 
        self._frame          = None  
        self._toolbar_parent = None   
        self._toolbar        = None
        self._canvas_widget  = None

    # ---- Figure / Canvas Lifecycle ----

    def init_bivariate_plot(self, **kwargs) -> tuple:
        """
        Initialise a new figure and axes for the current x_order and y_order.
        Any kwargs are passed to hades.visuals.init_bivariate_plot().

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to hades.visuals.init_bivariate_plot().

        Returns
        -------
        fig, ax : matplotlib.Figure, matplotlib.Axes
            Figure and axes objects for the new plot. The axes are also stored in self.ax.
        """
        self.fig, self.ax = init_bivariate_plot(
            x_order=self.x_order,
            y_order=self.y_order,
            **kwargs,
        )
        return self.fig, self.ax

    def mount(self, frame, toolbar_parent=None) -> None:
        """
        Embed self.fig as a tkinter canvas and attach an optional nav toolbar.

        Stores both frame references so that rebuild() can remount without the caller having to pass them again.

        Parameters
        ----------
        frame : tk/ttk widget
            Grid row 0 of this widget receives the canvas.
        toolbar_parent : tk/ttk widget | None
            Grid row 0 of this widget receives the NavigationToolbar.
            Typically the controls frame below the canvas.
        """
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg, NavigationToolbar2Tk,
        )

        self._frame          = frame
        self._toolbar_parent = toolbar_parent

        self._destroy_canvas()                      # tear down any previous canvas

        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self._canvas_widget = canvas.get_tk_widget()
        self._canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        self.canvas = canvas

        if toolbar_parent is not None:
            self._toolbar = NavigationToolbar2Tk(
                canvas, toolbar_parent, pack_toolbar=False,
            )
            self._toolbar.grid(row=0, column=0, sticky="ew")
            self._toolbar.update()

    def rebuild(self, x_order = None, y_order = None) -> None:
        """
        Reinitialise the figure with (optionally updated) axis orders and remount it in the same tkinter frames.

        All tracked artists are discarded because the axes are replaced. Call the plot_* methods afterwards to repopulate.

        Parameters
        ----------
        x_order : list[str] | None
            New x-axis order; if None, the previous order is retained.
        y_order : list[str] | None
            New y-axis order; if None, the previous order is retained.
        """
        if x_order is not None:
            self.x_order = list(x_order)
        if y_order is not None:
            self.y_order = list(y_order)

        self._clear_all()
        self.init_bivariate_plot()
        self.mount(self._frame, self._toolbar_parent)

    def _destroy_canvas(self) -> None:
        """Safely destroy the current canvas widget and toolbar."""
        for attr in ('_canvas_widget', '_toolbar'):
            widget = getattr(self, attr, None)
            if widget is not None:
                try:
                    widget.destroy()
                except Exception:
                    pass
                setattr(self, attr, None)
        self.canvas = None

    # ---- Internal Helpers ----

    def _refresh(self) -> None:
        """Redraw the canvas if it exists."""
        if self.canvas is not None:
            self.canvas.draw_idle()

    def _remove(self, artist_list: list) -> None:
        """Remove every artist in the list from its axes, then clear it."""
        for artist in artist_list:
            try:
                artist.remove()
            except Exception:
                pass
        artist_list.clear()

    def _clear_all(self) -> None:
        """Discard all artist references (called before a full rebuild)."""
        for lst in self._artists.values():
            lst.clear()
        self._magma.clear()

    def rescale_axes(self, ax=None) -> None:
        """Autoscale the given axes (or self.ax if None) and refresh the canvas."""
        target = ax if ax is not None else self.ax
        if target is None:
            return
        for a in np.atleast_2d(target).flat:
            a.relim()
            a.autoscale_view()
        self._refresh()

    def clear_data_suite(self) -> None:
        """Remove tracked data suite artists."""
        self._remove(self._artists['datasuite'])
        self._refresh()

    def plot_data_suite(self, model, ax=None) -> None:
        """Draw (or redraw) the data suite for the given model. Clears any existing data suite artists first."""
        ax = self.ax if ax is None else ax
        self.clear_data_suite()
        new = plot_datasuite(ax, model, self.x_order, self.y_order)
        self._artists['datasuite'].extend(new)   # new is always a list
        self._refresh()

    def clear_magma(self, mode : str | None = None, phase_idxs : int | list[int] | None = None) -> None:
        """
        Remove tracked magma artists.

        Parameters
        ----------
        mode : str | None
            If None, all magma artists are cleared. Otherwise, only artists for the given mode are cleared.
        phase_idxs : int | list[int] | None
            If None, all phases for the given mode are cleared. Otherwise, only artists for the specified phase indices are cleared.
        """
        if mode is None:
            for artist_list in self._magma.values():
                self._remove(artist_list)
            self._magma.clear()
        else:
            if phase_idxs is None:
                keys = [k for k in self._magma if k.startswith(f"{mode}_")]
            else:
                if isinstance(phase_idxs, int):
                    phase_idxs = [phase_idxs]
                keys = [f"{mode}_phase_{p}" for p in phase_idxs]
            for key in keys:
                if key in self._magma:
                    self._remove(self._magma[key])
        self._refresh()

    def plot_magma(self, model : "hades.model.Obol", mode : str = 'initial', transition_idxs : int | list[int] | None = None, phase_highlight : int | list[int] | None = None, ax=None) -> None:
        """
        Draw (or redraw) the magma path for the given model and mode. Clears any existing magma artists for the specified mode and phase indices first.

        Parameters
        ----------
        model : hades.model.Obol
            The model instance containing the magma path data.
        mode : str
            The mode of the magma path to plot (e.g., 'initial', 'final').
        transition_idxs : int | list[int] | None
            The phase indices to plot. If None, all phases for the given mode are plotted.
        phase_highlight : int | list[int] | None
            The phase indices to highlight in the plot. If None, no phases are highlighted.
        ax : matplotlib.Axes | None
            The axes to plot on. If None, self.ax is used.
        """
        ax = self.ax if ax is None else ax
        self.clear_magma(mode=mode, phase_idxs=transition_idxs)
        new = plot_magma(
            ax, model, self.x_order, self.y_order,
            transition_idxs=transition_idxs,
            mode=mode,
            phase_highlight=phase_highlight,
        )
        for key, artists in new.items():
            self._magma.setdefault(key, []).extend(artists)
        self._refresh()

    def clear_minerals(self) -> None:
        """Remove tracked mineral artists."""
        self._remove(self._artists['minerals'])
        self._refresh()

    def plot_minerals(self, model : "hades.model.Obol", phase_idx : int, ax=None) -> None:
        """
        Draw (or redraw) the mineral compositions for the given model and phase index. Clears any existing mineral artists first.
        
        Parameters
        ----------
        model : hades.model.Obol
            The model instance containing the mineral composition data.
        phase_idx : int
            The index of the phase for which to plot mineral compositions.
        ax : matplotlib.Axes | None
            The axes to plot on. If None, self.ax is used
        """
        ax = self.ax if ax is None else ax
        self.clear_minerals()
        data_matrix = np.vstack([
            model.results[phase_idx].cotectics,
            model.results[phase_idx].bulk_mineralogy,
            model.assimilant.composition[:8],
        ])
        new = plot_minerals(
            ax, data_matrix,
            geochem=model.namespace.geochem,
            labels=model.meta.minerals_ + ['bulk', 'assimilant'],
            x_order=self.x_order,
            y_order=self.y_order,
        )
        self._artists['minerals'].extend(new)
        self._refresh()
