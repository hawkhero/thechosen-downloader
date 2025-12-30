# Build & Release Guide

This document explains how to build TheChosenDownloader macOS app and create a DMG installer.

## Prerequisites

- Python 3.12+ with uv
- PyInstaller (installed in venv)
- create-dmg (`brew install create-dmg`)

## Quick Build

```bash
# Build everything (app + DMG)
./release.sh
```

## Manual Build Steps

### 1. Build the .app Bundle

```bash
# Activate venv and run PyInstaller
source .venv/bin/activate
pyinstaller TheChosenDownloader.spec -y

# Or using uv
uv run pyinstaller TheChosenDownloader.spec --noconfirm
```

Output: `dist/TheChosenDownloader.app` (~177MB)

### 2. Create DMG Installer

```bash
create-dmg \
  --volname "The Chosen Downloader" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "TheChosenDownloader.app" 200 190 \
  --hide-extension "TheChosenDownloader.app" \
  --app-drop-link 600 185 \
  "dist/The-Chosen-Downloader.dmg" \
  "dist/TheChosenDownloader.app"
```

Output: `dist/The-Chosen-Downloader.dmg`

## PyInstaller Spec File

The `TheChosenDownloader.spec` configures the build:

```python
# Key settings:

# Hidden imports - modules not auto-detected
hiddenimports = ['playwright']

# Data files bundled with app
datas = [('season1.json', '.')]

# Onedir mode for fast startup (no extraction at runtime)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # Binaries go in COLLECT
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    ...
)

# macOS app bundle with Info.plist settings
app = BUNDLE(
    coll,
    name='TheChosenDownloader.app',
    bundle_identifier='com.hawk.thechosendownloader',
    info_plist={
        'LSBackgroundOnly': False,
        'LSUIElement': False,
        'NSPrincipalClass': 'NSApplication',
    },
)
```

## Build Modes Comparison

| Mode | Spec Change | Size | Startup | Use Case |
|------|-------------|------|---------|----------|
| Onefile | `a.binaries, a.datas` in EXE | 66MB | 10+ sec | Smaller download |
| Onedir | `exclude_binaries=True` + COLLECT | 177MB | ~2 sec | **Current (fast startup)** |

### Switch to Onefile Mode (if needed)

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Include binaries in EXE
    a.datas,     # Include data in EXE
    [],
    name='TheChosenDownloader',
    ...
)
# Remove COLLECT step
app = BUNDLE(
    exe,  # Use exe directly, not coll
    ...
)
```

## Troubleshooting

### Dock icon disappears during startup
- Ensure using onedir mode (not onefile)
- Check Info.plist has `LSBackgroundOnly: False` and `LSUIElement: False`

### season1.json not found
- File must be in `datas` list in spec: `datas = [('season1.json', '.')]`
- In code, check `sys._MEIPASS` for bundled path:
  ```python
  if hasattr(sys, '_MEIPASS'):
      path = Path(sys._MEIPASS) / 'season1.json'
  ```

### App doesn't launch GUI by default
- Check `cli.py` detects `sys.frozen` and defaults to `--gui` mode

### Build fails with missing module
- Add to `hiddenimports` in spec file
- Rebuild: `pyinstaller TheChosenDownloader.spec -y`

## Alternative: py2app (Experimental)

py2app produces smaller bundles (109MB vs 177MB) but has compatibility issues with modern setuptools.

```bash
# Must run from temp directory to avoid pyproject.toml conflicts
cd /tmp && mkdir py2app_build && cd py2app_build
cp /path/to/project/setup_py2app.py .
cp /path/to/project/season1.json .
source /path/to/project/.venv/bin/activate
python setup_py2app.py py2app
```

See `setup_py2app.py` for configuration.

## File Structure After Build

```
dist/
├── TheChosenDownloader.app/
│   └── Contents/
│       ├── MacOS/
│       │   └── TheChosenDownloader  # Main executable (~10MB)
│       ├── Frameworks/              # Python + libraries
│       ├── Resources/               # Data files, icons
│       └── Info.plist
└── The-Chosen-Downloader.dmg        # Installer
```
