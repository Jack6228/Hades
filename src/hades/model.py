"""Primary module for the Hades backend.

Contains data structures and the main Obol class which encapsulates the model's functionality. The Obol class is the main interface for running geochemical simulations, managing data, and retrieving results. It interacts with various supporting classes and functions to perform calculations related to mineralogy, phase transitions, and trace element analysis. The GUI application interacts with this module.
"""

# Dependencies
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import os, sys
from importlib.machinery import EXTENSION_SUFFIXES
from os.path import abspath, dirname, join, normpath
from dataclasses import dataclass, field, fields, asdict, is_dataclass

from .logger import warn, log, log_meta, log_warning
from . import phases as _phases
from .utils import sanity_check, nice_display, get_nested_attr, set_nested_attr, convert_to_serialisable, sort_geochem, from_dict, get_asset_path

_phases_path = str(getattr(_phases, "__file__", "")).lower()
PHASES_ACCELERATED = any(
    _phases_path.endswith(suffix.lower()) for suffix in EXTENSION_SUFFIXES
)
if not PHASES_ACCELERATED:
    log_warning(
        "NOTE: Hades is not optimised for this version of Python of your OS. You may notice slower performance.",
        no_time=True,
    )

lookup_mineral_bank_cotectic = _phases.lookup_mineral_bank_cotectic
compute_phase_cost_batch = _phases.compute_phase_cost_batch
compute_phase_evolution_batch = _phases.compute_phase_evolution_batch
compute_cost = _phases.compute_cost

MINERALS: Tuple[str, ...] = ['olivine', 'spinel', 'clinopyroxene', 'orthopyroxene', 'plagioclase', 'amphibole', 'kfeldspar', 'biotite', 'quartz', 'magnetite', 'ilmenite', 'titanaugite', 'nepheline', 'leucite', 'nosean_hauyne', 'alkali_amphibole']
# IMA–CNMNC Mineral Symbols
MINERALS_SHORT: Tuple[str, ...] = ['ol', 'spl', 'cpx', 'opx', 'pl', 'amp', 'kfs', 'bt', 'qz', 'mag', 'ilm', 'taug', 'nph', 'lct', 'nsn/hyn', 'A-amp']
MINERALS_TITLE: Tuple[str, ...] = ['Olivine', 'Spinel', 'Clinopyroxene', 'Orthopyroxene', 'Plagioclase', 'Amphibole', 'K-feldspar', 'Biotite', 'Quartz', 'Magnetite', 'Ilmenite', 'Titanaugite', 'Nepheline', 'Leucite', 'Nosean/Hauyne', 'Alkali-amphibole']
KD_MINERALS: Tuple[str, ...] = ['plagioclase', 'clinopyroxene', 'orthopyroxene', 'amphibole', 'kfeldspar', 'biotite', 'titanaugite', 'nepheline', 'leucite', 'nosean_hauyne', 'alkali_amphibole']

ACCESSORY_MINERALS: Tuple[str, ...] = ['Apatite', 'Zircon', 'Monazite', 'Allanite']
ACCESSORY_MINERALS_SHORT: Tuple[str, ...] = ['Ap', 'Zr', 'Mnz', 'All']
ACCESSORY_MINERALS_FORMAL: Tuple[str, ...] = ['Apatite', 'Zircon', 'Monazite', 'Allanite']

OXIDES: Tuple[str, ...] = ['SiO2', 'TiO2', 'Al2O3', 'Fe2O3', 'MgO', 'CaO', 'Na2O', 'K2O']
TRACES: Tuple[str, ...] = ['P', 'Ba', 'Rb', 'Sr', 'Nb', 'Zr', 'Y', 'La', 'Ce', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'Th', 'U']
STRUCTURALS: Tuple[str, ...] = OXIDES + ['P', 'Zr', 'La', 'Ce', 'Nd', 'Y', 'Th']
GEOCHEM: Tuple[str, ...] = OXIDES + TRACES
GEOCHEM_UNITS: Tuple[str, ...] = ['wt%'] * len(OXIDES) + ['ppm'] * len(TRACES)

PHASES: Tuple[str, ...] = ['Primary', 'Primitive', 'Basic', 'Intermediate', 'Evolved', 'End']
PHASES_SHORT: Tuple[str, ...] = ['Prmy', 'Prmt', 'Bsc', 'Intr', 'Evld', 'End']
PHASE_TRANSITIONS: Tuple[str, ...] = ['Primary > Primitive', 'Primitive > Basic', 'Basic > Intermediate', 'Intermediate > Evolved', 'Evolved > End']
PHASE_TRANSITIONS_ABBREV: Tuple[str, ...] = ['p-P', 'P-B', 'B-I', 'I-E', 'E-e']

@dataclass()
class Metadata:
    """Holds the primary metadata for the model."""
    # Primary customisable metadata for the model
    mode: str = 'subalkaline'
    submode: str = 'tholeiitic'
    FeO_Fe2pO_Ratio: float = 0.9
    SiO2_phase_bounds: np.ndarray = field(default_factory=lambda: np.zeros(4, dtype=np.float64))

    # List to only contain alkaline or subalkaline minerals
    minerals_: List[str] = field(default_factory=lambda: [])

@dataclass(frozen=True)
class Constants:
    """Holds fixed constants used in the model."""
    # Constants
    Fe2O3_FeO_Ratio: float = 0.9
    molecular_weights: np.ndarray = field(default_factory=lambda: np.array([60.08500, 79.89900, 50.98100, 71.84600, 40.31100, 56.07900, 30.98950, 47.10150], dtype=np.float64))

@dataclass
class PhaseResult:
    """Holds the outputs for a specific phase of the model."""
    cost: float = 0.0
    F: float = 0.0
    name: str = ""
    isrun: bool = False
    minerals: list = field(default_factory=lambda: [])
    usage: list = field(default_factory=lambda: [])
    opt_result: Any = None

    solution: dict = field(default_factory=lambda: {})
    weights: np.ndarray = field(default_factory=lambda: np.array([]))
    cotectics: np.ndarray = field(default_factory=lambda: np.array([]))
    bulk_mineralogy: np.ndarray = field(default_factory=lambda: np.zeros([]))
    melt_evolution: np.ndarray = field(default_factory=lambda: np.array([]))
    olivine_composition: np.ndarray = field(default_factory=lambda: np.array([]))

    # For the trace elements, store which traces are structural components of the melt
    structurals: list = field(default_factory=lambda: [])
    traces: np.ndarray = field(default_factory=lambda: np.array([]))  # New attribute for trace elements

    def reset(self):
        """Reset the phase result to its initial state."""
        self.cost = 0.0
        self.F = 0.0
        self.name = ""
        self.isrun = False
        self.minerals = []
        self.usage = []
        self.opt_result = None

        self.solution = {}
        self.weights = np.array([])
        self.cotectics = np.array([])
        self.bulk_mineralogy = np.zeros([])
        self.melt_evolution = np.array([])
        self.olivine_composition = np.array([])

        self.structurals = []
        self.traces = np.array([])

@dataclass
class Results:
    """The master container for all results generated by a single model."""
    Primary2Primitive: PhaseResult = field(default_factory=PhaseResult)
    Primitive2Basic: PhaseResult = field(default_factory=PhaseResult)
    Basic2Intermediate: PhaseResult = field(default_factory=PhaseResult)
    Intermediate2Evolved: PhaseResult = field(default_factory=PhaseResult)
    Evolved2End: PhaseResult = field(default_factory=PhaseResult)

    def __getitem__(self, index: int):
        # Get all fields defined on this dataclass
        cls_fields = fields(self)
        # Extract the field name at the requested index (raises error if out of bounds)
        field_name = cls_fields[index].name
        # Fetch the actual object stored in that attribute
        return getattr(self, field_name)

@dataclass
class MagmaState:
    """Holds the shifting compositions of magma during a model."""
    initial: np.ndarray = field(default_factory=lambda: np.full((6, 32), np.nan))
    computed: np.ndarray = field(default_factory=lambda: np.full((6, 32), np.nan))
    traces: np.ndarray = field(default_factory=lambda: np.full((6, 32), np.nan))
    autocomp: np.ndarray = field(default_factory=lambda: np.full((6, 32), np.nan))
    # Sample names
    samples: List[str] = field(default_factory=lambda: [])
    autocomp_samples: List[str] = field(default_factory=lambda: [])
    magma_samples: List[str] = field(default_factory=lambda: [])

@dataclass
class DataSuite:
    """Holds the data suite loaded from a file."""
    filepath: str = 'Click Browse... to load a data suite'
    data: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))
    sample_names: List[str] = field(default_factory=list)
    geochem: List[str] = field(default_factory=list)

@dataclass
class Assimilant:
    """Holds information about the assimilant used in the model."""
    composition: np.ndarray = field(default_factory=lambda: np.zeros(32, dtype=np.float64))
    percentages: np.ndarray = field(default_factory=lambda: np.zeros(5, dtype=np.float64))

@dataclass(frozen=True)
class Namespaces:
    """Groups oxide metadata and array data together."""
    # Mineralogy
    minerals_title: List[str] = field(default_factory=lambda: list(MINERALS_TITLE))
    minerals: List[str] = field(default_factory=lambda: list(MINERALS))
    minerals_short: List[str] = field(default_factory=lambda: list(MINERALS_SHORT))

    # Accessory Minerals
    accessory_minerals: List[str] = field(default_factory=lambda: list(ACCESSORY_MINERALS))
    accessory_minerals_short: List[str] = field(default_factory=lambda: list(ACCESSORY_MINERALS_SHORT))
    accessory_minerals_formal: List[str] = field(default_factory=lambda: list(ACCESSORY_MINERALS_FORMAL))

    # Geochemistry
    oxides: List[str] = field(default_factory=lambda: list(OXIDES))
    traces: List[str] = field(default_factory=lambda: list(TRACES))
    structurals: List[str] = field(default_factory=lambda: list(STRUCTURALS))
    geochem: List[str] = field(default_factory=lambda: list(GEOCHEM))
    geochem_units: List[str] = field(default_factory=lambda: list(GEOCHEM_UNITS))

    # Phases
    phases: List[str] = field(default_factory=lambda: list(PHASES))
    phases_short: List[str] = field(default_factory=lambda: list(PHASES_SHORT))
    phase_transitions: List[str] = field(default_factory=lambda: list(PHASE_TRANSITIONS))
    phase_transitions_abbrev: List[str] = field(default_factory=lambda: list(PHASE_TRANSITIONS_ABBREV))

@dataclass
class Optimising:
    """Metadata for the optimisation process."""
    # Default values for optimisation
    bounds: List[List[float]] = field(default_factory=lambda: [])
    bounds_default : List[List[float]] = field(default_factory=lambda: [])
    max_iter: int = 500
    pop_size: int = 50
    tol: float = 1e-5
    strategy: str = 'currenttobest1exp'
    init: str = 'random'
    mutation: tuple = (0.8, 1.5)
    recombination: float = 0.5

    def reset_bounds(self):
        """Resets the optimisation bounds to their default values."""
        self.bounds = [list(b) for b in self.bounds_default]

@dataclass
class MineralBank:
    """
    Holds the minerall related data for a specific mineral bank.
    
    Mineral banks only contain major oxide data
    """
    name: str
    filepath: str
    data: np.ndarray = field(default_factory=lambda: np.array([]))
    names: List[str] = field(default_factory=list)

    def load_data(self, base_path: str):
        """Resolves the absolute path and loads data into this bank."""
        # Resolve path safely
        if not os.path.isabs(self.filepath):
            self.filepath = join(base_path, self.filepath.lstrip('./\\'))
        self.filepath = normpath(self.filepath)
        
        try:
            from .loading import parse_file
            parsed_data, headers, sample_names = parse_file(self.filepath)
            # Ensure correct geochem ordering
            ordered_data, _ = sort_geochem(
                parsed_data.T, headers, OXIDES
            )
            
            self.data = ordered_data.T
            self.names = sample_names
        except Exception as e:
            # TODO: Error handling?
            warn(f"Failed to load mineral bank for {self.name} from {self.filepath}: {e}")

@dataclass
class Minerals:
    """
    Holds all mineral bank data and related metadata for the model.
    
    Parameters
    ----------
    filepaths : Optional[Dict[str, str]]
        A dictionary mapping mineral names to custom file paths for their mineral banks. If provided and filepaths are valid, these paths will override the default paths. Note that the format of mineral banks must match that of the default mineral banks provided by Hades. This optional argument is not a core or well tested feature of hades-obol, and should only be used by advanced users.
    """

    filepaths: Optional[Dict[str, str]] = None
    banks: Dict[str, MineralBank] = field(default_factory=dict)

    KD_minerals: List[str] = field(default_factory=lambda: list(KD_MINERALS))
    KD_minerals_short: List[str] = field(default_factory=lambda: [MINERALS_SHORT[MINERALS.index(mineral)] for mineral in KD_MINERALS])
    KD_minerals_title: List[str] = field(default_factory=lambda: [MINERALS_TITLE[MINERALS.index(mineral)] for mineral in KD_MINERALS])
    whole_rock_ratios: Dict[str, float] = field(default_factory=lambda: {
        'olivine': None,
        'spinel': None,
        'clinopyroxene': 'Fe/Mg',
        'orthopyroxene': 'Fe/Mg',
        'plagioclase': 'Ca/Na',
        'amphibole': 'Fe/Mg',
        'kfeldspar': 'K/Na',
        'biotite': 'Fe/Mg',
        'quartz': None,
        'magnetite': None,
        'ilmenite': None,
        'titanaugite': 'Fe/Mg',
        'nepheline': 'Ca/Na',
        'leucite': 'K/Na',
        'nosean_hauyne': 'Ca/Na',
        'alkali_amphibole': 'Fe/Mg'
    })

    KD_vals: np.ndarray = field(default_factory=lambda: np.array([
            [1.2, 0.28, 0.29, 0.37, 1.3, 1., 1., 1., 1., 1., 1.],    # stage 1
            [1.2, 0.28, 0.29, 0.37, 1.3, 1., 1., 1., 1., 1., 1.],    # stage 2
            [1.2, 0.28, 0.29, 0.37, 1.3, 1., 1., 1., 1., 1., 1.],    # stage 3
            [1.2, 0.28, 0.29, 0.37, 1.3, 1., 1., 1., 1., 1., 1.],    # stage 4
            [1.2, 0.28, 0.29, 0.37, 1.3, 1., 1., 1., 1., 1., 1.]     # stage 5
    ], dtype=np.float64 ))

    # Trace element KD values (5 phases, 20 minerals, 32 trace elements)
    trace_KDs: np.ndarray = field(default_factory=lambda: np.zeros((5, 20, 32), dtype=np.float64))

    usage : np.ndarray = field(default_factory=lambda: np.ones((5, 16), dtype=bool))
    custom_mineralogies: np.ndarray = field(default_factory=lambda: np.full((5, 16, 8), np.nan, dtype=np.float64))
    

    def __post_init__(self):
        """Resolves the PyInstaller/development base asset path."""

        if self.banks:
            # If banks are already provided (e.g. from loading .hades file), skip
            log_meta("Mineral banks already provided; skipping load.", level=7)
            return

        if hasattr(sys, '_MEIPASS'):
            self._base_path = join(sys._MEIPASS, './assets/')
        else:
            self._base_path = abspath(join(dirname(__file__), './assets/'))

        # Use the default filepaths for mineral banks, but pass in any custom paths provided by the user
        default_filepaths = {
            name: str(get_asset_path("hades.assets", f"mineral_banks/{name}.csv"))
            for name in MINERALS
        }
        
        custom_filepaths = self.filepaths or {}
        
        unknown = set(custom_filepaths) - set(MINERALS)
        if unknown:
            warn(f"Custom filepaths provided for unknown minerals: {unknown}. These will be ignored.")
            custom_filepaths = {k: v for k, v in custom_filepaths.items() if k in MINERALS}
        
        valid_custom_filepaths = {}
        
        for name, filepath in custom_filepaths.items():
            if not isinstance(filepath, (str, os.PathLike)):
                warn(
                    f"Custom path for mineral '{name}' is not a valid path. "
                    "Using the default mineral bank."
                )
                continue
        
            filepath = os.fspath(filepath)
        
            if os.path.isfile(filepath):
                valid_custom_filepaths[name] = filepath
            else:
                warn(
                    f"Custom mineral bank for '{name}' was not found at "
                    f"'{filepath}'. Using the default mineral bank."
                )
        
        paths = {
            **default_filepaths,
            **valid_custom_filepaths,
        }
        
        self.filepaths = paths
        self.banks = {
            name: MineralBank(name=name, filepath=filepath)
            for name, filepath in paths.items()
        }

    def load_trace_KDs(self, oxides, traces):
        # Load trace KDs for this phase
        from .loading import parse_file
        for p, phase in enumerate(['primary', 'primitive', 'basic', 'intermediate', 'evolved']):

            # file = os.path.join(self._base_path, 'trace_KDs', f'{phase}KDs.csv')
            file = get_asset_path('hades.assets', f"trace_KDs/{phase}KDs.csv")
            KDs = np.genfromtxt(file, delimiter=',', skip_header=1, usecols=range(1, 24))
            # Load and sort for all majors and minors
            parsed_data, headers, sample_names = parse_file(file)
            KDs, sample_names = sort_geochem(
                        parsed_data, sample_names, oxides + traces
                )
            KDs = np.nan_to_num(KDs, nan=0.0)  # Replace nan with 0

            # Store the sorted KDs in the trace_KDs dictionary
            self.trace_KDs[p] = KDs

    def load_mineral_banks(self, Fe2O3_FeO_Ratio: float):
        """Iterates through each MineralBank and triggers its local load method."""
        log_meta(f"Loading mineral banks from base path: {self._base_path}", level=7)
        for bank in self.banks.values():
            # Ignore olivine
            if bank.name == 'olivine':
                continue
            bank.load_data(os.path.join(self._base_path, 'mineral_banks'))

            # Now restructure the mineral bank depend on its whole-rock ratio
            ratio_key = self.whole_rock_ratios.get(bank.name)
            # NOTE: Hard-coded oxide indices are used below based on the expected order of oxides

            if ratio_key == 'Ca/Na':
                WR = (bank.data[5] / 56.1) / (2 * (bank.data[6] / 62))
            elif ratio_key == 'Fe/Mg':
                WR = (bank.data[3] * Fe2O3_FeO_Ratio / 71.846) / (bank.data[4] / 40.311)
            elif ratio_key == 'K/Na':
                WR = (2 * bank.data[7] / 94.2) / (2 * bank.data[6] / 62)

            if ratio_key is not None:
                # Append the whole-rock ratio as a new row
                bank.data = np.vstack((bank.data, WR))  

                # Sort columns by the RW values, increasing. This is neccessary for np.searchsorted to work correctly later on. Achieved via perumtuation to ensure we can also track the sample names' ordering.
                vals = bank.data[-1, :]
                perm = np.argsort(vals)
                bank.data = bank.data[:, perm]
                bank.names = [bank.names[i] for i in perm]
                # NOTE: This retains the WR as the last row (9); minerals with no WR will only have the major oxide rows (8)

            bank.data[:8] = sanity_check(bank.data[:8], axis=0)  # Ensure each column sums to 100 (or very close)

        log_meta(f"Mineral banks loaded", level=11)
        
class Obol:
    """
    The main class for the Hades model. This class encapsulates all the data and methods required to run a geochemical simulation. The Windows GUI application interacts with this class to perform simulations and retrieve results.

    Notes
    -----
    - Underscore prefixed methods are such to exclude from the API reference in the documentation, as they are not intended for public use.

    Examples
    --------
    >>> model = Obol.newModel()
    """

    def __init__(self, minerals: Minerals = None, namespace: Namespaces = None, optimising: Optimising = None, meta: Metadata = None, constants: Constants = None):

        # Initialise/inherit structured data containers
        self.magma = MagmaState()
        self.datasuite = DataSuite()
        self.assimilant = Assimilant()
        self.constants = constants
        self.minerals = minerals
        self.namespace = namespace
        self.optimising = optimising
        self.meta = meta

        # Initialise an empty, structured results object
        self.results = Results()
        self.trace_results = Results()
        # Keep track of the crystallisation sequence and the minerals that crystallise at each phase transition
        self.crystallisation_dict = {}

    # %% ---- User-facing Methods ----

    @classmethod
    def newModel(cls, mode: str = 'subalkaline', submode: Optional[str] = None, FeO_Fe2pO_Ratio: float = 0.9, custom_mineral_paths: Dict[str, str] = None):
        """
        This class method creates a new instance of the Obol model with the passed optional parameters. It initialises the necessary data structures and loads mineral banks and trace KDs.

        Parameters
        ----------
        mode : str, optional
            The mode of the model, either 'alkaline' or 'subalkaline'. Default is 'subalkaline'.
        submode : str, optional
            The submode of the model, either 'tholeiitic' or 'calcalkaline'. Only relevant if mode is 'subalkaline'. Default is None which will fallback to 'tholeiitic' if mode is 'subalkaline'.
        FeO_Fe2pO_Ratio : float, optional
            The ratio of FeO to Fe2O3 used in the model. Default is 0.9.
        custom_mineral_paths : dict, optional
            A dictionary mapping mineral names to custom file paths for their mineral banks. If provided and valid, these paths will override the default paths.
        
        Returns
        -------
        Obol
            A new instance of the Obol model, fully initialised with the specified parameters and loaded mineral banks and trace KDs.

        Examples
        --------
        Create the default tholeiitic subalkaline model:

        >>> model = Obol.newModel()

        Create an alkaline model with a custom FeO to Fe2O3 ratio:

        >>> model = Obol.newModel(mode='alkaline', submode=None, FeO_Fe2pO_Ratio=0.85)
        """
                
        log_meta(f"""
New Model Created
─────────────────────────────────────────────────────────────────────────────────────────────────
\nModel Initialised with mode={mode}, submode={submode}, FeO_Fe2pO_Ratio={FeO_Fe2pO_Ratio}""",
        no_time=True
        )

        if mode == "subalkaline" and submode in [None, "", 'None']:
            submode = "tholeiitic"

        # mode must be 'alkaline' or 'subalkaline', default to 'subalkaline'
        if mode not in ["alkaline", "subalkaline"]:
            warn(f"Invalid mode '{mode}' provided. Defaulting to 'subalkaline'.")
            mode = "subalkaline"
        # submode must be 'tholeiitic' or 'calcalkaline' if mode is 'subalkaline', otherwise None
        if mode == "subalkaline" and submode not in ["tholeiitic", "calcalkaline"]:
            warn(f"Invalid submode '{submode}' provided for mode 'subalkaline'. Defaulting to 'tholeiitic'.")
            submode = "tholeiitic"
        if mode == "alkaline" and submode is not None:
            warn(f"Submode is not a required argument for mode 'alkaline'. Ignoring provided submode '{submode}'.")
            submode = None
        # FeO_Fe2pO_Ratio must be a float
        assert isinstance(FeO_Fe2pO_Ratio, float), warn(f"FeO_Fe2pO_Ratio must be a float. Received: {FeO_Fe2pO_Ratio}")

        # Create some of the dataclasses to use in this function
        meta = Metadata(mode=mode, submode=submode, FeO_Fe2pO_Ratio=FeO_Fe2pO_Ratio)
        namespace = Namespaces()
        optimising = Optimising()
        constants = Constants()

        # We could pass mineral bank filespaths as an arg and update the defaults
        if custom_mineral_paths is not None:
            minerals = Minerals(custom_mineral_paths)
        else:
            minerals = Minerals()

        # Load the mineral banks from disk 
        minerals.load_mineral_banks(constants.Fe2O3_FeO_Ratio)
        minerals.load_trace_KDs(namespace.oxides, namespace.traces)

        # Depending on the mode/submode, set different defaults
        # These don't need validation as they are being set explicitly
        if meta.mode == 'subalkaline':
            # Subalkaline uses 11 minerals
            meta.minerals_ = ['olivine', 'spinel', 'clinopyroxene', 'orthopyroxene', 'plagioclase', 'amphibole', 'kfeldspar', 'biotite', 'quartz', 'magnetite', 'ilmenite']

            # .99999 to avoid 100% FC but still provide equal chance of 99% being chosen
            optimising.bounds_default = [[0, .99999], [0, 0.4], [0, 0.05], [0, 0.8], [0, 0.4], [0, 0.8], [0., 0.6], [0, 0.5], [0., 0.2], [0, 0.4], [0, 0.2], [0, 0.2]]
            # Set usage of alkaline-only minerals to False
            minerals.usage[:, np.where(~np.isin(namespace.minerals, meta.minerals_))[0]] = False
            meta.SiO2_phase_bounds = np.array([45, 52, 56, 63], dtype=np.float64)
            
            # Furthermore, depending on the submode for subalkaline (alkaline is just alkaline), we may remove further minerals
            if meta.submode == 'tholeiitic':
                # Primary - Primitive
                minerals.usage[0, 2:] = False
                # Primitive - Basic
                minerals.usage[1, np.isin(namespace.minerals, ['orthopyroxene', 'amphibole', 'kfeldspar', 'biotite', 'quartz', 'magnetite'])] = False
                # Basic - Intermediate
                minerals.usage[2, np.isin(namespace.minerals, ['spinel', 'orthopyroxene', 'amphibole', 'kfeldspar', 'biotite', 'quartz', 'magnetite'])] = False
                # Intermediate - Evolved
                minerals.usage[3, np.isin(namespace.minerals, ['olivine', 'spinel', 'amphibole', 'kfeldspar', 'biotite'])] = False
                # Evolved - End
                minerals.usage[4, np.isin(namespace.minerals, ['spinel', 'amphibole', 'biotite'])] = False
            elif meta.submode == 'calcalkaline':
                # Primary - Primitive
                minerals.usage[0, 2:] = False
                # Primitive - Basic
                minerals.usage[1, np.isin(namespace.minerals, ['orthopyroxene', 'kfeldspar', 'ilmenite', 'biotite', 'quartz'])] = False
                # Basic - Intermediate
                minerals.usage[2, np.isin(namespace.minerals, ['spinel', 'kfeldspar', 'ilmenite', 'biotite', 'quartz'])] = False
                # Intermediate - Evolved
                minerals.usage[3, np.isin(namespace.minerals, ['olivine', 'spinel', 'kfeldspar', 'ilmenite', 'biotite'])] = False
                # Evolved - End
                minerals.usage[4, np.isin(namespace.minerals, ['olivine', 'spinel', 'ilmenite'])] = False

                # Set the KD values for plagioclase to 3.4
                minerals.KD_vals[:, 0] = 3.4

        # And for alkaline
        else:
            optimising.bounds_default = [[0, .99999], [0, 0.4], [0, 0.4], [0., 0.6], [0, 0.5], [0, 0.2], [0, 0.2], [0, 0.2], [0, 1], [0, 1], [0, 1], [0, .1], [0, 1]]
            # Alkaline uses 12 minerals
            meta.minerals_ = ['olivine', 'spinel', 'plagioclase', 'kfeldspar', 'biotite', 'magnetite', 'ilmenite', 'titanaugite', 'nepheline', 'leucite', 'nosean_hauyne', 'alkali_amphibole']
            meta.SiO2_phase_bounds = np.array([43, 48, 56, 63], dtype=np.float64)
            # Set usage of subalkaline-only minerals to False
            minerals.usage[:, np.where(~np.isin(namespace.minerals, meta.minerals_))[0]] = False

            # Set usage of subalkaline-only minerals
            # Primary - Primitive
            minerals.usage[0, 2:] = False
            # Primitive - Basic
            minerals.usage[1, np.isin(namespace.minerals, ['kfeldspar', 'biotite'])] = False
            # Basic - Intermediate
            minerals.usage[2, np.isin(namespace.minerals, ['spinel', 'kfeldspar', 'biotite'])] = False
            # Intermediate - Evolved
            minerals.usage[3, 1] = False
            # Evolved - End
            minerals.usage[4, 1] = False

        return cls(
            minerals=minerals,
            namespace=namespace,
            optimising=optimising,
            meta=meta,
            constants=constants,
        )

    def set_KDs(self, **kwargs) -> None:
        """
        Set multiple KD values for minerals in each phase at once using keyword arguments.

        This function accepts keyword arguments where the key is a string in the format 'transition__mineral' and the value is the KD value to set. The function will update the KD values for the specified transition and mineral.

        Parameters
        ----------
        **kwargs : 
            Keyword arguments where each key is in the format 'transition__mineral' and the value is the KD value to set.

        Notes
        -----
        - Mineral and phase names are case-insensitive and can be abbreviated (e.g., 'plag' for 'plagioclase').
        - Invalid transitions or minerals will be skipped with a warning message.
        - To set a value for all minerals or all phases, use the wildcard 'all' or leave the transition/mineral part blank.
        - The order in which the arguments are provided will specify the order of execution, thus you could set all Kd values for a mineral across all phases first, and then override the value for a specific phase later in the same call.
            
        Examples
        --------
        To set the Kd value for plagioclase in the basic to intermediate phase to 1.2:
        
        >>> model.set_KDs(Basic__Plagioclase=1.2)

        To set the Kd value for olivine across all phases to 0.45 and spinel across all phases to 0.55:

        >>> model.set_KDs(__olivine=0.45, __spinel=0.55)
        or equivalently:
        >>> model.set_KDs(all__olivine=0.45, all__spinel=0.55)

        To use a Kd value of 0.98 for all minerals in the primitive to basic phase:

        >>> model.set_KDs(Primitive__all=0.98)

        Set all plagioclase Kd values to 1.2 but then override the value for the basic to intermediate phase to 1.5:

        >>> model.set_KDs(__plagioclase=1.2, Basic__Plagioclase=1.5)
        """
        transitions = [l.lower() for l in self.namespace.phases[:-1]]
        minerals = [l.lower().replace('-','') for l in self.minerals.KD_minerals_short]
        minerals_abbrev = [l.lower().replace('-','') for l in self.minerals.KD_minerals]

        wildcards = {"all", ""}

        for key, value in kwargs.items():
            if "__" not in key:
                print(f"Invalid parameter format '{key}'. Use 'Transition__Mineral=value' (e.g., set_KDs(primitive__Olivine=0.45)). Skipping.")
                continue

            transition, mineral = key.split("__", 1)
            trans_str = transition.lower().strip()
            min_str = mineral.lower().strip()

            # Resolve Target Transition Indices
            if trans_str in wildcards:
                target_trans_indices = list(range(len(transitions)))
            elif trans_str in transitions:
                target_trans_indices = [transitions.index(trans_str)]
            else:
                print(f"Invalid transition '{transition}'. Valid options: {transitions} or 'all'. Skipping '{key}'.")
                continue

            # Resolve Target Mineral Indices
            if min_str in wildcards:
                target_min_indices = list(range(len(minerals)))
            elif min_str in minerals:
                target_min_indices = [minerals.index(min_str)]
            elif min_str in minerals_abbrev:
                target_min_indices = [minerals_abbrev.index(min_str)]
            else:
                print(f"Invalid mineral '{mineral}'. Valid options: {minerals} or 'all'. Skipping '{key}'.")
                continue

            # Apply value across resolved index slices
            val_float = float(value)
            for t_idx in target_trans_indices:
                for m_idx in target_min_indices:
                    self.minerals.KD_vals[t_idx, m_idx] = val_float

    def set_mineralogies(self, **kwargs) -> None:
        """
        Set the major oxide compositions of minerals in each phase at once using keyword arguments.

        This function accepts keyword arguments where the key is a string in the format 'transition__mineral' and the value is either a 1D array of oxide weight percentages (matching the number of oxides) or a 2D array (matching the number of transitions x number of oxides). The dimensionality of the array provided should match the intended target (either a specific transition/mineral combination or all transitions for a mineral).

        Parameters
        ----------
        **kwargs : 
            Keyword arguments where each key is in the format 'transition__mineral' and the value is either a 1D or 2D array of oxide weight percentages.

        Notes
        -----
        - Mineral and phase names are case-insensitive and can be abbreviated (e.g., 'plag' for 'plagioclase').
        - Invalid transitions or minerals will be skipped with a warning message.
        - The composition arrays will be normalised to 100 wt% if they do not already sum to 100.
        - The order in which the arguments are provided will specify the order of execution, thus you could set all compositions for a mineral across all phases first, and then override specific transitions/minerals later in the same call.

        Examples
        --------
        To set the composition of plagioclase in the basic to intermediate phase:

        >>> model.set_mineralogies(Basic__Plagioclase=[50, 0, 30, 10, 5, 5, 0, 0])

        To set the composition of spinel and plagioclase in the primitive to basic phase:

        >>> model.set_mineralogies(
        >>>     primitive__spinel=[0, 0, 0, 20, 30, 10, 40, 0],
        >>>     primitive__plagioclase=[50, 0, 30, 10, 5, 5, 0, 0]
        >>> )

        To set the composition of olivine across all phases:

        >>> model.set_mineralogies(__olivine=[40, 0, 0, 10, 50, 0, 0, 0])
        or equivalently:
        >>> model.set_mineralogies(all__olivine=[40, 0, 0, 10, 50, 0, 0, 0])

        Or, to set unique compositions of olivine at each phase, use a 2D array:
    
        >>> model.set_mineralogies(
        >>>     olivine=np.array([0, 0, 0, 10, 50, 0, 0, 0], dtype=float),
        >>>     olivine=np.array([0, 0, 0, 15, 45, 0, 0, 0], dtype=float),
        >>>     olivine=np.array([0, 0, 0, 20, 40, 0, 0, 0], dtype=float),
        >>>     olivine=np.array([0, 0, 0, 25, 35, 0, 0, 0], dtype=float),
        >>>     olivine=np.array([0, 0, 0, 30, 30, 0, 0, 0], dtype=float)
        >>> )        
        """
        transitions = [l.lower() for l in self.namespace.phases[:-1]]
        minerals = [l.lower().replace('-','') for l in self.namespace.minerals]
        minerals_abbrev = [l.lower().replace('-','') for l in self.namespace.minerals_short]
        num_oxides = len(self.namespace.oxides)
        wildcards = {"all", ""}

        for key, value in kwargs.items():
            comp_array = np.asarray(value, dtype=float)

            if "__" in key:
                # Updating a specific transition/mineral combination
                transition, mineral = key.split("__", 1)
                trans_str = transition.lower().strip()
                min_str = mineral.lower().strip()

                # Resolve Target Transition Indices
                if trans_str in wildcards:
                    target_trans_indices = list(range(len(transitions)))
                elif trans_str in transitions:
                    target_trans_indices = [transitions.index(trans_str)]
                else:
                    print(f"Warning: Invalid transition '{transition}'. Valid options: {transitions}")
                    continue

                # Resolve Target Mineral Indices
                if min_str in wildcards:
                    target_min_indices = list(range(len(minerals)))
                elif min_str in minerals:
                    target_min_indices = [minerals.index(min_str)]
                elif min_str in minerals_abbrev:
                    target_min_indices = [minerals_abbrev.index(min_str)]
                else:
                    print(f"Warning: Invalid mineral '{mineral}'. Valid options: {minerals}")
                    continue

                # Validate Shape (Must be 1D vector matching oxide count)
                if comp_array.ndim != 1 or len(comp_array) != num_oxides:
                    print(f"Warning: Composition array for '{key}' must be 1D with length {num_oxides}. Received shape: {comp_array.shape}")
                    continue

                # Normalise to 100 wt%
                comp_sum = np.sum(comp_array)
                if comp_sum != 0 and not np.isclose(comp_sum, 100.0):
                    print(f"Normalising composition for {key} to 100 wt%. Original sum: {comp_sum:.2f}")
                    comp_array = (comp_array / comp_sum) * 100.0

                # Apply across resolved targets
                for t_idx in target_trans_indices:
                    for m_idx in target_min_indices:
                        self.minerals.custom_mineralogies[t_idx, m_idx, :] = (comp_array)

            else:
                # Updating all transitions for a mineral at once using a 2D matrix
                mineral = key
                if mineral.lower() not in minerals:
                    print(f"Invalid mineral '{mineral}'. Valid options: {minerals}")
                    continue

                expected_shape = (len(transitions), num_oxides)
                if comp_array.shape != expected_shape:
                    print(f"Full composition matrix for '{mineral}' must have shape {expected_shape}. Received shape: {comp_array.shape}")
                    continue

                # Normalise each row (transition) to 100 wt%
                comp_sum = np.sum(comp_array, axis=1, keepdims=True)
                comp_normalised = ( np.divide(comp_array, comp_sum, out=np.zeros_like(comp_array), where=comp_sum != 0) * 100 )

                min_idx = minerals.index(mineral.lower())
                self.minerals.custom_mineralogies[:, min_idx, :] = comp_normalised

    def set_mineral_usage(self, **kwargs) -> None:
        """
        Specify which minerals are allowed to crystallise at each phase transition using keyword arguments.

        This function accepts keyword arguments where the key is a string in the format 'transition__mineral' and the value is a boolean (True/False) indicating whether the mineral is allowed to crystallise at that transition.

        Parameters
        ----------
        **kwargs : 
            Keyword arguments where each key is in the format 'transition__mineral' and the value is a boolean indicating whether the mineral is allowed to crystallise at that transition.

        Notes
        -----
        - Mineral and phase names are case-insensitive and can be abbreviated (e.g., 'plag' for 'plagioclase').
        - Invalid transitions or minerals will be skipped with a warning message.
        - To set a value for all minerals or all phases, use the wildcard 'all' or leave the transition/mineral part blank.
        - The order in which the arguments are provided will specify the order of execution, thus you could set all values in one phase to False, then override a specific mineral to True in a subsequent call.

        Examples
        --------
        To allow plagioclase to crystallise at the basic to intermediate phase:

        >>> model.set_mineral_usage(Basic__Plagioclase=True)

        To disallow olivine across all phases:

        >>> model.set_mineral_usage(__olivine=False)
        or equivalently:
        >>> model.set_mineral_usage(all__olivine=False)

        To allow multiple minerals to crystallise at a specific phase transition:

        >>> model.set_mineral_usage(Primitive__Spinel=True, Primitive__Plagioclase=True)

        Or, set many values at once:

        >>> model.set_mineral_usage(
        >>>     __spinel=True,
        >>>     basic__plagioclase=True,
        >>>     intermediate__kfeldspar=False,
        >>>     evolved__biotite=True,
        >>> )

        Set all minerals to be considered at all phases, but then override the value for plagioclase at the basic to intermediate phase to False:

        >>> model.set_mineral_usage(
        >>>     __=True,
        >>>     Basic__Plagioclase=False, 
        >>> )
        """
        transitions = [l.lower() for l in self.namespace.phases[:-1]]
        minerals = [l.lower().replace('-','') for l in self.namespace.minerals]
        minerals_abbrev = [l.lower().replace('-','') for l in self.namespace.minerals_short]
        wildcards = {"all", ""}

        for key, value in kwargs.items():
            if "__" not in key:
                print(f"Invalid parameter format '{key}'. Use 'Transition__Mineral=bool' (e.g., set_mineral_usage(primitive__Olivine=True))")
                continue

            transition, mineral = key.split("__", 1)
            trans_str = transition.lower().strip()
            min_str = mineral.lower().strip()

            # Resolve Target Transition Indices
            if trans_str in wildcards:
                target_trans_indices = list(range(len(transitions)))
            elif trans_str in transitions:
                target_trans_indices = [transitions.index(trans_str)]
            else:
                print(f"Invalid transition '{transition}'. Valid options: {transitions}")
                continue

            # Resolve Target Mineral Indices
            if min_str in wildcards:
                target_min_indices = list(range(len(minerals)))
            elif min_str in minerals:
                target_min_indices = [minerals.index(min_str)]
            elif min_str in minerals_abbrev:
                target_min_indices = [minerals_abbrev.index(min_str)]
            else:
                print(f"Invalid mineral '{mineral}'. Valid options: {minerals}")
                continue

            # Apply boolean value across resolved targets
            bool_val = bool(value)
            for t_idx in target_trans_indices:
                for m_idx in target_min_indices:
                    self.minerals.usage[t_idx, m_idx] = bool_val

    def summary(self) -> None:
        """
        Prints a human-readable summary of the current model's results, if available.
        """
        isrun_ = [p for p in range(5) if self.results[p].isrun]
        tracesisrun_ = [p for p in range(5) if self.trace_results[p].isrun]
        
        # Identify run type for each phase
        which = ['Traces' if p in tracesisrun_ else 'Majors' for p in isrun_]

        # Include accessory minerals if traces were run in at least one phase
        num_majors = len(self.meta.minerals_)
        used_minerals = (
            self.meta.minerals_ + self.namespace.accessory_minerals
            if len(tracesisrun_) > 0
            else self.meta.minerals_
        )

        ## Title 
        titles = "".join([f"{x:^11}" for i, x in enumerate(self.namespace.phase_transitions_abbrev) if i in isrun_])
        print(f"{'':>19} {titles} |  {'Total':^11}")
        print("-" * (16 * (2 + len(isrun_))))

        ## Metadata
        # Type
        print(f"{'Type':>16}  | ", "".join([f" {w:^8}  " for w in which]) + f"| {'':^8}   ")
        # Cost
        print(f"{'Cost':>16}  | ", "".join([f" {self.results[p].cost:>7.2f}   " if p not in tracesisrun_ else f"  {self.trace_results[p].cost:>7.2f}  " for p in isrun_]) + f"| {'':>8}   ")
        print("-" * (16 * (2 + len(isrun_))))

        ## Optimised Parameters
        # Melt fraction (F)
        F_vals = [f"{int(100*self.results[p].F):>8.0f}   " for p in isrun_] + [f"|  {100:>8.0f}   "]
        print(f"{'F':>16}  | ", "".join(F_vals), "%")
        
        # Mineral weights
        for i, m in enumerate(used_minerals):
            is_accessory = i >= num_majors
            formatted_cols = []
            
            for p in isrun_:
                if p in tracesisrun_:
                    # Fetch weights from trace_results when traces are run
                    # If mineral not used, print ' '
                    if self.trace_results[p].usage[i] == False:
                        formatted_cols.append(f"{' ':>8}   ")
                    else:
                        weight = self.trace_results[p].weights[i]
                        if weight > 0:
                            formatted_cols.append(f"{100 * weight:>8.3f}   ")
                        else:
                            formatted_cols.append(f"{'-':>8}   ")
                else:
                    # If traces are NOT run, print empty field for accessory rows, else fetch from results
                    if is_accessory:
                        formatted_cols.append(f"{'':>8}   ")
                    else:
                        # If mineral not used, print ' '
                        if self.results[p].usage[i] == False:
                            formatted_cols.append(f"{' ':>8}   ")
                        else:
                            weight = self.results[p].weights[i]
                            if weight > 0:
                                formatted_cols.append(f"{100 * weight:>8.3f}   ")
                            else:
                                formatted_cols.append(f"{'-':>8}   ")

            # Add the total weight for the mineral across all phases
            if self.crystallisation_dict['total_minerals_wt'][i] > 0:
                formatted_cols.append(f"|  {self.crystallisation_dict['total_minerals_wt'][i]:>8.3f}   ")
            else:
                formatted_cols.append(f"|  {' ':>8}   ")

            if is_accessory:
                min_name = self.namespace.accessory_minerals_formal[self.namespace.accessory_minerals.index(m)]
            else:
                min_name = self.namespace.minerals_title[self.namespace.minerals.index(m)] if not is_accessory else m
            print(f"{min_name:>16}  | ", "".join(formatted_cols), "wt.%")
        print("-" * (16 * (2 + len(isrun_))))

        print(f"Total melt fraction crystallised across all phases: {100 * self.crystallisation_dict['delta_S'].sum():.2f} wt.%")
        print(f"\n'-' indicates the mineral was used but has a wt.% of exactly 0")
        print(f" 0.0 implies the mineral has a small, but non-zero wt.%")
        print(f" blank cells indicate the mineral was not used in that phase")

    def save_config(self, filepath: str = './config.hades') -> None:
        """
        Saves the current model configuration to a .hades file in JSON format.
        The configuration includes the meta, assimilant, optimising, magma,
        minerals, and datasuite attributes of the model. Mineral source paths
        are deliberately omitted because the corresponding data is stored in
        the configuration.

        Parameters
        ----------
        filepath : str, optional
            The path to the file where the configuration will be saved. Default is './config.hades'.

        Notes
        -----
        - Results of models are not saved, only the data suite, auto-computed LLOD, and all customisable parameters (Kd values, mineral compositions, mineral usage, etc.) are saved.
        """
        data_to_save = {}

        # Set which paths to save
        include_paths = [
            'meta',
            'assimilant',
            'optimising',
            'magma',
            'minerals',
            'datasuite',
        ]

        for path in include_paths:
            try:
                val = get_nested_attr(self, path)
                if is_dataclass(val):
                    data_to_save[path] = asdict(val)
                else:
                    data_to_save[path] = val
            except AttributeError:
                print(f"Warning: Path '{path}' not found. Skipping.")

        # File paths are runtime metadata, not part of the portable model
        # configuration. Keep the bank data and names, but omit each source
        # path. The data suite path identifies this configuration file rather
        # than the original data source.
        minerals_data = data_to_save.get('minerals')
        if isinstance(minerals_data, dict):
            minerals_data.pop('filepaths', None)
            banks_data = minerals_data.get('banks')
            if isinstance(banks_data, dict):
                for bank_data in banks_data.values():
                    if isinstance(bank_data, dict):
                        bank_data.pop('filepath', None)

        datasuite_data = data_to_save.get('datasuite')
        if isinstance(datasuite_data, dict):
            datasuite_data['filepath'] = os.path.basename(os.path.abspath(filepath))

        # Write to file using our custom converter
        with open(filepath, 'w') as f:
            json.dump(data_to_save, f, default=convert_to_serialisable, indent=4)
        print(f"Successfully saved configuration to {filepath}")
  
    def load_config(self, filepath: str = './config.hades') -> bool:
        """
        Loads a model configuration from a .hades file in JSON format. The function will attempt to read the file, validate its contents, and update the model's attributes accordingly. 
        
        Parameters
        ----------
        filepath : str, optional
            The path to the .hades file to load. Default is './config.hades'.

        Returns
        -------
        bool
            Returns True if the configuration was successfully loaded and applied, False otherwise. Utilised in the GUI.

        See Also
        --------
        save_config : Saves the current model configuration to a .hades file.
        """
        # Minimal error handling to ensure the file exists
        if not os.path.exists(filepath):
            print(f"Error: The file '{filepath}' does not exist. Aborting load.")
            return False

        try:
            with open(filepath, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: '{filepath}' contains invalid JSON formatting.")
            return False
            
        include_paths = [
            'meta',
            'assimilant',
            'optimising',
            'magma',
            'minerals',
            'datasuite',
        ]
            
        # Strip out unexpected top-level keys completely.
        sanitised_data = {}
        for path, value in saved_data.items():
            if path in include_paths:
                sanitised_data[path] = value
            else:
                log_meta(f"Ignored unexpected parameter in JSON: '{path}'")

        # Reconstruct runtime-only mineral paths from the package defaults.
        # The saved bank data remains authoritative, so no external bank files
        # are read during config loading.
        minerals_data = sanitised_data.get('minerals')
        if isinstance(minerals_data, dict):
            minerals_data.pop('filepaths', None)
            default_filepaths = {
                name: str(get_asset_path(
                    "hades.assets", f"mineral_banks/{name}.csv"
                ))
                for name in MINERALS
            }
            minerals_data['filepaths'] = default_filepaths

            banks_data = minerals_data.get('banks')
            if isinstance(banks_data, dict):
                for name, bank_data in banks_data.items():
                    if not isinstance(bank_data, dict):
                        continue
                    bank_data.pop('filepath', None)
                    bank_data['filepath'] = default_filepaths.get(
                        name,
                        str(get_asset_path(
                            "hades.assets", f"mineral_banks/{name}.csv"
                        )),
                    )

        # The data suite contents are stored in the config, so the path from
        # the JSON is intentionally ignored and replaced with the config name.
        datasuite_data = sanitised_data.get('datasuite')
        if isinstance(datasuite_data, dict):
            datasuite_data['filepath'] = os.path.basename(os.path.abspath(filepath))

        # TODO: Validation, e.g.:
        # try:
        #     # Pass through validation pipeline
        #     sanitised_data = self._validation(sanitised_data)
        # except (ValueError, TypeError, KeyError) as e:
        #     print(f"Load canceled. Configuration validation failed:\n  -> {e}")
        #     return False

        # print(f"Loading configuration from {os.path.basename(filepath)} with sanitised paths: {list(sanitised_data.keys())}")

        for path, value in sanitised_data.items():
            try:
                current_val = get_nested_attr(self, path)

                if is_dataclass(current_val):
                    # Recursively rebuild the whole (possibly nested) dataclass tree
                    updated_dataclass = from_dict(type(current_val), value)
                    set_nested_attr(self, path, updated_dataclass)
                else:
                    if isinstance(current_val, np.ndarray):
                        value = np.array(value)
                    set_nested_attr(self, path, value)

            except AttributeError:
                print(f"Warning: Path '{path}' doesn't exist in current structure.")
            except TypeError as e:
                print(f"Error applying path '{path}': {e}")

        # Display the main loaded arrays:
        nice_display(self.minerals.KD_vals, self.namespace.phase_transitions, self.minerals.KD_minerals, title="Loaded KD Values:", title_level=10, level=13)
        nice_display(self.datasuite.data, self.datasuite.sample_names, self.datasuite.geochem, title="Loaded Data Suite:", right_col=self.namespace.geochem_units, max_rows=10, max_cols=6, title_level=10, level=13)
        nice_display(self.magma.initial, self.namespace.phases, self.namespace.geochem, title="Loaded Initial Magma Compositions:", right_col=self.namespace.geochem_units, max_cols=6, title_level=10, level=13)
        nice_display(self.assimilant.composition.reshape(1, -1), ['Assimilant'], self.namespace.geochem, title="Loaded Assimilant Compositions:", right_col=self.namespace.geochem_units, max_cols=6, title_level=10, level=13)
        nice_display(self.assimilant.percentages.reshape(1, -1), ['Assimilant'], self.namespace.phase_transitions_abbrev, title="Loaded Assimilant Percentages:", right_col=self.namespace.geochem_units, max_cols=6, title_level=10, level=13)

    def load_data_suite(self, filepath: str) -> None:
        """
        Loads a data suite of geochemical data from a .csv or .xlsx file. The function reads the file, validates its contents, and updates the model's datasuite and magma attributes accordingly. See the online documentation for the expected format of the input file.

        Parameters
        ----------
        filepath : str
            The path to the .csv or .xlsx file containing the geochemical data suite.

        Notes
        -----
        - The function will drop any samples where all major oxides are equal to 0.
        - The function will automatically compute initial magma compositions (a preliminary LLOD) based on the provided data suite and the model's SiO2 phase bounds.
        - The function will ensure that each row's major oxides sum to 100 (or very close) and will normalise them if necessary.
        """

        # Validate filepath
        log_meta(f"Loading data suite:", level=7)

        if not any (filepath.lower().endswith(ext) for ext in ['.csv', '.xlsx']):
            raise ValueError(f"Unsupported file format for '{filepath}'. Please provide a .csv or .xlsx file.")
        if not os.path.exists(filepath):
            # Return a tuple of the title and content of a tkinter messagebox to display
            raise FileNotFoundError(f"File '{filepath}' not found. Please check the file path.")
        
        # Read file
        from .loading import parse_file, autocompute_initial_magma
        parsed_data, headers, names = parse_file(filepath)

        # Validate that all sample names are unique, if not, append a suffix to make them unique
        if len(names) != len(set(names)):
            log_warning("Duplicate sample names found in the data suite. Appending suffixes to make them unique.", level=14)
            name_counts = {}
            for i, name in enumerate(names):
                if name in name_counts:
                    name_counts[name] += 1
                    names[i] = f"{name}_{name_counts[name]}"
                else:
                    name_counts[name] = 1

        # Drop samples where all majors are 0
        zero_major_mask = np.all(parsed_data[:8] == 0., axis=0)
        if np.any(zero_major_mask):
            log_meta(f"Dropping {np.sum(zero_major_mask)} samples with all major oxides equal to 0:", level=14)
            log_meta(f"{', '.join([name for i, name in enumerate(names) if zero_major_mask[i]])}", level=15)
            parsed_data = parsed_data[:,~zero_major_mask]
            names = [name for i, name in enumerate(names) if not zero_major_mask[i]]

        parsed_data, headers = sort_geochem(parsed_data.T, headers, self.namespace.oxides + self.namespace.traces)

        # Ensure each row's majors sum to 100 (or very close)
        parsed_data[:, :8] = sanity_check(parsed_data[:, :8], axis=1, tol=1e-6)  

        autocomp, autocomp_sample_names = autocompute_initial_magma(self.meta.SiO2_phase_bounds, parsed_data, names)
        autocomp[:, :8] = sanity_check(autocomp[:, :8], axis=1, tol=1e-6)  # Ensure each row sums to 100 (or very close)

        log_meta("", level=13)
        nice_display(parsed_data.T, headers, names, title=f"Data Suite:", max_rows=10, max_cols=6, right_col=self.namespace.geochem_units, title_level=10, level=13)
        nice_display(autocomp, self.namespace.phases, self.namespace.geochem, title=f"Auto-Computed Initial Magma Compositions:", right_col=self.namespace.geochem_units, max_cols=10, title_level=10, level=13)

        log_meta("", level=12)

        # Set data suite properties
        self.datasuite.filepath = filepath
        self.datasuite.data = parsed_data.copy()
        self.datasuite.sample_names = names.copy()
        self.datasuite.geochem = headers.copy()

        # Set magma variables, ensuring unique ownership of mutable arrays
        self.magma.initial = autocomp.copy()
        self.magma.computed = autocomp.copy()
        self.magma.traces = autocomp.copy()
        self.magma.autocomp = autocomp.copy()
        self.magma.magma_samples = autocomp_sample_names
        self.magma.autocomp_samples = autocomp_sample_names

    def select_initial_composition(self, sample_names: List[str]) -> None:
        """
        Accepts (up to) 6 sample names from the loaded data suite to use as the expected magma composition in the LLOD for each phase. 
        
        Sample names are case sensitive and must match those in the data suite (either from column headers or default names). Phases can be ignored by passing a `None` type instead of a sample name, or 'auto' will keep the auto-computed initial composition for that phase. If a sample name is not found in the data suite, it will be ignored and filled with NaNs.
        
        Parameters
        ----------
        sample_names : list
            A list of sample names to use as the initial magma compositions for each phase. The length of the list should be 6, corresponding to the 6 phases. If a sample name is not found in the data suite, it will be ignored and filled with NaNs.

        Returns
        -------
        None

        Examples
        --------
        To select specific samples for each phase:

        >>> model.select_initial_composition(['Sample1', 'Sample2', None, 'Sample4', 'auto', 'Sample6'])
        """
        log_meta(f"Manual initial magma selection:", level=7)
        # If sample names is not length 6, pad/crop and warn
        if len(sample_names) != 6:
            log_warning("sample_names should be length 6. Padding/cropping as needed.", level=14)
            if len(sample_names) < 6:
                sample_names = sample_names + [None]*(6-len(sample_names))
            else:
                sample_names = sample_names[:6]
        
        # Get the indices of samples in sample_names, if present, else None
        idxs = [self.datasuite.sample_names.index(name) if name in self.datasuite.sample_names else None for name in sample_names]
        for i, (name, idx) in enumerate(zip(sample_names, idxs)):
            if idx is not None:
                log(f"{self.namespace.phases[i]:<14}: '{name}'", level=14)
            elif name and name.lower() in ['auto', '[auto]']:
                # update name and idx
                sample_names[i] = self.magma.autocomp_samples[i]
                # In the event where auto-sample is None (e.g. GUI default), break into else clause
                if sample_names[i] is None:
                    log(f"{self.namespace.phases[i]:<14}: n/a", level=14)
                    continue
                idxs[i] = self.datasuite.sample_names.index(sample_names[i])
                log(f"{self.namespace.phases[i]:<14}: '{sample_names[i]}' [auto]", level=14)
            else:
                log(f"{self.namespace.phases[i]:<14}: n/a", level=14)

        compositions = []
        for i, (name, idx) in enumerate(zip(sample_names, idxs)):
            if name and name.lower() in ['auto', '[auto]']:
                compositions.append(self.magma.autocomp[i])
            elif idx is not None:
                compositions.append(self.datasuite.data[idx])
            else:
                # TODO: Remove hard-coded number of oxides + traces?
                compositions.append(np.full(32, np.nan))

        compositions = np.vstack(compositions)

        # Assign these new compositions to the magma - not the autocomputed initial conditions as that is the reference
        self.magma.initial = compositions.copy()
        self.magma.computed = compositions.copy()
        self.magma.traces = compositions.copy()
        self.magma.magma_samples = sample_names

        N_non_nan_phases = np.sum(~np.isnan(compositions).all(axis=1))
        log(f"{N_non_nan_phases}/6 phases have been set with user-provided initial compositions.", level=11)

        nice_display(self.magma.initial, self.namespace.phases, self.namespace.geochem, title=f"Selected Magma Compositions:", right_col=self.namespace.geochem_units, max_cols=10)

    def set_assimilant(self, composition: List[float] = None, percentages: List[float] = None, filepath: str = None) -> None:
        """
        Set the assimilant composition and percentage of the assimilant which should be incorporated into the melt in each phase.

        Compostions can be provided directly as an array or list of floats, or they can be loaded from a .csv or .xlsx file. If both a composition and a filepath are provided, the file will take precedence.

        For filepaths, the expected format is the same as the data suite. If more than one sample is present in the file, only the first sample will be used as the assimilant composition.

        Parameters
        ----------
        composition : array-like of shape (32,), optional
            An array or list of either 8 or 32 floats representing the weight percent of each oxide in the assimilant. If 8 values are provided, they will be assumed to correspond to the major oxides (SiO2, TiO2, Al2O3, FeO, MgO, CaO, Na2O, K2O) in that order and will be padded with zeros for the trace elements. If 32 values are provided, they will be assumed to correspond to all oxides and trace elements in the order defined by the model's namespace (see `self.namespace.geochem`). If no composition is provided, it will default to an array of zeros.
        percentages : array-like of shape (5,), optional
            An array or list of 5 floats representing the weight percent of the assimilant to be incorporated into the melt for each of the 5 phases. If no percentages are provided, it will default to an array of zeros, thus not incorporating any assimilant into the melt, even if a composition is provided.
        filepath : str, optional
            The path to a .csv or .xlsx file containing the assimilant composition and percentages.

        Returns
        -------
        None

        Examples
        --------
        To set the assimilant composition and percentages directly, for major oxides only:

        >>> model.set_assimilant(composition=[50, 10, 15, 5, 5, 10, 3, 2], percentages=[10, 20, 30, 20, 20])

        To set the assimilant composition and percentages from a file:

        >>> model.set_assimilant(filepath='path/to/assimilant_data.csv', percentages=[10, 20, 30, 20, 20])
        """
        # Parse a composition (up to 32 oxides) and percentages (5 phases) from the user, or load from a file if provided. If both are provided, the file takes precedence.
        if composition is None:
            composition = np.zeros(32, dtype=np.float64)
        if percentages is None:
            percentages = np.zeros(5, dtype=np.float64)

        # If a filepath is provided, validate and load
        if filepath is not None:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Assimilant file '{filepath}' not found. Please check the file path.")
            if not any (filepath.lower().endswith(ext) for ext in ['.csv', '.xlsx']):
                raise ValueError(f"Unsupported file format for '{filepath}'. Please provide a .csv or .xlsx file.")
            
            # Load the assimilant data from the file
            from .loading import parse_file
            assimilant_data, headers, names = parse_file(filepath)
            log_meta(f"Loaded assimilant data from '{filepath}':\n > {assimilant_data.shape[1]} samples\n > {assimilant_data.shape[0]} geochemical records")

            # Sort
            assimilant_data, headers = sort_geochem(assimilant_data.T, headers, self.namespace.oxides + self.namespace.traces)

            # Extract the composition (first and only sample)
            composition = assimilant_data[0]

        nice_display(composition.reshape(-1, 1), headers, ['Composition'], title=f"Loaded Assimilant Data from '{filepath}':", max_rows=16, max_cols=6, right_col=self.namespace.geochem_units)

        # Sanity check, but only pass the oxides not traces
        composition[:8] = sanity_check(composition[:8])

        # TODO: Validation normalisation, read from csv to have all traces, etc.
        nice_display(composition.reshape(-1, 1), headers, ['Composition'], title=f"Loaded Assimilant Data from '{filepath}':", max_rows=16, max_cols=6, right_col=self.namespace.geochem_units)

        self.assimilant.composition = np.array(composition, dtype=np.float64)
        self.assimilant.percentages = np.array(percentages, dtype=np.float64)
        print(f"Loaded assimilant data from '{filepath}'")

    def run(self, phase, params=None, bounds=None) -> None:
        """
        Calls Hades to run an optimisation for a given phase, using the provided parameters and bounds if specified, to model the LLOD at this phase. 
        
        If no parameters are provided, the function will find the optimal mineral abundances and amount of fractional crystallisation required to model the preliminary LLOD at this phase.

        Parameters
        ----------
        phase : int
            The phase number to run the optimisation for. Must be between 1 and 5, inclusive.
        params : array-like of shape (n,), optional
            An array or list of floats representing the parameters to use for the optimisation. The first value is the % of fractional crystallisation (0-1) and following values are the weights of each mineral in the order defined by the model's namespace (0-1). If no parameters are provided, the function will find the optimal parameters automatically.
        bounds : array-like of shape (n, 2), optional
            An array or list of tuples representing the bounds for each parameter in the optimisation. Each tuple should contain two floats, representing the lower and upper bounds for that parameter. 
        """

        # Phase must be 1-5
        if phase < 1 or phase > 5:
            raise ValueError(f"Phase must be between 1 and 5, inclusive. Received: {phase}")

        log_meta(f"[Major-oxides] {self.namespace.phase_transitions[phase-1]}", level=7)

        # Validate bounds if provided, else use default bounds
        if bounds:
            # Accept custom bounds if correct shape
            if (isinstance(bounds, list) or isinstance(bounds, np.ndarray)) and (len(bounds) == len(self.meta.minerals_)+1):
                self.optimising.bounds = bounds
            else:
                raise ValueError(f"Bounds for phase {phase} must be an array-like structure of length {len(self.meta.minerals_)+1}, received length {len(bounds)}")
        else:
            # Ensure that the bounds are reset
            self.optimising.reset_bounds()

        # Ensure params is array of correct length, if provided
        if params is not None:
            params = np.asarray(params, dtype=np.float64)
            if len(params) != len(self.optimising.bounds):
                raise ValueError(f"Params for phase {phase} must be of shape ({len(self.optimising.bounds)} - FC% + {len(self.optimising.bounds)-1} mineral weights), but got {params.shape}")
            log_meta(f"Running using provided parameters", level=8)
            log_meta(f"{np.round(np.asarray(params), 4)}", level=14)
        else:
            log_meta(f"Finding optimal solution", level=8)

        # Extract the starting and expected compositions for the oxides
        if np.isnan(self.magma.computed[phase-1, :8]).all():
            log_meta(f"Computed magma of previous phase not available, using initial composition for this phase", level=14)
            init_comp = self.magma.initial[phase-1, :8].copy()
            if np.isnan(init_comp).all():
                warn(f"Initial composition is empty; this phase is not covered by the data suite. Skipping optimisation and computation.")
                return None, None, None, None
        else:
            init_comp = self.magma.computed[phase-1, :8].copy()
            log_meta(f"Using previously computed magma composition", level=14)

        exp_comp = self.magma.initial[phase, :8].copy()
        comp_arr = np.vstack( (init_comp, exp_comp) )

        # If the expected composition is all NaN, catch this and return early
        if np.isnan(exp_comp).all():
            log_warning(f"Expected composition for empty; this phase is not covered by the data suite. Skipping optimisation and computation.", level=15)
            return None, None, None, None

        # Compute cotectics to use for this phase
        cotectics, params = self._compile_mineral_bank(phase, params, init_comp)

        log_meta(f"Using bounds:", level=14)
        log_meta(f"{self.optimising.bounds}", level=15)

        if params is None:
            # Find optimal params and then run
            params, opt_result = self._optimise( 
                compute_phase_cost_batch, 
                ( 
                init_comp,
                exp_comp, 
                cotectics,
                self.assimilant.composition[:8],
                self.assimilant.percentages[phase-1],
                self.constants.Fe2O3_FeO_Ratio,
                self.meta.FeO_Fe2pO_Ratio,
                self.constants.molecular_weights,
                ),
            )
        else:
            opt_result = None

        result_p3, result, olivine_comp = compute_phase_evolution_batch(
            params.reshape(1, -1),
            init_comp,
            cotectics,
            self.assimilant.composition[:8],
            self.assimilant.percentages[phase-1],
            self.constants.Fe2O3_FeO_Ratio,
            self.meta.FeO_Fe2pO_Ratio,
            self.constants.molecular_weights,
        )

        log_meta(f"Config and results:", level=9)

        # Assign the final olivine composition that's not all 0s to the cotectics
        zero_mask = np.all(olivine_comp == 0, axis=1)
        max_false = np.max(np.where(~zero_mask)[0]) if np.any(~zero_mask) else None
        cotectics[0, :] = olivine_comp[max_false] if max_false is not None else np.zeros(8)

        # Print current variables and parameters to the log
        nice_display(self.minerals.KD_vals[phase-1, :].reshape(1, -1), [self.namespace.phase_transitions[phase-1]], self.minerals.KD_minerals, title=f"KD Values:", title_level=10, level=13)
        # Assimilant composition and percentages
        nice_display(self.assimilant.composition.reshape(1, -1), ['Assimilant Composition'], self.namespace.geochem, title=f"Assimilant Composition with {self.assimilant.percentages[phase-1]}% total uptake:", right_col=['wt%']*1, max_cols=10, title_level=10, level=13)
        # Mineral compositions (and implied usage)
        nice_display(cotectics, self.meta.minerals_, self.namespace.oxides, title=f"> Custom Mineralogy for {self.namespace.phase_transitions[phase-1]}:", right_col=['wt%']*cotectics.shape[0], title_level=10, level=13)
        # Magma compositions
        comp_arr = np.vstack( (comp_arr, result_p3.flatten()) )
        nice_display(comp_arr, ['Initial', 'Expected', 'Computed'], self.namespace.oxides, title=f"> Initial, Expected, and Computed Compositions for Phase {phase}:", right_col=['wt%']*comp_arr.shape[0], title_level=10, level=13)

        # Optimised parameters
        if opt_result is not None:
            nice_display(
                np.vstack( (np.asarray(opt_result.x), params) ),
                ['Raw Optimised', 'Normalised'],
                ['FC%'] + self.meta.minerals_,
                title=f"> Optimised Parameters for Phase Transition {self.namespace.phase_transitions[phase-1]}:", title_level=10, level=13
            )
        else:
            nice_display(
                params.reshape(1, -1),
                ['Provided'],
                ['FC%'] + self.meta.minerals_,
                title=f"> Provided Parameters for Phase Transition {self.namespace.phase_transitions[phase-1]}:", title_level=10, level=13
            )
        log_meta("", level=12)

        # Save results back to self
        self.magma.computed[phase, :8] = result_p3.flatten()

        # Store results in a PhaseResult dataclass for this phase
        self.results[phase-1].cotectics = cotectics
        self.results[phase-1].cost = compute_cost(result_p3, exp_comp).item()
        self.results[phase-1].usage = self.minerals.usage[phase-1, [self.namespace.minerals.index(mineral) for mineral in self.meta.minerals_]].astype(bool)
        self.results[phase-1].opt_result = opt_result
        self.results[phase-1].weights = params[1:] if opt_result is not None else params[1:]
        self.results[phase-1].F = params[0] if opt_result is not None else params[0]

        # Create a tidy set of % and wt.% values
        solution = np.concatenate((self.results[phase-1].F.reshape(1,), self.results[phase-1].weights))
        solution[0] = int(100 * solution[0])  # Convert FC% to integer percentage
        solution[1:] = np.round(100 * solution[1:], 3)  # Convert weights to wt.% and round to 3 decimal places
        # Convert to a dict of floats and drop any exact 0s
        solution = {k: float(v) for k, v in zip(['FC%'] + self.meta.minerals_, solution) if v != 0.0}

        self.results[phase-1].solution = solution
        self.results[phase-1].melt_evolution = result.copy()
        self.results[phase-1].olivine_composition = olivine_comp.copy()
        self.results[phase-1].bulk_mineralogy = np.average(
            np.nan_to_num(cotectics),
            axis=0, 
            weights=params[1:]
        )

        self.results[phase-1].name = self.namespace.phase_transitions[phase-1]
        self.results[phase-1].isrun = True
        self.results[phase-1].minerals = self.meta.minerals_
        self.results[phase-1].trace_minerals = self.meta.minerals_ + self.namespace.accessory_minerals

        # Update the total mineral contributions and melt/solid evolution up to this phase
        self.crystallisation_dict = self.calculate_mineral_proportions(phase-1)

    def runTraces(self, phase, accessory_weights=np.zeros(4)) -> None:
        """
        Building on an existing run of a phase where mineral abundances and fractional crystallisation have been optimised or specified, this function computes the trace element evolution for that phase. It uses those prior mineral abundances and fractional crystallisation values along with the provided accessory mineral weights (accessory_weights) of accessory minerals to compute the trace element evolution.

        See the online documentation for more details on the workings of this function.

        Parameters
        ----------
        phase : int
            The phase number to compute the trace element evolution for. Must be between 1 and 5, inclusive.
        accessory_weights : array-like of shape (4,), optional
            An array or list of 4 floats representing the weight percent of each accessory mineral in the order: apatite, zircon, monazite, allanite. The values should be between 0 and 100. If not provided, it defaults to an array of zeros, meaning no accessory minerals are considered in the trace element computation.

        Notes
        -----
        - If a total of 5 wt.% of accessory minerals is specified, the function will normalise the weights of accessory and non-accessory minerals to sum to 100 wt.% before computing the trace element evolution.

        Examples
        --------
        To compute the trace element evolution for phase 3 with 2 wt.% apatite, 1 wt.% zircon, 1 wt.% monazite, and 1 wt.% allanite:

        >>> model.runTraces(phase=3, accessory_weights=[2, 1, 1, 1])
        """
        log_meta(f"[Traces] {self.namespace.phase_transitions[phase-1]}", level=7)

        # Convert from 0 - 100 to 0 - 1
        Wacc = np.asarray(accessory_weights, dtype=np.float64) / 100.0

        phase_idx = phase - 1 # 0-indexed

        # Ensure Wacc is a 1D bool-like array of length 4
        if not isinstance(Wacc, (list, np.ndarray)) or len(Wacc) != 4:
            raise ValueError(f"Wacc must be a list or numpy array of length 4. Received: {Wacc}")
        Wacc = np.asarray(Wacc)

        run_phases = [p for p in range(5) if self.results[p].isrun]
        if phase_idx < 0 or phase_idx >= 5:
            raise ValueError(f"Phase must be between 1 and 5, inclusive. Received: {phase}")
        if phase_idx not in run_phases:
            raise ValueError(f"Phase {phase} ({self.namespace.phase_transitions[phase_idx]}) has not been run yet. Please run the phase using `model.run({phase})` first before computing traces.")

        # TODO: Vaildation & error handling

        phase_name = self.namespace.phases[phase_idx]
        F = int(100 * self.results[phase_idx].F)

        # Load best-fit cotectics
        M_main = self.results[phase_idx].cotectics.copy()  # Main mineral compositions for the first phase
        # Zero the olivine composition to force recomputation during optimisation
        M_main[0] = 0
        accessory_geochem = self.namespace.oxides + ['P','Zr','La','Ce','Nd','Th','Y']
        target_indices = [self.namespace.geochem.index(t) for t in accessory_geochem]
        # Create a 4x32 matrix filled with zeros
        M_acc = np.zeros((4, 32), dtype=np.float64)
        M_acc_raw = np.array([
            [0, 0, 0, 0, 0, 55, 0, 0, 196470, 0, 0, 0, 0, 0, 0],
            [35, 0, 0, 0, 0, 0, 0, 0, 0, 481000, 0, 0, 0, 0, 0],
            [30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 170535.8787, 298817.9381, 85734.66476, 43940.31207, 0],
            [30, 0, 18, 10, 0, 12, 0, 0, 0, 0, 85267.93935, 85376.55374, 42867.33238, 0, 39372.06625],
        ], dtype=np.float64)
        # Slot the columns into their designated positions across all rows
        M_acc[:, target_indices] = M_acc_raw
        # Pad both to 32 elements with 0s
        M_main = np.pad(M_main, ((0, 0), (0, 32 - M_main.shape[1])), mode='constant', constant_values=0)
        M = np.vstack((M_main, M_acc))

        # Extract the parent, expected daughter and assimilants
        parent = self.magma.traces[phase_idx].copy()
        daughter = self.magma.initial[phase_idx + 1].copy()
        assimilant = self.assimilant.composition.copy()
        a = self.assimilant.percentages[phase_idx]

        # Check structurals and drop any with NaN values - this way we only optimise for the major oxides and traces that we need to - i.e. reducing the compelxity of forward modelling and components of the cost function
        parent_structural, daughter_structural, assimilant_structural, M_structural, idx_structurals, idx_non_structurals = self._check_structurals(Wacc, parent, daughter, assimilant, M)

        # Now run but appending trace elements to compositions and using updated mineral weights
        f = self.results[phase_idx].F
        weights = self.results[phase_idx].weights
        # Correct weights so that [weights] + [Wacc] = 1.0
        old_total = np.sum(weights)
        acc_total = np.sum(Wacc)
        diff = old_total - acc_total
        new_weights = weights * (diff)

        params = np.concatenate([np.array([f]), new_weights, Wacc])

        result_p3, result, olivine_comp = compute_phase_evolution_batch(params.reshape(1, -1), parent_structural, M_structural, assimilant_structural, a, self.constants.Fe2O3_FeO_Ratio, self.meta.FeO_Fe2pO_Ratio, self.constants.molecular_weights)

        result_p3 = result_p3[0]  # Extract the first (and only) result from the returned array

        daughter_computed = np.full(32, dtype=np.float64, fill_value=np.nan)
        daughter_computed[idx_structurals] = result_p3.copy()

        # Compute the rest by KDs
        KDs = self.minerals.trace_KDs[phase_idx].copy()

        # Extract only minerals (axis=0) which are in model.meta.minerals_
        KDs = KDs[[i for i, mineral in enumerate(self.namespace.minerals + self.namespace.accessory_minerals) if mineral in self.meta.minerals_ or mineral in self.namespace.accessory_minerals], :]
        W = params[1:] * 100

        # Apply mineral weights to get the bulk KDs
        B = (W.reshape(1, -1)/100 @ KDs)[0]

        Ci = parent
        A = assimilant

        Z = (a + (B-1)) / (a-1)
        f = 1 - F/100
        # Temporarily silence division by zero and invalid operation warnings for when Ci is zero - we are happy for it to go to nan
        with np.errstate(divide='ignore', invalid='ignore'):
            res = Ci * (np.power(f, -Z) + (a/(a-1) * (A/(Ci)) * (1-np.power(f, -Z)) ) )

        # Keep only non-structural elements [~idx]
        res[idx_structurals] = np.nan

        prev_ans = daughter_computed.copy()
        daughter_computed[idx_non_structurals] = np.delete(res, idx_structurals)

        self.magma.traces[phase_idx+1] = daughter_computed.copy()  # Store the parent composition for this phase
        self.trace_results[phase-1].isrun = True

        log_meta(f"Config and results:", level=9)
        nice_display(Wacc.reshape(1, -1), [self.namespace.phase_transitions[phase_idx]], self.namespace.accessory_minerals, title=f"Accessory Mineral Usage:", title_level=10, level=13, boolean=False)

        nice_display(assimilant.reshape(1, -1), ['Assimilant Composition'], self.namespace.geochem, title=f"Assimilant Composition with {a}% total uptake:", right_col=['wt%']*1, max_cols=10, title_level=10, level=13)

        structural_names = [self.namespace.geochem[i] for i in idx_structurals]
        nice_display(M_structural.T, structural_names, self.meta.minerals_ + self.namespace.accessory_minerals, title=f"> Custom Mineralogy for {self.namespace.phase_transitions[phase-1]}:", right_col=['wt%']*8 + ['ppm']*(len(structural_names)-8), title_level=10, level=13)
        comp_arr = np.vstack( (parent, daughter, daughter_computed, prev_ans, res) )
        nice_display(comp_arr.T, self.namespace.geochem, ['Initial', 'Expected', 'Computed', '  (melt)', '  (KDs)'], title=f"> Initial, Expected, and Computed Compositions for Phase {phase}:", right_col=['wt%']*8 + ['ppm']*24, title_level=10, level=13)

        log_meta("", level=12)

        # Assign the final olivine composition that's not all 0s to the cotectics
        #  but now with zero padding for structurals
        zero_mask = np.all(olivine_comp == 0, axis=1)
        max_false = np.max(np.where(~zero_mask)[0]) if np.any(~zero_mask) else None

        if max_false is not None:
            olivine_toadd = np.pad(olivine_comp[max_false], (0, M_structural.shape[1] - olivine_comp.shape[1]), mode='constant', constant_values=0)
        else:
            olivine_toadd = np.zeros(M_structural.shape[1])
        M_structural[0, :] = olivine_toadd

        # Store results in a PhaseResult dataclass for this phase
        self.trace_results[phase-1].cotectics = M_structural
        Waccusage = Wacc > 0
        self.trace_results[phase-1].usage = np.concatenate((self.results[phase-1].usage, Waccusage)).astype(bool)
        self.trace_results[phase-1].weights = params[1:]
        self.trace_results[phase-1].F = params[0]
        self.trace_results[phase-1].structurals = structural_names
        self.trace_results[phase-1].melt_evolution = result.copy()
        self.trace_results[phase-1].olivine_composition = olivine_comp.copy()
        self.trace_results[phase-1].bulk_mineralogy = np.average( 
            np.nan_to_num(M_structural),
            axis=0, 
            weights=params[1:]
        )

        # Update the total mineral contributions and melt/solid evolution up to this phase
        self.crystallisation_dict = self.calculate_mineral_proportions(phase-1)

    def savePDF(self, filepath=None) -> None:
        """
        Compiles and saves all model data to a PDF file for interpretation.

        Parameters
        ----------
        filepath : str, optional
            Full path of the output .pdf file. Defaults to None which will generate a timestamped name in the current working directory.
        """
        from hades.export import compile_pdf

        if filepath is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"./Hades_Report_{timestamp}.pdf"

        if not os.path.exists(os.path.dirname(filepath)):
            print(f"Warning: Not saving PDF as directory does not exist: {os.path.dirname(filepath)}")
            return

        compile_pdf(self, filepath)

    def saveData(self, filepath=None) -> None:
        """
        Compiles and saves all model data to an Excel file.

        Parameters
        ----------
        filepath : str, optional
            Full path of the output .xlsx file. Defaults to None which will generate a timestamped name in the current working directory.
        """
        from hades.export import compile_excel

        if filepath is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"./Hades_Data_{timestamp}.xlsx"

        if not os.path.exists(os.path.dirname(filepath)):
            print(f"Warning: Not saving data as directory does not exist: {os.path.dirname(filepath)}")
            return

        compile_excel(self, filepath)

    # %% ---- Helper Functions ---- 
    
    def calculate_mineral_proportions(self, phase):
        """
        For a set of mineral proportions (arr) and a set of fractional crystallisation stages (Fs), this function calculates the absolute solid formed per stage (ΔS), the remaining liquid fraction, and the total crystallised amount of each mineral.

        Parameters
        ----------
        arr : array_like
            A 2D array where each row corresponds to a stage and each column corresponds to a mineral. Each entry represents the proportion of that mineral at that stage.
        Fs : tuple of float
            A tuple representing the fractional crystallisation percentages for each stage. 

        Returns
        -------
        dict
            A dictionary containing:
            - 'delta_S': The absolute solid formed per stage (ΔS).
            - 'remaining': The remaining liquid fraction after all stages.
            - 'total_minerals': The total crystallised amount of each mineral.
            - 'total_minerals_norm': The normalised total crystallised amount of each mineral.
            - 'total_minerals_wt': The total crystallised amount of each mineral expressed in weight percent.
        """

        # Check if any trace element analyses were run
        tracesRun = any([self.trace_results[i].isrun for i in range(5)])

        if tracesRun:
            results_ = self.trace_results
            print("Trace element analyses were run. Using trace results for mineral proportions.")
        else:
            results_ = self.results

        # First, compile the arrays of completed stages
        run_stages = [i for i in range(5) if results_[i].isrun and i <= phase]
        arr = np.vstack([results_[i].weights for i in run_stages])
        f = np.array([results_[i].F for i in run_stages])

        remaining = 1.0
        delta_S = np.zeros(len(f))

        for i, fi in enumerate(f):
            delta_S[i] = fi * remaining
            remaining *= 1 - fi

        total_minerals = delta_S @ arr
        total_minerals_norm = total_minerals / total_minerals.sum()
        total_minerals_wt = total_minerals_norm * 100

        return {
            "delta_S": delta_S,
            "remaining": remaining,
            "total_minerals": total_minerals,
            "total_minerals_norm": total_minerals_norm,
            "total_minerals_wt": total_minerals_wt,
        }

    def _check_structurals(self, Wacc, parent, daughter, assimilant, M) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list, list]:
        """
        Helper function to check which elements are structurals based on the Wacc flags and the geochemical data. It returns the cropped arrays for structurals and the indices of structural and non-structural elements in the geochem array.

        Parameters
        ----------
        Wacc : array-like of shape (4,)
            An array or list of 4 floats representing the weight percent of each accessory mineral in the order: apatite, zircon, monazite, allanite. The values should be between 0 and 1.
        parent : array-like of shape (32,)
            An array or list of 32 floats representing the weight percent of each oxide in the parent melt composition. 
        daughter : array-like of shape (32,)    
            An array or list of 32 floats representing the weight percent of each oxide in the daughter melt composition.
        assimilant : array-like of shape (32,)
            An array or list of 32 floats representing the weight percent of each oxide in the assimilant composition.
        M : array-like of shape (N, 32)
            A 2D array or list of shape (N, 32) representing the mineral compositions for the N minerals in the model.

        Returns
        -------
        parent_struct : np.ndarray of shape (M,)
            A 1D numpy array containing the weight percent of each structural oxide in the parent melt composition, where M is the number of structural elements.
        daughter_struct : np.ndarray of shape (M,)
            A 1D numpy array containing the weight percent of each structural oxide in the daughter melt composition, where M is the number of structural elements.
        assimilant_struct : np.ndarray of shape (M,)
            A 1D numpy array containing the weight percent of each structural oxide in the assimilant composition, where M is the number of structural elements.
        M_struct : np.ndarray of shape (N, M)   
            A 2D numpy array containing the mineral compositions for the N minerals in the model, but only for the M structural elements.
        idx_structurals : list of int
            A list of indices corresponding to the positions of structural elements in the original geochem array.
        idx_non_structurals : list of int
            A list of indices corresponding to the positions of non-structural elements in the original geochem array.
        """
        # Map Wacc flags to conditional elements
        Waccelements = {
            0: ["P"],
            1: ["Zr"],
            2: ["La", "Ce", "Nd", "Th"],
            3: ["La", "Ce", "Nd", "Y"],
        }

        # Build ordered unique list of structurals
        structurals = list(self.namespace.oxides)
        for idx, flag in enumerate(Wacc):
            if flag != 0:
                structurals.extend(Waccelements.get(idx, []))

        # Remove duplicates preserving order
        structurals = list(dict.fromkeys(structurals))
        structural_set = set(structurals)

        # Partition geochem indices into structural vs non-structural
        geochem = self.namespace.geochem
        idx_structurals = [i for i, ox in enumerate(geochem) if ox in structural_set]
        idx_non_structurals = [i for i, ox in enumerate(geochem) if ox not in structural_set]

        # Crop input arrays to structural elements
        parent_struct = parent[idx_structurals]
        daughter_struct = daughter[idx_structurals]
        assimilant_struct = assimilant[idx_structurals]
        M_struct = M[:, idx_structurals]

        # Replace 0s with NaN to avoid misleading calculations
        parent_struct[parent_struct == 0] = np.nan
        daughter_struct[daughter_struct == 0] = np.nan

        # Identify NaNs in parent/daughter compositions
        nan_parent = np.isnan(parent_struct)
        nan_daughter = np.isnan(daughter_struct)
        has_nan = nan_parent | nan_daughter

        # Logging warnings for invalid elements
        if np.any(nan_parent):
            invalid_p = [structurals[i] for i in np.where(nan_parent)[0]]
            print(f"  # Warning: Trace elements {invalid_p} have NaN values in initial melt. Ignoring.")

        if np.any(nan_daughter):
            invalid_d = [structurals[i] for i in np.where(nan_daughter)[0]]
            print(f"  # Warning: Trace elements {invalid_d} have NaN values in daughter melt. Using Kd instead.")

        # Filter out NaN elements using boolean mask (~has_nan)
        if np.any(has_nan):
            dropped_indices = np.where(has_nan)[0]
            print(f"  # Dropping structurals at positions {dropped_indices} due to NaNs.")

            # Move dropped indices from structural to non-structural list
            dropped_geochem_indices = [idx_structurals[i] for i in dropped_indices]
            idx_non_structurals.extend(dropped_geochem_indices)

            # Keep valid entries
            valid_mask = ~has_nan
            parent_struct = parent_struct[valid_mask]
            daughter_struct = daughter_struct[valid_mask]
            assimilant_struct = assimilant_struct[valid_mask]
            M_struct = M_struct[:, valid_mask]

            # Update tracking lists
            idx_structurals = [idx for i, idx in enumerate(idx_structurals) if valid_mask[i]]
            structurals = [ox for i, ox in enumerate(structurals) if valid_mask[i]]

        # Ensure indices are sorted for consistency
        idx_structurals.sort()
        idx_non_structurals.sort()

        return (
            parent_struct,
            daughter_struct,
            assimilant_struct,
            M_struct,
            idx_structurals,
            idx_non_structurals,
        )

    def _compile_mineral_bank(self, phase, params, init_comp) -> tuple[np.ndarray, np.ndarray]:
        """
        Helper function which uses the mineral banks, any provided custom mineralogies, mineral usage array, whole-rock ratios and the initial magma composition to find the mineral composition to be used for this phase. Returns 'cotectics', a (Nmins, Noxides) array of the mineral compositions for this phase and mode.

        Parameters
        ----------
        phase : int
            The phase number to compute the mineral compositions for. Must be between 1 and 5, inclusive.
        params : array-like of shape (N,)
            An array or list of floats representing the parameters for the phase transition. The first element is the fractional crystallisation percentage (FC%), and the remaining elements are the weights of each mineral in the order specified by self.meta.minerals_.
        init_comp : array-like of shape (8,)
            An array or list of 8 floats representing the initial composition of the magma for this phase, corresponding to the oxides in self.namespace.oxides.

        Returns
        -------
        cotectics : np.ndarray of shape (Nmins, Noxides)
            A 2D numpy array containing the mineral compositions for this phase and mode, where Nmins is the number of minerals and Noxides is the number of oxides (8).
        params : np.ndarray of shape (N,)
            A 1D numpy array containing the parameters for the phase transition, where the first element is the fractional crystallisation percentage (FC%), and the remaining elements are the weights of each mineral in the order specified by self.meta.minerals_.
        """
        
        # First, use the whole-rock ratios to find the mineral composition from each mineral bank, depending on the initial composition
        # Extract KD values 
        plag_kd, Cpx_kd, Opx_kd, Amph_kd, kf_kd, biot_kd, alkcpx_kd, neph_kd, leuc_kd, nose_kd, alkamph_kd = self.minerals.KD_vals[phase-1]

        # Compute the whole-rock partitioning ratios for each mineral depending on which oxides it incorporates
        plag_CaNa = plag_kd * ((init_comp[5] / 56.1) / (2 * (init_comp[6] / 62)))
        cpx_FeMg = Cpx_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))
        opx_FeMg = Opx_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))
        amph_FeMg = Amph_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))
        kfeld_KNa = kf_kd * (2 * init_comp[7] / 94.2) / (2 * init_comp[6] / 62)
        biot_FeMg = biot_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))
        alk_cpx_WR = alkcpx_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))
        neph_WR = neph_kd * ((init_comp[5] / 56.1) / (2 * (init_comp[6] / 62)))
        leuc_WR = leuc_kd * (2 * init_comp[7] / 94.2) / (2 * init_comp[6] / 62)
        nose_WR = nose_kd * (2 * ((init_comp[5] / 56.1) + (init_comp[7] / 94.2))) / (2 * init_comp[6] / 62)
        alkamph_WR = alkamph_kd * (((init_comp[3] * 0.8998) / 71.846) / (init_comp[4] / 40.311))

        # Mineral Bank Lookups
        # Depending on the mode being used, use the provided (fixed) mineral composition or find the cotectic compositions through KD-based batch lookups for the relevant minerals and their mineral banks
        # cotectics is of shape (No. candidates, No. minerals, 8 oxides)
        if self.meta.mode == 'subalkaline':
            cotectics = np.zeros(( 11, 8))
            # cotectics[ 0, :] = self.minerals.banks['olivine'].data  # shape (N, 8)
            cotectics[ 1, :] = self.minerals.banks['spinel'].data[:,0]
            cotectics[ 2, :] = lookup_mineral_bank_cotectic(cpx_FeMg, self.minerals.banks['clinopyroxene'].data)
            cotectics[ 3, :] = lookup_mineral_bank_cotectic(opx_FeMg, self.minerals.banks['orthopyroxene'].data)
            cotectics[ 4, :] = lookup_mineral_bank_cotectic(plag_CaNa, self.minerals.banks['plagioclase'].data)
            cotectics[ 5, :] = lookup_mineral_bank_cotectic(amph_FeMg, self.minerals.banks['amphibole'].data)
            cotectics[ 6, :] = lookup_mineral_bank_cotectic(kfeld_KNa, self.minerals.banks['kfeldspar'].data)
            cotectics[ 7, :] = lookup_mineral_bank_cotectic(biot_FeMg, self.minerals.banks['biotite'].data)
            cotectics[ 8, :] = self.minerals.banks['quartz'].data[:,0]
            cotectics[ 9, :] = self.minerals.banks['magnetite'].data[:,0]
            cotectics[ 10, :] = self.minerals.banks['ilmenite'].data[:,0]
        else:  # alkaline
            cotectics = np.zeros((12, 8))
            # cotectics[0, :] = self.minerals.banks['olivine'].data
            cotectics[1, :] = self.minerals.banks['spinel'].data[:,0]
            cotectics[2, :] = lookup_mineral_bank_cotectic(plag_CaNa, self.minerals.banks['plagioclase'].data)
            cotectics[3, :] = lookup_mineral_bank_cotectic(kfeld_KNa, self.minerals.banks['kfeldspar'].data)
            cotectics[4, :] = lookup_mineral_bank_cotectic(biot_FeMg, self.minerals.banks['biotite'].data)
            cotectics[5, :] = self.minerals.banks['magnetite'].data[:,0]
            cotectics[6, :] = self.minerals.banks['ilmenite'].data[:,0]
            cotectics[7, :] = lookup_mineral_bank_cotectic(alk_cpx_WR, self.minerals.banks['titanaugite'].data)
            cotectics[8, :] = lookup_mineral_bank_cotectic(neph_WR, self.minerals.banks['nepheline'].data)
            cotectics[9, :] = lookup_mineral_bank_cotectic(leuc_WR, self.minerals.banks['leucite'].data)
            cotectics[10, :] = lookup_mineral_bank_cotectic(nose_WR, self.minerals.banks['nosean_hauyne'].data)
            cotectics[11, :] = lookup_mineral_bank_cotectic(alkamph_WR, self.minerals.banks['alkali_amphibole'].data)

        log_meta(f"Assigning mineral compositions", level=8)

        # Overwrite with any custom mineralogies - compositions will be nan if not used
        for i, mineral in enumerate(self.meta.minerals_):
            default_ = True

            if not np.isnan(self.minerals.custom_mineralogies[phase-1, self.namespace.minerals.index(mineral)]).all():
                cotectics[i, :] = self.minerals.custom_mineralogies[phase-1, self.namespace.minerals.index(mineral)]
                log_meta(f"{mineral:<16} '[custom]'", level=14)
                default_ = False

            # Also, if the mineral is not used in this phase, set its composition to NaN (later 0) and the bounds also to [0, 0] - this will ensure it is not used in the optimisation, and doubly-sure that if it is erroneously used somehow, it will be zeroed out
            if not self.minerals.usage[phase-1, self.namespace.minerals.index(mineral)]:
                log_meta(f"{mineral:<16} not used - setting composition to NaN and bounds to [0, 0].", level=14)
                cotectics[i, :] = np.nan
                # Set bounds and mineral weight
                self.optimising.bounds[i+1] = [0, 0]
                if params is not None:
                    params[i+1] = 0.0
                default_ = False

            if default_:
                log_meta(f"{mineral:<16} [default]", level=14)

        # Force normalise the cotectics to 100 wt% for each mineral, ignoring any NaNs (which will be set to 0 later)
        for i in range(cotectics.shape[0]):
            if not np.isnan(cotectics[i, :]).all():
                total = np.nansum(cotectics[i, :])
                if total > 0:
                    cotectics[i, :] = (cotectics[i, :] / total) * 100
                else:
                    # log_warning(f"  > Mineral '{self.meta.minerals_[i]}' in phase {phase} has a total composition of 0. Setting to NaN.")
                    cotectics[i, :] = np.nan

        # Convert all nans to zeros
        cotectics = np.nan_to_num(cotectics, nan=0.0)
        
        return cotectics, params

    def _optimise(self, func, args, vectorized=True, x0=None) -> tuple[np.ndarray, "OptimizeResult"]:
        """
        Wrapper for scipy's differential_evolution function, using the parameters set in self.optimising. Returns the optimised parameters and the result object.

        Parameters
        ----------
        func : callable
            The objective function to be minimized. It should take a 1D array of parameters as input and return a scalar cost.
        args : tuple
            Additional arguments to pass to the objective function.
        vectorized : bool, optional
            If True, the objective function is assumed to be vectorized and can accept a 2D array of parameters. If False, the objective function is assumed to accept a 1D array of parameters. Defaults to True.
        x0 : array-like, optional
            An initial guess for the parameters. If provided, it should be a 1D array of the same length as the number of parameters. If None, the optimizer will generate its own initial population. Defaults to None.

        Returns
        -------
        opt_params : np.ndarray
            A 1D array containing the optimised parameters that minimize the objective function.
        result : OptimizeResult
            The result object returned by scipy's differential_evolution function, containing information about the optimisation process
        """
        from scipy.optimize import differential_evolution
        updating = 'deferred' if vectorized else 'immediate'

        result = differential_evolution(
            func,
            self.optimising.bounds,
            args=args,
            maxiter=self.optimising.max_iter,
            popsize=self.optimising.pop_size,
            tol=self.optimising.tol,
            strategy=self.optimising.strategy,
            mutation=self.optimising.mutation,
            recombination=self.optimising.recombination,
            init=self.optimising.init,
            x0=x0,
            workers=1,
            vectorized=vectorized,
            disp=False,
            updating=updating,
            polish=False,
        )
        log_meta(f"Optimisation completed", level=8)
        log_meta(f"cost = {result.fun:.2f}", level=14)
        log_meta(f"ran {result.nit}/{self.optimising.max_iter} iters", level=14)
        log_meta(f"{result.nfev} function evaluations", level=14)
        log_meta(f"population size = {self.optimising.pop_size}", level=14)
        log_meta(f"message: '{result.message}'", level=14)
        print(f"> Optimisation completed with cost = {result.fun:.2f} after {result.nit}/{self.optimising.max_iter} iters and {result.nfev} func. evals with population size {self.optimising.pop_size} because of: '{result.message}'")

        opt_params = result.x.copy()
        # Normalise the mineral compositions for each phase, 
        opt_params[1:] = list(np.array(opt_params[1:]/sum(opt_params[1:])))

        # Adjust the value of fractional crystallisation to still be between 0 and 1, but to reflect the actual value used by Hades (i.e. integer percentage)
        opt_params[0] = (opt_params[0] * 100).astype(np.int64) / 100

        # Return the optimised parameters and cost
        return [opt_params, result]
