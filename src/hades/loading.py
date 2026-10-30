"""File loading functions for Hades. 

This module provides utilities to load and parse .xlsx and .csv files, automatically handling orientation and extracting relevant data structures.
"""

# Dependencies
import openpyxl
import numpy as np
import csv
import os
from typing import Tuple, List, Any

from .logger import warn, log, log_warning, log_meta, log_debug

def parse_file(file_path: str) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Parses either an .xlsx or a .csv file, automatically handling orientation, and returns a tuple of: (final_matrix, row_names, col_headers).

    Parameters
    ----------
    file_path : str
        Path to the .xlsx or .csv file to be parsed.    
    
    Returns
    -------
    final_matrix : np.ndarray
        A 2D numpy array containing the numeric data extracted from the file.
    row_names : List[str]
        A list of row names (or sample identifiers) extracted from the file.
    col_headers : List[str]
        A list of column headers (or feature names) extracted from the file.

    Examples
    --------
    >>> final_matrix, row_names, col_headers = parse_file("data.xlsx")
    """
    ext = os.path.splitext(file_path)[-1].lower()
    raw_grid = []
    skipped_rows_count = 0

    log_debug(f"{os.path.basename(file_path)}", level=8)

    if ext == '.xlsx':
        # Load the workbook and read the active sheet
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        for row in sheet.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                raw_grid.append(list(row))
            else:
                skipped_rows_count += 1
                
    elif ext == '.csv':
        # Read the CSV file, handling empty rows
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                processed_row = [cell for cell in row]
                if any(cell is not None for cell in processed_row):
                    raw_grid.append(processed_row)
                else:
                    skipped_rows_count += 1
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Drop empty rows
    if skipped_rows_count > 0:
        log_debug(f"Skipped {skipped_rows_count} completely empty rows during initial file read.", level=14)
    
    log_debug(f"Raw grid dimensions: {len(raw_grid)} rows x {max(len(row) for row in raw_grid) if raw_grid else 0} columns", level=14)

    # Process the grid to determine orientation, headers, and row names
    final_matrix, row_names, col_headers = process_grid(raw_grid)

    log_debug(f"Loaded data with shape: {final_matrix.shape}", level=14)
    log_debug(f"{len(row_names)} rows: '{row_names[0]}' ... '{row_names[-1]}'", level=15)
    log_debug(f"{len(col_headers)} cols: '{col_headers[0]}' ... '{col_headers[-1]}'", level=15)

    return final_matrix, row_names, col_headers

def process_grid(grid: List[List[Any]]) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Validates and processes the raw grid data to determine the presence of column headers and row names, and extracts the numeric data into a numpy array.

    Parameters
    ----------
    grid : List[List[Any]]
        A 2D list representing the raw data grid extracted from the file.
    
    Returns
    -------
    final_matrix : np.ndarray
        A 2D numpy array containing the numeric data extracted from the grid.
    row_names : List[str]
        A list of row names (or sample identifiers) extracted from the grid.
    col_headers : List[str]
        A list of column headers (or feature names) extracted from the grid.
    """
    if not grid or not grid[0]:
        raise ValueError("The provided file is empty.")

    def is_numeric(val) -> bool:
        """
        Helper function to check if a value can be interpreted as a numeric type (int or float).
        """
        if val is None:
            return False
        try:
            float(str(val).strip())
            return True
        except ValueError:
            return False

    # Detect structures (Headers & Row Names) by checking corners
    has_col_headers = not all(is_numeric(x) for x in grid[0][1:] if x is not None)
    has_row_names = not all(is_numeric(r[0]) for r in grid[1:] if len(r) > 0 and r[0] is not None)

    def get_stats(values):
        """
        Helper to calculate average and variance safely from a list of numbers
        """
        nums = [float(x) for x in values if x is not None and is_numeric(x)]
        if not nums:
            return None, None
        mean = sum(nums) / len(nums)
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        return mean, variance

    # Column headers detection (Top Row)
    row0_values = grid[0][1:]
    # Flatten a sample of the actual body data to compare against
    body_data_samples = [item for r in grid[1:] for item in r[1:]]

    # Compute statistics for the top row and body data
    r0_mean, r0_var = get_stats(row0_values)
    body_mean, body_var = get_stats(body_data_samples)

    # Initial non-numeric check
    has_col_headers = not all(is_numeric(x) for x in row0_values if x is not None)

    # If top row IS numeric, run the variance/mean shift check
    if not has_col_headers and r0_mean is not None and body_mean is not None:
        # Flag as header if the average value shifts significantly, 
        # or if the data body has vastly higher variance than the rigid header row
        mean_shift = abs(r0_mean - body_mean) > (abs(body_mean) * 0.3)
        variance_gap = body_var > (r0_var * 3) if r0_var > 0 else body_var > 0
        
        if mean_shift or variance_gap:
            has_col_headers = True

    # Row names detection (First Column)
    col0_values = [r[0] for r in grid[1:] if len(r) > 0]
    
    c0_mean, c0_var = get_stats(col0_values)

    # Initial non-numeric check
    has_row_names = not all(is_numeric(x) for x in col0_values if x is not None)

    # If first column IS numeric, run the variance/mean shift check
    if not has_row_names and c0_mean is not None and body_mean is not None:
        mean_shift = abs(c0_mean - body_mean) > (abs(body_mean) * 0.3)
        variance_gap = body_var > (c0_var * 3) if c0_var > 0 else body_var > 0
        
        if mean_shift or variance_gap:
            has_row_names = True

    # Index offsets for data extraction
    data_start_row = 1 if has_col_headers else 0
    data_start_col = 1 if has_row_names else 0

    # Determine Orientation based on the maximum bounds of the inner matrix
    inner_rows = len(grid) - data_start_row
    inner_cols = max(len(row) for row in grid) - data_start_col

    log_debug(f" >> Default setup is {inner_rows} rows x {inner_cols} columns")
    log_debug(f" >> Has headers: {has_col_headers}")
    log_debug(f" >> Has row names: {has_row_names}")
    log_debug(f" >> Entries per row: {np.unique([len(row) for row in grid])}")

    # Standard layout vs Transposed layout detection
    if inner_cols > inner_rows:
        log_debug(" >> [Orientation] Detected Samples as column headers")
        
        # Recalculate states because orientation flipped axes
        has_col_headers, has_row_names = has_row_names, has_col_headers
        data_start_row = 1 if has_col_headers else 0
        data_start_col = 1 if has_row_names else 0

    # Extract headers
    if has_col_headers:
        col_headers = [str(x).strip() if x is not None else f"Column {i+1}" for i, x in enumerate(grid[0])]
        col_headers = col_headers[data_start_col:]
    else:
        col_headers = [f"Column {i+1}" for i in range(max(len(row) for row in grid) - data_start_col)]

    log_debug(f" >> Column headers: {col_headers}")

    # Extract data and row names
    data_rows = grid[data_start_row:]
    num_samples = len(data_rows)
    num_features = max(len(row) for row in grid) - data_start_col
    
    final_matrix = np.zeros((num_samples, num_features), dtype=np.float64)
    row_names = []
    value_conversion_errors = 0

    for sample_idx, row in enumerate(data_rows):
        # Extract row label
        if has_row_names and len(row) > 0 and row[0] is not None:
            row_names.append(str(row[0]).strip())
        else:
            row_names.append(f"Sample {sample_idx + 1}")

        # Extract numeric content
        for f_idx in range(num_features):
            col_idx = f_idx + data_start_col
            val = row[col_idx] if col_idx < len(row) else None
            
            try:
                final_matrix[sample_idx, f_idx] = float(val) if val is not None else 0.0
            except ValueError:
                value_conversion_errors += 1
                final_matrix[sample_idx, f_idx] = 0.0

    log_debug(f" >> Row names: {row_names}")

    if value_conversion_errors > 0:
        log_debug(f" >> Replaced {value_conversion_errors} non-numeric values with 0.0.")

    log_debug(f"--- Processing Complete: Matrix Shape {final_matrix.shape} ({len(row_names)} samples) ---\n")
    return final_matrix, row_names, col_headers

def autocompute_initial_magma(SiO2_phase_bounds: list = None, data: np.ndarray = None, data_sample_names: list = None) -> Tuple[np.ndarray, list]:
    """
    Automatically computes initial magmas based on provided SiO2 phase bounds and dataset.
    
    Parameters
    ----------
    SiO2_phase_bounds : list
        A list of SiO2 phase boundaries to segment the dataset.
    data : np.ndarray
        A 2D numpy array containing the dataset, where the first column is assumed to be SiO2 content.
    data_sample_names : list
        A list of sample names corresponding to the rows in the data array.

    Returns
    -------
    np.ndarray
        An array of initial magma compositions computed based on the provided phase bounds.1
    list
        A list of sample names corresponding to the computed initial magmas.
    """
    
    log_meta("Auto-computing initial magmas", level=8)
    comp, sample_names = [], []
    for i in range(len(SiO2_phase_bounds) + 1):
        # Keep only points with SiO2 between the bounds
        df = data.copy()
        if i == 0:
            df = df[(df[:,0] <= SiO2_phase_bounds[i])]
        elif i == len(SiO2_phase_bounds):
            df = df[(df[:,0] >= SiO2_phase_bounds[i-1])]
        else:
            df = df[(df[:,0] >= SiO2_phase_bounds[i-1]) & (df[:,0] <= SiO2_phase_bounds[i])]

        if df.shape[0] == 0:
            comp.append(np.full(data.shape[1], np.nan))  # Append NaN array for this range
            sample_names.append(None)
            log_meta(f"{df.shape[0]:<4} sample(s) {SiO2_phase_bounds[i-1] if i > 0 else '-inf'} <= SiO2 <= {SiO2_phase_bounds[i] if i < len(SiO2_phase_bounds) else 'inf'} --> sample = [empty]", level=14)
            continue

        # Get the mean SiO2 value
        mean_SiO2 = np.mean(df[:,0])
        # Find the closest point to the mean SiO2 value
        closest_idx = np.argmin(np.abs(data[:,0] - mean_SiO2))
        closest_point = data[closest_idx]
        log_meta(f"{df.shape[0]:<4} sample(s) {SiO2_phase_bounds[i-1] if i > 0 else '-inf'} <= SiO2 <= {SiO2_phase_bounds[i] if i < len(SiO2_phase_bounds) else 'inf'} --> sample = {data_sample_names[closest_idx]}", level=14)
        comp.append(closest_point)
        sample_names.append(data_sample_names[closest_idx])

    # For the 'end' point, use the highest SiO2 sample in the dataset, unless it is already included or the previous point (df.shape[0] == 0) was empty
    if df.shape[0] > 0:
        highest_idx = np.argmax(data[:,0])
        highest_point = data[highest_idx]
        if not any(np.array_equal(highest_point, c) for c in comp):
            log_meta(f"End sample ({np.max(data[:,0]):.2f} wt%) = {data_sample_names[highest_idx]}", level=14)
            comp.append(highest_point)
            sample_names.append(data_sample_names[highest_idx])
        else:
            log_meta(f"End sample ({np.max(data[:,0]):.2f} wt%) already --> end magma ignored", level=14)
            comp.append(np.full(data.shape[1], np.nan))  # Append NaN array for this range
            sample_names.append(None)
    else:
        log_meta(f"End sample not available", level=14)
        comp.append(np.full(data.shape[1], np.nan))  # Append NaN array for this range
        sample_names.append(None)

    N_non_nan = sum(1 for c in comp if not np.isnan(c).all())
    log_meta(f"{N_non_nan}/{len(comp)} initial magmas successfully computed", level=9)

    return np.array(comp), sample_names


