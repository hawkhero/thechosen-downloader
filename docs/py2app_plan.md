# py2app Packaging Plan (for macOS)

This document outlines the steps to package the `thechosen-downloader` application into a standalone macOS application bundle (`.app`) using `py2app`.

## Plan

1.  **Install `py2app`**: Add `py2app` to the project's development dependencies in `pyproject.toml` (e.g., `uv add py2app --dev`) and install it using `uv`.

2.  **Create `setup.py`**: Create a `setup.py` file in the project root for `py2app` configuration.

    ```python
    # setup.py example
    from setuptools import setup

    APP_NAME = "The Chosen Downloader"
    APP = ['src/thechosen_downloader/cli.py'] # Main entry point
    DATA_FILES = [] # To be populated with yt-dlp, playwright, and other assets
    OPTIONS = {
        'argv_emulation': True,
        'iconfile': 'path/to/icon.icns', # Optional: specify application icon
        'plist': {
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier': 'com.yourcompany.thechosendownloader',
            'NSHumanReadableCopyright': 'Copyright © 2023, Your Company, All Rights Reserved',
            # Add specific GUI-related keys if needed, e.g., LSUIElement for menubar apps
        },
        'packages': ['customtkinter', 'yt_dlp', 'playwright', 'bs4'], # Explicitly include key packages
        'includes': [], # For modules that py2app might miss
        'resources': [], # For additional files like season1.json
    }

    setup(
        app=APP,
        name=APP_NAME,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    ```

3.  **Configure `setup.py`**:
    *   **Entry Point**: Set `APP` to `['src/thechosen_downloader/cli.py']`. `py2app` will interpret arguments passed to the `.app` bundle, allowing for `--gui`.
    *   **Data Files (`DATA_FILES` and `resources`)**:
        *   Include `season1.json`.
        *   Include `yt-dlp`'s executable.
        *   **Handle `playwright`**: This is the most complex part. `playwright`'s browser binaries need to be bundled. This typically involves copying the entire `playwright` installation directory (or at least its browser binaries) into the `.app` bundle's `Contents/Resources` or similar location. The exact path will depend on where `uv` installs `playwright` and its browsers.
    *   **Packages (`packages`)**: Explicitly list all top-level packages used, such as `customtkinter`, `yt_dlp`, `playwright`, `bs4`, etc.
    *   **Options (`OPTIONS`)**:
        *   `argv_emulation`: Set to `True` to allow command-line arguments to be passed to the main script.
        *   `iconfile`: Point to an `.icns` icon file for the application.
        *   `plist`: Customize the `Info.plist` file within the `.app` bundle.

4.  **Build the App Bundle**:
    *   Run the `py2app` command from the terminal: `python setup.py py2app`.
    *   The `.app` bundle will be created in the `dist` directory.

5.  **Test the App Bundle**:
    *   Navigate to the `dist` directory and launch the generated `.app` bundle (e.g., `open "dist/The Chosen Downloader.app"`).
    *   Verify that both the GUI and CLI functionalities (by running the executable inside the bundle or using `open -a "The Chosen Downloader" --args --gui`) work correctly, including video downloading.

## Dependencies and Data Paths to Investigate

*   `yt-dlp` executable path.
*   `playwright` browser installation paths and how they are structured within the `uv` environment.
*   Path to `season1.json`.
*   Any other assets (images, fonts) used by `customtkinter` or the application itself.
*   Creating a `.icns` file for the application icon.