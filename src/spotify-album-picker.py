#!/usr/bin/env python3
"""Search for albums and prompt to pick one to copy."""
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


def search_albums(query: str, session: requests.Session, token: str, limit: int = 8) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "album", "limit": limit}
    response = session.get(SPOTIFY_SEARCH_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("albums", {}).get("items", [])


def choose_album(albums: list[dict]) -> Optional[dict]:
    for idx, album in enumerate(albums, start=1):
        artists = ", ".join(artist.get("name", "?") for artist in album.get("artists", []))
        print(f"{idx}. {album.get('name')} — {artists}")
    try:
        choice = int(input("Choose a number (blank = first): ").strip() or 1)
    except ValueError:
        print("Invalid selection")
        return None
    if 1 <= choice <= len(albums):
        return albums[choice - 1]
    print("Choice out of range")
    return None


def main() -> None:
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Search terms (artist, album): ").strip()
    if not query:
        print("Query required")
        raise SystemExit(1)

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

    albums = search_albums(query, session, token)
    if not albums:
        print("No albums found")
        raise SystemExit(0)

    picked = choose_album(albums)
    if not picked:
        raise SystemExit(1)

    url = picked.get("external_urls", {}).get("spotify")
    if url:
        pyperclip.copy(url)
        print(f"Copied {url}")
    else:
        print("No URL available")


if __name__ == "__main__":
    main()
