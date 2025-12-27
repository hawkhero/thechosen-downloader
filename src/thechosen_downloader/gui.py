"""GUI interface for The Chosen downloader using CustomTkinter"""

import json
import os
import sys
import threading
from datetime import datetime # Added for logging
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional

import customtkinter as ctk


from .downloader import VideoDownloader

# Subtitle language options
SUBTITLE_LANGUAGES = [
    ("zh-TW", "Chinese (Taiwan)"),
    ("zh-CN", "Chinese (Simplified)"),
    ("en", "English"),
    ("es", "Spanish"),
    ("pt", "Portuguese"),
    ("ko", "Korean"),
    ("ja", "Japanese"),
]

def _log_debug(message):
    log_file_path = Path.home() / "thechosen_downloader_gui_debug.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Explicitly format timestamp
    with open(log_file_path, "a") as f:
        f.write(f"[DEBUG] {timestamp}: {message}\n")

def get_season1_path() -> Path:
    """Get the path to season1.json"""
    # Try to find season1.json relative to this module
    module_dir = Path(__file__).parent

    # Check in project root (two levels up from src/thechosen_downloader)
    project_root = module_dir.parent.parent
    season1_path = project_root / "season1.json"

    if season1_path.exists():
        return season1_path

    # Check in current working directory
    cwd_path = Path.cwd() / "season1.json"
    if cwd_path.exists():
        return cwd_path

    raise FileNotFoundError("season1.json not found")


def load_episodes() -> list:
    """Load episodes from season1.json"""
    season1_path = get_season1_path()
    with open(season1_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("episodes", [])


class TheChosenDownloaderGUI(ctk.CTk):
    """Main GUI application for The Chosen Downloader"""

    def __init__(self):
        _log_debug("TheChosenDownloaderGUI.__init__ started.")
        super().__init__()
        _log_debug("super().__init__() called.")

        # Window setup
        self.title("The Chosen Downloader")
        self.geometry("700x620")
        self.minsize(600, 620)
        _log_debug("Window setup complete.")

        # Set appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        _log_debug("Appearance mode and color theme set.")

        # Load episodes
        try:
            self.episodes = load_episodes()
            _log_debug(f"Episodes loaded: {len(self.episodes)} episodes.")
        except FileNotFoundError as e:
            self.episodes = []
            _log_debug(f"Warning: {e} - Episodes not loaded.")

        # Episode checkbox variables
        self.episode_vars = []

        # Download state
        self.is_downloading = False
        self.download_thread: Optional[threading.Thread] = None

        # Create widgets
        _log_debug("Calling create_widgets().")
        self.create_widgets()
        _log_debug("create_widgets() finished.")
        _log_debug("TheChosenDownloaderGUI.__init__ finished.")

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Season 1 - Select Episodes to Download:",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.title_label.pack(anchor="w", pady=(0, 10))

        # Episode list frame with scrollable area
        self.episode_frame = ctk.CTkScrollableFrame(
            self.main_frame, height=200
        )
        self.episode_frame.pack(fill="x", pady=(0, 10))

        # Manually bind mouse wheel for macOS compatibility
        self.episode_frame._parent_canvas.bind("<MouseWheel>", self._on_mouse_wheel)

        # Create checkboxes for each episode
        for episode in self.episodes:
            var = ctk.BooleanVar(value=False)
            self.episode_vars.append(var)

            checkbox = ctk.CTkCheckBox(
                self.episode_frame,
                text=f"{episode['episode']}. {episode['title']}",
                variable=var,
                font=ctk.CTkFont(size=13),
            )
            checkbox.pack(anchor="w", pady=2)

        # Select All / Deselect All buttons
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=(0, 15))

        self.select_all_btn = ctk.CTkButton(
            self.button_frame,
            text="Select All",
            command=self.select_all,
            width=120,
        )
        self.select_all_btn.pack(side="left", padx=(0, 10))

        self.deselect_all_btn = ctk.CTkButton(
            self.button_frame,
            text="Deselect All",
            command=self.deselect_all,
            width=120,
        )
        self.deselect_all_btn.pack(side="left")

        # Download location section
        self.location_label = ctk.CTkLabel(
            self.main_frame,
            text="Download Location:",
            font=ctk.CTkFont(size=14),
        )
        self.location_label.pack(anchor="w", pady=(10, 5))

        self.location_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.location_frame.pack(fill="x", pady=(0, 15))

        self.location_entry = ctk.CTkEntry(
            self.location_frame,
            placeholder_text="Select download folder...",
        )
        self.location_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Set default download location
        default_downloads = str(Path.home() / "Downloads")
        self.location_entry.insert(0, default_downloads)

        self.browse_btn = ctk.CTkButton(
            self.location_frame,
            text="Browse...",
            command=self.browse_folder,
            width=100,
        )
        self.browse_btn.pack(side="right")

        # Options frame (Subtitle only)
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 15))

        # Subtitle language selection
        self.subtitle_label = ctk.CTkLabel(
            self.options_frame,
            text="Subtitle Language:",
            font=ctk.CTkFont(size=14),
        )
        self.subtitle_label.pack(side="left")

        # Create display names for dropdown
        self.subtitle_display_names = [name for _, name in SUBTITLE_LANGUAGES]
        self.subtitle_var = ctk.StringVar(value="Chinese (Taiwan)")
        self.subtitle_dropdown = ctk.CTkOptionMenu(
            self.options_frame,
            values=self.subtitle_display_names,
            variable=self.subtitle_var,
            width=180,
        )
        self.subtitle_dropdown.pack(side="left", padx=(10, 0))

        # Progress section
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill="x", pady=(10, 15))

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)

        # Download button
        self.download_btn = ctk.CTkButton(
            self.main_frame,
            text="Download Selected Episodes",
            command=self.download_selected,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
        )
        self.download_btn.pack(side="right", pady=(10, 0))

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling for episode frame"""
        # Check if mouse is over the scrollable frame
        if not self.episode_frame.winfo_containing(event.x_root, event.y_root) == self.episode_frame:
            return

        # Check if the scrollable frame is scrollable
        if self.episode_frame._parent_canvas.yview() == (0.0, 1.0):
            return

        # Determine scroll direction
        if sys.platform == "darwin":
            # macOS uses event.delta directly
            scroll_dir = -1 * event.delta
        else:
            # Windows/Linux use multiples of 120
            scroll_dir = -1 * int(event.delta / 120)

        self.episode_frame._parent_canvas.yview_scroll(scroll_dir, "units")

    def select_all(self):
        """Select all episodes"""
        for var in self.episode_vars:
            var.set(True)

    def deselect_all(self):
        """Deselect all episodes"""
        for var in self.episode_vars:
            var.set(False)

    def browse_folder(self):
        """Open folder picker dialog"""
        folder = filedialog.askdirectory(
            title="Select Download Folder",
            initialdir=self.location_entry.get() or str(Path.home() / "Downloads"),
        )
        if folder:
            self.location_entry.delete(0, "end")
            self.location_entry.insert(0, folder)

    def get_selected_subtitle_code(self) -> str:
        """Get the language code for selected subtitle"""
        display_name = self.subtitle_var.get()
        for code, name in SUBTITLE_LANGUAGES:
            if name == display_name:
                return code
        return "zh-TW"  # Default

    def get_selected_episodes(self) -> list:
        """Get list of selected episodes"""
        selected = []
        for i, var in enumerate(self.episode_vars):
            if var.get() and i < len(self.episodes):
                selected.append(self.episodes[i])
        return selected

    def update_status(self, message: str):
        """Update status label (thread-safe)"""
        self.after(0, lambda: self.status_label.configure(text=f"Status: {message}"))

    def update_progress(self, value: float):
        """Update progress bar (thread-safe), value should be 0.0 to 1.0"""
        self.after(0, lambda: self.progress_bar.set(value))

    def set_downloading_state(self, is_downloading: bool):
        """Enable/disable UI during download"""
        state = "disabled" if is_downloading else "normal"
        self.after(0, lambda: self.download_btn.configure(state=state))
        self.after(0, lambda: self.browse_btn.configure(state=state))
        self.after(0, lambda: self.select_all_btn.configure(state=state))
        self.after(0, lambda: self.deselect_all_btn.configure(state=state))
        self.is_downloading = is_downloading

    def download_selected(self):
        """Start downloading selected episodes"""
        selected = self.get_selected_episodes()

        if not selected:
            self.update_status("No episodes selected")
            return

        download_path = self.location_entry.get()
        if not download_path:
            self.update_status("Please select a download location")
            return

        # Create download directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)

        # Start download in background thread
        self.download_thread = threading.Thread(
            target=self._download_episodes,
            args=(selected, download_path),
            daemon=True,
        )
        self.download_thread.start()

    def _download_episodes(self, episodes: list, download_path: str):
        """Download episodes in background thread"""
        self.set_downloading_state(True)

        subtitle_lang = self.get_selected_subtitle_code()

        total = len(episodes)
        failed = []

        for i, episode in enumerate(episodes, 1):
            ep_num = episode["episode"]
            title = episode["title"]
            video_url = episode.get("video_url")

            if not video_url:
                self.update_status(f"Episode {ep_num}: No video URL")
                failed.append(ep_num)
                continue

            # Create downloader with progress callback for this episode
            def progress_callback(msg):
                self.update_status(f"[{i}/{total}] {title}: {msg}")

            downloader = VideoDownloader(verbose=False, progress_callback=progress_callback)

            self.update_status(f"[{i}/{total}] Starting: {title}")
            self.update_progress((i - 1) / total)

            # Generate output filename
            output_filename = f"S01E{ep_num:02d} - {title}.mp4"
            output_path = os.path.join(download_path, output_filename)

            try:
                success = downloader.download(
                    url=video_url,
                    output_path=output_path,
                    subtitles=True,
                    subtitle_lang=subtitle_lang,
                )

                if not success:
                    failed.append(ep_num)
                    self.update_status(f"Failed: Episode {ep_num}")

            except Exception as e:
                failed.append(ep_num)
                self.update_status(f"Error: {e}")

        # Complete
        self.update_progress(1.0)

        if failed:
            self.update_status(
                f"Complete with errors. Failed episodes: {', '.join(map(str, failed))}"
            )
        else:
            self.update_status(f"Successfully downloaded {total} episode(s)")

        self.set_downloading_state(False)


def main():
    """Main entry point for GUI"""
    _log_debug("GUI main() function started.")
    app = TheChosenDownloaderGUI()
    _log_debug("TheChosenDownloaderGUI instance created.")
    app.mainloop()
    _log_debug("GUI mainloop exited.")


if __name__ == "__main__":
    main()
