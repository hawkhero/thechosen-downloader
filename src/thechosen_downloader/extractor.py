"""URL extraction from The Chosen web pages"""

import re
from pathlib import Path
from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup
import yt_dlp
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class URLExtractor:
    """Extract m3u8 video URLs from The Chosen streaming pages"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def extract_from_url(self, url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract m3u8 URL and episode title from a live episode URL.

        Args:
            url: The episode URL (e.g., https://watch.thechosen.tv/video/...)

        Returns:
            Tuple of (m3u8_url, episode_title, error_message)
        """
        # Use Playwright to capture network requests for m3u8 URLs
        try:
            # Always show status (not just verbose)
            print("  Launching browser...")

            m3u8_url = None
            title = None

            with sync_playwright() as p:
                # Launch browser in headless mode
                try:
                    browser = p.chromium.launch(headless=True)
                except Exception as e:
                    return None, None, f"Failed to launch browser: {e}"

                context = browser.new_context()
                page = context.new_page()

                # Capture network requests
                m3u8_requests = []
                all_requests = []

                def capture_request(request):
                    all_requests.append(request.url)
                    # Look for m3u8 requests
                    if '.m3u8' in request.url:
                        m3u8_requests.append(request.url)
                        if self.verbose:
                            print(f"  Found m3u8 URL: {request.url[:100]}...")

                # Listen to all requests
                page.on("request", capture_request)

                try:
                    # Navigate to page
                    print(f"  Loading page...")
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")

                    # Wait for video player to load
                    print(f"  Waiting for video player...")

                    # Try to wait for video element
                    try:
                        page.wait_for_selector('video', timeout=10000)
                        print(f"  Video player loaded")
                    except PlaywrightTimeout:
                        print(f"  Timeout waiting for video, but continuing...")

                    # Wait a bit more for video to start loading
                    page.wait_for_timeout(5000)

                    # Try to extract m3u8 URL from JavaScript on page
                    if not m3u8_requests:
                        print(f"  Extracting video URL from page...")

                    # Try to get video source from page
                    try:
                        # Check if there's an m3u8 URL in the page HTML
                        html_content = page.content()
                        m3u8_pattern = r'https://[^"\s]+/hls\.m3u8\?[^"\s]+'
                        matches = re.findall(m3u8_pattern, html_content)
                        if matches:
                            m3u8_requests.extend(matches)
                            print(f"  Video URL extracted successfully")
                        else:
                            print(f"  Warning: Could not find video URL")
                    except Exception as e:
                        if self.verbose:
                            print(f"  Error extracting from HTML: {e}")

                    # Try to get title from page
                    try:
                        title_element = page.query_selector('meta[property="og:title"]')
                        if title_element:
                            title = title_element.get_attribute('content')
                        if not title:
                            title = page.title()
                    except:
                        pass

                except PlaywrightTimeout:
                    if self.verbose:
                        print("  Page load timeout, but may have captured m3u8 URL")
                except Exception as e:
                    if self.verbose:
                        print(f"  Error during page load: {e}")
                    browser.close()
                    return None, None, f"Error during page load: {e}"

                browser.close()

                # Use the first m3u8 URL found
                if m3u8_requests:
                    m3u8_url = m3u8_requests[0]

                if self.verbose:
                    print(f"  Title: {title}")
                    if m3u8_url:
                        print(f"  m3u8 URL: {m3u8_url[:100]}...")
                
                if not m3u8_url:
                    return None, title, "No m3u8 URL found in network requests or page content."

                return m3u8_url, title, None

        except Exception as e:
            if self.verbose:
                print(f"Error extracting from URL: {e}")
            return None, None, str(e)

    def extract_from_file(self, file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract m3u8 URL and episode title from a saved HTML file.

        Args:
            file_path: Path to saved HTML file

        Returns:
            Tuple of (m3u8_url, episode_title, error) or (None, None, error) if extraction fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                if self.verbose:
                    print(f"File not found: {file_path}")
                return None, None, f"File not found: {file_path}"

            with open(path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            return self.extract_from_html(html_content)

        except Exception as e:
            if self.verbose:
                print(f"Error reading file: {e}")
            return None, None, str(e)

    def extract_from_html(self, html_content: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract m3u8 URL and episode title from HTML content.

        Args:
            html_content: HTML content as string

        Returns:
            Tuple of (m3u8_url, episode_title, error) or (None, None, error) if extraction fails
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract m3u8 URL
        m3u8_url = self._extract_m3u8_url(soup, html_content)

        # Extract episode title
        title = self._extract_title(soup)

        if self.verbose:
            print(f"Extracted m3u8 URL: {m3u8_url[:100] if m3u8_url else 'None'}...")
            print(f"Extracted title: {title}")
        
        if not m3u8_url:
            return None, title, "m3u8 URL not found in HTML"

        return m3u8_url, title, None

    def _extract_m3u8_url(self, soup: BeautifulSoup, html_content: str) -> Optional[str]:
        """Extract m3u8 URL from page using multiple strategies"""

        # Strategy 1: Check og:url meta tag
        og_url = soup.find('meta', property='og:url')
        if og_url and og_url.get('content'):
            url = og_url['content']
            if 'hls.m3u8' in url and 'viewerToken=' in url:
                return url

        # Strategy 2: Search for m3u8 URLs in HTML using regex
        m3u8_pattern = r'https://[^"\s]+/hls\.m3u8\?viewerToken=[^"\s]+'
        matches = re.findall(m3u8_pattern, html_content)
        if matches:
            return matches[0]

        # Strategy 3: Look for m3u8 URLs in script tags
        for script in soup.find_all('script'):
            if script.string:
                matches = re.findall(m3u8_pattern, script.string)
                if matches:
                    return matches[0]

        return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract episode title from page"""

        # Strategy 1: Check og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']

        # Strategy 2: Check title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        return None

    def extract_episode_number(self, title: str) -> Optional[int]:
        """
        Extract episode number from title.

        Args:
            title: Episode title (e.g., "Season 1 Episode 1: I Have Called You By Name")

        Returns:
            Episode number or None if not found
        """
        # Match patterns like "Episode 1", "Ep 1", "E1"
        patterns = [
            r'Episode\s+(\d+)',
            r'Ep\s+(\d+)',
            r'E(\d+)',
            r'第\s*(\d+)\s*集',  # Chinese pattern
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None
