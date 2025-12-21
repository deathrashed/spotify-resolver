# Contributing to Spotify Album Resolver

Thank you for your interest in contributing to Spotify Album Resolver! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Be respectful, constructive, and professional in all interactions.

### Expected Behavior

- ✅ Use welcoming and inclusive language
- ✅ Be respectful of differing viewpoints and experiences
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what is best for the project and community
- ✅ Show empathy towards other community members

### Unacceptable Behavior

- ❌ Harassment, trolling, or insulting comments
- ❌ Publishing others' private information without permission
- ❌ Other conduct which could reasonably be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- macOS (or appropriate testing environment)
- Git for version control
- A Spotify Developer account (for API testing)

### First Steps

1. **Fork the repository** (when available on GitHub)
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/spotify-resolver.git
   cd spotify-resolver
   ```

3. **Set up development environment:**
   ```bash
   ./install-spotify-resolver.sh
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🛠️ Development Setup

### Install Dependencies

```bash
# Install Python packages
pip3 install requests pyperclip

# For development/testing
pip3 install pytest pylint black mypy
```

### Configuration

1. **Set up Spotify API credentials:**
   ```bash
   cp config.json.example ~/.config/spotify-resolver/config.json
   # Edit config.json with your credentials
   ```

2. **Verify installation:**
   ```bash
   ./test-spotify-resolver.sh
   ```

### Development Tools

**Recommended IDE/Editors:**
- VS Code with Python extension
- PyCharm
- Sublime Text with Python plugins

**Recommended VS Code Extensions:**
- Python (Microsoft)
- Pylance
- Python Indent
- GitLens

---

## 📁 Project Structure

```
spotify-resolver/
├── spotify-album-resolver.py      # Main script
├── spotify-album-search.py        # Search helper
├── spotify-album-picker.py        # Interactive picker
├── spotify_resolver_utils.py      # Shared utilities
├── install-spotify-resolver.sh    # Installation script
├── test-spotify-resolver.sh       # Test suite
├── README.md                      # Main documentation
├── CONTRIBUTING.md                # This file
├── config.json.example            # Configuration template
├── .gitignore                     # Git ignore rules
```

### Key Components

**Core Scripts:**
- `spotify-album-resolver.py` - Main entry point, handles all search/clipboard logic
- `spotify_resolver_utils.py` - Shared functions (config loading, session creation, token management)

**Helper Scripts:**
- `spotify-album-search.py` - Returns numbered list of search results
- `spotify-album-picker.py` - Interactive selection interface

**Infrastructure:**
- `install-spotify-resolver.sh` - Idempotent installer
- `test-spotify-resolver.sh` - Comprehensive test suite

---

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these conventions:

#### General

- **Line length:** 120 characters maximum
- **Indentation:** 4 spaces (no tabs)
- **Encoding:** UTF-8
- **Quotes:** Double quotes for strings, single quotes for dict keys

#### Naming Conventions

```python
# Variables and functions: snake_case
user_input = "example"
def get_spotify_token():
    pass

# Classes: PascalCase
class SpotifyClient:
    pass

# Constants: UPPER_SNAKE_CASE
SPOTIFY_API_URL = "https://api.spotify.com/v1"
CONFIG_DIR = Path.home() / ".config"

# Private functions/methods: _leading_underscore
def _internal_helper():
    pass
```

#### Imports

```python
# Standard library imports
import sys
import json
from pathlib import Path

# Third-party imports
import requests
import pyperclip

# Local imports
from spotify_resolver_utils import load_config
```

#### Docstrings

Use Google-style docstrings:

```python
def search_spotify_album(session: requests.Session, query: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Search Spotify for an album using the official Web API.

    Args:
        session: Active requests session with retry configuration
        query: Search query string (e.g., "artist:Metallica album:Master of Puppets")
        config: Configuration dictionary with API credentials and settings

    Returns:
        Dictionary containing album data if found, None otherwise

    Raises:
        requests.exceptions.RequestException: If API request fails after retries
    """
    pass
```

### Code Quality Tools

**Linting:**
```bash
# Check code style
pylint spotify-album-resolver.py

# Auto-format code
black spotify-album-resolver.py
```

**Type Checking:**
```bash
# Run type checker
mypy spotify-album-resolver.py
```

### Best Practices

1. **Error Handling:**
   ```python
   # Good: Specific exception handling with logging
   try:
       response = session.get(url, timeout=10)
       response.raise_for_status()
   except requests.exceptions.Timeout:
       logging.error("Request timed out")
       return None
   except requests.exceptions.RequestException as e:
       logging.error(f"Request failed: {e}")
       return None
   ```

2. **Logging:**
   ```python
   # Good: Appropriate log levels
   logging.debug(f"Search query: {query}")  # Development info
   logging.info(f"Found album: {album_name}")  # Important events
   logging.warning(f"No results for: {query}")  # Potential issues
   logging.error(f"API error: {error}")  # Errors
   ```

3. **Configuration:**
   ```python
   # Good: Use configuration with defaults
   timeout = config.get("timeout", 10)
   max_retries = config.get("max_retries", 3)
   ```

4. **Security:**
   ```python
   # Good: Never log credentials
   logging.debug(f"Using client_id: {client_id[:4]}...")  # Partial only

   # Bad: Don't do this
   logging.debug(f"Credentials: {client_id}:{client_secret}")  # ❌
   ```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run full test suite
./test-spotify-resolver.sh

# Run with verbose output
./test-spotify-resolver.sh --verbose

# Test specific functionality
./spotify-album-resolver.py --verbose --band "Metallica" --album "Master of Puppets"
```

### Writing Tests

When adding new features, update `test-spotify-resolver.sh`:

```bash
# Add test function
test_new_feature() {
    echo "Testing new feature..."

    # Test command
    result=$(your_test_command)

    # Verify result
    if [[ $result == *"expected"* ]]; then
        echo "✅ New feature test passed"
        return 0
    else
        echo "❌ New feature test failed"
        return 1
    fi
}

# Add to test runner
run_all_tests() {
    test_new_feature || FAILED=$((FAILED + 1))
    # ... other tests
}
```

### Test Coverage

Ensure tests cover:
- ✅ Happy path scenarios
- ✅ Error conditions
- ✅ Edge cases
- ✅ Input validation
- ✅ Configuration loading
- ✅ Integration points

---

## 📤 Submitting Changes

### Commit Guidelines

**Commit Message Format:**
```
type(scope): Brief description

Detailed explanation of changes (if needed)

- Bullet points for specifics
- Reference issue numbers: #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
feat(search): Add support for artist-only searches

Allows users to search for all albums by a specific artist
without specifying an album name.

- Added --artist-only flag
- Updated search query builder
- Added tests for artist-only mode
```

```bash
fix(clipboard): Handle clipboard errors gracefully

Previously would crash if clipboard unavailable. Now falls back
to printing URL if clipboard copy fails.

Fixes #42
```

### Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Run test suite** and ensure all tests pass
4. **Update CHANGELOG** (if applicable)
5. **Submit PR** with clear description of changes

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Tested manually

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## 📖 Documentation

### Documentation Standards

**All new features must include:**
1. **Inline code comments** for complex logic
2. **Docstrings** for all functions/classes
3. **README updates** for user-facing changes
4. **Example usage** in appropriate guides

### Documentation Files

- `README.md` - Main project documentation (includes all integration guides)
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - This file
- `GIT-SETUP.md` - Git workflow guide

### Updating Documentation

```bash
# After making changes, verify documentation is current
grep -r "TODO" *.md  # Check for incomplete docs
grep -r "FIXME" *.md  # Check for known issues
```

---

## 🚢 Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version numbers** in:
   - `src/spotify-album-resolver.py`
   - `README.md`

2. **Update CHANGELOG** with release notes

3. **Run full test suite:**
   ```bash
   ./test-spotify-resolver.sh
   ```

4. **Tag release:**
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin v1.0.1
   ```

5. **Create release notes** documenting:
   - New features
   - Bug fixes
   - Breaking changes
   - Upgrade instructions

---

## ❓ Questions?

### Getting Help

- **Check existing documentation** first
- **Search existing issues** (when on GitHub)
- **Ask in discussions** (when available)
- **Contact maintainers** for specific questions

### Useful Resources

- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api/)
- [Python Requests Documentation](https://docs.python-requests.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

**Happy coding! 🎵**
