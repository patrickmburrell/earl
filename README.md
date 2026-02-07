# Earl

**Earl** - Your friendly URL launcher

Earl is a Python CLI tool that helps you organize and quickly launch web URLs by group. It supports Chrome profiles, Safari, pinned tabs, and project-specific URL sets.

## Features

- 🗂️ **Organized URLs**: Store URLs in groups using TOML format
- 🔍 **Interactive selection**: Browse groups and URLs with fzf
- 🌐 **Chrome profiles**: Open URLs in specific Chrome profiles (work/personal separation)
- 📌 **Pinned tabs**: Auto-pin important tabs in Chrome
- 🦁 **Safari support**: Open URLs in Safari with multiple tabs
- 📁 **Project URLs**: Add `.earl.toml` to projects to open all project URLs at once
- ⚡ **Fast filtering**: Type group prefix to narrow down instantly

## Installation

### Local Install (Recommended)

```bash
# Global install - available everywhere
cd /Users/AIUW003/Projects/PMB/earl
uv tool install --editable .
```

### From GitHub

```bash
# Install from remote repository
uv tool install git+https://github.com/patrickmburrell/earl
```

## Usage

```bash
# Interactive mode - select group, then URL
earl

# Interactive, with group filter
earl browse work          # Show all work.* groups
earl browse pmb           # Show all pmb.* groups

# Open all URLs in a global group
earl open-all work.aws

# Open project URLs from nearest .earl.toml (searches up tree)
earl project open

# Open project URLs from explicit file
# earl project open path/to/.earl.toml

# List Chrome profiles
earl chrome profiles

# Capture current Chrome window -> .earl.toml
earltmp="/tmp/.earl.toml" && earl capture chrome -o "$earltmp"

# Capture current Safari window -> .earl.toml
earltmp="/tmp/.earl.safari.toml" && earl capture safari -o "$earltmp"

# Show help
earl --help
```

## Configuration

### Global URLs

Earl stores global URLs at `~/.config/earl/urls.toml`.

Edit your global URLs:

```bash
# Open in your editor
code ~/.config/earl/urls.toml
# or
open ~/.config/earl/urls.toml
```

Format:

```toml
[work.aws]
"Console Home" = "https://console.aws.amazon.com"
"EC2 Instances" = "https://console.aws.amazon.com/ec2"

[work.gcp]
"Cloud Console" = "https://console.cloud.google.com"

[pmb.finance]
"Vanguard" = "https://vanguard.com"
"Fidelity" = "https://fidelity.com"
```

### Project URLs

Create `.earl.toml` in your project root:

```toml
[options]
browser = "chrome"
chrome_profile = "Amway"  # Use profile name or directory

[[urls]]
name = "Production Dashboard"
url = "https://dashboard.your-project.com"
pinned = true  # Pin this tab

[[urls]]
name = "Project Repository"
url = "https://github.com/your-org/your-project"

[[urls]]
name = "CI/CD Pipeline"
url = "https://ci.your-project.com"
```

Then from anywhere in your project:

```bash
earl project open  # Opens all project URLs in Chrome with specified profile
```

## Chrome Profiles

Find your Chrome profile directory names:

```bash
earl chrome profiles
```

Output:
```
Directory            Profile Name
============================================
Default              Your Chrome
Profile 1            Patrick
Profile 2            Amway
```

Use either the profile name or directory in your `.earl.toml`:

```toml
[options]
browser = "chrome"
chrome_profile = "Amway"       # Profile name (easier)
# OR
chrome_profile = "Profile 2"   # Directory name
```

## Pinned Tabs

Mark tabs to be pinned (Chrome only):

```toml
[[urls]]
name = "Dashboard"
url = "https://dashboard.example.com"
pinned = true  # This tab will be pinned on the left
```

**Requirements for pinning:**
- macOS Accessibility permissions for your terminal (Warp/Terminal)
- Go to **System Settings** → **Privacy & Security** → **Accessibility**
- Add your terminal to the allowed apps list

## Browser Options

### Chrome (with profile)
```toml
[options]
browser = "chrome"
chrome_profile = "Work"
```

### Safari
```toml
[options]
browser = "safari"
```

### Default browser
```toml
[options]
browser = "default"  # Or omit [options] entirely
```

## Configuration

### File Locations

Earl checks for urls.toml in the following order:

1. **`$EARL_DIR/urls.toml`** - Explicit override (if `$EARL_DIR` is set)
2. **`~/.config/earl/urls.toml`** - Default location (XDG standard)

### Environment Variables

- `EARL_DIR`: Override default config directory (optional)

## Development

```bash
# Sync dependencies
uv sync

# Run in development mode
uv run earl

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## Related Projects

Part of the CLI tools suite:
- **[Shelly](https://github.com/patrickmburrell/shelly)** - General command discovery
- **[Grant](https://github.com/patrickmburrell/grant)** - Authentication command helper
- **Earl** (this project) - URL launcher
- **Libby** - Bibliography manager

All follow the same Python + typer + fzf pattern.

## License

Personal project - use at your own risk.
