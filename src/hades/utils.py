"""Utility functions for Hades geochemical modelling.

This module provides a collection of utility functions that support the Hades geochemical modelling workflow. It includes functions for data validation, array manipulation, asset management, and serialisation/deserialisation of dataclasses.
"""

# Dependencies
import numpy as np
from dataclasses import is_dataclass, fields
from typing import Union, get_type_hints, get_origin, get_args, Any
import sys
from functools import reduce
from importlib import resources
from pathlib import Path

from .logger import log_meta, log_debug

# %% ---- Other Helpers ----

def get_asset_path(package_name: str, filename: str) -> Path:
    """
    Safely locate an asset in both pip-installed environments and PyInstaller .exes.

    Parameters
    ----------
    package_name : str
        The name of the package where the asset is located (e.g., 'hades.assets').
    filename : str
        The name of the asset file (e.g., 'default_data.csv').

    Returns
    -------
    Path
        A pathlib.Path object pointing to the asset file. If the asset cannot be found, returns an empty Path and logs a warning.
    
    Example
    -------
    >>> get_asset_path('hades.assets', 'default_data.csv')
    >>> get_asset_path('hades_plouton.assets', 'logo.png')
    """
    # First try to use importlib.resources (works for pip-installed packages)
    try:
        # This creates a context manager that extracts the file if it's zipped inside a .whl or just returns the path if it's on disk.
        path = resources.files(package_name).joinpath(filename)
        if path.exists():
            return path
    except Exception:
        pass

    # Fallback for PyInstaller (if it packaged assets differently)
    if hasattr(sys, '_MEIPASS'):
        # Construct path expecting PyInstaller preserved the package structure
        # _MEIPASS / package_name (converted to folder) / filename
        package_folder = package_name.replace('.', '/')
        fallback = Path(sys._MEIPASS) / package_folder / filename
        
        if fallback.exists():
            return str(fallback)

    # If fail, warn and return an empty Path (or raise an error)
    print(f"Warning: Could not locate asset '{filename}' in package '{package_name}'.")
    return ''

def nice_display(arr : np.ndarray, rows : list[str], cols : list[str], title="", decimals=2, max_rows=None, max_cols=None, right_col=None, title_level=0, level=0, boolean=False) -> None:
    """
    Tidy display of 2D numpy array with row and column labels.

    Parameters
    ----------
    arr : array_like
        Array to display. One-dimensional arrays are reshaped into a single column; the resulting array must be two-dimensional.
    rows : sequence
        Labels for the rows of ``arr``.
    cols : sequence
        Labels for the columns of ``arr``.
    title : str, optional
        Title to display above the array.
    decimals : int, optional
        Number of decimal places to which values are rounded.
    max_rows : int or None, optional
        Maximum number of rows to display. If exceeded, omitted rows are represented by an ellipsis.
    max_cols : int or None, optional
        Maximum number of columns to display. If exceeded, omitted columns are represented by an ellipsis.
    right_col : sequence or None, optional
        Additional values to display in a right-hand column.
    title_level : int, optional
        Logging level used when displaying the title.
    level : int, optional
        Logging level used when displaying the table.
    boolean : bool, optional
        If True, display values as check or cross symbols instead of numbers.
    """
    arr = np.asarray(arr)
    if arr.ndim != 2:
        # Reshape to be 2D if it's 1D, otherwise raise an error
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        else:
            raise ValueError("Array must be 2-dimensional")
    
    if len(rows) != arr.shape[0] or len(cols) != arr.shape[1]:
        raise ValueError(f"rows ({len(rows)}) and cols ({len(cols)}) lengths must match array dimensions ({arr.shape})")
    
    # Convert to float for consistent formatting
    arr = np.round(arr.astype(float), decimals)

    # Crop columns if max_cols is specified
    if max_cols is not None and arr.shape[1] > max_cols:
        # Crop to first max_cols-1, add '...' and then last col
        arr = np.hstack((arr[:, :max_cols-1], np.full((arr.shape[0], 1), np.nan), arr[:, -1:]))
        cols = cols[:max_cols-1] + ['...'] + [cols[-1]]
    # Crop rows
    if max_rows is not None and arr.shape[0] > max_rows:
        arr = np.vstack((arr[:max_rows-1, :], np.full((1, arr.shape[1]), np.nan), arr[-1:, :]))
        rows = rows[:max_rows-1] + ['...'] + [rows[-1]]
    
    # Calculate column widths
    col_widths = [max((len(str(c)) for c in cols), default=0)]
    for j in range(arr.shape[1]):
        col_widths.append(max(
            len(str(cols[j])),
            max((len(str(x)) for x in arr[:, j]), default=0)
        ))
    
    row_label_width = max(len(str(r)) for r in rows) + 1
    
    # Print Title
    if title:
        log_meta(f"{title}", level=title_level)
        log_meta("=" * (len(title) + 4), level=level)
    
    # Header
    header = " " * row_label_width + "  "
    for j, col in enumerate(cols):
        header += f"{str(col):>{col_widths[j+1]}}  "
    log_meta(header.rstrip(), level=level)
    log_meta("-" * len(header), level=level)
    
    # Data rows
    for i, row_name in enumerate(rows):
        line = f"{str(row_name):<{row_label_width}}| "
        for j in range(arr.shape[1]):
            # If boolean option is True, convert to bool and then replace with tick or cross symbols
            if boolean:
                val = '✔' if arr[i, j] else '✖'
                # place in the middle not left or right aligned
                line += f"{val:^{col_widths[j+1]}}  "
            else:
                val = '-' if np.isnan(arr[i, j]) else arr[i, j]
                line += f"{val:>{col_widths[j+1]}}  "

        # If right_col is provided, append it as a final row, accounting for max_rows cropping
        if right_col is not None and i < len(right_col):
            line += f"| {right_col[i]}"

        log_meta(line, level=level)
    # Blank line
    log_meta("", level=level)

# %% ---- Data Helpers ----

def sanity_check(arr : np.ndarray, axis: int = 0, tol: float = 1e-6, to1: bool = False) -> np.ndarray:
    """
    For a given numpy array, verifies that the sums along the specified axis are normalised to 100 (or 1 if to1=True) within a specified tolerance. Raises a ValueError if the check fails.
    Ignores rows/columns that are entirely NaN.
    This is used to ensure compositional data are properly normalised before further processing. If the check fails, it will log a warning and attempt to enforce normalisation by scaling the array accordingly.

    Parameters
    ----------
    arr : np.ndarray
        The input array to check.
    axis : int, optional
        The axis along which to sum (0 for columns, 1 for rows). Default is 0.
    tol : float, optional
        The tolerance for checking normalisation. Default is 1e-6.
    to1 : bool, optional
        If True, checks for sums normalised to 1 instead of 100. Default is False.

    Returns
    -------
    np.ndarray
        The original array if normalisation is within tolerance, or a scaled array if normalisation was enforced.
    """
    log_debug(f"Normalisation Check:", level=4)
    arr = np.asarray(arr)
    if axis < 0 or axis >= arr.ndim:
        raise ValueError(f"Axis {axis} is out of bounds for array with {arr.ndim} dimensions.")
    
    sums = np.sum(arr, axis=axis, where=~np.isnan(arr).all(axis=axis, keepdims=True))
    # Mask for rows/columns that are not entirely NaN
    not_all_nan = ~np.isnan(arr).all(axis=axis)
    
    target = 1.0 if to1 else 100.0
    # Count how many of the values are outside the tolerance (excluding all-NaN rows/cols)
    Noutside = np.sum(np.abs(sums[not_all_nan] - target) > tol)

    if not np.all(np.abs(sums[not_all_nan] - target) <= tol):
        log_meta(f"{Noutside}/{not_all_nan.sum()} sums along axis {axis} are not within {tol} of {target}, enforcing normalisation...", level=15)
        # Force the sums to be exactly 100 or 1 for the purpose of the check
        arr = arr / sums[..., np.newaxis] * target if axis == 1 else arr / sums[np.newaxis, ...] * target
        assert np.all(np.abs(np.sum(arr, axis=axis, where=~np.isnan(arr).all(axis=axis, keepdims=True))[not_all_nan] - target) <= tol), "  > Sanity check failed after correction."

    log_debug(f"  > {not_all_nan.sum()} valid sums along axis {axis} are within {tol} of {target}")

    return arr

def sort_geochem(data : np.ndarray, geochem : list[str], expected_order : list[str]) -> tuple[np.ndarray, list[str]]:
    """
    For a given numpy array and two lists of the true and expected, ordered, geochemical headers, this function returns the data array and headers sorted to match the expected order. Missing columns are filled with zeros. Unsupported columns are dropped and reported.

    Parameters
    ----------
    data : np.ndarray
        The input data array, shape (N_samples, N_elements).
    geochem : list of str
        The list of geochemical headers corresponding to the columns of `data`.
    expected_order : list of str
        The desired order of geochemical headers.

    Returns
    -------
    sorted_data : np.ndarray
        The data array sorted to match `expected_order`, with missing columns filled with zeros.
    final_geochem : list of str
        The list of geochemical headers in the order of `expected_order`, including any missing elements that were filled with zeros.
    """
    # Convert all to lower case for case-insensitive matching
    geochem_lower = [g.lower() for g in geochem]
    expected_order_lower = [e.lower() for e in expected_order]

    # Identify and report unsupported values
    unsupported_elements = [
        orig for orig, low in zip(geochem, geochem_lower) 
        if low not in expected_order_lower
    ]
    if unsupported_elements:
        log_debug(f"Unsupported geochemistry removed: {unsupported_elements}", level=14)

    # Number of samples (rows) in the existing dataset
    num_samples = data.shape[0]
    
    # Trackers for our built-up sorted objects
    sorted_columns = []
    final_geochem = []
    missing_elements = []

    # Iterate through the expected order to build out the matrix correctly
    for orig_expected, low_expected in zip(expected_order, expected_order_lower):
        if low_expected in geochem_lower:
            # Element exists: Extract its corresponding column from the data matrix
            curr_idx = geochem_lower.index(low_expected)
            column_data = data[:, curr_idx]
            
            # Keep original casing from the user's input if it matched
            final_geochem.append(geochem[curr_idx])
        else:
            # Element is missing: Create a column of zeros matching sample length
            column_data = np.zeros(num_samples)
            
            # Use casing from the expected_order array
            final_geochem.append(orig_expected)
            missing_elements.append(orig_expected)
            
        sorted_columns.append(column_data)

    # Stack columns horizontally to form the final sorted matrix
    # np.column_stack automatically handles the 1D arrays extracted/generated above
    sorted_data = np.column_stack(sorted_columns) if sorted_columns else np.empty((num_samples, 0))

    if missing_elements:
        log_debug(f"Added zero compositions for unprovided elements: {missing_elements}", level=14)

    return sorted_data, final_geochem

# %% ---- Dataclass & Serialisation Helpers ----

def get_nested_attr(obj : object, path: str) -> object:
    """
    Retrieve a nested attribute from an object using a dot-separated path.
    
    Parameters
    ----------
    obj : object
        The object from which to retrieve the attribute.
    path : str
        Dot-separated string representing the nested attribute path (e.g., 'a.b.c').
        
    Returns
    -------
    object
        The value of the nested attribute, or raises AttributeError if any part of the path is invalid.
    """
    return reduce(getattr, path.split('.'), obj)

def set_nested_attr(obj : object, path: str, value : object) -> None:
    """
    Set a nested attribute on an object using a dot-separated path.

    Parameters
    ----------
    obj : object
        The object on which to set the attribute.
    path : str
        Dot-separated string representing the nested attribute path (e.g., 'a.b.c').
    value : any
        The value to set for the nested attribute.
    """
    parts = path.split('.')
    parent = reduce(getattr, parts[:-1], obj) if len(parts) > 1 else obj
    setattr(parent, parts[-1], value)

def convert_to_serialisable(obj : object) -> object:
    """
    Convert an object to a JSON-serialisable format. Handles dataclasses, numpy arrays, and basic types.

    Parameters
    ----------
    obj : object
        The object to convert.

    Returns
    -------
    object
        A JSON-serialisable representation of the object.

    Raises
    ------  
    TypeError
        If the object type is not serialisable. 
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {type(obj)} not serialisable")

def _deserialise(value : Any, type_hint : type) -> Any:
    """
    Reconstruct a value from a dictionary or list into the specified type, handling nested dataclasses, lists, and dictionaries.

    Parameters
    ----------
    value : any
        The value to deserialise, typically a dict or list.
    type_hint : type
        The expected type to deserialise into, which can be a dataclass, list, dict, or basic type.

    Returns
    -------
    object
        The deserialised object of the specified type.
    """
    if value is None:
        return None

    # Get the origin and arguments of the type hint (e.g., List[int] -> list, int)
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Treat Union types (e.g., Optional[T] is Union[T, NoneType])
    if origin is Union:
        for candidate in (a for a in args if a is not type(None)):
            try:
                return _deserialise(value, candidate)
            except Exception:
                continue
        return value

    # Nested dataclass reconstruction
    if is_dataclass(type_hint) and isinstance(value, dict):
        return from_dict(type_hint, value)

    # Dict[K, V] reconstruction
    if origin in (dict,) and isinstance(value, dict):
        _key_t, val_t = args if args else (object, object)
        return {k: _deserialise(v, val_t) for k, v in value.items()}

    # List[T] or Tuple[T, ...] reconstruction
    if origin in (list, tuple) and isinstance(value, list):
        val_t = args[0] if args else object
        seq = [_deserialise(v, val_t) for v in value]
        return tuple(seq) if origin is tuple else seq

    # Numpy array reconstruction
    if type_hint is np.ndarray:
        return np.array(value)

    # All other types are returned as-is (int, float, str, etc.)

    return value

def from_dict(cls, data):
    """
    Build a dataclass instance from a (possibly nested) dict.

    Parameters
    ----------
    cls : type
        The dataclass type to instantiate.
    data : dict
        The dictionary containing the data to populate the dataclass.

    Returns
    ------- 
    object
        An instance of the dataclass `cls` populated with data from the dictionary.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict for {cls.__name__}, got {type(data).__name__}")

    # Resolve type hints for the dataclass, including forward references
    hints = get_type_hints(cls)
    valid = {f.name for f in fields(cls)}
    kwargs = {}

    for k, v in data.items():
        if k not in valid:
            print(f"Ignored unexpected sub-parameter '{k}' for {cls.__name__}")
            continue
        kwargs[k] = _deserialise(v, hints.get(k, object))

    # Missing fields will be filled with default values if defined in the dataclass, otherwise a TypeError will be raised.
    return cls(**kwargs)

