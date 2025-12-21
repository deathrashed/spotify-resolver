# Git Initialization Guide

This guide will help you initialize this project as a Git repository and prepare it for version control.

---

## 🚀 Quick Start

```bash
# Navigate to project directory (adjust to your installation path)
cd /path/to/spotify-resolver

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Spotify Album Resolver v1.0.0

Complete production-ready CLI tool for resolving Spotify album links.

Features:
- Multiple search methods (flags, query, interactive, piped)
- Official Spotify Web API integration
- Search helpers and interactive picker
- Comprehensive error handling and retry logic
- Keyboard Maestro and Raycast integration
- Full documentation suite
- Automated installer and test suite

Files included:
- Core scripts: resolver, search, picker, utilities
- Documentation: README, CONTRIBUTING, CHANGELOG
- Configuration: .gitignore, config template, LICENSE
- Tools: installer, test suite
- Backups: organized in separate directory"

# View status
git status
```

---

## 📋 Step-by-Step Instructions

### 1. Initialize Repository

```bash
cd /path/to/spotify-resolver  # Adjust to your installation path
git init
```

This creates a `.git` directory and initializes version control.

### 2. Review What Will Be Committed

```bash
git status
```

You should see:
- ✅ All `.py` scripts
- ✅ All `.sh` scripts
- ✅ All `.md` documentation files
- ✅ `.gitignore` file
- ✅ `config.json.example`
- ✅ `LICENSE` file

You should NOT see (thanks to `.gitignore`):
- ❌ `config.json` (contains credentials)
- ❌ `.DS_Store` or other system files
- ❌ `__pycache__/` directories
- ❌ `*.pyc` files
- ❌ Log files

### 3. Review .gitignore

```bash
cat .gitignore
```

Ensure it includes:
- Python artifacts (`__pycache__`, `*.pyc`)
- Configuration files with credentials (`config.json`)
- Logs (`*.log`, `logs/`)
- OS files (`.DS_Store`)
- IDE files (`.vscode/`, `.idea/`)
- Backup files in backups directory

### 4. Stage All Files

```bash
git add .
```

### 5. Verify Staged Files

```bash
git status
```

Check that:
- All project files are staged
- No sensitive files (config.json, logs, credentials) are staged

### 6. Create Initial Commit

```bash
git commit -m "Initial commit: Spotify Album Resolver v1.0.0

Complete production-ready CLI tool for resolving Spotify album links.

Features:
- Multiple search methods (flags, query, interactive, piped)
- Official Spotify Web API integration
- Search helpers and interactive picker
- Comprehensive error handling and retry logic
- Keyboard Maestro and Raycast integration
- Full documentation suite
- Automated installer and test suite"
```

### 7. Verify Commit

```bash
git log --oneline
```

You should see your initial commit.

---

## 🔗 Setting Up Remote Repository (Optional)

If you want to push to GitHub, GitLab, or another remote:

### GitHub

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/your-username/spotify-resolver.git
git branch -M main
git push -u origin main
```

### GitLab

```bash
# Create repository on GitLab first, then:
git remote add origin https://gitlab.com/your-username/spotify-resolver.git
git branch -M main
git push -u origin main
```

### Private Git Server

```bash
git remote add origin user@server:/path/to/repo.git
git branch -M main
git push -u origin main
```

---

## 🔐 Protecting Sensitive Data

### Before First Commit - Checklist

- [ ] Verify `.gitignore` is in place
- [ ] Confirm `config.json` is NOT staged (check `git status`)
- [ ] Confirm no log files are staged
- [ ] Confirm no cache files are staged
- [ ] Review all staged files: `git diff --cached --name-only`

### If You Accidentally Commit Credentials

```bash
# Remove file from staging (before commit)
git reset HEAD config.json

# Remove file from last commit (after commit, before push)
git reset --soft HEAD~1
# Remove the file from staging
git reset HEAD config.json
# Re-commit without the file
git commit -m "Your commit message"

# Remove from history (DANGEROUS - rewrites history)
git filter-branch --index-filter 'git rm --cached --ignore-unmatch config.json' HEAD

# For more complex cases, use BFG Repo-Cleaner
# See: https://rtyley.github.io/bfg-repo-cleaner/
```

### Security Best Practices

1. **Never commit:**
   - `config.json` (contains API credentials)
   - `*.log` files (may contain sensitive data)
   - `cache.json` (may contain cached responses)
   - Any files with passwords, tokens, or keys

2. **Always commit:**
   - `config.json.example` (template without real credentials)
   - `.gitignore` (protection against accidental commits)
   - Documentation files
   - Source code

3. **Double-check before pushing:**
   ```bash
   git diff origin/main..HEAD --name-only
   ```

---

## 📝 Recommended Commit Message Format

### Standard Format

```
type(scope): Brief description

Detailed explanation of changes (if needed)

- Bullet points for specific changes
- Reference issue numbers: #123
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build/tooling changes

### Examples

```bash
# Feature addition
git commit -m "feat(search): Add artist-only search mode

Allows searching for all albums by an artist without
specifying album name.

- Added --artist-only flag
- Updated search query builder
- Added tests for new mode"

# Bug fix
git commit -m "fix(clipboard): Handle clipboard unavailable gracefully

Previously crashed when clipboard not available. Now falls back
to printing URL.

Fixes #42"

# Documentation
git commit -m "docs(readme): Update installation instructions

- Added troubleshooting section
- Clarified API setup steps
- Added examples for common use cases"
```

---

## 🌿 Branching Strategy

### Simple Workflow (Solo Developer)

```bash
# Work directly on main
git checkout main
# Make changes
git add .
git commit -m "Your message"
```

### Feature Branch Workflow (Recommended)

```bash
# Create feature branch
git checkout -b feature/album-picker-improvements

# Make changes
git add .
git commit -m "feat(picker): Improve search accuracy"

# Switch back to main
git checkout main

# Merge feature
git merge feature/album-picker-improvements

# Delete feature branch
git branch -d feature/album-picker-improvements
```

### Release Workflow

```bash
# Create release branch
git checkout -b release/v1.1.0

# Update version numbers
# Update CHANGELOG.md
git add .
git commit -m "chore(release): Prepare v1.1.0"

# Merge to main
git checkout main
git merge release/v1.1.0

# Tag release
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push tag
git push origin v1.1.0
```

---

## 🏷️ Tagging Releases

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial production release"

# List tags
git tag

# Show tag details
git show v1.0.0

# Push tag to remote
git push origin v1.0.0

# Push all tags
git push origin --tags

# Delete tag (local)
git tag -d v1.0.0

# Delete tag (remote)
git push origin :refs/tags/v1.0.0
```

---

## 🔍 Useful Git Commands

### Status & Information

```bash
# View status
git status

# View commit history
git log
git log --oneline
git log --graph --oneline --all

# View changes
git diff
git diff --staged
git diff HEAD~1

# View specific commit
git show <commit-hash>

# View file history
git log --follow -- path/to/file
```

### Staging & Committing

```bash
# Stage all changes
git add .

# Stage specific file
git add path/to/file

# Unstage file
git reset HEAD path/to/file

# Commit
git commit -m "message"

# Amend last commit
git commit --amend
```

### Branching

```bash
# List branches
git branch

# Create branch
git branch feature-name

# Switch branch
git checkout branch-name

# Create and switch
git checkout -b branch-name

# Delete branch
git branch -d branch-name

# Force delete
git branch -D branch-name
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- path/to/file

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert commit (creates new commit)
git revert <commit-hash>
```

---

## ✅ Post-Initialization Checklist

After initializing Git:

- [ ] Repository initialized (`git init` completed)
- [ ] Initial commit created
- [ ] `.gitignore` working correctly (no sensitive files committed)
- [ ] Remote added (if using GitHub/GitLab)
- [ ] First push successful (if using remote)
- [ ] Tag created for v1.0.0
- [ ] Repository URL documented in README (if public)
- [ ] CI/CD configured (if applicable)

---

## 📚 Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)

---

**Ready to initialize? Run the Quick Start commands at the top of this guide!**
