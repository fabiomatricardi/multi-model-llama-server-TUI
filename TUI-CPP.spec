# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['tui_cpp.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'textual',
        'textual.app',
        'textual.containers',
        'textual.widgets',
        'textual.binding',
        'textual.reactive',
        'textual.geometry',
        'textual.css',
        'textual.dom',
        'textual.driver',
        'textual.drivers.windows_driver',
        'textual.drivers.win32',
        'textual._clipboard',
        'rich',
        'rich.console',
        'rich.markdown',
        'rich.syntax',
        'psutil',
        'typing_extensions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TUI-CPP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='llama.ico' if os.path.exists('llama.ico') else None,
)
