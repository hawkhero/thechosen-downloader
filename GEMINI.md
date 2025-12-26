## Project Overview

This project, "The Chosen Downloader," is a Python-based tool for downloading episodes of the TV series "The Chosen" from its official streaming website. It provides both a command-line interface (CLI) and a graphical user interface (GUI) for ease of use.

The core functionality is built around `yt-dlp` for video downloading, with `playwright` and `BeautifulSoup` used to extract video stream URLs from the website. The project also features automatic caching of video URLs to speed up subsequent downloads, and it supports quality selection and subtitle downloading.

The GUI is built with `customtkinter`, providing a modern and user-friendly way to select and download episodes. The project is well-structured, with separate modules for the CLI, GUI, downloader, extractor, and cache management.

## Building and Running

### Setup

1.  **Install `uv`:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install `ffmpeg`:**
    *   **macOS:** `brew install ffmpeg`
    *   **Ubuntu/Debian:** `sudo apt-get install ffmpeg`

3.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    uv pip install -e ".[dev]"
    ```

4.  **Install Playwright Browsers:**
    Since Playwright browsers are not bundled with the application to keep the distribution size small, you need to install them separately:
    ```bash
    uv run playwright install
    ```
    This will install Chromium, Firefox, and WebKit. If you only need a specific browser, you can run `uv run playwright install chromium`, `uv run playwright install firefox`, or `uv run playwright install webkit`.

### Running the application

*   **CLI:**
    ```bash
    thechosen-downloader --help
    ```

*   **GUI:**
    ```bash
    thechosen-downloader --gui
    ```
    or
    ```bash
    thechosen-gui
    ```

### Running tests

```bash
pytest
```

## Development Conventions

*   **Dependency Management:** The project uses `uv` for package management, with dependencies defined in `pyproject.toml`.
*   **Code Structure:** The main application logic is located in the `src/thechosen_downloader` directory, with a clear separation of concerns between modules.
*   **Entry Points:** The project defines two console scripts in `pyproject.toml`: `thechosen-downloader` for the CLI and `thechosen-gui` for the GUI.
*   **Testing:** Tests are located in the `tests` directory and use `pytest`. The existing tests demonstrate a practice of using temporary directories for isolated test runs.
*   **Documentation:** The project includes a `README.md` file with detailed usage instructions and a `docs` directory with a GUI specification.

## Packaging

The macOS application is packaged using PyInstaller, resulting in a `.app` bundle and a `.dmg` installer. To keep the distribution size manageable, Playwright's browser binaries (which are hundreds of megabytes) are **not** bundled with the application.

Therefore, after installing the application, users must manually install the Playwright browsers by running the following command in their terminal:

```bash
uv run playwright install
```

This ensures the downloader functions correctly while maintaining a small initial download size for the application itself.