# Building macOS Application (.app) and Disk Image (.dmg)

This guide outlines the process of packaging the `thechosen-downloader` application for macOS, including building a standalone `.app` bundle using PyInstaller and then creating a Disk Image (`.dmg`) for distribution using `create-dmg`.

## Key Considerations for Smaller Distribution Size

To significantly reduce the size of the final `.app` and `.dmg` files, Playwright's browser binaries are *not* bundled with the application. Users will need to install these separately. This dramatically cuts down the application's footprint from hundreds of megabytes to a few tens of megabytes.

## Prerequisites

1.  **`uv`**: Ensure `uv` is installed and configured for dependency management.
2.  **`ffmpeg`**: Install `ffmpeg` on your system.
    *   **macOS:** `brew install ffmpeg`
    *   **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
3.  **`create-dmg`**: Install `create-dmg` for creating `.dmg` files.
    *   **macOS:** `brew install create-dmg`

## Step-by-Step Guide

### 1. Prepare the Environment and Dependencies

Before building, ensure all project dependencies are installed in your development environment.

```bash
# Create and activate a virtual environment (if not already done)
uv venv
source .venv/bin/activate # or uv shell

# Install project dependencies
uv pip install -e ".[dev]"

# Install PyInstaller
uv pip install pyinstaller
```

### 2. Configure PyInstaller (The Spec File)

PyInstaller uses a `.spec` file to control the build process. A basic one can be generated, and then customized. The provided `TheChosenDownloader.spec` file has been configured for the `thechosen-downloader` project.

**`TheChosenDownloader.spec` (Key Sections):**

*   **`datas`**: This includes static files like `season1.json`. Crucially, it **excludes** Playwright browser binaries to keep the package small.
    ```python
datas = [('season1.json', '.')]
    ```
*   **`hiddenimports`**: Ensures that dynamically imported modules (like `playwright`) are included.
    ```python
hiddenimports = ['playwright']
    ```
*   **`collect_all('customtkinter')`**: This hook ensures all necessary files for `customtkinter` are included.
*   **`exe = EXE(...)`**: Defines the executable. `console=False` is used for a GUI application that doesn't show a terminal window.
*   **`app = BUNDLE(...)`**: Defines the macOS `.app` bundle. The `icon` and `bundle_identifier` are specified here. If no custom icon is provided, PyInstaller uses a default.

    ```python
    # Example excerpt from TheChosenDownloader.spec
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TheChosenDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to True for CLI-only application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='TheChosenDownloader.app',
    icon='assets/icon.icns', # Path to your .icns icon file
    bundle_identifier='com.hawk.thechosendownloader', # Unique identifier for your app
)
    ```

### 3. Build the macOS Application (`.app`)

Execute PyInstaller using the `.spec` file. This will create the `.app` bundle in the `dist` directory.

```bash
uv run pyinstaller TheChosenDownloader.spec --noconfirm
```

*   The `--noconfirm` flag prevents interactive prompts during the build process.
*   A folder named `TheChosenDownloader.app` will be created in the `dist/` directory.

### 4. Create the Disk Image (`.dmg`)

Once the `.app` bundle is successfully built, use `create-dmg` to package it into a user-friendly Disk Image.

```bash
create-dmg \
  --volname "The Chosen Downloader" \
  --window-pos 200 120 \
  --window-size 800 400 \
  "dist/The-Chosen-Downloader.dmg" \
  "dist/TheChosenDownloader.app"
```

*   `--volname`: Sets the name of the mounted volume (what users see in Finder).
*   `--window-pos` / `--window-size`: Configures the position and dimensions of the opened DMG window.
*   `"dist/The-Chosen-Downloader.dmg"`: The output path and filename for the `.dmg` file.
*   `"dist/TheChosenDownloader.app"`: The path to the `.app` bundle to include in the DMG.

    *(Optional: To add custom icons, background images, and a drag-and-drop link to Applications, you can include options like `--icon`, `--background`, and `--app-drop-link`. Refer to `create-dmg --help` for full details.)*

### 5. Post-Installation for Users

Since Playwright browsers are not bundled, users will need to install them manually after installing the application from the `.dmg`. The application itself (`src/thechosen_downloader/extractor.py`) has been modified to detect this and provide instructions.

Users should run the following command in their terminal:

```bash
uv run playwright install
```
This will download and set up the necessary browser binaries (Chromium, Firefox, WebKit) for Playwright to function.

## Result

Following these steps will produce a lightweight `.dmg` file (around 16MB) in the `dist/` directory, containing your `thechosen-downloader.app` application. The application will guide users through the necessary Playwright browser installation step, optimizing download size while maintaining functionality.
