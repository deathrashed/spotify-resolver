#!/usr/bin/env python3
"""Interactive artist search with beautiful Gum UI: search → pick artist → browse albums → pick album → copy."""
from __future__ import annotations

import logging
import subprocess
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


def gum_available() -> bool:
    """Check if gum is installed."""
    try:
        # Use --version flag (not 'version' command)
        result = subprocess.run(["gum", "--version"], capture_output=True, check=True, shell=False)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Also try with full path if available
        import shutil
        gum_path = shutil.which("gum")
        if gum_path:
            try:
                subprocess.run([gum_path, "--version"], capture_output=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, OSError):
                pass
        return False


def gum_input(prompt: str, placeholder: str = "") -> Optional[str]:
    """Get user input using gum. Returns the user's input."""
    cmd = ["gum", "input", "--prompt", prompt]
    if placeholder:
        cmd.extend(["--placeholder", placeholder])

    # Add styling to the prompt
    cmd.extend([
        "--prompt.foreground", "212",
        "--placeholder.foreground", "240",
        "--cursor.foreground", "212"
    ])

    # Gum input outputs to stdout - we need to capture it but allow TTY access
    try:
        process = subprocess.Popen(
            cmd,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True
        )
        stdout, _ = process.communicate()
        if process.returncode == 0:
            return stdout.strip()
    except Exception:
        pass
    return None


def gum_choose(items: list[str], header: str = "") -> Optional[str]:
    """Let user choose from a list using gum. Returns the selected item."""
    if not items:
        return None

    cmd = ["gum", "choose"]
    if header:
        cmd.extend(["--header", header])

    # Add beautiful styling to the choose menu
    cmd.extend([
        "--header.foreground", "212",
        "--cursor.foreground", "212",
        "--selected.foreground", "48",
        "--item.foreground", "7",
        "--cursor", "▶ ",
        "--selected-prefix", "✓ ",
        "--unselected-prefix", "  ",
        "--height", "15"
    ])

    cmd.extend(items)

    # Gum choose displays UI and outputs selection to stdout
    try:
        process = subprocess.Popen(
            cmd,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True
        )
        stdout, _ = process.communicate()
        if process.returncode == 0:
            selected = stdout.strip()
            return selected if selected else None
    except Exception as e:
        logging.debug(f"Gum choose failed: {e}")
    return None


def gum_style(text: str, **kwargs) -> None:
    """Style text using gum and print it directly."""
    cmd = ["gum", "style"]

    # Add style flags based on kwargs
    if kwargs.get("bold"):
        cmd.append("--bold")
    if kwargs.get("faint"):
        cmd.append("--faint")
    if kwargs.get("italic"):
        cmd.append("--italic")
    if kwargs.get("underline"):
        cmd.append("--underline")
    if kwargs.get("strikethrough"):
        cmd.append("--strikethrough")

    color = kwargs.get("foreground") or kwargs.get("color")
    if color:
        cmd.extend(["--foreground", color])

    bg = kwargs.get("background")
    if bg:
        cmd.extend(["--background", bg])

    # Border styling
    border = kwargs.get("border")
    if border:
        cmd.extend(["--border", border])
        border_fg = kwargs.get("border_foreground")
        if border_fg:
            cmd.extend(["--border-foreground", border_fg])
        border_bg = kwargs.get("border_background")
        if border_bg:
            cmd.extend(["--border-background", border_bg])

    # Padding and margin
    padding = kwargs.get("padding")
    if padding:
        cmd.extend(["--padding", padding])

    margin = kwargs.get("margin")
    if margin:
        cmd.extend(["--margin", margin])

    # Alignment
    align = kwargs.get("align")
    if align:
        cmd.extend(["--align", align])

    # Width
    width = kwargs.get("width")
    if width:
        cmd.extend(["--width", str(width)])

    # Add the text to style as arguments
    cmd.append(text)

    # Run and print the styled output
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout, end="")
        else:
            print(text, end="")
    except Exception:
        print(text, end="")


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
        "include_groups": "album",
        "limit": limit,
        "market": "US"
    }
    response = session.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("items", [])


def format_artist_choice(artist: dict) -> str:
    """Format artist for display in gum choose."""
    name = artist.get("name", "?")
    followers = artist.get("followers", {}).get("total", 0)
    genres = ", ".join(artist.get("genres", [])[:2])

    if followers > 0:
        if followers >= 1000000:
            followers_str = f"{followers / 1000000:.1f}M"
        elif followers >= 1000:
            followers_str = f"{followers / 1000:.1f}K"
        else:
            followers_str = str(followers)

        info = f"({followers_str} followers"
        if genres:
            info += f", {genres}"
        info += ")"
        return f"{name} {info}"
    return name


def format_album_choice(album: dict) -> str:
    """Format album for display in gum choose."""
    name = album.get("name", "?")
    release_date = album.get("release_date", "")
    year = release_date[:4] if release_date else "?"
    return f"{name} ({year})"


def main() -> None:
    """Interactive workflow with Gum UI: search artist → pick artist → browse albums → pick album → copy."""
    use_gum = gum_available()

    if not use_gum:
        print("⚠️  Gum is not installed. Install with: brew install gum")
        print("Falling back to basic input...")

    # Step 1: Get search query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        if use_gum:
            # Style the header with a nice border
            gum_style("🎵 Spotify Artist Resolver",
                     foreground="212",
                     bold=True,
                     border="rounded",
                     border_foreground="212",
                     padding="1 3",
                     margin="1 0",
                     align="center")
            print()
            query = gum_input("🎤 Search for artist: ", "Artist name...")
            if not query:
                print("No query provided")
                raise SystemExit(1)
        else:
            print("🎵 Spotify Artist Resolver\n")
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
    if use_gum:
        gum_style("🔍 Searching Spotify...",
                 foreground="212",
                 faint=True,
                 italic=True,
                 padding="0 2")
        print()
    else:
        print(f"\nSearching for artists: {query}...")

    artists = search_artists(query, session, token)

    if not artists:
        if use_gum:
            gum_style("❌ No artists found",
                     foreground="196",
                     bold=True,
                     border="rounded",
                     border_foreground="196",
                     padding="1 2",
                     margin="1 0")
            print()
        else:
            print("No artists found.")
        raise SystemExit(0)

    # Step 3: Let user pick an artist
    artist_choices = [format_artist_choice(artist) for artist in artists]

    if use_gum:
        gum_style(f"✨ Found {len(artists)} artist(s)",
                 foreground="48",
                 bold=True,
                 padding="0 2",
                 margin="1 0")
        print()
        header = f"🎤 Select an artist ({len(artists)} found):"
        selected_artist_str = gum_choose(artist_choices, header=header)
    else:
        print(f"\nFound {len(artists)} artist(s). Select one:")
        for idx, choice in enumerate(artist_choices, start=1):
            print(f"{idx}. {choice}")
        try:
            choice_input = input("\nChoose a number (blank = first): ").strip()
            selected_idx = int(choice_input) - 1 if choice_input else 0
            if 0 <= selected_idx < len(artists):
                selected_artist_str = artist_choices[selected_idx]
            else:
                selected_artist_str = None
        except (ValueError, KeyboardInterrupt):
            selected_artist_str = None

    if not selected_artist_str:
        raise SystemExit(1)

    # Find selected artist
    selected_artist = None
    for artist in artists:
        if format_artist_choice(artist) == selected_artist_str:
            selected_artist = artist
            break

    if not selected_artist:
        print("Error: Artist not found")
        raise SystemExit(1)

    artist_name = selected_artist.get("name", "Unknown")
    artist_id = selected_artist.get("id")

    if not artist_id:
        print("Error: No artist ID found")
        raise SystemExit(1)

    # Step 4: Get albums by selected artist
    if use_gum:
        gum_style(f"📀 Loading albums by {artist_name}...",
                 foreground="212",
                 faint=True,
                 italic=True,
                 padding="0 2",
                 margin="1 0")
        print()
    else:
        print(f"\nLoading albums by {artist_name}...")

    albums = get_artist_albums(artist_id, session, token)

    if not albums:
        if use_gum:
            gum_style(f"❌ No albums found for {artist_name}",
                     foreground="196",
                     bold=True,
                     border="rounded",
                     border_foreground="196",
                     padding="1 2",
                     margin="1 0")
            print()
        else:
            print(f"No albums found for {artist_name}.")
        raise SystemExit(0)

    # Remove duplicates and sort
    seen = set()
    unique_albums = []
    for album in albums:
        album_id = album.get("id")
        if album_id and album_id not in seen:
            seen.add(album_id)
            unique_albums.append(album)

    unique_albums.sort(key=lambda x: x.get("release_date", ""), reverse=True)

    # Step 5: Let user pick an album
    album_choices = [format_album_choice(album) for album in unique_albums[:50]]
    album_choices.append("🎵 ALL albums (copy all URLs)")

    if use_gum:
        gum_style(f"✨ Found {len(unique_albums)} album(s) by {artist_name}",
                 foreground="48",
                 bold=True,
                 padding="0 2",
                 margin="1 0")
        print()
        header = f"📀 Select an album ({len(unique_albums)} found, or choose ALL):"
        selected_album_str = gum_choose(album_choices, header=header)
    else:
        print(f"\nFound {len(unique_albums)} album(s) by {artist_name}. Select one:")
        for idx, choice in enumerate(album_choices, start=1):
            print(f"{idx}. {choice}")
        try:
            choice_input = input("\nChoose a number (blank = first): ").strip()
            selected_idx = int(choice_input) - 1 if choice_input else 0
            if 0 <= selected_idx < len(album_choices):
                selected_album_str = album_choices[selected_idx]
            else:
                selected_album_str = None
        except (ValueError, KeyboardInterrupt):
            selected_album_str = None

    if not selected_album_str:
        raise SystemExit(1)

    # Step 6: Handle selection
    if selected_album_str == "🎵 ALL albums (copy all URLs)":
        urls = [album.get("external_urls", {}).get("spotify") for album in unique_albums if album.get("external_urls", {}).get("spotify")]
        urls_text = "\n".join(urls)
        pyperclip.copy(urls_text)
        if use_gum:
            gum_style(f"✅ Copied {len(urls)} album URLs to clipboard!",
                     foreground="48",
                     bold=True,
                     border="rounded",
                     border_foreground="48",
                     padding="1 3",
                     margin="1 0")
            print()
        else:
            print(f"\n✅ Copied {len(urls)} album URLs to clipboard!")
    else:
        # Find selected album
        selected_album = None
        for album in unique_albums:
            if format_album_choice(album) == selected_album_str:
                selected_album = album
                break

        if not selected_album:
            print("Error: Album not found")
            raise SystemExit(1)

        url = selected_album.get("external_urls", {}).get("spotify")
        if url:
            pyperclip.copy(url)
            album_name = selected_album.get("name", "Unknown")

            if use_gum:
                gum_style("✅ Copied to clipboard!",
                         foreground="48",
                         bold=True,
                         border="rounded",
                         border_foreground="48",
                         padding="1 3",
                         margin="1 0",
                         align="center")
                print()
                gum_style(f"📀 {album_name}",
                         foreground="212",
                         bold=True,
                         padding="0 2")
                print()
                gum_style(f"   👤 {artist_name}",
                         foreground="99",
                         faint=True,
                         padding="0 2")
                print()
                gum_style(f"🔗 {url}",
                         foreground="33",
                         italic=True,
                         padding="0 2",
                         margin="0 0 1 0")
                print()
            else:
                print(f"\n✅ Copied to clipboard: {artist_name} - {album_name}")
                print(f"   {url}")
        else:
            print("No URL available")


if __name__ == "__main__":
    main()
