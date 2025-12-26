# PyInstaller Packaging Plan

This document outlines the steps to package the `thechosen-downloader` application into a standalone executable using PyInstaller.

## Plan

1.  **Install PyInstaller**: Add `pyinstaller` to the project's development dependencies in `pyproject.toml` (e.g., `uv add pyinstaller --dev`) and install it using `uv`.

2.  **Create a Spec File**:
    *   Generate an initial spec file by running `pyinstaller --onefile --name thechosen-downloader src/thechosen_downloader/cli.py`. This will create `thechosen-downloader.spec` in the project root.
    *   **Customize the Spec File**: Modify the generated `.spec` file to address specific needs:
        *   **Entry Point**: Ensure `a.scripts` points to `src/thechosen_downloader/cli.py`.
        *   **Data Files**: Crucially, include necessary data files, especially for `yt-dlp` and `playwright`. This will involve adding entries to the `a.datas` list. For example, `('path/to/yt-dlp/binary', 'yt-dlp')` and directories for `playwright` browser binaries. The paths will need to be discovered.
        *   **Hidden Imports**: Add any modules that PyInstaller might miss, especially those used dynamically. This can be added to `a.hiddenimports`.
        *   **GUI Entry Point**: If packaging for GUI, ensure `src/thechosen_downloader/gui.py` is correctly handled as an entry point, potentially by adding a separate `EXE` definition or by launching it from the main CLI entry point.
        *   **Icon**: Specify an icon file if available (e.g., `icon='path/to/icon.icns'`).
        *   **Console/NoConsole**: For the GUI version, `console=False` should be used.

3.  **Handle `playwright`**:
    *   `playwright` requires its browser binaries to be present at runtime. The `.spec` file needs to include these. This usually involves copying the installed `playwright` browser directories into the build. The exact paths will need to be identified based on the `uv` environment.

4.  **Build the Executable**:
    *   Execute PyInstaller using the customized spec file: `pyinstaller thechosen-downloader.spec`.
    *   The executable will be generated in the `dist` directory.

5.  **Test the Executable**:
    *   Run the generated executable: `dist/thechosen-downloader`.
    *   Test both CLI functionality (e.g., `dist/thechosen-downloader --version`) and GUI functionality (e.g., `dist/thechosen-downloader --gui`).
    *   Verify that episodes can be selected and downloaded successfully, and that the GUI displays correctly.

## Dependencies and Data Paths to Investigate

*   `yt-dlp` executable path.
*   `playwright` browser installation paths (e.g., Chromium, Firefox, WebKit).
*   Any other assets (images, `season1.json`, etc.) used by the application that are not automatically included.