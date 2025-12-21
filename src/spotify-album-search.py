#!/usr/bin/env python3
"""Interactive album search: search → pick album(s) → copy to clipboard."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

# pyperclip is only needed for interactive mode (copying to clipboard)
try:
    import pyperclip
except ImportError:
    pyperclip = None

from spotify_resolver_utils import (
    create_session,
    get_spotify_token,
    load_config,
    SPOTIFY_SEARCH_URL,
)


def search_albums(query: str, session: requests.Session, token: str, limit: int = 20) -> list[dict]:
    """Search for albums matching the query."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "album", "limit": limit}
    response = session.get(SPOTIFY_SEARCH_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("albums", {}).get("items", [])


def choose_album(albums: list[dict], allow_all: bool = True) -> tuple[Optional[dict], bool]:
    """Display albums and let user choose one or all."""
    if not albums:
        return None, False

    for idx, album in enumerate(albums, start=1):
        artists = ", ".join(artist.get("name", "?") for artist in album.get("artists", []))
        print(f"{idx}. {album.get('name')} — {artists}")

    if allow_all:
        print(f"{len(albums) + 1}. ALL albums (copy all URLs)")

    try:
        choice_input = input(f"\nChoose a number (blank = first): ").strip()
        if not choice_input:
            return albums[0], False

        choice = int(choice_input)

        if allow_all and choice == len(albums) + 1:
            return None, True  # Return None with all=True flag

        if 1 <= choice <= len(albums):
            return albums[choice - 1], False
        print("Choice out of range")
        return None, False
    except ValueError:
        print("Invalid selection")
        return None, False
    except EOFError:
        return None, False


def main() -> None:
    """Interactive workflow: search albums → pick album(s) → copy."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive album search and picker.")
    parser.add_argument("query", nargs="*", help="Search query (optional - will prompt if not provided)")
    parser.add_argument("--limit", type=int, default=20, help="Number of results to show (default: 20)")
    parser.add_argument("--list-only", action="store_true", help="Just list results, don't prompt for selection")
    args = parser.parse_args()

    # Step 1: Get search query
    if args.query:
        query = " ".join(args.query)
    elif not sys.stdin.isatty():
        # Reading from pipe/non-interactive
        query = sys.stdin.read().strip()
    else:
        query = input("Search for albums (artist, album, keywords): ").strip()

    if not query:
        print("Query required")
        raise SystemExit(1)

    # Load config and get token
    config = load_config()
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    if not client_id or not client_secret:
        logging.error("Missing Spotify credentials")
        raise SystemExit(1)

    session = create_session(config)
    token = get_spotify_token(session, client_id, client_secret)
    if not token:
        raise SystemExit(1)

    # Step 2: Search for albums
    if sys.stdin.isatty() and not args.list_only:
        print(f"\nSearching for albums: {query}...")
    albums = search_albums(query, session, token, args.limit)

    if not albums:
        print("No albums found.")
        raise SystemExit(0)

    # If list-only mode (for AppleScript compatibility), just print results
    if args.list_only or not sys.stdin.isatty():
        for idx, album in enumerate(albums, start=1):
            artists = ", ".join(artist.get("name", "?") for artist in album.get("artists", []))
            print(f"{idx}. {album.get('name')} — {artists}")
            print(f"   {album.get('external_urls', {}).get('spotify')}")
            print()
        return

    # Step 3: Interactive mode - let user pick an album (or all)
    print(f"\nFound {len(albums)} album(s). Select one:")
    selected_album, copy_all = choose_album(albums, allow_all=True)

    if copy_all:
        # Copy all album URLs (one per line)
        urls = [album.get("external_urls", {}).get("spotify") for album in albums if album.get("external_urls", {}).get("spotify")]
        urls_text = "\n".join(urls)
        if pyperclip:
            pyperclip.copy(urls_text)
            print(f"\n✅ Copied {len(urls)} album URLs to clipboard!")
        else:
            print(f"\n{len(urls)} album URLs (install pyperclip for clipboard support):")
            print(urls_text)
    elif selected_album:
        # Copy single album URL
        url = selected_album.get("external_urls", {}).get("spotify")
        if url:
            if pyperclip:
                pyperclip.copy(url)
                album_name = selected_album.get("name", "Unknown")
                artists = ", ".join(artist.get("name", "?") for artist in selected_album.get("artists", []))
                print(f"\n✅ Copied to clipboard: {album_name} — {artists}")
                print(f"   {url}")
            else:
                album_name = selected_album.get("name", "Unknown")
                artists = ", ".join(artist.get("name", "?") for artist in selected_album.get("artists", []))
                print(f"\n{album_name} — {artists}")
                print(f"   {url}")
                print("\n(Install pyperclip for clipboard support)")
        else:
            print("No URL available")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
