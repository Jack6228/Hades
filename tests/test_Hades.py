"""Unit tests for hades-obol.
"""

import pytest
import numpy as np
import csv
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg") # Force Matplotlib to use the non-interactive Agg backend for testing

def test_package_version():
    """
    Verify that the package has a version attribute and that it is a string.
    """
    import hades
    assert hasattr(hades, "__version__")
    assert isinstance(hades.__version__, str)

@pytest.mark.parametrize("plot", [True, False])
@pytest.mark.parametrize(
    "mode, export",
    [
        ("run", "no"),          # Mode 'run' with export disabled
        ("run", "pdf"),
        ("run", "excel"),
        ("run_w_traces", "no"), # Mode 'run_w_traces' with export options
        ("run_w_traces", "pdf"),
        ("run_w_traces", "excel"),
    ]
)
def test_Thingmuli(tmp_path, mode, plot, export):
    """
    Test that the core functionality of the package works as expected.
    """
    # Replace core_function with your actual function call
    from hades import Obol
    from hades.logger import pause_logging
    pause_logging()  

    model = Obol.newModel()
    model.set_mineral_usage(
        __spinel=False,
        __cpx=True,
        __opx=False,
        intermediate__opx=True,
        __plag=True,
        __mag=True,
        __ilm=True,
        __quartz=False,
        evolved__quartz=True,
    )
    if plot:
        from hades.visuals import mineral_usage, bivar, tas, harker
        mineral_usage(model, return_fig_ax=True)
        plt.close()

    model.set_KDs(
        __plagioclase=0.95, 
        __cpx=0.25,
    )

    model.set_mineralogies(
        basic__plag =        [51.10, 0.07, 30.07, 0.78,  0.17, 14.39, 3.33, 0.08 ],
        intermediate__plag = [57.83, 0.04, 26.13, 0.51,  0.03,  9.06, 6.08, 0.31 ],
        evolved__plag =      [59.90, 0.02, 24.85, 0.38,  0.01,  7.15, 7.14, 0.54 ],
        basic__cpx =         [50.78, 1.08, 1.97, 12.28, 14.07, 19.51, 0.31, 0.00 ],
        intermediate__cpx =  [48.86, 0.76, 1.65, 22.42,  9.21, 16.86, 0.24, 0.00 ],
        evolved__cpx =       [47.21, 0.44, 0.95, 29.34,  3.11, 18.70, 0.25, 0.00 ],
    )

    model.load_data_suite('examples/iceland/thingmuli_hekla.xlsx')

    model.select_initial_composition([None, 'T3-01', 'T7-03', 'auto', 'auto', 'T3-12'])

    # Reduce computational load
    model.optimising.max_iter = 50
    model.optimising.pop_size = 10

    model.run(2)
    model.run(3)
    model.run(4)
    model.run(5)

    if mode in ["run_w_traces", "run_w_traces_plot"]:
        Wacc = [1, 0.0, 0.0, 0.0]
        model.runTraces(2, Wacc)
        model.runTraces(3, Wacc)
        model.runTraces(4, Wacc)
        model.runTraces(5, Wacc)

    if plot:
        tas(model, return_fig_ax=True)
        harker(model, y_order=['La', 'Ce', 'Zr', 'Sr', 'Rb', 'Nb', 'Th', 'U'], nrows=2, return_fig_ax=True)
        if mode == "run":
            bivar(model, x_order=['SiO2'], y_order=['TiO2'], return_fig_ax=True)
        elif mode == "run_w_traces":
            bivar(model, x_order=['SiO2'], y_order=['TiO2'], mode='traces', return_fig_ax=True)

    model.summary()

    # Construct an isolated file path inside the temporary test folder
    if export == "pdf":
        export_file = tmp_path / "report.pdf"
        model.savePDF(export_file.as_posix())
    elif export == "excel":
        export_file = tmp_path / "data.xlsx"
        model.saveData(export_file.as_posix())

    # Verify the exported file was actually created when expected
    if export in ["pdf", "excel"]:
        assert export_file.exists()
        assert export_file.stat().st_size > 0

@pytest.mark.parametrize("shuffle_mode", ["rows", "columns", "both"])
def test_file_load_orientation_resilience(tmp_path, shuffle_mode):
    """
    Tests that an input file can be loaded correctly regardless of the order of rows and/or columns in the input data.
    """
    from hades import Obol
    from hades.logger import pause_logging
    pause_logging()  

    model_orig = Obol.newModel()
    model_orig.load_data_suite("examples/iceland/thingmuli_hekla.xlsx")

    # Create a randomized copy of the original worksheet without pandas.
    workbook = load_workbook("examples/iceland/thingmuli_hekla.xlsx", data_only=True)
    worksheet = workbook.active
    worksheet_rows = [list(row) for row in worksheet.iter_rows(values_only=True)]
    header = worksheet_rows[0]
    data_rows = worksheet_rows[1:]

    # Apply row and/or column shuffling using fixed seeds per parameter
    rng = np.random.default_rng(seed=123)

    if shuffle_mode in ("rows", "both"):
        data_rows = [data_rows[i] for i in rng.permutation(len(data_rows))]

    if shuffle_mode in ("columns", "both"):
        # Keep the index column first; shuffle the actual data columns.
        column_order = rng.permutation(len(header) - 1) + 1
        data_rows = [
            [row[0]] + [row[i] for i in column_order]
            for row in data_rows
        ]
        header = [header[0]] + [header[i] for i in column_order]

    # Save the shuffled DataFrame to a temporary CSV file
    csv_path = tmp_path / f"test_data_{shuffle_mode}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(data_rows)

    # Load data using your package function
    # (Assuming load_data returns a pandas DataFrame or similar parsed structure)
    model = Obol.newModel()  # Replace with actual model initialisation if needed
    model.load_data_suite(csv_path.as_posix())  # Ensure path is string for compatibility

    # Extract initial magma compositions
    original = model_orig.magma.initial
    parsed = model.magma.initial

    # Assert that all float values match exactly despite the original input shuffle
    assert np.allclose(parsed, original, rtol=1e-8, atol=1e-10), f"Parsed data does not match original after {shuffle_mode} shuffling."