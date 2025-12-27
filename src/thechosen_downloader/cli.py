"""Command-line interface for The Chosen downloader"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from thechosen_downloader.extractor import URLExtractor
from thechosen_downloader.downloader import VideoDownloader
from thechosen_downloader.preprocessor import Preprocessor
from thechosen_downloader.cache import Cache, CacheEntry

# Automatic cache location for single downloads
AUTO_CACHE_PATH = ".cache/downloads.json"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Download episodes from The Chosen streaming platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download single episode
  %(prog)s https://watch.thechosen.tv/video/184683594334

  # Download from saved HTML
  %(prog)s "Season 1 Episode 1.html"

  # Preprocess URLs
  %(prog)s --preprocess season1.md --output cache/season1.json

  # Batch download
  %(prog)s --batch cache/season1.json --episodes 1-3

  # Override defaults (subtitles and quality are automatic)
  %(prog)s URL --quality 720p --subtitle-lang en

  # Disable subtitles
  %(prog)s URL --no-subtitles
        '''
    )

    # Main arguments
    parser.add_argument(
        'sources',
        nargs='*',
        help='Episode URL(s), HTML file(s), or cache file (with --batch). Multiple URLs can be provided for batch download.'
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--preprocess',
        metavar='FILE',
        help='Preprocess URL list file (extract and cache m3u8 URLs)'
    )
    mode_group.add_argument(
        '--batch',
        action='store_true',
        help='Batch download mode (source should be cache file)'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output filename or cache file path'
    )
    parser.add_argument(
        '--quality', '-q',
        choices=['360p', '480p', '720p', '1080p', '2160p'],
        default='1080p',
        help='Video quality preference (default: 1080p)'
    )

    # Subtitle options
    parser.add_argument(
        '--subtitles', '-s',
        action='store_true',
        default=True,
        help='Download and embed subtitles (default: enabled, use --no-subtitles to disable)'
    )
    parser.add_argument(
        '--no-subtitles',
        action='store_false',
        dest='subtitles',
        help='Disable subtitle download'
    )
    parser.add_argument(
        '--subtitles-only',
        action='store_true',
        help='Download subtitles only without video'
    )
    parser.add_argument(
        '--subtitle-lang',
        default='zh-TW',
        help='Subtitle language code (default: zh-TW for Chinese Taiwan)'
    )

    # Batch options
    parser.add_argument(
        '--episodes', '-e',
        help='Episode selection for batch mode (e.g., "1-3" or "1,3,5")'
    )
    parser.add_argument(
        '--season',
        type=int,
        default=1,
        help='Season number for preprocessing (default: 1)'
    )

    # General options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch graphical user interface'
    )

    args = parser.parse_args()

    # Launch GUI if requested
    if args.gui:
        from thechosen_downloader.gui import main as gui_main
        gui_main()
        return 0

    # Validate arguments
    if not args.preprocess and not args.sources:
        parser.error("at least one source is required unless using --preprocess")

    # Execute appropriate mode
    try:
        if args.preprocess:
            return preprocess_mode(args)
        elif args.batch:
            return batch_mode(args)
        elif len(args.sources) > 1:
            return multi_download_mode(args)
        else:
            return single_download_mode(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def preprocess_mode(args):
    """Preprocessing mode - extract and cache m3u8 URLs"""
    if not args.output:
        print("Error: --output required for preprocessing mode", file=sys.stderr)
        return 1

    print(f"Preprocessing URLs from: {args.preprocess}")
    print(f"Output cache file: {args.output}")
    print(f"Season: {args.season}\n")

    preprocessor = Preprocessor(verbose=args.verbose, rate_limit=1.5)
    success = preprocessor.process_url_list(
        url_list_file=args.preprocess,
        cache_file=args.output,
        season=args.season,
    )

    return 0 if success else 1


def multi_download_mode(args):
    """Multi-URL download mode - download multiple episodes"""
    sources = args.sources

    print(f"Downloading {len(sources)} episode(s)\n")

    downloader = VideoDownloader(verbose=args.verbose)
    extractor = URLExtractor(verbose=args.verbose)
    failed = []

    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] Processing: {source}")

        should_cache = False
        m3u8_url = None
        title = None
        error_message = None

        # Extract URL if needed
        if Path(source).exists():
            # Extract from file
            print(f"  Extracting URL from file...")
            m3u8_url, title, error_message = extractor.extract_from_file(source)
            should_cache = True
        elif source.startswith('http'):
            if 'watch.thechosen.tv' in source and 'hls.m3u8' not in source:
                # Extract m3u8 from episode page
                print(f"  Extracting URL from page...")
                m3u8_url, title, error_message = extractor.extract_from_url(source)
                should_cache = True
            else:
                # Direct m3u8 URL
                m3u8_url = source
        else:
            print(f"  Error: Invalid source: {source}")
            failed.append(source)
            continue

        if not m3u8_url:
            print(f"  Error: Failed to extract m3u8 URL. Reason: {error_message}")
            failed.append(source)
            continue

        # Cache if extraction occurred
        if should_cache:
            _save_to_auto_cache(source, m3u8_url, title, verbose=args.verbose)

        # Determine output filename
        if args.output:
            # If custom output provided, use it for first file and auto-number others
            if i == 1:
                output_path = args.output
            else:
                base, ext = args.output.rsplit('.', 1) if '.' in args.output else (args.output, 'mp4')
                output_path = f"{base}_{i}.{ext}"
        else:
            output_path = f"{title}.mp4" if title else f"video_{i}.mp4"

        print(f"  Downloading to: {output_path}")

        # Download
        success = downloader.download(
            url=m3u8_url,
            output_path=output_path,
            quality=args.quality,
            subtitles=args.subtitles or args.subtitles_only,
            subtitle_lang=args.subtitle_lang,
            subtitles_only=args.subtitles_only,
        )

        if not success:
            failed.append(source)
            print(f"  Failed!")

    # Summary
    print(f"\n\nDownload complete:")
    print(f"  Successful: {len(sources) - len(failed)}")
    print(f"  Failed: {len(failed)}")
    if failed:
        print(f"  Failed sources: {failed}")

    return 0 if not failed else 1


def batch_mode(args):
    """Batch download mode - download from cache"""
    cache_file = args.sources[0]

    if not Path(cache_file).exists():
        print(f"Error: Cache file not found: {cache_file}", file=sys.stderr)
        return 1

    # Load cache
    cache = Cache(cache_file)
    if not cache.load():
        print(f"Error: Failed to load cache from {cache_file}", file=sys.stderr)
        return 1

    # Get episodes to download
    if args.episodes:
        episodes = parse_episode_selection(args.episodes, cache)
    else:
        episodes = cache.get_all_episodes()

    if not episodes:
        print("No episodes to download")
        return 0

    print(f"Downloading {len(episodes)} episode(s)\n")

    # Download each episode
    downloader = VideoDownloader(verbose=args.verbose)
    failed = []

    for i, episode in enumerate(episodes, 1):
        print(f"\n[{i}/{len(episodes)}] Episode {episode.episode_number}: {episode.title}")

        # Determine output filename
        output_path = f"{episode.title}.mp4"

        # Download
        success = downloader.download(
            url=episode.m3u8_url,
            output_path=output_path,
            quality=args.quality,
            subtitles=args.subtitles or args.subtitles_only,
            subtitle_lang=args.subtitle_lang,
            subtitles_only=args.subtitles_only,
        )

        if not success:
            failed.append(episode.episode_number)
            print(f"Failed to download episode {episode.episode_number}")

    # Summary
    print(f"\n\nDownload complete:")
    print(f"  Successful: {len(episodes) - len(failed)}")
    print(f"  Failed: {len(failed)}")
    if failed:
        print(f"  Failed episodes: {', '.join(map(str, failed))}")

    return 0 if not failed else 1


def _save_to_auto_cache(
    source_url: str,
    m3u8_url: str,
    title: Optional[str],
    verbose: bool = False
) -> None:
    """
    Save extracted URL to automatic cache.

    Args:
        source_url: The original URL or file path provided by user
        m3u8_url: The extracted m3u8 URL
        title: Episode title (if available)
        verbose: Whether to show cache operations
    """
    try:
        from .extractor import URLExtractor

        # Load existing cache
        cache = Cache(AUTO_CACHE_PATH)
        cache.load()

        # Try to extract episode number from title
        episode_number = 1
        if title:
            extractor = URLExtractor()
            extracted_num = extractor.extract_episode_number(title)
            if extracted_num:
                episode_number = extracted_num

        # Create cache entry
        entry = CacheEntry(
            episode_number=episode_number,
            title=title or f"Episode {episode_number}",
            episode_url=source_url,
            m3u8_url=m3u8_url,
        )

        # Add/update entry
        cache.add_episode(entry)

        # Save cache
        if cache.save():
            if verbose:
                print(f"  Cached to: {AUTO_CACHE_PATH}")
                print(f"  Episode: {episode_number} - {title}")
        else:
            if verbose:
                print(f"  Warning: Failed to save cache")

    except Exception as e:
        if verbose:
            print(f"  Warning: Failed to cache URL: {e}")


def single_download_mode(args):
    """Single download mode"""
    source = args.sources[0]
    should_cache = False  # Track if we should cache this extraction
    m3u8_url = None
    title = None
    error_message = None

    # Check if source is a file or URL
    if Path(source).exists():
        # Extract from file
        print(f"Extracting URL from file: {source}")
        extractor = URLExtractor(verbose=args.verbose)
        m3u8_url, title, error_message = extractor.extract_from_file(source)

        if not m3u8_url:
            print(f"Error: Failed to extract m3u8 URL from file. Reason: {error_message}", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"Extracted title: {title}")
            print(f"m3u8 URL: {m3u8_url[:100]}...")

        should_cache = True  # Cache HTML file extractions
        url_to_download = m3u8_url
        default_filename = f"{title}.mp4" if title else "video.mp4"

    elif source.startswith('http'):
        # Check if it's a watch.thechosen.tv URL or direct m3u8
        if 'watch.thechosen.tv' in source and 'hls.m3u8' not in source:
            # Extract m3u8 from episode page
            print(f"Extracting URL from page: {source}")
            extractor = URLExtractor(verbose=args.verbose)
            m3u8_url, title, error_message = extractor.extract_from_url(source)

            if not m3u8_url:
                print(f"Error: Failed to extract m3u8 URL from page. Reason: {error_message}", file=sys.stderr)
                return 1

            should_cache = True  # Cache live URL extractions
            url_to_download = m3u8_url
            default_filename = f"{title}.mp4" if title else "video.mp4"
        else:
            # Direct m3u8 URL - don't cache
            url_to_download = source
            default_filename = "video.mp4"
    else:
        print(f"Error: Invalid source: {source}", file=sys.stderr)
        return 1

    # Automatically cache extracted URL if extraction occurred
    if should_cache and m3u8_url:
        _save_to_auto_cache(source, m3u8_url, title, verbose=args.verbose)

    # Download
    output_path = args.output or default_filename

    if args.subtitles_only:
        print(f"\nDownloading subtitles only\n")
    else:
        print(f"\nDownloading to: {output_path}\n")

    downloader = VideoDownloader(verbose=args.verbose)
    success = downloader.download(
        url=url_to_download,
        output_path=output_path,
        quality=args.quality,
        subtitles=args.subtitles or args.subtitles_only,  # Enable subtitles if subtitles-only
        subtitle_lang=args.subtitle_lang,
        subtitles_only=args.subtitles_only,
    )

    return 0 if success else 1


def parse_episode_selection(selection: str, cache: Cache) -> list:
    """Parse episode selection string"""
    episodes = []

    for part in selection.split(','):
        part = part.strip()

        if '-' in part:
            # Range (e.g., "1-3")
            try:
                start, end = map(int, part.split('-'))
                episodes.extend(cache.get_episodes_in_range(start, end))
            except ValueError:
                print(f"Warning: Invalid range: {part}")
        else:
            # Single episode
            try:
                ep_num = int(part)
                ep = cache.get_episode(ep_num)
                if ep:
                    episodes.append(ep)
                else:
                    print(f"Warning: Episode {ep_num} not found in cache")
            except ValueError:
                print(f"Warning: Invalid episode number: {part}")

    return episodes


if __name__ == '__main__':
    sys.exit(main())
