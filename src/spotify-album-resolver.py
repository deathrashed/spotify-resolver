#!/usr/bin/env python3
"""
Spotify Album Link Resolver

Resolves Spotify album links from band and album names.
Searches Spotify Web API and copies the album URL to clipboard.

Version: 1.0.0
Author: cursor
Created: December 23rd, 2025
"""

import sys
import json
import logging
import argparse
import urllib.parse
import re
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Try to import clipboard functionality
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    # Fallback for macOS using pbcopy
    import subprocess


# Configuration
CONFIG_DIR = Path.home() / ".config" / "spotify-resolver"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = Path.home() / ".local" / "log" / "spotify-resolver"
LOG_FILE = LOG_DIR / "spotify-resolver.log"

# Spotify URLs and API endpoints
SPOTIFY_ALBUM_BASE = "https://open.spotify.com/album/"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stderr)
        ]
    )


def load_config(config_file: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file, creating default if missing."""
    default_config = {
        "timeout": 10,
        "max_retries": 3,
        "retry_delay": 1,
        "default_market": "US",
        "log_level": "INFO",
        "cache_results": True,
        "cache_file": str(CONFIG_DIR / "cache.json"),
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "client_id": None,
        "client_secret": None
    }

    config_path = config_file if config_file else CONFIG_FILE
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Error loading config: {e}. Using defaults.")

    return default_config


def get_spotify_token(session: requests.Session, client_id: str, client_secret: str) -> Optional[str]:
    """Get Spotify access token using Client Credentials flow."""
    import base64

    try:
        logging.debug("Requesting Spotify access token...")

        # Spotify requires Basic Auth with base64 encoded credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'client_credentials'
        }

        response = session.post(
            SPOTIFY_TOKEN_URL,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get('access_token')

        if access_token:
            logging.debug("Successfully obtained access token")
            return access_token
        else:
            logging.error("No access token in response")
            logging.debug(f"Token response: {token_data}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining access token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response status: {e.response.status_code}")
            logging.error(f"Response body: {e.response.text[:500]}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing token response: {e}")
        return None


def save_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True if successful."""
    try:
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(text)
            logging.debug(f"Copied to clipboard using pyperclip: {text[:50]}...")
            return True
        else:
            # macOS fallback using pbcopy
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate(input=text.encode('utf-8'))
            if process.returncode == 0:
                logging.debug(f"Copied to clipboard using pbcopy: {text[:50]}...")
                return True
            else:
                logging.error("Failed to copy to clipboard using pbcopy")
                return False
    except Exception as e:
        logging.error(f"Error copying to clipboard: {e}")
        return False


def create_session(config: Dict[str, Any]) -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()

    retry_strategy = Retry(
        total=config.get("max_retries", 3),
        backoff_factor=config.get("retry_delay", 1),
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        'User-Agent': config.get("user_agent", "Spotify-Resolver/1.0"),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    })

    return session


def search_spotify_album(session: requests.Session, query: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Search Spotify for an album using the official Web API.
    """
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")

    # Check if we have API credentials
    if not client_id or not client_secret:
        logging.error("Spotify API credentials not configured. Please add client_id and client_secret to config.json")
        return None

    # Get access token
    access_token = get_spotify_token(session, client_id, client_secret)
    if not access_token:
        logging.error("Failed to obtain Spotify access token")
        return None

    # Build search query
    # Clean query - keep artist: and album: prefixes if present
    search_query = query

    # Set up search parameters
    params = {
        'q': search_query,
        'type': 'album',
        'limit': 20,
        'market': config.get("default_market", "US")
    }

    try:
        logging.info(f"Searching Spotify API for: {search_query}")

        # Add authorization header
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = session.get(
            SPOTIFY_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=config.get("timeout", 10)
        )
        response.raise_for_status()

        data = response.json()
        albums = data.get('albums', {}).get('items', [])

        if not albums:
            logging.warning(f"No albums found for query: {search_query}")
            return None

        logging.info(f"Found {len(albums)} album(s)")
        return albums[0]  # Return the first (most relevant) result

    except requests.exceptions.Timeout:
        logging.error("Request timed out while searching Spotify")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error searching Spotify: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response status: {e.response.status_code}")
            logging.error(f"Response body: {e.response.text[:200]}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing Spotify response: {e}")
        return None


def build_album_url(album_id: str) -> str:
    """Build Spotify album URL from album ID."""
    return f"{SPOTIFY_ALBUM_BASE}{album_id}"


def parse_input(args: argparse.Namespace) -> str:
    """Parse input from arguments or prompt user."""
    if args.band and args.album:
        return f"artist:{args.band} album:{args.album}"
    elif args.query:
        return args.query
    else:
        # Interactive mode - prompt user
        if sys.stdin.isatty():
            print("Enter band and album name:")
            print("Format: 'Band Name - Album Name' or just paste the text")
            user_input = input("> ").strip()
            if not user_input:
                logging.error("No input provided")
                sys.exit(1)

            # Try to parse "Band - Album" format
            if " - " in user_input:
                parts = user_input.split(" - ", 1)
                return f"artist:{parts[0].strip()} album:{parts[1].strip()}"
            else:
                return user_input
        else:
            # Read from stdin (for piping)
            user_input = sys.stdin.read().strip()
            if not user_input:
                logging.error("No input from stdin")
                sys.exit(1)
            return user_input


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Resolve Spotify album links from band and album names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --band "Metallica" --album "Master of Puppets"
  %(prog)s --query "artist:Metallica album:Master of Puppets"
  echo "Metallica - Master of Puppets" | %(prog)s
  %(prog)s  # Interactive mode
        """
    )

    parser.add_argument(
        '--band', '-b',
        help='Band/artist name'
    )
    parser.add_argument(
        '--album', '-a',
        help='Album name'
    )
    parser.add_argument(
        '--query', '-q',
        help='Full search query (e.g., "artist:Metallica album:Master of Puppets")'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--no-clipboard',
        action='store_true',
        help='Print URL instead of copying to clipboard'
    )
    parser.add_argument(
        '--config',
        type=str,
        help=f'Path to config file (default: {CONFIG_FILE})'
    )

    args = parser.parse_args()

    # Load config
    config_file_path = Path(args.config) if args.config else CONFIG_FILE
    config = load_config(config_file_path)

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Spotify Album Resolver v1.0.0")
    logger.info("=" * 60)

    try:
        # Parse input
        query = parse_input(args)
        logger.info(f"Search query: {query}")

        # Create session
        session = create_session(config)

        # Search Spotify
        album = search_spotify_album(session, query, config)

        if not album:
            logger.error("Album not found")
            print("❌ Album not found on Spotify", file=sys.stderr)
            sys.exit(1)

        # Extract album info
        album_id = album.get('id')
        album_name = album.get('name', 'Unknown')
        artists = [artist.get('name', 'Unknown') for artist in album.get('artists', [])]
        artist_name = ', '.join(artists)

        if not album_id:
            logger.error("No album ID in response")
            print("❌ Invalid response from Spotify", file=sys.stderr)
            sys.exit(1)

        # Build URL
        album_url = build_album_url(album_id)

        logger.info(f"Found album: {artist_name} - {album_name}")
        logger.info(f"Album URL: {album_url}")

        # Copy to clipboard or print
        if args.no_clipboard:
            print(album_url)
        else:
            if save_to_clipboard(album_url):
                print(f"✅ Copied to clipboard: {artist_name} - {album_name}")
                print(f"   {album_url}")
                logger.info("Successfully copied URL to clipboard")
            else:
                print(f"❌ Failed to copy to clipboard")
                print(f"   URL: {album_url}")
                logger.error("Failed to copy to clipboard")
                sys.exit(1)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
