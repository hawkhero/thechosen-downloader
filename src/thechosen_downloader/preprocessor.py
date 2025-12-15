"""Batch URL preprocessing"""

import time
from pathlib import Path
from typing import List
from .extractor import URLExtractor
from .cache import Cache, CacheEntry


class Preprocessor:
    """Preprocess episode URLs and cache m3u8 URLs"""

    def __init__(self, verbose: bool = False, rate_limit: float = 1.0):
        self.verbose = verbose
        self.rate_limit = rate_limit  # seconds between requests
        self.extractor = URLExtractor(verbose=verbose)

    def process_url_list(
        self,
        url_list_file: str,
        cache_file: str,
        season: int = 1,
    ) -> bool:
        """
        Process a list of episode URLs and cache the m3u8 URLs.

        Args:
            url_list_file: Path to file containing episode URLs (one per line)
            cache_file: Path to output cache file
            season: Season number

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read URL list
            urls = self._read_url_list(url_list_file)
            if not urls:
                print("No URLs found in file")
                return False

            if self.verbose:
                print(f"Found {len(urls)} URLs to process")

            # Initialize cache
            cache = Cache(cache_file)
            cache.season = season

            # Process each URL or file
            for i, item in enumerate(urls, 1):
                if self.verbose:
                    print(f"\n[{i}/{len(urls)}] Processing: {item}")

                # Check if it's a file or URL
                if Path(item).exists():
                    # Extract from HTML file
                    m3u8_url, title = self.extractor.extract_from_file(item)
                else:
                    # Extract from URL
                    m3u8_url, title = self.extractor.extract_from_url(item)

                if not m3u8_url:
                    print(f"Failed to extract m3u8 URL from: {item}")
                    continue

                # Determine episode number
                episode_number = i  # default to position in list
                if title:
                    extracted_num = self.extractor.extract_episode_number(title)
                    if extracted_num:
                        episode_number = extracted_num

                # Create cache entry
                entry = CacheEntry(
                    episode_number=episode_number,
                    title=title or f"Episode {episode_number}",
                    episode_url=url,
                    m3u8_url=m3u8_url,
                )

                cache.add_episode(entry)

                if self.verbose:
                    print(f"  Episode: {episode_number}")
                    print(f"  Title: {entry.title}")
                    print(f"  m3u8 URL: {m3u8_url[:80]}...")

                # Rate limiting
                if i < len(urls):
                    time.sleep(self.rate_limit)

            # Save cache
            if cache.save():
                print(f"\nSuccessfully cached {len(cache.episodes)} episodes to {cache_file}")
                return True
            else:
                print("Failed to save cache")
                return False

        except Exception as e:
            print(f"Error processing URLs: {e}")
            return False

    def _read_url_list(self, file_path: str) -> List[str]:
        """
        Read URLs or HTML file paths from file (one per line).
        Supports both URLs (starting with http) and local HTML file paths.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"File not found: {file_path}")
                return []

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Extract URLs or file paths
            items = []
            for line in lines:
                line = line.strip()
                # Accept URLs or file paths (check if file exists or is URL)
                if line.startswith('http') or Path(line).exists() or line.endswith('.html'):
                    items.append(line)

            return items

        except Exception as e:
            print(f"Error reading URL list: {e}")
            return []
