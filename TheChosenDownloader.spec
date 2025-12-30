# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

datas = [('season1.json', '.')]
binaries = [
    ('/usr/local/bin/ffmpeg', '.'),
    ('/usr/local/bin/ffprobe', '.'),
]
hiddenimports = ['playwright']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src/thechosen_downloader/cli.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Onedir mode: exe does NOT include binaries/datas (faster startup, no extraction)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # Binaries go in COLLECT, not in EXE
    name='TheChosenDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect all files into a directory (pre-extracted, instant startup)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TheChosenDownloader',
)

app = BUNDLE(
    coll,
    name='TheChosenDownloader.app',
    bundle_identifier='com.hawk.thechosendownloader',
    info_plist={
        'LSBackgroundOnly': False,  # Ensure app appears in dock
        'LSUIElement': False,       # Ensure app is not hidden
        'NSPrincipalClass': 'NSApplication',  # Standard macOS application
    },
)