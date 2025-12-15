"""Cache management for preprocessed URLs"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class CacheEntry:
    """Represents a cached episode"""

    def __init__(
        self,
        episode_number: int,
        title: str,
        episode_url: str,
        m3u8_url: str,
        extracted_at: Optional[str] = None,
    ):
        self.episode_number = episode_number
        self.title = title
        self.episode_url = episode_url
        self.m3u8_url = m3u8_url
        self.extracted_at = extracted_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'episode_number': self.episode_number,
            'title': self.title,
            'episode_url': self.episode_url,
            'm3u8_url': self.m3u8_url,
            'extracted_at': self.extracted_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(
            episode_number=data['episode_number'],
            title=data['title'],
            episode_url=data['episode_url'],
            m3u8_url=data['m3u8_url'],
            extracted_at=data.get('extracted_at'),
        )


class Cache:
    """Manage episode URL cache"""

    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self.season: Optional[int] = None
        self.episodes: List[CacheEntry] = []

    def load(self) -> bool:
        """
        Load cache from file.

        Returns True if cache was loaded successfully, False if file doesn't exist
        or loading failed. If file doesn't exist, initializes an empty cache.
        """
        if not self.cache_file.exists():
            # Initialize empty cache - not an error
            self.season = None
            self.episodes = []
            return True

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.season = data.get('season')
            self.episodes = [
                CacheEntry.from_dict(ep) for ep in data.get('episodes', [])
            ]

            return True

        except Exception as e:
            print(f"Error loading cache: {e}")
            return False

    def save(self) -> bool:
        """
        Save cache to file using atomic write.

        Writes to a temporary file first, then atomically renames it to the
        target path to prevent corruption if write fails or is interrupted.
        """
        try:
            # Create parent directory if it doesn't exist
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'season': self.season,
                'episodes': [ep.to_dict() for ep in self.episodes],
            }

            # Write to temporary file in same directory
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.cache_file.parent,
                prefix='.tmp_',
                suffix='.json'
            )

            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Atomic rename
                os.replace(temp_path, self.cache_file)
                return True

            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise

        except Exception as e:
            print(f"Error saving cache: {e}")
            return False

    def add_episode(self, entry: CacheEntry) -> None:
        """Add or update an episode in the cache"""
        # Remove existing entry with same episode number
        self.episodes = [
            ep for ep in self.episodes
            if ep.episode_number != entry.episode_number
        ]

        # Add new entry
        self.episodes.append(entry)

        # Sort by episode number
        self.episodes.sort(key=lambda ep: ep.episode_number)

    def get_episode(self, episode_number: int) -> Optional[CacheEntry]:
        """Get episode by number"""
        for ep in self.episodes:
            if ep.episode_number == episode_number:
                return ep
        return None

    def get_episodes_in_range(self, start: int, end: int) -> List[CacheEntry]:
        """Get episodes in a range"""
        return [
            ep for ep in self.episodes
            if start <= ep.episode_number <= end
        ]

    def get_all_episodes(self) -> List[CacheEntry]:
        """Get all episodes"""
        return self.episodes.copy()

    def clear(self) -> None:
        """Clear all cached episodes"""
        self.episodes = []
        self.season = None
