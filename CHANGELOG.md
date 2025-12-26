# Changelog

All notable changes to Spotify Album Resolver will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-12-23

### 🎉 Initial Release

Complete production-ready Spotify album link resolver with comprehensive documentation and integration support.

### Added

#### Core Functionality
- **Main resolver script** (`spotify-album-resolver.py`)
  - Search Spotify Web API for albums by band and album name
  - Multiple input methods: flags, query, interactive, piped input
  - Automatic clipboard integration with macOS fallback
  - Robust error handling with automatic retries
  - Comprehensive logging system
  - Configuration file support

- **Search helpers**
  - `spotify-album-search.py` - List search results with numbered output
  - `spotify-album-picker.py` - Interactive album selection interface

- **Shared utilities** (`spotify_resolver_utils.py`)
  - Common configuration loading
  - Session creation with retry logic
  - Spotify API token management

#### Installation & Setup
- **Automated installer** (`install-spotify-resolver.sh`)
  - Dependency checking and installation
  - Directory structure creation
  - Configuration setup
  - Permission handling
  - Installation verification

- **Test suite** (`test-spotify-resolver.sh`)
  - Comprehensive test coverage
  - Multiple test scenarios
  - Color-coded output
  - Pass/fail reporting

#### Configuration
- **JSON configuration file** with options for:
  - API credentials (client_id, client_secret)
  - Request timeouts and retries
  - Market/region settings
  - Logging configuration
  - Cache settings
  - User agent customization

- **Configuration template** (`config.json.example`)

#### Documentation
- **README.md** - Complete project overview with:
  - Feature highlights
  - Installation instructions
  - Quick start guide
  - Configuration reference
  - Integration guides (Keyboard Maestro, Raycast, AppleScript, Shell)
  - Troubleshooting section
  - Development setup

- **CONTRIBUTING.md** - Contributor guide with:
  - Development setup
  - Coding standards
  - Testing guidelines
  - Pull request process
  - Documentation standards

- **CHANGELOG.md** - Version history and release notes

- **GIT-SETUP.md** - Git initialization and workflow guide

#### Project Management
- **Git repository setup**:
  - `.gitignore` - Comprehensive ignore rules for Python, IDEs, OS files
  - `LICENSE` - MIT license
  - `CHANGELOG.md` - This file

- **Organized structure**:
  - Clean separation of scripts, docs, and config

### Features

#### Multiple Input Methods
- Command-line flags: `--band` and `--album`
- Search query: `--query "artist:X album:Y"`
- Interactive mode with user prompts
- Piped input from other commands

#### Robust Error Handling
- Automatic retry with exponential backoff
- Timeout handling
- Network error recovery
- Clear error messages with emoji indicators
- Comprehensive logging to file and console

#### Smart Clipboard Integration
- Primary: `pyperclip` library
- Fallback: macOS `pbcopy` command
- Option to print URL instead: `--no-clipboard`

#### Configuration System
- External JSON configuration file
- Sensible defaults
- Override via command-line or config file
- Template provided for easy setup

#### Integration Ready
- Works with Keyboard Maestro
- Works with Raycast
- Works with Alfred (similar to Raycast)
- Shell alias support (`splink`)
- Scriptable for custom integrations

#### Developer Experience
- Verbose mode for debugging: `--verbose`
- Detailed logging with multiple levels
- Test suite for verification
- Clean code with comprehensive comments
- Modular design for extensibility

### Technical Details

#### Dependencies
- Python 3.8+
- `requests` - HTTP library
- `pyperclip` - Clipboard integration

#### Platform Support
- macOS (primary platform)
- Tested on M3 MacBook Air with 8GB RAM

#### API Integration
- Spotify Web API using Client Credentials flow
- OAuth 2.0 token management
- Search endpoint with market filtering
- Proper error handling and rate limiting

---

## [Unreleased]

### Planned Features
- Windows and Linux support
- Additional output formats (JSON, CSV)
- Batch processing mode
- Album metadata export
- Custom search filters
- Playlist support

---

## Version History Legend

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes and improvements

---

[1.0.0]: https://github.com/deathrashed/spotify-resolver/releases/tag/v1.0.0
