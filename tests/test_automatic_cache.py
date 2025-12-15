"""Tests for automatic cache functionality"""

import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thechosen_downloader.cache import Cache, CacheEntry
from thechosen_downloader.cli import _save_to_auto_cache, AUTO_CACHE_PATH


def test_cache_creation():
    """Test that cache file is created when it doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Verify no cache exists
            assert not Path(AUTO_CACHE_PATH).exists(), "Cache should not exist initially"

            # Save to cache
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video.m3u8",
                title="Test Episode",
                verbose=False
            )

            # Verify cache was created
            assert Path(AUTO_CACHE_PATH).exists(), "Cache file should be created"

            # Verify cache contents
            with open(AUTO_CACHE_PATH, 'r') as f:
                data = json.load(f)

            assert data['season'] is None
            assert len(data['episodes']) == 1
            assert data['episodes'][0]['title'] == "Test Episode"
            assert data['episodes'][0]['episode_url'] == "https://watch.thechosen.tv/video/123456"
            assert data['episodes'][0]['m3u8_url'] == "https://example.com/video.m3u8"

            print("✓ Cache creation test passed")

        finally:
            os.chdir(original_dir)


def test_cache_update():
    """Test that existing cache entries are updated"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Create initial cache entry
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video1.m3u8",
                title="Episode 1",
                verbose=False
            )

            # Update with new m3u8 URL (same episode)
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video1_new.m3u8",
                title="Episode 1",
                verbose=False
            )

            # Verify cache was updated, not duplicated
            with open(AUTO_CACHE_PATH, 'r') as f:
                data = json.load(f)

            assert len(data['episodes']) == 1, "Should have only 1 episode, not duplicates"
            assert data['episodes'][0]['m3u8_url'] == "https://example.com/video1_new.m3u8"

            print("✓ Cache update test passed")

        finally:
            os.chdir(original_dir)


def test_cache_multiple_episodes():
    """Test caching multiple different episodes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Add episode 1
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video1.m3u8",
                title="Season 1 Episode 1: Test",
                verbose=False
            )

            # Add episode 2
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123457",
                m3u8_url="https://example.com/video2.m3u8",
                title="Season 1 Episode 2: Test",
                verbose=False
            )

            # Verify both episodes are cached
            with open(AUTO_CACHE_PATH, 'r') as f:
                data = json.load(f)

            assert len(data['episodes']) == 2, "Should have 2 episodes"
            assert data['episodes'][0]['episode_number'] == 1
            assert data['episodes'][1]['episode_number'] == 2

            print("✓ Multiple episodes test passed")

        finally:
            os.chdir(original_dir)


def test_cache_directory_creation():
    """Test that .cache directory is created automatically"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Verify .cache directory doesn't exist
            assert not Path(".cache").exists(), ".cache directory should not exist initially"

            # Save to cache
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video.m3u8",
                title="Test Episode",
                verbose=False
            )

            # Verify .cache directory was created
            assert Path(".cache").exists(), ".cache directory should be created"
            assert Path(".cache").is_dir(), ".cache should be a directory"

            print("✓ Cache directory creation test passed")

        finally:
            os.chdir(original_dir)


def test_cache_atomic_writes():
    """Test that cache writes are atomic (no temp files left behind)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Save to cache
            _save_to_auto_cache(
                source_url="https://watch.thechosen.tv/video/123456",
                m3u8_url="https://example.com/video.m3u8",
                title="Test Episode",
                verbose=False
            )

            # Check for leftover temp files
            cache_dir = Path(".cache")
            temp_files = [f for f in cache_dir.iterdir() if f.name.startswith('.tmp_')]

            assert len(temp_files) == 0, f"Found leftover temp files: {temp_files}"

            print("✓ Atomic writes test passed")

        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    print("Running automatic cache tests...\n")

    test_cache_creation()
    test_cache_update()
    test_cache_multiple_episodes()
    test_cache_directory_creation()
    test_cache_atomic_writes()

    print("\n✅ All tests passed!")
