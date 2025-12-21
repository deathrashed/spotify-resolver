# Scripts

This directory contains shell scripts and AppleScript for installation, testing, and integration.

## Files

### Installation & Setup

- **`install-spotify-resolver.sh`** - Automated installer
  - Checks and installs Python dependencies
  - Creates necessary directories
  - Sets up configuration files
  - Configures logging
  - Verifies installation

### Testing

- **`test-spotify-resolver.sh`** - Comprehensive test suite
  - Tests all input methods
  - Validates error handling
  - Checks configuration loading
  - Tests clipboard integration
  - Color-coded output with pass/fail reporting

### Integration Scripts

**AppleScript Interfaces:**

- **`spotify-album-resolver.applescript`** - Quick resolver (first result)
  - Dialog-based search interface
  - Automatically returns top match
  - Clean output (no warnings/debug info)
  - Fast and simple

- **`spotify-album-selector.applescript`** - Album selector (choose from list)
  - Shows all search results (up to 20)
  - Choose from list dialog
  - Perfect for browsing multiple matches
  - Only copies after selection

- **`spotify-album-interactive-selector.applescript`** - Interactive album selector
  - Full interactive workflow with dialogs
  - Search → select from list → copy
  - Includes "ALL albums" option for copying multiple URLs

- **`spotify-artist-album-selector.applescript`** - Artist → Album selector
  - Two-step interactive workflow
  - Search artist → select artist → browse albums → select album → copy
  - Perfect for exploring artist discographies

## Usage

### Installation

```bash
./scripts/install-spotify-resolver.sh
```

### Testing

```bash
./scripts/test-spotify-resolver.sh
```

### AppleScript Usage

**Quick Resolver (first result):**
```bash
osascript scripts/spotify-album-resolver.applescript
```

**Album Selector (choose from results):**
```bash
osascript scripts/spotify-album-selector.applescript
```

## Making Scripts Executable

If scripts aren't executable:

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.applescript
```
