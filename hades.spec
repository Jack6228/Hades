# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Correctly mapping your assets based on the new structure:
# Format: (source_path_on_disk, destination_folder_inside_exe)
datas = [
    ('src/hades_plouton/assets', 'src/hades_plouton/assets'),
    ('src/hades/assets', 'src/hades/assets'),
] + collect_data_files('tkextrafont')

binaries = []

hiddenimports = [
    'scipy.spatial',
    'scipy.linalg',
    'scipy.special',
    'scipy.optimize',
    'scipy.fft',
    'scipy._lib',
    'openpyxl',
    'matplotlib.backends.backend_svg',
]

a = Analysis(
    ['src/hades_plouton/app.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        # (Source raw folder,  Destination inside Pyinstaller's _MEIPASS)
        ('src/hades/assets/*', 'hades/assets'),
        ('src/hades_plouton/assets/*', 'hades_plouton/assets'),
        # ('docs/_build/html', 'docs/_build/html'), # if including docs into the .exe build
        ('LICENSE', '.'),  # Include LICENSE in the root of the build
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'contourpy', 
        'python-dateutil', 
        'altgraph', 
        'setuptools',
        'tcl8',
        'charset_normalizer',
        '_tcl_data.tzdata',
        '_tk_data.images', 
        'scipy.stats',
        'scipy.signal',
        'scipy.io',
        'scipy.integrate',
        'scipy.interpolate',
        'scipy.cluster',
        'scipy.ndimage',
        'scipy.odr',
        'numba',
        'sphinx',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

splash = Splash(
    'src/hades_plouton/assets/HadesLogo_Dark_Text.png', # Path to your splash image
    binaries=a.binaries,
    datas=a.datas,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,                 # === 2. ADD SPLASH TO THE EXE TARGET ===
    splash.binaries,        # === 3. ADD SPLASH BINARIES TO THE EXE TARGET ===
    exclude_binaries=True,
    name='Hades',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # whether to show a console window or not
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src/hades_plouton/assets/hades_icon_dark.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,       # === 4. ADD SPLASH BINARIES TO THE COLLECT TARGET ===
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Hades',
)
