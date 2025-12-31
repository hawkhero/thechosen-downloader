Feature: Video Quality Selection
  As a user
  I want to select the video quality when downloading
  So that I can balance file size and video quality according to my needs

  Background:
    Given the video URL "https://api.frontrow.cc/channels/12884901895/VIDEO/184683594340/v2/hls.m3u8"
    And the following quality options are available from the stream:
      | quality | resolution  | estimated_size |
      | 2160p   | 3840x2160   | 8.81 GB        |
      | 1440p   | 2560x1440   | 4.08 GB        |
      | 1080p   | 1920x1080   | 1.31 GB        |
      | 720p    | 1280x720    | 692 MB         |
      | 480p    | 854x480     | 303 MB         |

  # Downloader Core Tests

  Scenario Outline: Convert quality string to yt-dlp format string
    When I request quality "<quality>"
    Then the format string should be "<format_string>"

    Examples:
      | quality | format_string                                          |
      | 2160p   | bestvideo[height<=2160]+bestaudio/best[height<=2160]   |
      | 1440p   | bestvideo[height<=1440]+bestaudio/best[height<=1440]   |
      | 1080p   | bestvideo[height<=1080]+bestaudio/best[height<=1080]   |
      | 720p    | bestvideo[height<=720]+bestaudio/best[height<=720]     |
      | 480p    | bestvideo[height<=480]+bestaudio/best[height<=480]     |

  Scenario: Default quality should be best available
    When I request quality with no preference
    Then the format string should be "bestvideo+bestaudio/best"

  Scenario: Invalid quality falls back to best
    When I request quality "invalid"
    Then the format string should be "bestvideo+bestaudio/best"

  Scenario: Quality string is case insensitive
    When I request quality "1080P"
    Then the format string should be "bestvideo[height<=1080]+bestaudio/best[height<=1080]"

  # CLI Tests

  Scenario: CLI accepts valid quality options
    Given the CLI argument "--quality 1080p"
    When I parse the arguments
    Then the quality should be "1080p"

  Scenario: CLI defaults to 1080p quality
    Given no quality argument is provided
    When I parse the arguments
    Then the quality should be "1080p"

  Scenario Outline: CLI accepts all supported qualities
    Given the CLI argument "--quality <quality>"
    When I parse the arguments
    Then the quality should be "<quality>"

    Examples:
      | quality |
      | 480p    |
      | 720p    |
      | 1080p   |
      | 1440p   |
      | 2160p   |

  # GUI Tests

  Scenario: GUI displays quality selection dropdown
    When I open the GUI
    Then I should see a quality selection dropdown
    And the dropdown should contain the following options:
      | option           |
      | Auto (Best)      |
      | 2160p (4K)       |
      | 1440p            |
      | 1080p            |
      | 720p             |
      | 480p             |

  Scenario: GUI defaults to 1080p quality
    When I open the GUI
    Then the selected quality should be "1080p"

  Scenario: Quality selection persists during download
    Given I select quality "720p" in the GUI
    When I start a download
    Then the download should use quality "720p"

  # Integration Tests

  Scenario: Download with specific quality limits resolution
    Given a video with multiple quality streams
    When I download with quality "720p"
    Then the downloaded video should have resolution at most 1280x720

  Scenario: Quality affects download file size
    Given a video with multiple quality streams
    When I compare download sizes for "720p" and "2160p"
    Then the "720p" file should be smaller than the "2160p" file
