# The Chosen Downloader

Download episodes from The Chosen streaming platform (watch.thechosen.tv) for offline viewing.

## Why This Project?

While watching The Chosen on the official website, I experienced slow streaming speeds and constant buffering issues. The videos would frequently stutter and lag, making it difficult to enjoy the content smoothly. This frustration led me to develop a tool to download episodes for offline viewing.

I realized that others might face similar streaming problems, so I decided to open-source this project and share it with the community. Whether you have a slow internet connection, want to watch offline during travel, or simply prefer a smoother viewing experience, this tool is for you.

## Features

- Download videos with quality selection
- Subtitle download and embedding
- Batch download support for multiple episodes
- URL preprocessing and caching
- **Automatic URL caching** for all single downloads
- Progress tracking with ETA
- Automatic retry on network errors

## Requirements

- Python 3.8 or higher
- `uv` (Python package installer)
- `ffmpeg` (for video processing)

## Installation

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Install thechosen-downloader

```bash
git clone <repo-url>
cd thechosen-downloader
uv venv
uv pip install -e .
```

## Usage

### Download a single episode

By default, videos are downloaded at **1080p quality** with **Chinese (Taiwan) subtitles** embedded.

**Note:** The extracted video URL is automatically cached to `.cache/downloads.json` for future reuse.

```bash
# Using episode URL (downloads 1080p with zh-TW subtitles by default)
thechosen-downloader https://watch.thechosen.tv/video/184683594334

# Using saved HTML file
thechosen-downloader "Season 1 Episode 1.html"
```

### Preprocess URLs for batch download

**Note:** Due to JavaScript-based video loading on the website, you need to save the HTML files first (Right-click → Save As in your browser), then preprocess from the saved files.

```bash
# First, save episode pages as HTML files in a directory, then create a list:
# Example file list (season1-files.txt):
# Season 1 Episode 1.html
# Season 1 Episode 2.html
# etc.

# Then extract m3u8 URLs from the saved HTML files
thechosen-downloader --preprocess season1-files.txt --output cache/season1.json
```

### Batch download

```bash
# Download all episodes from cache
thechosen-downloader --batch cache/season1.json

# Download specific episodes
thechosen-downloader --batch cache/season1.json --episodes 1-3
```

### Advanced options

```bash
# Change quality (default is 1080p)
thechosen-downloader URL --quality 720p

# Change subtitle language (default is zh-TW)
thechosen-downloader URL --subtitle-lang en

# Disable subtitles
thechosen-downloader URL --no-subtitles

# Download subtitles only (no video)
thechosen-downloader URL --subtitles-only

# Download English subtitles only
thechosen-downloader URL --subtitles-only --subtitle-lang en

# Custom output filename
thechosen-downloader URL --output "Episode 1.mp4"

# Verbose mode
thechosen-downloader URL --verbose
```

## Automatic URL Caching

When you download a single episode using a URL or HTML file (not a direct m3u8 URL), the tool automatically saves the extracted video URL to `.cache/downloads.json`. This cache:

- **Saves time**: Avoids re-extracting URLs for the same episodes (which takes 10-30 seconds with browser automation)
- **Works transparently**: No flags needed, happens automatically in the background
- **Uses same format**: Compatible with the preprocessing cache format
- **Persists across sessions**: Cache is kept on disk for future use

### Managing the cache

The cache is stored at `.cache/downloads.json` relative to your working directory.

```bash
# View cache contents
cat .cache/downloads.json

# Clean up cache manually if needed
rm -rf .cache

# See cache operations (verbose mode)
thechosen-downloader URL --verbose
```

## Development

### Setup development environment

```bash
uv venv
uv pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

## Troubleshooting

### "ffmpeg not found"
Make sure ffmpeg is installed and in your PATH.

### "Token expired" errors
m3u8 URLs contain authentication tokens that expire. If preprocessing, download soon after extraction. The tool will automatically retry with fresh URLs if tokens expire.

### "Network error"
The tool includes automatic retry logic. Check your internet connection if downloads repeatedly fail.

## License

MIT License (see LICENSE file)
