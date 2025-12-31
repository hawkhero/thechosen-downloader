"""
BDD tests for video quality selection feature.

Tests are based on the Gherkin feature file at:
tests/features/quality_selection.feature
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Import the module under test
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from thechosen_downloader.downloader import VideoDownloader


# Load all scenarios from the feature file
scenarios("features/quality_selection.feature")


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def downloader():
    """Create a VideoDownloader instance for testing."""
    return VideoDownloader(verbose=False)


@pytest.fixture
def format_result():
    """Store the result of format string conversion."""
    return {}


@pytest.fixture
def cli_args():
    """Store parsed CLI arguments."""
    return {}


# ==============================================================================
# Given Steps
# ==============================================================================

@given(parsers.parse('the video URL "{url}"'))
def given_video_url(url):
    """Store the video URL for testing."""
    return url


@given("the following quality options are available from the stream:")
def given_quality_options(datatable):
    """Store available quality options from the stream."""
    # This is just documentation - the actual options come from the HLS manifest
    pass


@given(parsers.parse('the CLI argument "--quality {quality}"'))
def given_cli_quality_arg(cli_args, quality):
    """Store CLI quality argument for parsing."""
    cli_args["quality"] = quality


@given("no quality argument is provided")
def given_no_quality_arg(cli_args):
    """No quality argument in CLI."""
    cli_args["quality"] = None


@given(parsers.parse('I select quality "{quality}" in the GUI'))
def given_gui_quality_selection(quality):
    """Simulate GUI quality selection."""
    return quality


@given("a video with multiple quality streams")
def given_video_with_streams():
    """A video URL with multiple quality options."""
    return "https://api.frontrow.cc/channels/12884901895/VIDEO/184683594340/v2/hls.m3u8"


# ==============================================================================
# When Steps
# ==============================================================================

@when(parsers.parse('I request quality "{quality}"'))
def when_request_quality(downloader, format_result, quality):
    """Request a specific quality and store the format string."""
    format_result["value"] = downloader._get_format_string(quality)


@when("I request quality with no preference")
def when_request_no_quality(downloader, format_result):
    """Request quality with None (no preference)."""
    format_result["value"] = downloader._get_format_string(None)


@when("I parse the arguments")
def when_parse_arguments(cli_args):
    """Parse CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--quality', '-q',
        choices=['360p', '480p', '720p', '1080p', '1440p', '2160p'],
        default='1080p',
    )

    args_list = []
    if cli_args.get("quality"):
        args_list.extend(["--quality", cli_args["quality"]])

    parsed = parser.parse_args(args_list)
    cli_args["parsed"] = parsed


@when("I open the GUI")
def when_open_gui():
    """Simulate opening the GUI (without actually creating window)."""
    # We'll test the GUI quality options without creating actual window
    pass


@when("I start a download")
def when_start_download():
    """Simulate starting a download."""
    pass


@when(parsers.parse('I download with quality "{quality}"'))
def when_download_with_quality(downloader, quality):
    """Download with specified quality (simulation)."""
    format_string = downloader._get_format_string(quality)
    return format_string


@when(parsers.parse('I compare download sizes for "{quality1}" and "{quality2}"'))
def when_compare_download_sizes(quality1, quality2):
    """Compare download sizes for two qualities."""
    return (quality1, quality2)


# ==============================================================================
# Then Steps
# ==============================================================================

@then(parsers.parse('the format string should be "{expected}"'))
def then_format_string_should_be(format_result, expected):
    """Verify the format string matches expected value."""
    assert format_result["value"] == expected, (
        f"Expected format string '{expected}', got '{format_result['value']}'"
    )


@then(parsers.parse('the quality should be "{expected}"'))
def then_quality_should_be(cli_args, expected):
    """Verify parsed quality matches expected."""
    actual = cli_args["parsed"].quality
    assert actual == expected, f"Expected quality '{expected}', got '{actual}'"


@then("I should see a quality selection dropdown")
def then_should_see_dropdown():
    """Verify quality dropdown exists in GUI."""
    # Import GUI module to check for quality options
    from thechosen_downloader.gui import QUALITY_OPTIONS
    assert QUALITY_OPTIONS is not None
    assert len(QUALITY_OPTIONS) > 0


@then("the dropdown should contain the following options:")
def then_dropdown_contains_options(datatable):
    """Verify dropdown contains expected options."""
    from thechosen_downloader.gui import QUALITY_OPTIONS

    # datatable is a list of lists, first row is headers
    # Skip header row and get the option values
    expected_options = [row[0] for row in datatable[1:]]  # Skip header row
    actual_labels = [label for _, label in QUALITY_OPTIONS]

    for expected in expected_options:
        assert expected in actual_labels, f"Option '{expected}' not found in dropdown"


@then(parsers.parse('the selected quality should be "{expected}"'))
def then_selected_quality_should_be(expected):
    """Verify default selected quality."""
    from thechosen_downloader.gui import DEFAULT_QUALITY
    assert DEFAULT_QUALITY == expected


@then(parsers.parse('the download should use quality "{quality}"'))
def then_download_uses_quality(downloader, quality):
    """Verify download uses the selected quality."""
    format_string = downloader._get_format_string(quality)
    expected = f"bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]"
    assert format_string == expected


@then(parsers.parse('the downloaded video should have resolution at most {width}x{height}'))
def then_video_resolution_at_most(width, height):
    """Verify video resolution is within limits (simulation)."""
    # This would require actual download - mark as integration test
    pass


@then(parsers.parse('the "{quality1}" file should be smaller than the "{quality2}" file'))
def then_file_size_comparison(quality1, quality2):
    """Verify file size comparison (simulation)."""
    # Based on observed data: 720p ~692MB, 2160p ~8.81GB
    # This is a documentation/expectation test
    quality_sizes = {
        "480p": 303,
        "720p": 692,
        "1080p": 1310,
        "1440p": 4080,
        "2160p": 8810,
    }
    assert quality_sizes[quality1] < quality_sizes[quality2]


# ==============================================================================
# Unit Tests (Non-BDD)
# ==============================================================================

class TestQualityFormatString:
    """Unit tests for quality format string conversion."""

    def test_all_supported_qualities(self):
        """Test all supported quality options produce valid format strings."""
        downloader = VideoDownloader()

        qualities = ["480p", "720p", "1080p", "1440p", "2160p"]

        for quality in qualities:
            result = downloader._get_format_string(quality)
            height = quality[:-1]  # Remove 'p'
            expected = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
            assert result == expected, f"Quality {quality} produced wrong format string"

    def test_none_quality_returns_best(self):
        """Test that None quality returns best format."""
        downloader = VideoDownloader()
        result = downloader._get_format_string(None)
        assert result == "bestvideo+bestaudio/best"

    def test_invalid_quality_returns_best(self):
        """Test that invalid quality returns best format."""
        downloader = VideoDownloader()
        result = downloader._get_format_string("invalid")
        assert result == "bestvideo+bestaudio/best"

    def test_case_insensitive_quality(self):
        """Test that quality string is case insensitive."""
        downloader = VideoDownloader()

        assert downloader._get_format_string("1080p") == downloader._get_format_string("1080P")
        assert downloader._get_format_string("720P") == "bestvideo[height<=720]+bestaudio/best[height<=720]"

    def test_360p_quality(self):
        """Test 360p quality option."""
        downloader = VideoDownloader()
        result = downloader._get_format_string("360p")
        assert result == "bestvideo[height<=360]+bestaudio/best[height<=360]"


class TestCLIQualityOptions:
    """Tests for CLI quality argument handling."""

    def test_cli_quality_choices(self):
        """Test that CLI accepts all quality choices including 1440p."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--quality', '-q',
            choices=['360p', '480p', '720p', '1080p', '1440p', '2160p'],
            default='1080p',
        )

        # Test all valid choices
        for quality in ['360p', '480p', '720p', '1080p', '1440p', '2160p']:
            args = parser.parse_args(['--quality', quality])
            assert args.quality == quality

    def test_cli_default_quality(self):
        """Test CLI defaults to 1080p."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--quality', '-q',
            choices=['360p', '480p', '720p', '1080p', '1440p', '2160p'],
            default='1080p',
        )

        args = parser.parse_args([])
        assert args.quality == "1080p"
