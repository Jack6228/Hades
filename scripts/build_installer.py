"""Script to build the Hades executable and Windows installer.

Uses PyInstaller to create a standalone executable from the Hades source code (hades.spec), and Inno Setup to package the executable into a Windows installer (HadesSetup.iss).

Example usage:

    python scripts/build_installer.py --iscc-path "path/to/ISCC.exe" --upx-dir "path/to/upx-5.0.2-win64/upx-5.0.2-win64"
"""

# Dependencies
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Base directory of the repository (1 level up from scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist" / "hades"
_INTERNAL_DIR = DIST_DIR / "_internal"

# Resolve repository relative files
SPEC_FILE = REPO_ROOT / "hades.spec"
ISS_FILE = REPO_ROOT / "HadesSetup.iss"

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the build script.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments with attributes:
        - iscc_path (str): Path to the Inno Setup Compiler executable.
        - upx_dir (str or None): Path to the UPX directory for compression (optional).
    """
    parser = argparse.ArgumentParser(description="Build Hades executable and installer")
    # Default to the standard install path (used by GitHub Actions)
    parser.add_argument(
        "--iscc-path", 
        type=str, 
        default=r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        help="Path to Inno Setup Compiler"
    )
    # Make UPX optional
    parser.add_argument(
        "--upx-dir", 
        type=str, 
        default=None,
        help="Path to UPX directory for compression"
    )
    return parser.parse_args()

def hashprint(msg: str) -> None:
    """
    Print a message with a hash border for emphasis.

    Parameters
    ----------
    msg : str
        The message to print.
    """
    border = "#" * (len(msg) + 4)
    print(f"\n{border}\n# {msg} #\n{border}\n")

def run_pyinstaller(upx_dir : str) -> None:
    """
    Run PyInstaller to build the Hades executable.

    Parameters
    ----------
    upx_dir : str
        Path to the UPX directory for compression (optional).
    """
    hashprint("Step 1: Running PyInstaller Build...")
    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--clean", "--noconfirm"]
    
    if upx_dir:
        hashprint(f"Using UPX compression from: {upx_dir}")
        cmd.extend(["--upx-dir", upx_dir])

    hashprint(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        hashprint("PyInstaller compilation failed!")
        sys.exit(1)
    hashprint("PyInstaller build complete.")


def purge_redundant_files() -> None:
    """
    Remove unnecessary files and directories from the _internal folder to reduce installer size.
    """
    hashprint("Step 2: Purging Redundant Artifacts from _internal...")

    targets_to_remove = [
        'alabaster',
        'babel',
        'docutils',
        'sphinx',
        'sphinxcontrib',
        'tzdata',
        'matplotlib/mpl-data/fonts/afm',
        'matplotlib/mpl-data/fonts/pdfcorefonts',
    ]

    targets = [_INTERNAL_DIR / target for target in targets_to_remove]

    if not _INTERNAL_DIR.exists():
        hashprint("Warning: _internal directory not found. Skipping purge. (Are you building in --onedir mode?)")
        return

    for path in targets:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    hashprint(f"Removed Folder: {path.relative_to(REPO_ROOT)}")
                else:
                    path.unlink()
                    hashprint(f"Removed File: {path.relative_to(REPO_ROOT)}")
            except Exception as e:
                hashprint(f"Could not remove {path}: {e}")
        else:
            hashprint(f"Already absent/skipped: {path.name}")


def compile_inno_setup(iscc_path : str) -> None:
    """
    Compile the Windows installer using Inno Setup.

    Parameters
    ----------
    iscc_path : str
        Path to the Inno Setup Compiler executable.
    """
    hashprint("Compiling Windows Installer via Inno Setup...")

    if not os.path.exists(iscc_path):
        hashprint(f"Inno Setup Compiler missing at expected path:\n   {iscc_path}\nPlease verify your Inno Setup installation directory or pass --iscc-path.")
        sys.exit(1)

    cmd = [iscc_path, str(ISS_FILE)]
    hashprint(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        hashprint("Inno Setup compilation failed!")
        sys.exit(1)
    hashprint("Windows Installer compilation completely successful!")


if __name__ == "__main__":
    args = parse_args()

    if len(sys.argv) == 1:
        print("No arguments provided. Using default paths for Inno Setup Compiler and UPX.")
        print(f"Default Inno Setup Compiler path: {args.iscc_path}")
        print(f"Default UPX directory: {args.upx_dir if args.upx_dir else 'None (no compression)'}")

    print("\n=== Hades Build Script ===")
    print(f"Using Inno Setup Compiler at: {args.iscc_path}")
    print(f"Using UPX directory at: {args.upx_dir if args.upx_dir else 'None (no compression)'}")
    print(f"Repository root: {REPO_ROOT}")
    print(f"Distribution directory: {DIST_DIR}")
    print(f"Internal directory: {_INTERNAL_DIR}")
    print(f"Spec file: {SPEC_FILE}")
    print(f"Inno Setup script: {ISS_FILE}")
    print(f"Python executable: {sys.executable}")
    print(f"=========================")

    # Ensure working directory consistency
    os.chdir(REPO_ROOT)

    run_pyinstaller(args.upx_dir)
    purge_redundant_files()
    compile_inno_setup(args.iscc_path)

