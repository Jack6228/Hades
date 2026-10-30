"""Logging utilities for Hades.

Provides a structured logging system for Hades, allowing for categorized messages, verbosity control, and log file management. The logger supports different levels of message importance and can output to both the console and a rotating log file.
"""

# Dependencies
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import platformdirs, warnings
from datetime import datetime

# %% ---- Constants & Setup ---- 

LEVEL_PREFIXES = {
    0:  "",        # Root / top-level message
    1:  "### ",    # Section titles / major steps
    2:  "##  ",    # Subsection
    3:  "• ",      # Main entries / key items
    4:  "  >> ",   # Sub-entries
    5:  "   >  ",  # Deeper sub-entries
    6:  " ┴ ",
    7:  "─┬─ ",     # Normal branch
    8:  " ├── ",     # Nested branch
    9:  " ├──┬─ ",   # Nested branch
    10: " │  ├── ",
    11: " └── ",     # Last at level 3
    12: " ┴  ┴ ",
    13: " │  │ ",
    14: " │     ",
    15: " │       ",
    16: " ├──┴─ ",
}
newline_prefixes = [1, 7]

# Create root logger
logger = logging.getLogger("hades")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Global flags
_logging_paused = False

# %% ---- Utilities ---- 

class CategoryFormatter(logging.Formatter):
    """
    Custom log record formatter supporting category tags and dynamic timestamps.

    Extends standard :class:`logging.Formatter` to construct log output dynamically based on custom attributes attached to a :class:`logging.LogRecord` (such as ``category`` and ``no_time``).

    Parameters
    ----------
    include_timestamp : bool, default=True
        If True, prefixes formatted log messages with a standard ISO-like timestamp (`YYYY-MM-DD HH:MM:SS`).

    Examples
    --------
    >>> import logging
    >>> logger = logging.getLogger("app")
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(CategoryFormatter(include_timestamp=True))
    >>> logger.addHandler(handler)
    >>> logger.info("Database connected", extra={"category": "DB"})
    2026-08-08 20:25:15 [DB] Database connected
    """

    def __init__(self, include_timestamp: bool = True) -> None:
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified log record into a formatted text string.

        Inspects the incoming log record for custom attributes:
        - ``no_time``: If True, returns only the raw message body.
        - ``category``: If present, wraps the category string in brackets ``[CATEGORY]``.

        Parameters
        ----------
        record : logging.LogRecord
            The log record instance containing log metadata and message content.

        Returns
        -------
        str
            The fully formatted log line ready for output handlers.
        """
        category = getattr(record, "category", "")
        no_time = getattr(record, "no_time", False)
        if no_time:
            return record.getMessage()
        tag = f"[{category}] " if category else ""
        time_str = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} " if self.include_timestamp else ""
        return f"{time_str}{tag}{record.getMessage()}"

def _ensure_initialised() -> None:
    """
    Auto-initialise logging with default configuration if unconfigured.

    Checks the root application logger for attached handlers. If no handlers are detected, automatically invokes :func:`setup_logger` to prevent unhandled logging errors or missing log records.
    """
    if not logger.handlers:
        setup_logger()

def cleanup_old_logs(log_dir: Path, max_keep: int = 5) -> None:
    """
    Deletes old session log files, keeping only the most recent ones.
    
    Parameters
    ----------
    log_dir : Path
        Directory where log files are stored.
    max_keep : int, default=5
        Maximum number of log files to retain. Older files beyond this count will be deleted.
        
    Notes
    -----
    Log files follow the naming convention: `hades_YYYY-MM-DD_HH-MM-SS.log`.
    """
    
    log_files = sorted(log_dir.glob("hades_*.log"), key=lambda p: p.stat().st_mtime)
    while len(log_files) >= max_keep:
        oldest = log_files.pop(0)
        try:
            oldest.unlink()
        except OSError:
            pass

# %% ---- Logging Setup ---- 

def setup_logger() -> None:
    """
    Initialises the Hades logging system with console and rotating file handlers.
    """
    global _logging_paused

    _logging_paused = False

    logger.setLevel(logging.DEBUG)

    # Check if already initialised by inspecting the singleton handlers
    existing_console = None
    existing_file = None

    for h in logger.handlers:
        if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler):
            existing_console = h
        elif isinstance(h, RotatingFileHandler):
            existing_file = h

    # If handlers exist and no explicit log_file override was passed, just adjust levels & exit
    if (existing_console or existing_file):
        if existing_console:
            existing_console.setLevel(logging.INFO)
        return

    # Clear old handlers if we are re-configuring with an explicit new log_file
    logger.handlers.clear()
    logger.propagate = False

    # Create Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CategoryFormatter(include_timestamp=False))
    logger.addHandler(console_handler)

    # Create File Handler
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = Path(platformdirs.user_log_dir(appname="Hades", appauthor=False))
    log_dir.mkdir(parents=True, exist_ok=True)
    resolved_log_path = log_dir / f"hades_{timestamp}.log"

    cleanup_old_logs(log_dir=resolved_log_path.parent, max_keep=5)

    # Create Rotating File Handler
    try:
        _file_handler = RotatingFileHandler(
            str(resolved_log_path),
            encoding="utf-8",
            mode="w"
        )
        _file_handler.setLevel(logging.DEBUG)
        _file_handler.setFormatter(CategoryFormatter(include_timestamp=True))
        logger.addHandler(_file_handler)
    except Exception as e:
        print(f"Failed to create log file at {resolved_log_path}: {e}", file=sys.stderr)

    # ASCII Header Art
    try:
        from .utils import get_asset_path
        with open(get_asset_path('hades.assets', 'ascii_art_hades.txt'), 'r', encoding='utf-8') as f:
            ascii_art = f.read()
        log_meta(f"\n\n{ascii_art}\n\n", no_time=True)
    except Exception:
        pass

# %% ---- Logging Utils ---- 

def pause_logging() -> None:
    """
    Pauses all logging output. Useful for temporarily suppressing log messages during sensitive operations.
    """
    global _logging_paused
    _logging_paused = True

def resume_logging() -> None:
    """
    Resumes logging output after a pause. Call this after `pause_logging()` to restore normal logging behavior.
    """
    global _logging_paused
    _logging_paused = False

def _emit_log(msg: str, level: int, log_level: int, category: str = "", no_time: bool = False) -> None:
    """
    Internal utility to emit a log message with the specified level and category.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int
        The hierarchical level of the message (used for prefixing).
    log_level : int
        The logging module level (e.g., logging.DEBUG, logging.INFO).
    category : str, optional
        A custom category tag to prefix the message with (default is empty).
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).
    """    
    if _logging_paused:
        return

    # Auto-initialise on first log call if setup_logger hasn't been called manually
    _ensure_initialised()

    # Apply level-based prefix to the message
    prefix = LEVEL_PREFIXES.get(level, "")
    if level in newline_prefixes:
        # Log empty line 
        logger.log(log_level, f"   ", extra={"category": category, "no_time": True})
    
    # Pass custom category to Formatter via extra dict
    logger.log(log_level, f"{prefix}{msg}", extra={"category": category, "no_time": no_time})

def log(msg: str, level: int = 0, no_time: bool = False) -> None:
    """
    Standard log message, also prints directly to the console for immediate feedback.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int, optional
        The hierarchical level of the message (used for prefixing, default is 0).   
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).
    """
    print(msg)  # Print to console
    _emit_log(msg, level, logging.DEBUG, category="LOG", no_time=no_time)

def log_meta(msg: str, level: int = 0, no_time: bool = False) -> None:
    """
    Meta-level log message ([META] prefix), used for high-level information or metadata.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int, optional
        The hierarchical level of the message (used for prefixing, default is 0).   
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).
    """
    _emit_log(msg, level, logging.DEBUG, category="LOG", no_time=no_time)

def log_debug(msg: str, level: int = 0, no_time: bool = False) -> None:
    """
    Debug message ([DBG] prefix), used for detailed internal state information.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int, optional
        The hierarchical level of the message (used for prefixing, default is 0).   
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).
    """
    _emit_log(msg, level, logging.DEBUG, category="DBG", no_time=no_time)

def log_gui(msg: str, level: int = 0, no_time: bool = False) -> None:
    """
    GUI message ([GUI] prefix), used for messages related to the graphical user interface.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int, optional
        The hierarchical level of the message (used for prefixing, default is 0).   
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).
    """
    _emit_log(msg, level, logging.DEBUG, category="GUI", no_time=no_time)

def log_warning(msg: str, level: int = 0, no_time: bool = False) -> None:
    """
    Warning message ([WRN] prefix), used for non-critical issues that may require attention.

    Parameters
    ----------
    msg : str
        The message to log.
    level : int, optional
        The hierarchical level of the message (used for prefixing, default is 0).   
    no_time : bool, optional
        If True, suppresses the timestamp in the log output (default is False).

    See Also
    --------
    :func:`warn` - A wrapper for `warnings.warn` that logs the warning message to the Hades logger and the console.
    """
    _emit_log(msg, level, logging.WARNING, category="WRN", no_time=no_time)
    
# %% ---- Custom Warning ---- 

# Don't print UserWarnings to the terminal - the custom `warn` function will auto print them
warnings.filterwarnings("ignore", category=UserWarning)

def warn(message, category=UserWarning, stacklevel=2) -> None:
    """
    `warnings.warn` wrapper that logs the warning message to the Hades logger and the console.

    Parameters
    ----------
    message : str
        The warning message to display.
    category : Warning, optional
        The warning category (default is UserWarning).
    stacklevel : int, optional
        The stack level to indicate where the warning originated (default is 2).
    """
    # This will trigger the normal warning system (prints to stderr by default)
    warnings.warn(message, category=category, stacklevel=stacklevel)
    # Log the warning message manually
    # print(f"{category.__name__}: {message}", file=sys.stderr)
    log_warning(message)