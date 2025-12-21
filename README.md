<div align="center">

# Spotify Resolver

<img src="assets/spotify-resolver.png" alt="Spotify Album Resolver" width="256" height="256">

**A powerful CLI tool for resolving Spotify album links with one command**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Integration](#-integration) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

**Spotify Album Resolver** is a production-ready command-line tool that searches Spotify for albums and copies their URLs to your clipboard. Perfect for integration with download managers, music cataloging systems, or any workflow that needs quick access to Spotify album links.

## ✨ Features

- 🔍 **Multiple Search Methods** - Command-line flags, interactive prompts, piped input, or direct queries
- 📋 **Smart Clipboard** - Automatic clipboard integration with macOS fallback support
- 🔄 **Robust Error Handling** - Automatic retries, timeout handling, and comprehensive logging
- ⚙️ **Fully Configurable** - JSON configuration with sensible defaults
- 🎨 **Clean Output** - No GUI windows, just clean terminal output with emoji indicators
- 🔌 **Integration Ready** - Works with Keyboard Maestro, Raycast, Alfred, AppleScript, and shell scripts
- 🧪 **Well Tested** - Comprehensive test suite included

---

## 📦 Installation

### Quick Install (Recommended)

Install the project anywhere you like:

```bash
# Clone or download the repository to your preferred location
git clone <repo-url> ~/spotify-resolver  # or any path you prefer
cd ~/spotify-resolver

# Run the installer
./scripts/install-spotify-resolver.sh
```

**Note:** The scripts work from any installation location. If you place it in a different path, update the paths in documentation examples accordingly.

The installer will:
- ✅ Check and install required Python packages
- ✅ Create necessary directories
- ✅ Set up configuration files
- ✅ Configure logging
- ✅ Verify the installation

### Manual Installation

```bash
# Install dependencies
pip3 install requests pyperclip

# Create directories
mkdir -p ~/.config/spotify-resolver
mkdir -p ~/.local/log/spotify-resolver

# Make scripts executable (adjust path to your installation location)
chmod +x /path/to/spotify-resolver/src/*.py
chmod +x /path/to/spotify-resolver/scripts/*.sh
```

### Spotify API Setup (Required)

This tool uses the official Spotify Web API and requires credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Copy your **Client ID** and **Client Secret**
5. Edit `~/.config/spotify-resolver/config.json`:

```json
{
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here"
}
```

A template is available at `config.json.example` in the project root.

---

## 🚀 Usage

### Basic Commands

```bash
# Method 1: Separate band and album arguments
spotify-album-resolver.py --band "Metallica" --album "Master of Puppets"

# Method 2: Search query
spotify-album-resolver.py --query "artist:Metallica album:Master of Puppets"

# Method 3: Interactive mode (prompts for input)
spotify-album-resolver.py

# Method 4: Pipe input from other commands
echo "Metallica - Master of Puppets" | spotify-album-resolver.py
```

### Search Helpers

#### List Search Results

Prints a numbered list of matching albums:

```bash
spotify-album-search.py "Metallica"
```

Output:
```
1. Metallica - Master of Puppets - https://open.spotify.com/album/...
2. Metallica - Ride the Lightning - https://open.spotify.com/album/...
3. Metallica - ...And Justice for All - https://open.spotify.com/album/...
```

#### Interactive Album Picker

Choose from search results interactively:

```bash
spotify-album-picker.py
# Or pass search terms:
spotify-album-picker.py Metallica Master
```

#### Beautiful UI with Gum 🎨

For a visually stunning experience, use the Gum-powered versions:

```bash
# Beautiful album search with interactive UI
python3 src/spotify-album-search-gum.py "Pink Floyd"

# Beautiful artist → albums workflow
python3 src/spotify-artist-search-gum.py "The Beatles"
```

**Features:**
- ✨ Beautiful styled prompts and selections
- 🎨 Color-coded status messages
- 📋 Interactive menus with Gum's elegant UI
- 🚀 Same functionality, better visuals

**Install Gum:**
```bash
brew install gum
```

These scripts automatically fall back to basic input if Gum isn't installed.

#### Artist Search

List artists matching your search:

```bash
spotify-artist-search.py "Pink Floyd"
spotify-artist-search.py "Radiohead" --limit 5
```

Output shows artist name, followers, genres, and Spotify link.

#### Artist → Albums Workflow

Browse an artist's full discography:

```bash
spotify-artist-album-picker.py "The Beatles"
# or just:
spotify-artist-album-picker.py  # (prompts for artist name)
```

**Workflow:**
1. Search for artist → shows list of matching artists
2. Pick an artist → loads all their albums
3. Browse albums → shows numbered list (sorted by release date, newest first)
4. Pick an album → copies URL to clipboard

Perfect for exploring an artist's complete discography!

### Command-Line Options

```
--band, -b          Band/artist name
--album, -a         Album name
--query, -q         Full search query
--verbose, -v       Enable verbose logging
--no-clipboard      Print URL instead of copying
--config            Path to custom config file
--help              Show help message
```

---

## ⊕ Integration

<details>
<summary><b>AppleScript Integration</b></summary>

### Two AppleScript Options

#### Option 1: Quick Resolver (First Result)

Fast single-result resolver - automatically copies the top match:

```bash
# From your installation directory
osascript scripts/spotify-album-resolver.applescript

# Or with full path
osascript /path/to/spotify-resolver/scripts/spotify-album-resolver.applescript
```

**Features:**
- ⚡ Fast - gets top result immediately
- ◎ Clean output - no warnings or debug info
- ⊙ Simple dialog showing artist, album, and URL
- ▣ Automatically copies to clipboard

**Best for:** When you know exactly what you're searching for

#### Option 2: Album Selector (Choose from List)

Shows all results and lets you select one:

```bash
# From your installation directory
osascript scripts/spotify-album-selector.applescript

# Or with full path
osascript /path/to/spotify-resolver/scripts/spotify-album-selector.applescript
```

**Features:**
- ▦ Shows all search results (up to 20 albums)
- ▣ Choose from list dialog
- ◎ Clean formatting: "Artist - Album"
- ⊙ Only copies after you select
- ⊕ Perfect for browsing multiple matches

**Best for:** When you want to browse and choose from multiple results

**Setting up as macOS Service:**

1. Open **Automator**
2. Create new **Quick Action**
3. Set "Workflow receives" to **no input** in **any application**
4. Add **Run AppleScript** action
5. Choose which script to use:

**For Quick Resolver:**
```applescript
do shell script "osascript /path/to/spotify-resolver/scripts/spotify-album-resolver.applescript"
```

**For Album Selector:**
```applescript
do shell script "osascript /path/to/spotify-resolver/scripts/spotify-album-selector.applescript"
```

**Note:** Replace `/path/to/spotify-resolver` with your actual installation path. The AppleScript files auto-detect their location, so this path just needs to point to the script file itself.

6. Save as "Spotify Album Resolver" (or "Spotify Album Selector")
7. Go to **System Preferences** → **Keyboard** → **Shortcuts** → **Services**
8. Assign a keyboard shortcut (e.g., ⌥⌘S for quick, ⌥⌘⇧S for selector)

**Usage:** Press your keyboard shortcut anywhere, search, get result!

</details>

<details>
<summary><b>Keyboard Maestro Integration</b></summary>

### Method 1: Simple Prompt (Recommended)

1. Open Keyboard Maestro Editor
2. Create new macro (⌘N)
3. Set trigger: **Hot Key** (e.g., ⌥⌘S)
4. Add action: **Execute a Shell Script**
5. Configure:
   ```
   Script: /path/to/spotify-resolver/src/spotify-album-resolver.py
   Input: Prompt for User Input
     - Prompt: "Enter Band - Album"
     - Title: "Spotify Album Resolver"
   Output: Ignore
   ```
6. Save the macro

**Usage:** Press hotkey → Enter "Metallica - Master of Puppets" → URL copied!

### Method 2: Use Selected Text

1. Create new macro
2. Set trigger: **Hot Key** (e.g., ⌥⌘⇧S)
3. Add action: **Get Selected Text** → Save to variable `SelectedText`
4. Add action: **Execute a Shell Script**:
   ```bash
   echo "$KMVAR_SelectedText" | /path/to/spotify-resolver/src/spotify-album-resolver.py
   ```
5. Save the macro

**Usage:** Select text like "Metallica - Master of Puppets" → Press hotkey → URL copied!

### Method 3: Separate Band/Album Fields

1. Create new macro
2. Set trigger: **Hot Key**
3. Add action: **Prompt for User Input**:
   - Variable `Band`: "Band Name"
   - Variable `Album`: "Album Name"
4. Add action: **Execute a Shell Script**:
   ```bash
   /path/to/spotify-resolver/src/spotify-album-resolver.py --band "$KMVAR_Band" --album "$KMVAR_Album"
   ```
5. Save the macro

**Usage:** Press hotkey → Enter band and album separately → URL copied!

### Method 4: AppleScript Interface

#### Quick Resolver (first result):
1. Create new macro
2. Set trigger: **Hot Key**
3. Add action: **Execute AppleScript**:
   ```applescript
   do shell script "osascript /path/to/spotify-resolver/scripts/spotify-album-resolver.applescript"
   ```

#### Album Selector (choose from list):
1. Create new macro
2. Set trigger: **Hot Key** (different from above)
3. Add action: **Execute AppleScript**:
   ```applescript
   do shell script "osascript /path/to/spotify-resolver/scripts/spotify-album-selector.applescript"
   ```

**Usage:** Press hotkey → Dialog appears → Search → Select (if using selector) → Copy!

</details>

<details>
<summary><b>Raycast Integration</b></summary>

### Simple Script Command

1. Open Raycast
2. Go to **Extensions** → **Create Extension** → **Script Command**
3. Fill in the form:
   - **Name:** Spotify Album Resolver
   - **Filename:** `spotify-album-resolver`
   - **Description:** Resolve Spotify album link
   - **Icon:** 🎵
   - **Script:**
     ```bash
     #!/bin/bash

     # Required parameters:
     # @raycast.schemaVersion 1
     # @raycast.title Spotify Album Resolver
     # @raycast.mode silent
     # @raycast.icon 🎵

     # Optional parameters:
     # @raycast.argument1 { "type": "text", "placeholder": "Band - Album" }
     # @raycast.description Resolve Spotify album link and copy to clipboard

     /path/to/spotify-resolver/src/spotify-album-resolver.py --query "$1"
     ```
4. Save and assign hotkey

**Usage:** Open Raycast → Type "Spotify" → Enter "Metallica - Master of Puppets" → Done!

### Script with Separate Arguments

```bash
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Spotify Album Resolver
# @raycast.mode silent
# @raycast.icon 🎵

# Optional parameters:
# @raycast.argument1 { "type": "text", "placeholder": "Band Name" }
# @raycast.argument2 { "type": "text", "placeholder": "Album Name" }

/path/to/spotify-resolver/src/spotify-album-resolver.py --band "$1" --album "$2"
```

</details>

<details>
<summary><b>Shell Integration (Zsh/Bash)</b></summary>

### Add Shell Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Spotify album link resolver
alias splink='/path/to/spotify-resolver/src/spotify-album-resolver.py'

# Or as a function for better syntax (adjust path):
splink() {
    if [ $# -eq 2 ]; then
        /path/to/spotify-resolver/src/spotify-album-resolver.py --band "$1" --album "$2"
    elif [ $# -eq 1 ]; then
        /path/to/spotify-resolver/src/spotify-album-resolver.py --query "$1"
    else
        /path/to/spotify-resolver/src/spotify-album-resolver.py
    fi
}
```

Reload shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Usage:**
```bash
# Two arguments
splink "Metallica" "Master of Puppets"

# Single query
splink "Metallica - Master of Puppets"

# Interactive
splink
```

</details>

<details>
<summary><b>Alfred Integration</b></summary>

### Workflow Setup

1. Open Alfred Preferences
2. Go to **Workflows** tab
3. Click **+** → **Blank Workflow**
4. Name it "Spotify Album Resolver"
5. Add **Keyword Input**:
   - Keyword: `spotify`
   - Argument: Required
   - Placeholder: "Band - Album"
6. Add **Run Script** action (connect to keyword):
   - Language: `/bin/bash`
   - Script:
     ```bash
     /path/to/spotify-resolver/src/spotify-album-resolver.py --query "{query}"
     ```
7. Save workflow

**Usage:** Open Alfred → Type "spotify Metallica Master of Puppets" → Enter!

</details>

---

## ⚙️ Configuration

### Configuration File

Location: `~/.config/spotify-resolver/config.json`

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "timeout": 10,
  "max_retries": 3,
  "retry_delay": 1,
  "default_market": "US",
  "log_level": "INFO",
  "cache_results": true,
  "cache_file": "~/.config/spotify-resolver/cache.json",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `client_id` | `null` | **Required** - Your Spotify API client ID |
| `client_secret` | `null` | **Required** - Your Spotify API client secret |
| `timeout` | `10` | Request timeout in seconds |
| `max_retries` | `3` | Maximum retry attempts for failed requests |
| `retry_delay` | `1` | Delay between retries (seconds) |
| `default_market` | `"US"` | Default market for search (ISO country code) |
| `log_level` | `"INFO"` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `cache_results` | `true` | Enable result caching |

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
./scripts/test-spotify-resolver.sh  # or /path/to/spotify-resolver/scripts/test-spotify-resolver.sh
```

The test suite validates:
- ✅ Basic search functionality
- ✅ Multiple input methods
- ✅ Error handling
- ✅ Configuration loading
- ✅ Clipboard integration

---

## 🐛 Troubleshooting

### Common Issues

**Album not found**
- Check spelling of band and album name
- Try using partial names
- Use search helper: `src/spotify-album-search.py "band name"`

**API credentials error**
- Ensure credentials are set in `~/.config/spotify-resolver/config.json`
- Verify at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

**Clipboard not working**
- Use `--no-clipboard` flag to print URL
- Install pyperclip: `pip3 install pyperclip`
- macOS uses `pbcopy` as fallback

**Script not found**
- Make executable: `chmod +x /path/to/spotify-resolver/src/*.py`
- Check PATH or use full path
- Re-run installer

### Debug Mode

Enable verbose logging:

```bash
src/spotify-album-resolver.py --verbose --band "Test" --album "Test"
```

View logs:

```bash
tail -f ~/.local/log/spotify-resolver/spotify-resolver.log
```

---

## 📁 Project Structure

```
spotify-resolver/
├── src/                               # Source code
│   ├── spotify-album-resolver.py      # Main resolver (first result)
│   ├── spotify-album-search.py        # Album search (list results)
│   ├── spotify-album-search-gum.py    # Interactive album search (Gum UI)
│   ├── spotify-album-picker.py        # Interactive album picker
│   ├── spotify-artist-search.py       # Artist search (list results)
│   ├── spotify-artist-search-gum.py   # Interactive artist search (Gum UI)
│   ├── spotify-artist-album-picker.py # Artist → Albums workflow
│   └── spotify_resolver_utils.py      # Shared utilities
├── scripts/                           # Scripts & automation
│   ├── install-spotify-resolver.sh    # Installer
│   ├── test-spotify-resolver.sh       # Test suite
│   ├── spotify-album-resolver.applescript # Quick album resolver (AppleScript)
│   ├── spotify-album-selector.applescript # Album selector (AppleScript)
│   ├── spotify-album-interactive-selector.applescript # Interactive album selector (AppleScript)
│   └── spotify-artist-album-selector.applescript # Artist → Album selector (AppleScript)
├── docs/                              # Documentation
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   └── GIT-SETUP.md
├── assets/                            # Images & media
│   └── spotify-resolver.png
├── config.json.example                # Configuration template
├── .gitignore                         # Git ignore rules
├── LICENSE                            # MIT license
└── README.md                          # This file
```

---

## 📚 Documentation

- **README.md** - This file (complete documentation)
- **docs/CHANGELOG.md** - Version history and release notes
- **docs/CONTRIBUTING.md** - Contributor guide
- **docs/GIT-SETUP.md** - Git initialization guide

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dependencies
pip3 install requests pyperclip

# Run tests
./scripts/test-spotify-resolver.sh

# Debug mode
./src/spotify-album-resolver.py --verbose --band "test" --album "test"
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- Uses [requests](https://docs.python-requests.org/) for HTTP handling
- Uses [pyperclip](https://pypi.org/project/pyperclip/) for clipboard functionality

---

## 📈 Version History

### Version 1.0.0 (December 2025)
- ✅ Initial production-ready release
- ✅ Full Spotify Web API integration
- ✅ Multiple input methods
- ✅ AppleScript dialog interface
- ✅ Comprehensive error handling
- ✅ Keyboard Maestro, Raycast, Alfred integration
- ✅ Complete documentation
- ✅ Test suite

---

<div align="center">

**Made with ❤️ for seamless Spotify album discovery**

[⬆ Back to Top](#-spotify-album-resolver)

</div>
