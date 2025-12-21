# Source Code

This directory contains the core Python source code for Spotify Album Resolver.

## Files

### Main Scripts

- **`spotify-album-resolver.py`** - Main resolver script
  - Entry point for album searching
  - Handles CLI arguments and input methods
  - Manages Spotify API authentication
  - Clipboard integration

- **`spotify-album-search.py`** - Search helper
  - Returns numbered list of search results
  - Useful for exploring matches
  - Displays artist, album, and URL

- **`spotify-album-picker.py`** - Interactive album picker
  - User-friendly selection interface
  - Interactive search and selection
  - Copies chosen result to clipboard

- **`spotify-artist-search.py`** - Artist search
  - Search for artists by name
  - Lists artists with followers, genres, and Spotify links
  - Useful for finding artist info

- **`spotify-artist-album-picker.py`** - Artist → Albums workflow
  - Search for artists
  - Pick an artist from results
  - Browse all albums by that artist
  - Pick an album to copy to clipboard
  - Perfect for exploring an artist's discography

- **`spotify-album-search-gum.py`** - Interactive album search (Gum UI)
  - Beautiful styled UI with Gum
  - Interactive search and selection
  - Falls back to basic input if Gum isn't installed
  - Same functionality as `spotify-album-search.py` with enhanced visuals

- **`spotify-artist-search-gum.py`** - Interactive artist search (Gum UI)
  - Beautiful styled UI with Gum
  - Search artist → select artist → browse albums → select album
  - Falls back to basic input if Gum isn't installed
  - Same functionality as `spotify-artist-album-picker.py` with enhanced visuals

### Utilities

- **`spotify_resolver_utils.py`** - Shared utility functions
  - Configuration loading
  - HTTP session management
  - Spotify OAuth token handling
  - Common constants and helpers

## Usage

All scripts should be run from the project root or using absolute paths:

```bash
# From project root
python3 src/spotify-album-resolver.py --band "Metallica" --album "Master of Puppets"

# Or using absolute path (adjust to your installation location)
python3 /path/to/spotify-resolver/src/spotify-album-resolver.py --query "..."

## Script Comparison

- **`spotify-album-resolver.py`** - Fast, gets first result, copies to clipboard
- **`spotify-album-search.py`** - Lists multiple album results (supports `--list-only` for scripting)
- **`spotify-album-search-gum.py`** - Interactive album search with beautiful Gum UI
- **`spotify-album-picker.py`** - Lists albums, lets you pick one, copies to clipboard
- **`spotify-artist-search.py`** - Lists artists with info (no clipboard)
- **`spotify-artist-search-gum.py`** - Interactive artist → albums workflow with beautiful Gum UI
- **`spotify-artist-album-picker.py`** - Search artist → pick artist → browse albums → pick album → copy

## Usage Examples

```bash
# Quick album lookup (first result)
python3 src/spotify-album-resolver.py --band "Metallica" --album "Master of Puppets"

# List album search results
python3 src/spotify-album-search.py "Pink Floyd Dark Side"

# Interactive album picker
python3 src/spotify-album-picker.py "The Beatles"

# List artists
python3 src/spotify-artist-search.py "Radiohead"

# Browse artist's albums (interactive)
python3 src/spotify-artist-album-picker.py "The Beatles"
```

## Development

When modifying these files:
1. Follow PEP 8 style guidelines
2. Add docstrings to all functions
3. Update tests in `tests/`
4. Run linter: `pylint src/*.py`
5. Test thoroughly before committing
