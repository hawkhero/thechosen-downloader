"""Video downloader using yt-dlp"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp


class VideoDownloader:
    """Download videos using yt-dlp"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        quality: Optional[str] = None,
        subtitles: bool = False,
        subtitle_lang: str = 'en',
        subtitles_only: bool = False,
    ) -> bool:
        """
        Download video from URL.

        Args:
            url: m3u8 URL or episode page URL
            output_path: Custom output filename (optional)
            quality: Quality preference (e.g., '720p', '1080p')
            subtitles: Whether to download and embed subtitles
            subtitle_lang: Subtitle language code
            subtitles_only: Download only subtitles without video

        Returns:
            True if download successful, False otherwise
        """
        try:
            ydl_opts = self._build_yt_dlp_options(
                output_path=output_path,
                quality=quality,
                subtitles=subtitles,
                subtitle_lang=subtitle_lang,
                subtitles_only=subtitles_only,
            )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.verbose:
                    print(f"Starting download: {url}")

                ydl.download([url])

            if self.verbose:
                print("Download completed successfully")

            return True

        except Exception as e:
            print(f"Download failed: {e}", file=sys.stderr)
            return False

    def _build_yt_dlp_options(
        self,
        output_path: Optional[str] = None,
        quality: Optional[str] = None,
        subtitles: bool = False,
        subtitle_lang: str = 'en',
        subtitles_only: bool = False,
    ) -> Dict[str, Any]:
        """Build yt-dlp options dictionary"""

        opts = {
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': False,
            'quiet': not self.verbose,
            'no_warnings': not self.verbose,
            'noprogress': False,
            # Browser-like headers to avoid throttling
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://watch.thechosen.tv',
                'Referer': 'https://watch.thechosen.tv/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
            },
        }

        # Skip video download if subtitles-only mode
        if subtitles_only:
            opts['skip_download'] = True
        else:
            opts['format'] = self._get_format_string(quality)
            # Connection optimization for video download
            opts['concurrent_fragment_downloads'] = 4  # Download 4 segments in parallel
            opts['http_chunk_size'] = 10485760  # 10MB chunks

        # Output template
        if output_path:
            # Make path absolute if it's relative
            if not os.path.isabs(output_path):
                output_path = os.path.join(os.getcwd(), output_path)
            opts['outtmpl'] = str(output_path)
        else:
            # Use current working directory for default output
            opts['outtmpl'] = os.path.join(os.getcwd(), '%(title)s.%(ext)s')

        # Subtitle options
        if subtitles:
            # Normalize language code: convert hyphens to underscores
            # (e.g., 'zh-TW' -> 'zh_tw' to match m3u8 manifest format)
            normalized_lang = subtitle_lang.replace('-', '_').lower()

            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = [normalized_lang]

            # Only embed subtitles if we're downloading video
            if not subtitles_only:
                opts['postprocessors'] = [{
                    'key': 'FFmpegEmbedSubtitle',
                }]

        # Progress hook
        if not self.verbose:
            opts['progress_hooks'] = [self._progress_hook]

        return opts

    def _get_format_string(self, quality: Optional[str]) -> str:
        """Convert quality preference to yt-dlp format string"""

        if not quality:
            return 'bestvideo+bestaudio/best'

        # Map quality names to format strings
        quality_map = {
            '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        }

        return quality_map.get(quality.lower(), 'bestvideo+bestaudio/best')

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for download status"""

        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            speed = d.get('speed')
            eta = d.get('eta')

            if total and total > 0:
                percent = (downloaded / total) * 100
                speed_mb = speed / (1024 * 1024) if speed else 0

                # Format progress message
                msg = f"\rDownloading: {percent:.1f}% "
                msg += f"({downloaded / (1024*1024):.1f}MB / {total / (1024*1024):.1f}MB) "
                if speed:
                    msg += f"@ {speed_mb:.2f}MB/s "
                if eta and eta > 0:
                    mins, secs = divmod(eta, 60)
                    msg += f"ETA: {int(mins)}:{int(secs):02d}"

                sys.stdout.write(msg)
                sys.stdout.flush()
            else:
                # If total size unknown, just show downloaded amount
                msg = f"\rDownloading: {downloaded / (1024*1024):.1f}MB"
                if speed:
                    speed_mb = speed / (1024 * 1024)
                    msg += f" @ {speed_mb:.2f}MB/s"
                sys.stdout.write(msg)
                sys.stdout.flush()

        elif d['status'] == 'finished':
            print("\nDownload finished, processing...")

    def get_available_qualities(self, url: str) -> list:
        """
        Get available video qualities for a URL.

        Args:
            url: Video URL

        Returns:
            List of available quality options
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return []

                formats = info.get('formats', [])
                qualities = set()

                for fmt in formats:
                    height = fmt.get('height')
                    if height:
                        qualities.add(f"{height}p")

                return sorted(list(qualities), key=lambda x: int(x[:-1]), reverse=True)

        except Exception as e:
            if self.verbose:
                print(f"Error getting qualities: {e}")
            return []
