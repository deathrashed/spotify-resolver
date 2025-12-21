#!/usr/bin/env python3
"""Search for artists, then browse their albums and copy one to clipboard."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import pyperclip
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spotify_resolver_utils import (
    create_session,
    get_spotify_token,
    load_config,
    SPOTIFY_SEARCH_URL,
)


def search_artists(query: str, session: requests.Session, token: str, limit: int = 20) -> list[dict]:
    """Search for artists matching the query."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "artist", "limit": limit}
    response = session.get(SPOTIFY_SEARCH_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("artists", {}).get("items", [])


def get_artist_albums(artist_id: str, session: requests.Session, token: str, limit: int = 50) -> list[dict]:
    """Get albums by a specific artist."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "include_groups": "album",  # Only albums, not singles/compilations
        "limit": limit,
        "market": "US"
    }
    response = session.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("items", [])


def choose_from_list(items: list[dict], item_type: str = "item") -> Optional[dict]:
    """Display a numbered list and let user choose one."""
    if not items:
        return None

    for idx, item in enumerate(items, start=1):
        if item_type == "artist":
            name = item.get("name", "?")
            genres = ", ".join(item.get("genres", [])[:3])  # First 3 genres
            followers = item.get("followers", {}).get("total", 0)
            if followers > 0:
                print(f"{idx}. {name} ({followers:,} followers)")
                if genres:
                    print(f"   {genres}")
            else:
                print(f"{idx}. {name}")
        else:  # album
            name = item.get("name", "?")
            artists = ", ".join(artist.get("name", "?") for artist in item.get("artists", []))
            release_date = item.get("release_date", "?")
            print(f"{idx}. {name} — {artists} ({release_date[:4] if release_date else '?'})")

    try:
        choice = int(input(f"\nChoose a number (blank = first): ").strip() or 1)
    except ValueError:
        print("Invalid selection")
        return None
    except EOFError:
        return None

    if 1 <= choice <= len(items):
        return items[choice - 1]
    print("Choice out of range")
    return None


def main() -> None:
    """Main workflow: search artist → pick artist → show albums → pick album → copy."""
    # Step 1: Get search query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Search for artist: ").strip()

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

    # Step 2: Search for artists
    print(f"\nSearching for artists: {query}...")
    artists = search_artists(query, session, token)

    if not artists:
        print("No artists found.")
        raise SystemExit(0)

    # Step 3: Let user pick an artist
    print(f"\nFound {len(artists)} artist(s). Select one:")
    selected_artist = choose_from_list(artists, "artist")

    if not selected_artist:
        raise SystemExit(1)

    artist_name = selected_artist.get("name", "Unknown")
    artist_id = selected_artist.get("id")

    if not artist_id:
        print("Error: No artist ID found")
        raise SystemExit(1)

    # Step 4: Get albums by selected artist
    print(f"\nLoading albums by {artist_name}...")
    albums = get_artist_albums(artist_id, session, token)

    if not albums:
        print(f"No albums found for {artist_name}.")
        raise SystemExit(0)

    # Remove duplicates (same album can appear multiple times with different markets/releases)
    seen = set()
    unique_albums = []
    for album in albums:
        album_id = album.get("id")
        if album_id and album_id not in seen:
            seen.add(album_id)
            unique_albums.append(album)

    # Sort by release date (newest first)
    unique_albums.sort(key=lambda x: x.get("release_date", ""), reverse=True)

    # Step 5: Let user pick an album
    print(f"\nFound {len(unique_albums)} album(s) by {artist_name}. Select one:")
    selected_album = choose_from_list(unique_albums[:50], "album")  # Limit display to 50

    if not selected_album:
        raise SystemExit(1)

    # Step 6: Copy URL to clipboard
    url = selected_album.get("external_urls", {}).get("spotify")
    if url:
        pyperclip.copy(url)
        album_name = selected_album.get("name", "Unknown")
        print(f"\n✅ Copied to clipboard: {artist_name} - {album_name}")
        print(f"   {url}")
    else:
        print("No URL available")


if __name__ == "__main__":
    main()
