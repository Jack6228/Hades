"""Exporting utilities for Hades model results to Excel and Typst formats.

Saves model results to Excel files with multiple sheets, and generates Typst code for tables and figures for PDF reports.
"""

# Dependencies
import typst
import numpy as np
from datetime import datetime
from pathlib import Path
import os, shutil
from .logger import log
import openpyxl

# %% ---- Excel Writer ----

def compile_excel(model : "hades.model.Obol", filename : str | None = None) -> None:
    """
    Compiles the model results into an Excel file with multiple sheets.
    
    Parameters  
    ----------
    model : hades.model.Obol
        The Hades model object containing results and metadata.
    filename : str | None
        The desired output filename. If None, a timestamped filename is generated.
    """
    # Generate a timestamped filename if none is provided
    if filename is None:
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Hades_{now_str}.xlsx"

    sheets_to_save = []

    # Run the processing functions to generate data for each sheet
    sheets_to_save.append(("Initial Magma", _process_magma(model, 'initial')))
    sheets_to_save.append(("Computed Magma", _process_magma(model, 'computed')))
    sheets_to_save.append(("Cotectics", _process_cotectics(model)))
    sheets_to_save.append(("Bulk Mineralogy", _process_bulk_min(model)))

    _write_excel(filename, sheets_to_save)

def _process_magma(model : "hades.model.Obol", mode : str = 'initial') -> list[list]:
    """
    Converts the magma compositions into a structured list suitable for Excel export.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing magma compositions.
    mode : str
        'initial' for initial magma compositions, 'computed' for computed magma compositions.

    Returns
    -------
    list[list]
        A 2D list representing the magma compositions, ready for Excel export.
    """
    data = [[f'{mode.title()} Magma Compositions']]
    data.append([''])
    
    # Extract values based on the mode and whether trace results are available
    if any(model.trace_results[phase].isrun for phase in range(5)):
        if mode == 'initial':
            vals = model.magma.initial[:,:]
        elif mode == 'computed':
            vals = model.magma.traces[:,:]
        cols = model.namespace.geochem
        units = ["wt.%"] * 8 + ["ppm"] * (len(cols) - 8)
        
    else:
        if mode == 'initial':
            vals = model.magma.initial[:,:8]
        elif mode == 'computed':
            vals = model.magma.computed[:,:8]
        cols = model.namespace.oxides
        units = ["wt.%"] * len(cols)

    rows = model.namespace.phases
    samples = model.magma.magma_samples

    # Replace nan with empty string for better Excel readability
    vals = np.where(np.isnan(vals), "", vals)

    cols_2d = np.array(cols)[:, np.newaxis]
    units = np.array(units)[:, np.newaxis]
    vals = np.hstack([cols_2d, vals.T, units])

    # Compile to data list
    data.append([''] + list(rows))
    data.append(['Sample'] + list(samples))
    data.extend(vals.tolist())
    data.append([''])
    
    return data

def _process_cotectics(model : "hades.model.Obol") -> list[list]:
    """
    Converts the cotectic compositions into a structured list suitable for Excel export.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing cotectic compositions.
    
    Returns
    -------
    list[list]
        A 2D list representing the cotectic compositions, ready for Excel export.
    """
    data = [['Cotectic Compositions (wt.%)']]
    data.append([''])

    # Extract cotectic compositions for each phase that has been run
    for phase in range(5):
        if model.results[phase].isrun:

            if model.trace_results[phase].isrun:
                cols = model.trace_results[phase].structurals
                rows = [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_] + model.namespace.accessory_minerals_formal
                vals = model.trace_results[phase].cotectics.round(2)
                units = ["wt.%"] * 8 + ["ppm"] * (len(cols) - 8)

            else:
                cols = model.namespace.oxides
                rows = [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_]
                vals = model.results[phase].cotectics.round(2)
                units = ["wt.%"] * len(cols)
        else:
            continue

        rows_2d = np.array(rows)[:, np.newaxis]
        vals = np.hstack([rows_2d, vals])

        # Compile to data list
        data.append([f"{model.namespace.phase_transitions[phase]}"])
        data.append([''] + list(cols))
        data.extend(vals.tolist())
        data.append([''] + list(units))
        data.append([''])

    return data

def _process_bulk_min(model : "hades.model.Obol") -> list[list]:
    """
    Extracts optimised mineral assemblage and fractions into a structured list suitable for Excel export.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing bulk mineralogy results.

    Returns
    -------
    list[list]
        A 2D list representing the bulk mineralogy, ready for Excel export.
    """
    data = [['Optimised Mineral Assemblage and Fractions (wt.%)']]
    data.append([''])

    bulk = []
    phases = []

    # Extract bulk mineralogy for each phase that has been run

    for phase in range(5):
        if model.results[phase].isrun:
            phases.append(model.namespace.phases[phase])

            if model.trace_results[phase].isrun:
                keys = ['FC%'] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_] + model.namespace.accessory_minerals_formal
                w = list(100 * np.asarray(model.trace_results[phase].weights).round(3))
                f = int(100 * model.trace_results[phase].F)
                vals = [f] + w
                bulk.append(model.trace_results[phase].bulk_mineralogy)

            else:
                keys = ['FC%'] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_]
                w = list(100 * np.asarray(model.results[phase].weights).round(3))
                f = int(100 * model.results[phase].F)
                vals = [f] + w
                bulk_cols = model.namespace.oxides
                bulk.append(model.results[phase].bulk_mineralogy)

        else:
            continue

        # Append phase transition title and data to the list
        data.append([f"{model.namespace.phase_transitions[phase]}"])
        data.append(keys)
        data.append(vals)
        data.append([''])

    # Add a table for the total fractionised mineral assemblage across all phases
    data.append([f"Total melt fraction crystallised = {100 * model.crystallisation_dict['delta_S'].sum():.2f} wt.%"])
    if any([model.trace_results[phase].isrun for phase in range(5)]):
        keys = ['FC%'] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_] + model.namespace.accessory_minerals_formal
    else:
        keys = ['FC%'] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_]
    data.append(keys)
    data.append(model.crystallisation_dict['total_minerals_wt'].round(2).tolist())
    data.append([''])

    # Add table for bulk compositions of used phases
    if any([model.trace_results[phase].isrun for phase in range(5)]):
        bulk_cols = model.namespace.structurals
    else:
        bulk_cols = model.namespace.oxides

    data.append(['Bulk Mineralogy of Used Phases wt.%'])
    data.append([''] + list(bulk_cols)) 

    for i, b in enumerate(bulk):
        if b.shape[0] < len(bulk_cols):
            b = np.hstack([b, np.full((len(bulk_cols) - b.shape[0],), np.nan)])
        else:
            b = b[:len(bulk_cols)]
        data.append([phases[i]] + list(b.round(2)))

    return data

def _write_excel(filename : str, sheets_to_save : list[tuple[str, list[list]]]) -> None:
    """
    Simple Excel writer. Converts a list of sheets (each with a title and 2D data) into an Excel file.

    Parameters
    ----------
    filename : str
        The desired output filename for the Excel file.
    sheets_to_save : list of tuples
        Each tuple contains a sheet title and a 2D list of data for that sheet.
    """
    wb = openpyxl.Workbook()

    if sheets_to_save:
        wb.remove(wb.active)  # Remove default blank sheet

    # Create each sheet and populate it with data
    for sheet_title, data in sheets_to_save:
        ws = wb.create_sheet(title=sheet_title)

        for row_idx, row in enumerate(data, start=1):
            if not isinstance(row, (list, tuple, np.ndarray)):
                row = [row]

            for col_idx, value in enumerate(row, start=1):
                if isinstance(value, str):
                    try:
                        value = float(value) if '.' in value else int(value)
                    except (ValueError, TypeError):
                        pass

                ws.cell(row=row_idx, column=col_idx, value=value)

    try:
        wb.save(filename)
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        print(f"Attempted to save to: {filename}")
        raise
    log(f"Excel file saved successfully: {filename}")

# %% ---- PDF Utilities ----

def numpy_to_typst_table(array : np.ndarray, col_names : list[str] | None = None, row_names : list[str] | None = None, caption : str | None = None, float_fmt : str = "{:.4g}", corner_label : str = "", max_cols : int | None = None) -> str:
    """
    Convert a 2D numpy array to styled Typst tables using `datatable`.

    Parameters
    ----------
    array : np.ndarray (2D)
        Data to convert into a Typst table.
    col_names : list[str] | None
        Column headers for the table.
    row_names : list[str] | None
        Row headers for the table.
    caption : str | None
        Caption text for the table. If None, no caption is added.
    float_fmt : str
        Format string for floating-point numbers, e.g., "{:.2f}".
    corner_label : str
        Label for the top-left corner cell when both row and column names are provided.
    max_cols : int | None
        Maximum number of columns to display in a single table. If the data exceeds this limit,
        it will be split into multiple tables with the same caption.

    Returns
    ------- 
    str
        A string containing the Typst code for the table(s).
    
    Notes
    -----
    - Special characters in headers and data are escaped to prevent Typst syntax issues.
    """
    array = np.atleast_2d(np.asarray(array))
    n_rows, n_cols = array.shape

    # Replace 'nan' with ''
    try:
        array = np.where(np.isnan(array), "", array)
    except Exception:
        array = np.where(array == "nan", "", array)

    def fmt(x):
        """Format a value for Typst table output, handling integers, floats, and strings."""
        if isinstance(x, (int, np.integer)):
            return str(int(x))
        if isinstance(x, (float, np.floating)):
            return float_fmt.format(float(x))
        return str(x)

    def esc(s):
        """Escape special characters in strings for Typst syntax."""
        s = str(s)
        for ch in ["\\", "#", "$", "*", "_", "`", "@", "<", ">"]:
            s = s.replace(ch, "\\" + ch)
        return s

    has_rownames = row_names is not None

    # Determine column slicing chunks
    if max_cols is None or max_cols >= n_cols:
        col_chunks = [range(n_cols)]
    else:
        col_chunks = [
            range(i, min(i + max_cols, n_cols))
            for i in range(0, n_cols, max_cols)
        ]

    total_parts = len(col_chunks)
    sub_tables = []

    # Build each sub-table for the chunks of columns
    for part_idx, col_indices in enumerate(col_chunks, start=1):
        num_chunk_cols = len(col_indices) + (1 if has_rownames else 0)

        # Build header cells
        header_cells = []
        if col_names is not None:
            if has_rownames:
                header_cells.append(f"[*{esc(corner_label)}*]")
            for j in col_indices:
                header_cells.append(f"[*{esc(col_names[j])}*]")

        # Build body cells
        body_rows = []
        for i in range(n_rows):
            row_cells = []
            if has_rownames:
                row_cells.append(f"[*{esc(row_names[i])}*]")
            for j in col_indices:
                row_cells.append(f"[{esc(fmt(array[i, j]))}]")
            body_rows.append("    " + ", ".join(row_cells) + ",\n")

        # Assemble sub-table
        header_str = ""
        if header_cells:
            header_str = (
                "    table.header(\n      "
                + ", ".join(header_cells)
                + ",\n    ),\n"
            )

        body_str = "".join(body_rows)

        # Pass caption: none to inner datatables when split (caption is on outer figure)
        inner_caption = (
            f"[{esc(caption)}]" if (total_parts == 1 and caption) else "none"
        )

        table_code = (
            f"  #datatable(\n"
            f"    columns: {num_chunk_cols},\n"
            f"    caption: {inner_caption},\n"
            f"{header_str}"
            f"{body_str}"
            f"  )"
        )

        # Apply positional alignment when split across multiple sub-tables
        if total_parts > 1:
            if part_idx == 1:
                table_code = f"#align(left)[\n{table_code}\n]"
            elif part_idx == total_parts:
                table_code = f"#align(right)[\n{table_code}\n]"
            else:
                table_code = f"#align(center)[\n{table_code}\n]"

        sub_tables.append(table_code)

    # Handle Single vs Multi-part Output 
    if total_parts == 1:
        return sub_tables[0] + "\n"

    # For multiple parts: wrap all sub-tables in a single figure block with one caption
    stacked_tables_str = "\n  #v(0.8em)\n".join(sub_tables)
    cap_arg = f", caption: [{esc(caption)}]" if caption else ""

    grouped_figure = (
        f"#figure(\n"
        f"  kind: table,\n"
        f"  supplement: [Table]{cap_arg},\n"
        f"  [\n"
        f"{stacked_tables_str}\n"
        f"  ]\n"
        f")\n"
    )

    return grouped_figure

def figures_to_typst(figure_specs : list[dict], fig_labels : list[bool] = None) -> str:
    """
    Convert a list of figure specifications into Typst code for figures.

    Parameters  
    ----------
    figure_specs : list of dict
        Each dict should contain:
        - 'path': str, path to the figure file
        - 'caption': str, caption for the figure (optional)
        - 'width': str, width of the figure (optional, default "85%")
    captions : list of Bool
        List of booleans indicating whether to include figure labelling for each figure.

    Returns
    -------
    str
        A string containing the Typst code for all specified figures.
    """

    if fig_labels is None:
        fig_labels = [True] * len(figure_specs)

    blocks = []
    # Iterate through each figure specification and generate Typst code
    for fi, f in enumerate(figure_specs):
        # print(f"Processing figure: {f}")
        width = f.get("width", "85%")
        caption = f.get("caption", "")
        cap = f'[{caption}]' if caption else "none"
        if fig_labels[fi]:
            blocks.append(
                f'#figure(\n'
                f'  image("{f["path"]}", width: {width}),\n'
                f'  caption: {cap},\n'
                f')\n#v(10pt)\n'
            )
        else:
            blocks.append(
                f'#figure('
                f'image("{f["path"]}", width: {width}),'
                f'caption: {cap},'
                f'numbering: none,'
                f')'
            )
    return "\n".join(blocks)

def stages_run_pills(model : "hades.model.Obol") -> str:
    """
    Return a string of Typst pills for the stages that have been run in the model.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing results and metadata.

    Returns
    -------
    str
        A Typst-formatted string representing pills for each stage that has been run.
    """
    phase_colours = ['#ffff00', '#ffd700', '#ffa500', '#ff8c00', '#ff4500', '#8b008b']
    # Get the stages that have been run and create pills for them
    stages_run = [x for x in range(5) if model.results[x].isrun]
    pills = []
    # Make pills
    for stage in stages_run:
        phasename = model.namespace.phases[stage]
        pills.append(f'#pill("{phasename}", bg: rgb("{phase_colours[stage]}"), fg: brand-dark-red)')
    return f"[{" ".join(pills)}]"

def typstPath(path : str) -> str:
    """
    Convert a file path to a Typst-compatible relative path.

    Parameters
    ----------
    path : str
        The original file path.

    Returns
    -------
    str
        A Typst-compatible relative path, using forward slashes and relative to the drive root.
    """
    abs_img_path = Path(path).resolve()
    # Get the drive root ("C:\") and calculate the path relative to drive root
    drive_root = abs_img_path.anchor  # Returns 'C:\\' on Windows
    rel_to_drive = abs_img_path.relative_to(drive_root).as_posix()

    return rel_to_drive

def phaseResults(model : "hades.model.Obol", phase : int, temp_dir_path : Path) -> str:
    """
    Compile the results for a specific phase into Typst code, including tables and figures.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing results and metadata.
    phase : int
        The phase index (0-4) for which to compile results.
    temp_dir_path : Path
        The directory path where temporary figure files will be saved.

    Returns
    -------
    str 
        A string containing the Typst code for the phase results, including tables and figures.
    """
    run = model.results[phase].isrun
    traces_run = model.trace_results[phase].isrun

    if not run:
        return ""

    # Compile results depending on run mode
    if traces_run:
        magma_table = numpy_to_typst_table(
            np.vstack([
                model.magma.traces[phase,:],
                model.magma.initial[phase+1,:],
                model.magma.traces[phase+1,:],
                100 * np.abs(model.magma.traces[phase+1,:] - model.magma.initial[phase+1,:]) / (model.magma.initial[phase+1,:] + 1e-10)  # Avoid division by zero
            ]).round(2).T,
            col_names=['Initial', 'Expected', 'Computed', '% Error'],
            row_names=model.namespace.geochem,
            corner_label="",
            caption="Magma compositions for this phase (wt.% for oxides, ppm for trace elements).",
        )

        optimised_params = numpy_to_typst_table(
            np.concatenate( [np.array([int(100 * model.trace_results[phase].F)]), (100 * model.trace_results[phase].weights).round(2),])[:, None],
            col_names=["Value"],
            row_names=["FC%"] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_] + model.namespace.accessory_minerals_formal,
            corner_label="",
            caption="Optimised parameters for this phase. Fractional crystallisation (FC) is expressed as a percentage, and mineral weights are wt.%.",
        )

        # If a mineral wasn't used, set to nan
        ctctcs = model.trace_results[phase].cotectics
        usage = model.trace_results[phase].usage
        ctctcs[~usage, :] = np.nan
        cotectics = numpy_to_typst_table(
            ctctcs.round(2),
            col_names=model.trace_results[phase].structurals,
            row_names=[model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_] + model.namespace.accessory_minerals_formal,
            corner_label="",
            caption="Cotectic compositions of the model phases (wt.% for oxides, ppm for trace elements). Blank rows indicate minerals that were not used in the optimisation for this phase.",
        )
        bulk = numpy_to_typst_table(
            model.trace_results[phase].bulk_mineralogy.round(2),
            col_names=model.trace_results[phase].structurals,
            row_names=['wt.%'],
            corner_label="",
            caption="Bulk mineralogy of the model phases (wt.%).",
        )
        
    else:
        magma_table = numpy_to_typst_table(
            np.vstack([
                model.magma.computed[phase,:8],
                model.magma.initial[phase+1,:8],
                model.magma.computed[phase+1,:8],
                100 * np.abs(model.magma.computed[phase+1,:8] - model.magma.initial[phase+1,:8]) / model.magma.initial[phase+1,:8]
                ]).round(2).T,
                col_names=['Initial', 'Expected', 'Computed', '% Error'],
                row_names=model.namespace.oxides,
                corner_label="",
                caption="Magma compositions for this phase (wt.% for oxides, ppm for trace elements).",
            )

        optimised_params = numpy_to_typst_table(
            np.concatenate( [np.array([int(100 * model.results[phase].F)]), (100 * model.results[phase].weights).round(2),])[:, None],
            col_names=["Value"],
            row_names=["FC%"] + [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_],
            corner_label="",
            caption="Optimised parameters for this phase. Fractional crystallisation (FC) is expressed as a percentage, and mineral weights are wt.%.",
        )

        # If a mineral wasn't used, set to nan
        ctctcs = model.results[phase].cotectics
        usage = model.results[phase].usage
        ctctcs[~usage, :] = np.nan
        cotectics = numpy_to_typst_table(
            ctctcs.round(2),
            col_names=model.namespace.oxides,
            row_names=model.meta.minerals_,
            corner_label="",
            caption="Cotectic compositions of the model phases (wt.%). Blank rows indicate minerals that were not used in the optimisation for this phase.",
        )
        bulk = numpy_to_typst_table(
            model.results[phase].bulk_mineralogy.round(2),
            col_names=model.namespace.oxides,
            row_names=['wt.%'],
            corner_label="",
            caption="Bulk mineralogy of the model phases (wt.%).",
        )

    phase_colours = ['#ffff00', '#ffd700', '#ffa500', '#ff8c00', '#ff4500', '#8b008b']
    pill = f'#pill("{model.namespace.phases[phase]}", bg: rgb("{phase_colours[phase]}"), fg: brand-dark-red)'

    # Bivariate plots with mineralogy - split into two to fit onto pages better
    from hades.visuals import bivar
    import matplotlib.pyplot as plt
    fig, ax = bivar(model, y_order=('TiO2', 'Fe2O3', 'Al2O3'), return_fig_ax=True, phase_highlight=phase, mode='computed' if not traces_run else 'traces', cropped=True)
    plt.savefig(temp_dir_path / "bivar.svg", transparent=True, bbox_inches='tight')
    plt.close(fig)
    figure = {"path": "bivar.svg", "caption": f"Bivariate plots continued overleaf.", "width": "80%"}

    fig, ax = bivar(model, y_order=('CaO', 'Na2O', 'K2O'), return_fig_ax=True, phase_highlight=phase, mode='computed' if not traces_run else 'traces', cropped=True)
    plt.savefig(temp_dir_path / "bivar2.svg", transparent=True, bbox_inches='tight')
    plt.close(fig)
    figure2 = {"path": "bivar2.svg", "caption": f"Bivariate plots of the data suite with the data-based and modelled LLODs. The {model.namespace.phases[phase]} to {model.namespace.phases[phase+1]} transition is highlighted in red and mineral compositions are also displayed for this phase transition. See the legend at the end of the PDF report for the legend.", "width": "80%"}

    typst_code = (
        f"== {model.namespace.phase_transitions[phase]}\n"
        f'#callout(title: [{pill}])['
        f"""#kv-grid(
                ("Population size", [{model.optimising.pop_size}]),
                ("Iterations", [{model.results[phase].opt_result['nit']}/{model.optimising.max_iter}]),
                ("Cost function", [{model.results[phase].cost:.2f}]),
                ("Trace analysis?", [{model.trace_results[phase].isrun}]),
            )
        ]\n\n"""
        f"*Magma Inspection*\n"
        f"{magma_table}\n\n"
        f"*Optimised Parameters*\n"
        f"{optimised_params}\n\n"
        f"*Bulk Crystallising Assemblage Composition*\n"
        f"{bulk}\n\n"
        f"*Cotectic Compositions*\n"
        f"{cotectics}\n\n"
        f"*Bivariate Plot*\n"
        f"{figures_to_typst([figure, figure2], [False, True])}\n"
    )

    return typst_code

def makeTables(model : "hades.model.Obol") -> dict[str, str]:
    """
    Generate Typst tables for the initial and computed magma compositions, as well as partition coefficients.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing results and metadata.

    Returns
    -------
    dict[str, str]
        A dictionary containing Typst code for the initial magma table, computed magma table, and partition coefficients.
    """
    tracesRun = len([x for x in range(5) if model.trace_results[x].isrun]) > 0

    # Generate tables for initial and computed magma compositions depending on whether trace results are available
    if tracesRun:
        initial_magma = numpy_to_typst_table(
                np.hstack([
                    np.asarray([x if x else '' for x in model.magma.magma_samples]).reshape(-1, 1),
                    model.magma.initial.round(2),
                ]).T,
                col_names=model.namespace.phases,
                row_names=["Sample"] + model.namespace.geochem,
                corner_label="",
                caption="Major oxide compositions of the model phases (wt.% for oxides, ppm for trace elements)."
            )

        computed_magma = numpy_to_typst_table(
            model.magma.traces.round(2).T,
            col_names=model.namespace.phases,
            row_names=model.namespace.geochem,
            corner_label="",
            caption="Major oxide compositions of the model phases (wt.%)."
        )

    else:

        initial_magma = numpy_to_typst_table(
            np.hstack([
                np.asarray([x if x else '' for x in model.magma.magma_samples]).reshape(-1, 1),
                model.magma.initial[:,:8].round(2),
            ]),
            col_names=["Sample"] + model.namespace.oxides,
            row_names=model.namespace.phases,
            corner_label="",
            caption="Major oxide compositions of the model phases (wt.%)."
        )

        computed_magma = numpy_to_typst_table(
            model.magma.computed[:,:8].round(2),
            col_names=model.namespace.oxides,
            row_names=model.namespace.phases,
            corner_label="",
            caption="Major oxide compositions of the model phases (wt.%)."
        )

    # Stack the mineral weights for all phases that have been run, along with the total mineral weights, depending on traces or not
    rows = []
    for i in range(5):
        if model.results[i].isrun:
            if model.trace_results[i].isrun:
                # Flatten trace weights and append F
                weights = np.ravel(100 * model.trace_results[i].weights).tolist()
                F_val = int(100 * model.trace_results[i].F)
                rows.append(weights + [F_val])
            else:
                # Flatten standard weights, pad accessory minerals with NaN, and append F
                weights = np.ravel(100 * model.results[i].weights).tolist()
                F_val = 100 * model.results[i].F
                if tracesRun:
                    acc_nan = [np.nan] * len(model.namespace.accessory_minerals_formal)
                    rows.append(weights + acc_nan + [F_val])
                else:
                    rows.append(weights + [F_val])

    # Add the total mineral weights as the last row
    rows.append(list(model.crystallisation_dict['total_minerals_wt']) + [np.nan])

    res = np.vstack(rows)

    # Replace exactly zero values with NaN to avoid displaying them in the table
    res[res == 0] = np.nan
    # Drop entries in res that are complete NaN rows (i.e., minerals that were not used in any phase)
    valid_rows = ~np.isnan(res).all(axis=0)
    res = res[:, valid_rows]

    mins = [model.namespace.minerals_title[model.namespace.minerals.index(mineral)] for mineral in model.meta.minerals_]
    if any([model.trace_results[i].isrun for i in range(5)]):
        mins += model.namespace.accessory_minerals_formal
    mins += ['FC%']
    mins = np.array(mins)[valid_rows].tolist()
    phases_run = [model.namespace.phases[i] for i in range(5) if model.results[i].isrun] + ["Total"]


    resultsGlance = numpy_to_typst_table(
        res.round(2).T,
        col_names=phases_run,
        row_names=mins,
        corner_label="",    
        caption="Optimised mineral weights for the model phases (wt.%). Blank rows indicate minerals that were not used in the optimisation for this phase."
    )

    KDvalues = numpy_to_typst_table(
        model.minerals.KD_vals.T,
        col_names=model.namespace.phases[:-1],
        row_names=model.minerals.KD_minerals_title,
        corner_label="",
        caption="Partition coefficients for the model phases."
    )

    return {
        "@@initial_magma@@": initial_magma,
        "@@computed_magma@@": computed_magma,
        "@@KDvalues@@": KDvalues,
        "@@resultsGlanceValue@@": f"The total melt fraction crystallised across all phases is {100 * model.crystallisation_dict['delta_S'].sum():.2f} wt.%",
        "@@resultsGlanceTable@@": resultsGlance,
    }

def makeFigures(model : "hades.model.Obol", output_dir : Path) -> list[dict]:
    """
    Generate figures for the model, including TAS diagrams and bivariate plots. Ensures valid svg paths for Typst and copies the legend asset to the output directory.

    Parameters
    ----------
    model : hades.model.Obol
        The Hades model object containing results and metadata.
    output_dir : Path
        The directory where figure files will be saved.

    Returns
    -------
    list[dict]
        A list of dictionaries, each containing the path, caption, and width for a figure.
    """
    import matplotlib.pyplot as plt
    from hades.visuals import tas, mineral_usage
    figures = []

    # TAS Diagram
    fig, ax = tas(model, return_fig_ax=True)
    plt.savefig(output_dir / "tas.svg", transparent=True)
    plt.close(fig)
    figures.append({"path": "tas.svg", "caption": "Total Alkali-Silica (TAS) diagram of the model phases.", "width": "80%"})

    # Mineral usage figure
    fig, ax = mineral_usage(model, return_fig_ax=True)
    plt.savefig(output_dir / "mineral_usage.svg", transparent=True)
    plt.close(fig)
    figures.append({"path": "mineral_usage.svg", "caption": "Mineral usage across the model phases.", "width": "80%"})

    # Load the pre-existing legend figure from assets and copy it to output_dir
    package_dir = Path(__file__).parent.resolve()
    legend_source = package_dir / ".." / "hades_plouton" / "assets" / "mineral_legend.svg"
    legend_dest = output_dir / "mineral_legend.svg"

    # Copy asset into the temporary export workspace
    shutil.copy(legend_source, legend_dest)

    # Append using the same relative filename convention as your other figures
    figures.append({
        "path": "mineral_legend.svg",
        "caption": "Legend for mineral symbols used in the figures.",
        "width": "100%"
    })

    return figures

# %% ---- PDF Writer ----

def compile_pdf(model, output_pdf_path: str, options: dict = {}):
    """
    Compiles a Typst template in an isolated temporary sandbox directory, ensuring that all assets are correctly referenced and the output PDF is generated.

    Options argument is currently unused but can be extended for future features or export configurations.

    Parameters
    ----------
    model : Obol
        The Hades model object containing results and metadata.
    output_pdf_path : str
        The desired output path for the generated PDF file.
    options : dict
        Additional options for PDF compilation.
    """
    import tempfile
    import shutil
    import hades

    package_dir = Path(__file__).parent.resolve()
    assets_dir = package_dir / "assets" / "pdf_assets"
    template_path = assets_dir / "template.typ"
        
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found at {template_path}"
        )

    tables = makeTables(model)

    # Open an isolated temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy the entire assets folder into the temp sandbox
        temp_assets = temp_dir_path / "pdf_assets"
        shutil.copytree(assets_dir, temp_assets)

        # Load the template from the copied assets
        temp_template_file = temp_assets / "template.typ"
        with open(temp_template_file, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Create figures to this directory as svgs
        figures_block = makeFigures(model, temp_dir_path)

        # Perform substitutions
        data_placeholders = {
                "@@software_name@@":  "Hades",
                "@@version@@":        hades.__version__,
                "@@report_title@@":   "Hades Model Report",
                "@@authors@@":        "J. L. Smith, A. R. Hastie, et al.",
                "@@date_ymd@@":       datetime.now().strftime("%d %b %Y"),
                "@@date_ymdhms@@":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "@@logo_path@@":      "pdf_assets/logo.png",
                "@@overview_text@@":  "This report summarises the calibration of the model against the reference dataset, including parameter estimates and convergence diagnostics.",
                "@@mode@@":           model.meta.mode.title(),
                "@@submode@@":        model.meta.submode.title() if model.meta.submode else "-",
                "@@data_suite@@":     os.path.basename(os.path.dirname(model.datasuite.filepath))+"/"+os.path.basename(model.datasuite.filepath),
                "@@FeOFe2p@@":        model.meta.FeO_Fe2pO_Ratio,
                "@@stages_run@@":     stages_run_pills(model),
                "@@config_file@@":    "config/run.yaml",
                "@@phase_results@@":  phaseResults(model, 0, temp_dir_path) + phaseResults(model, 1, temp_dir_path) + phaseResults(model, 2, temp_dir_path) + phaseResults(model, 3, temp_dir_path) + phaseResults(model, 4, temp_dir_path),
                "@@figures_block@@":  figures_to_typst(figures_block),
            }

        # Add tables and figures
        data_placeholders.update(tables)

        for key, value in data_placeholders.items():
            template_content = template_content.replace(key, str(value))

        # Write the filled template into the temp sandbox root
        working_typ_file = temp_dir_path / "document.typ"
        with open(working_typ_file, "w", encoding="utf-8") as f:
            f.write(template_content)

        # Compile using the temp directory as the Typst root
        # Setting root=temp_dir_path ensures Typst resolves all relative paths correctly
        try:
            typst.compile(
                working_typ_file,
                output=output_pdf_path,
                root=temp_dir_path,
            )
        except Exception as e:
            print(f"Error during Typst compilation: {e}")
            raise

        log(f"PDF compilation completed. Output saved to {output_pdf_path}")

    # TemporaryDirectory auto-cleans everything on exit (no orphan files left)