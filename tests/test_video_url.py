"""Tests for video URL validation"""

import json
from pathlib import Path
from urllib.parse import urlparse
import pytest
import requests


def get_season1_path() -> Path:
    """Get path to season1.json"""
    return Path(__file__).parent.parent / "season1.json"


def load_episodes() -> list:
    """Load episodes from season1.json"""
    with open(get_season1_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("episodes", [])


class TestVideoUrlFormat:
    """Test video URL format and structure"""

    def test_season1_json_exists(self):
        """Verify season1.json file exists"""
        assert get_season1_path().exists(), "season1.json not found"

    def test_episodes_have_video_urls(self):
        """Verify all episodes have video_url field"""
        episodes = load_episodes()
        assert len(episodes) > 0, "No episodes found"

        for ep in episodes:
            assert "video_url" in ep, f"Episode {ep.get('episode')} missing video_url"
            assert ep["video_url"], f"Episode {ep.get('episode')} has empty video_url"

    def test_video_urls_are_token_free(self):
        """Verify video URLs do not contain viewerToken (which can expire)"""
        episodes = load_episodes()

        for ep in episodes:
            video_url = ep.get("video_url", "")
            assert "viewerToken=" not in video_url, (
                f"Episode {ep['episode']} contains viewerToken which can expire. "
                "Use token-free URL instead."
            )

    def test_video_urls_are_valid_m3u8(self):
        """Verify video URLs point to m3u8 files"""
        episodes = load_episodes()

        for ep in episodes:
            video_url = ep.get("video_url", "")
            assert video_url.endswith(".m3u8"), (
                f"Episode {ep['episode']} video_url should end with .m3u8"
            )

    def test_video_urls_use_correct_api(self):
        """Verify video URLs use the frontrow API"""
        episodes = load_episodes()

        for ep in episodes:
            video_url = ep.get("video_url", "")
            parsed = urlparse(video_url)
            assert parsed.netloc == "api.frontrow.cc", (
                f"Episode {ep['episode']} should use api.frontrow.cc"
            )


class TestVideoUrlAccessibility:
    """Test video URL accessibility without downloading full content"""

    @pytest.mark.network
    def test_video_url_returns_valid_response(self):
        """
        Test that video URL is accessible (HEAD request only).

        This test makes a real network request but only fetches headers,
        not the actual video content. Skipped by default - run with:
            pytest -m network
        """
        episodes = load_episodes()

        # Only test first episode to minimize network requests
        ep = episodes[0]
        video_url = ep.get("video_url")

        # Use HEAD request to avoid downloading content
        # For m3u8, we need GET but with stream=True and only read first chunk
        try:
            response = requests.get(
                video_url,
                stream=True,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "Referer": "https://watch.thechosen.tv/",
                }
            )

            # Close immediately without reading body
            response.close()

            assert response.status_code == 200, (
                f"Episode {ep['episode']} URL returned {response.status_code}. "
                "Token may be expired or invalid."
            )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Network request failed: {e}")

    @pytest.mark.network
    def test_m3u8_manifest_contains_valid_segments(self):
        """
        Verify that m3u8 manifest contains segment URLs (not error response).

        Note: The server may return 200 for expired tokens but the manifest
        content or segment downloads will fail.
        """
        episodes = load_episodes()
        ep = episodes[0]
        video_url = ep.get("video_url")

        try:
            response = requests.get(
                video_url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "Referer": "https://watch.thechosen.tv/",
                }
            )

            # Check if response is a valid m3u8 playlist
            content = response.text
            is_valid_m3u8 = (
                "#EXTM3U" in content
                and ("#EXT-X-STREAM-INF" in content or "#EXTINF" in content)
            )

            assert is_valid_m3u8, (
                f"Episode {ep['episode']} returned invalid m3u8 manifest. "
                "Token may be expired. Content preview: "
                f"{content[:200]}..."
            )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Network request failed: {e}")
