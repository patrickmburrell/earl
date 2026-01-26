# Project Context: earl

> **For AI**: Read this for Python CLI project overview, architecture, key decisions, and current state. Then check HISTORY.md for timeline.
> **Project Type**: python-cli
> **Last Updated**: 2026-01-26

---

## Current State
**Status**: Phase 3 Complete - Testing
**Version**: 0.1.0
**Installation**: uv tool install git+https://github.com/patrickmburrell/earl
**Code Size**: ~500 lines Python
**Last Major Change**: Extracted from dotfiles zsh implementation to independent Python CLI

---

## 📋 Project Overview

### What We Built
Earl is a Python CLI tool that organizes and launches web URLs by group. It supports Chrome profiles, Safari, pinned tabs, and project-specific URL sets. Unlike simple bookmark managers, Earl provides Chrome profile separation (work/personal), automated tab pinning, and project-scoped URL collections.

Extracted from dotfiles as part of the "extract-cli-tools" refactoring to give it proper project structure and independent evolution. Follows the same Python + typer + fzf pattern as Shelly, Grant, and Libby.

### Problem It Solves
**Original Problem**: Users have many URLs organized by context (work projects, personal finance, documentation) and need to open sets of related URLs frequently. Managing multiple Chrome profiles and pinned tabs manually is tedious.

**Solution**: Earl stores URLs in TOML groups, presents them in interactive fzf menus, and opens them with proper browser profiles and pinned tab settings.

**Key Benefits**:
- **Organized access**: Group URLs by project, topic, or context
- **Browser profile separation**: Keep work and personal browsing separate
- **Automated tab pinning**: Important tabs (dashboards, monitoring) stay pinned
- **Project-specific URLs**: `.earl.toml` files in projects open all relevant URLs at once

---

## 🛠️ Environment Details

### Platform & Tools
**Language**: Python 3.12+
**CLI Framework**: typer
**Package Manager**: uv
**Type Checking**: mypy
**Linting**: ruff
**Testing**: pytest
**Logging**: None (simple CLI)
**IDE**: VSCode
**External Dependencies**: fzf (must be installed)
**Platform**: macOS only (uses `open` command and AppleScript)

### Project Structure
```
earl/
├── src/
│   └── earl/
│       ├── __init__.py
│       ├── cli.py           # Entry point and CLI definition
│       ├── config.py        # TOML loading and group discovery
│       ├── browsers.py      # Chrome/Safari profile and tab management
│       └── fzf.py          # fzf subprocess integration
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_browsers.py
│   └── test_fzf.py
├── ada/
├── pyproject.toml
├── README.md
└── .gitignore
```

### Key Configuration Files
**pyproject.toml**: Dependencies (typer, rich), entry point, build config, ruff settings
**src/earl/__init__.py**: Version string (0.1.0)
**Environment variables**:
- `EARL_DIR`: Directory containing urls.toml (default: `$DOTFILES_ROOT/os/mac/bin/earl`)
- `DOTFILES_ROOT`: Path to dotfiles repo (default: `~/Projects/PMB/dotfiles`)

**TOML Files**:
- Global URLs: `$EARL_DIR/urls.toml` - Organized by group (e.g., `work.aws`, `pmb.finance`)
- Project URLs: `.earl.toml` in project root - Project-specific URL sets with browser options

---

## 🎯 Key Technical Decisions

### Decision 1: Python + typer + fzf Pattern
**Chosen**: Python CLI with typer framework calling fzf subprocess

**Why**:
- Same pattern as Libby, Shelly, Grant - proven to work well
- Python better for complex logic (TOML parsing, AppleScript, JSON) than shell
- fzf provides excellent interactive UX
- Easy to test, maintain, and extend

**Alternatives Considered**:
- ❌ **Pure zsh**: Original implementation - hard to test, maintain
- ✅ **Python + typer + fzf**: Clean, testable, maintainable
- ❌ **Rust**: Overkill for this use case

### Decision 2: Chrome Profile Support
**Approach**: Parse Chrome's `Local State` JSON to discover profiles, resolve names to directories

**Why**: Users think in profile names ("Amway", "Patrick"), not directories ("Profile 2"). Auto-resolution provides better UX.

**Implementation**:
- Read `~/Library/Application Support/Google/Chrome/Local State`
- Parse JSON to get `profile.info_cache` mapping
- Map profile names to directories (case-insensitive)
- Fall back to directory name if not found

### Decision 3: AppleScript for Tab Pinning
**Chosen**: Use AppleScript to automate Chrome tab pinning via System Events

**Why**: Chrome doesn't provide command-line arguments for pinning tabs. AppleScript can click menu items programmatically.

**Implementation**:
- Wait 2 seconds for tabs to load
- For each pinned tab: activate Chrome, select tab, click "Pin Tab" menu item
- Requires macOS Accessibility permissions for terminal app

**Trade-offs**: Requires user to grant Accessibility permissions, fragile if Chrome changes menu structure

### Decision 4: TOML for URL Storage
**Chosen**: TOML format with nested groups using dot notation

**Why**:
- Human-readable and editable
- Supports nested structure naturally
- Python 3.11+ includes `tomllib` in stdlib
- Better than JSON (no comments) or YAML (complex, indentation-sensitive)

**Format**:
```toml
[work.aws]
"Console" = "https://..."

[[urls]]  # Project-specific format
name = "Dashboard"
url = "https://..."
pinned = true
```

### Decision 5: Project-Specific URLs
**Chosen**: `.earl.toml` files in project directories with `[[urls]]` array format

**Why**: Projects often need multiple related URLs opened together (dashboard, repo, CI/CD). Project-scoped TOML files keep URLs with the project.

**Search behavior**: Searches up directory tree from current location (like `.git`)

---

## 🏗️ CLI Architecture

### High-Level Flow
```
Interactive mode:
  User runs: earl [filter]
      ↓
  load_toml(urls.toml) → flatten_groups() → filter groups
      ↓
  fzf_select(groups) → user picks group
      ↓
  get_group_urls() → extract URLs for group
      ↓
  fzf_select(urls) → user picks URL
      ↓
  subprocess.run(["open", url])

Project mode (earl -p):
  find_project_file() → search up tree for .earl.toml
      ↓
  load_toml(.earl.toml) → parse [[urls]] and [options]
      ↓
  Based on browser option:
    - chrome: open_urls_chrome(urls, pinned_indices, profile)
    - safari: open_urls_safari(urls)
    - default: open_urls_default(urls)
```

### Module Responsibilities

**`cli.py`** - Entry point and CLI definition
- Uses typer for CLI framework
- Three modes: interactive, open-all, open-project, list-profiles
- Orchestrates: load → filter → fzf → open
- Delegates browser-specific opening to browsers.py

**`config.py`** - TOML loading and group discovery
- `get_urls_file()`: Locates global urls.toml
- `find_project_file()`: Searches up tree for .earl.toml
- `load_toml()`: Parses TOML with tomllib
- `flatten_groups()`: Converts nested dict to flat list ("work.aws", "pmb.finance")
- `get_group_urls()`: Extracts name→url dict for specific group path

**`browsers.py`** - Chrome/Safari profile and tab management
- `get_chrome_profiles()`: Reads Chrome Local State JSON for profile mapping
- `resolve_chrome_profile()`: Maps profile name → directory ("Amway" → "Profile 2")
- `open_urls_chrome()`: Opens URLs in Chrome with profile + pinned tabs
- `open_urls_safari()`: Opens URLs in Safari using AppleScript
- `open_urls_default()`: Opens URLs with system default browser

**`fzf.py`** - fzf integration
- `fzf_select(items, prompt, header)`: Subprocess call to fzf binary
- Returns selected item or None if cancelled
- Raises RuntimeError if fzf not installed

### Commands
**`earl [group_filter]`**:
- Purpose: Interactive selection of URL group and URL
- Arguments: `[group_filter]` - Optional filter string to narrow groups
- Options: None in basic mode
- Examples:
  - `earl` - Show all groups
  - `earl work` - Show groups containing "work"
  - `earl pmb.finance` - Direct to pmb.finance group

**`earl -a <group>` / `earl --open-all <group>`**:
- Purpose: Open all URLs in specified group
- Example: `earl -a work.aws` - Opens all work.aws URLs

**`earl -p` / `earl --open-project`**:
- Purpose: Open all URLs from .earl.toml in current/parent directory
- Searches up tree for .earl.toml
- Respects browser and pinned settings in file

**`earl --list-profiles`**:
- Purpose: List Chrome profiles with directory → name mapping
- Helps users find profile directory names for .earl.toml

### URL Organization

**Global URLs** (`urls.toml`):
```toml
[work.aws]
"Console Home" = "https://..."
"EC2" = "https://..."

[pmb.finance]
"Vanguard" = "https://..."
```

**Project URLs** (`.earl.toml`):
```toml
[options]
browser = "chrome"
chrome_profile = "Amway"  # Or "Profile 2"

[[urls]]
name = "Dashboard"
url = "https://..."
pinned = true

[[urls]]
name = "Repository"
url = "https://..."
```

---

## 📖 Usage

### Environment Setup
```bash
# Sync dependencies (creates .venv automatically)
uv sync

# Install as editable tool globally
uv tool install --editable .

# Uninstall
uv tool uninstall earl
```

### Installation
```bash
# Install from local directory
uv tool install --editable .

# Install from GitHub
uv tool install git+https://github.com/patrickmburrell/earl

# List installed tools
uv tool list

# Uninstall
uv tool uninstall earl
```

### Running
```bash
# Run in development mode
uv run earl

# Interactive - select group, then URL
uv run earl
earl  # After installing

# Filter to groups
earl work
earl pmb

# Open all URLs in group
earl -a work.aws

# Open project URLs
earl -p

# List Chrome profiles
earl --list-profiles

# Show help
earl --help
```

---

## 🧪 Testing

### Test Strategy
- **Unit tests**: TOML parsing, group flattening, profile resolution
- **Integration tests**: Full CLI flow with CliRunner
- **Manual testing**: Interactive fzf, browser opening, AppleScript pinning

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_config.py

# Run with coverage
uv run pytest --cov=src/earl --cov-report=html

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

---

## 🚀 Distribution

### Distribution Strategy
- **Primary**: GitHub + uv tool install
- **Not planned**: PyPI (personal tool)
- **Not planned**: Homebrew (personal tool)

---

## ⚠️ Key Design Constraints

1. **macOS only**: Uses `open` command and AppleScript (not portable to Linux/Windows)
2. **fzf required**: Must be installed (`brew install fzf`)
3. **Chrome Local State dependency**: Relies on Chrome's JSON format (could break with updates)
4. **Accessibility permissions**: Tab pinning requires terminal to have Accessibility access
5. **AppleScript fragility**: Menu item names could change in Chrome updates

## ⚠️ Common Issues

### Issue 1: fzf not installed
**Symptom**: `RuntimeError: fzf is not installed`

**Solution**:
```bash
brew install fzf
```

### Issue 2: No URLs file found
**Symptom**: `Error: URLs file not found at ...`

**Cause**: `EARL_DIR` or `DOTFILES_ROOT` not set correctly

**Solution**:
```bash
# Set environment variables
export DOTFILES_ROOT="$HOME/Projects/PMB/dotfiles"

# Or set EARL_DIR directly
export EARL_DIR="$HOME/Projects/PMB/dotfiles/os/mac/bin/earl"
```

### Issue 3: Tab pinning doesn't work
**Symptom**: Tabs open but don't pin

**Cause**: Terminal app doesn't have Accessibility permissions

**Solution**:
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Add your terminal app (Warp, Terminal, iTerm2)
3. Re-run earl -p

### Issue 4: Chrome profile not found
**Symptom**: Warning about profile not found

**Cause**: Profile name doesn't match or Chrome Local State is corrupted

**Solution**:
```bash
# List available profiles
earl --list-profiles

# Use exact directory name from output
[options]
chrome_profile = "Profile 2"  # Use directory, not name
```

### Issue 5: Project URLs not found
**Symptom**: `Error: No .earl.toml found`

**Cause**: Not in project directory or .earl.toml doesn't exist

**Solution**:
```bash
# Create .earl.toml in project root
cd ~/Projects/your-project
cat > .earl.toml << 'EOF'
[[urls]]
name = "Dashboard"
url = "https://..."
EOF

# Run from anywhere in project
earl -p
```

---

## 📁 Files Inventory

| File                     | Purpose                                          |
|--------------------------|--------------------------------------------------|
| `src/earl/cli.py`        | Entry point, CLI definition, mode orchestration  |
| `src/earl/config.py`     | TOML loading, group discovery, path resolution   |
| `src/earl/browsers.py`   | Chrome/Safari profile management, tab pinning    |
| `src/earl/fzf.py`        | fzf subprocess integration                       |
| `pyproject.toml`         | Dependencies (typer, rich), entry point, ruff    |
| `README.md`              | User-facing documentation                        |

---

## 🔗 Related Projects

Part of the CLI tools extraction from dotfiles:
- **[Shelly](https://github.com/patrickmburrell/shelly)** - General command discovery (excludes auth commands)
- **[Grant](https://github.com/patrickmburrell/grant)** - Auth command helper (okta-*, aws-*, gcp-*, claude-*)
- **Earl** (this project) - URL launcher with browser profiles and pinned tabs
- **Libby** - Bibliography manager (pattern reference)

All follow the same Python + typer + fzf pattern.

## 📝 Refactoring Context

See `ada/refactoring/extract-cli-tools/` in dotfiles repo for full extraction plan.

**Phase 3 Status**: ✅ Complete
- Extracted from `dotfiles/os/mac/bin/earl/`
- Converted zsh → Python CLI
- Maintained all features: Chrome profiles, pinned tabs, Safari support, project URLs
- Added profile name resolution ("Amway" → "Profile 2")
- Published to GitHub

**Next**: Test installation and verify URL launching, Chrome profiles, tab pinning before Phase 4 (Update dotfiles)

### Future Enhancements
- [ ] Firefox profile support
- [ ] Edge profile support (uses same profile structure as Chrome)
- [ ] URL templates with variable substitution
- [ ] Import bookmarks from browsers
- [ ] Export groups to browser bookmark folders
- [ ] URL health checking (dead link detection)
- [ ] Keyboard shortcuts in project URLs (open specific URL directly)

### Technical Debt
- AppleScript for tab pinning is fragile (could break with Chrome UI changes)
- No error handling for malformed TOML files (Python raises exception)
- Chrome Local State parsing assumes specific JSON structure

---

**For timeline and evolution, see HISTORY.md**
