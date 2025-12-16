# GUI Interface Specification for The Chosen Downloader

## Overview

Add a graphical user interface (GUI) for the existing `thechosen-downloader` CLI tool, allowing users to easily select and download episodes from The Chosen Season 1.

## Requirements

| Requirement | Description |
|-------------|-------------|
| Episode Selection | Display 8 checkboxes for Season 1 episodes (loaded from `season1.json`) |
| Episode Info | Show episode number and title for each checkbox |
| Download Button | Trigger download of selected episodes |
| Path Selection | Allow user to choose download destination folder |
| Quality Selection | Dropdown for video quality (360p-2160p) |
| Subtitle Language | Dropdown for subtitle language selection |
| Cross-Platform | Support Windows and macOS |
| Language | English only |

## Data Source

Episodes loaded from built-in `season1.json`:
```json
{
  "season": 1,
  "episodes": [
    {"episode": 1, "title": "I Have Called You By Name", "video_url": "..."},
    {"episode": 2, "title": "Shabbat", "video_url": "..."},
    ...
  ]
}
```

## UI Mockup

```
+------------------------------------------------------------------+
|  The Chosen Downloader                                      [_][X]|
+------------------------------------------------------------------+
|                                                                  |
|  Season 1 - Select Episodes to Download:                        |
|  +------------------------------------------------------------+  |
|  |  [ ] 1. I Have Called You By Name                          |  |
|  |  [ ] 2. Shabbat                                            |  |
|  |  [ ] 3. Jesus Loves The Little Children                    |  |
|  |  [ ] 4. The Rock On Which It Is Built                      |  |
|  |  [ ] 5. The Wedding Gift                                   |  |
|  |  [ ] 6. Indescribable Compassion                           |  |
|  |  [ ] 7. Invitations                                        |  |
|  |  [ ] 8. I Am He                                            |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|  [Select All]  [Deselect All]                                    |
|                                                                  |
|  Download Location:                                              |
|  +----------------------------------------------+ [Browse...]    |
|  | /Users/hawk/Downloads                        |                |
|  +----------------------------------------------+                |
|                                                                  |
|  Quality:           [1080p               v]                      |
|  Subtitle Language: [Chinese (Taiwan)    v]                      |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |  Status: Ready                                             |  |
|  |  [                                              ] 0%       |  |
|  +------------------------------------------------------------+  |
|                                                                  |
|                                    [Download Selected Episodes]  |
|                                                                  |
+------------------------------------------------------------------+
```

## Technology Choice

**CustomTkinter** - Modern cross-platform Python GUI framework

Reasons:
- Modern, clean appearance (not dated like standard tkinter)
- Simple API, builds on tkinter knowledge
- Cross-platform (Windows, macOS, Linux)
- Lightweight single dependency
- MIT license (no licensing concerns)

## Implementation Plan

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/thechosen_downloader/gui.py` | Create | Main GUI application (~200 lines) |
| `pyproject.toml` | Modify | Add customtkinter dependency |
| `cli.py` | Modify | Add `--gui` flag to launch GUI |

### GUI Class Structure

```python
class TheChosenDownloaderGUI(ctk.CTk):
    def __init__(self):
        # Window setup (800x600)
        # Load episodes from season1.json

    def create_widgets(self):
        # Episode checkboxes (8 items)
        # Select All / Deselect All buttons
        # Path entry + Browse button
        # Quality dropdown (360p, 480p, 720p, 1080p, 2160p)
        # Subtitle language dropdown
        # Progress bar + status label
        # Download button

    def browse_folder(self):
        # Open native folder picker dialog

    def download_selected(self):
        # Get selected episodes
        # Start download in background thread
        # Update progress bar
```

### Subtitle Language Options

| Code | Display Name |
|------|--------------|
| zh-TW | Chinese (Taiwan) |
| zh-CN | Chinese (Simplified) |
| en | English |
| es | Spanish |
| pt | Portuguese |
| ko | Korean |
| ja | Japanese |

### Download Integration

Reuse existing `VideoDownloader` class:
```python
from thechosen_downloader.downloader import VideoDownloader

downloader = VideoDownloader()
downloader.download(
    url=episode["video_url"],
    output_path=f"{download_path}/S01E{ep_num:02d} - {title}.mp4",
    quality=selected_quality,
    subtitles=True,
    subtitle_lang=selected_lang
)
```

### Threading Model

```
Main Thread (GUI)          Background Thread (Download)
     |                              |
     |-- Start Download ----------->|
     |                              |-- Download Episode 1
     |<-- Progress Update ---------|
     |                              |-- Download Episode 2
     |<-- Progress Update ---------|
     |                              |...
     |<-- Complete ----------------|
```

## Implementation Steps

1. Add `customtkinter>=5.2.0` to `pyproject.toml` dependencies
2. Create `src/thechosen_downloader/gui.py`:
   - Load episodes from `season1.json`
   - Build episode checkbox list with titles
   - Add folder picker using `filedialog.askdirectory()`
   - Add quality dropdown
   - Add subtitle language dropdown
   - Implement threaded download with progress updates
3. Add `--gui` flag to `cli.py`
4. Add `thechosen-gui` console script entry point

## Critical Files

- `src/thechosen_downloader/gui.py` (new)
- `src/thechosen_downloader/cli.py` (modify for --gui flag)
- `src/thechosen_downloader/downloader.py` (reference for download API)
- `pyproject.toml` (add dependency)
- `season1.json` (data source)
