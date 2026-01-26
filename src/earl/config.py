import os
import shutil
import tomllib
from pathlib import Path


#------------------------------------------------------------------------------------------------------------------------
def _migrate_from_dotfiles(dotfiles_path: Path, config_path: Path) -> None:
    """
    One-time migration: copy urls.toml from dotfiles to ~/.config/earl/.

    Args:
        dotfiles_path: Source path in dotfiles
        config_path: Destination path in ~/.config/earl/
    """
    # Create ~/.config/earl/ directory
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy urls.toml (don't move - keep original in dotfiles)
    shutil.copy2(dotfiles_path, config_path)
    print(f"Migrated urls.toml from {dotfiles_path} to {config_path}")


#------------------------------------------------------------------------------------------------------------------------
def get_urls_file() -> Path:
    """
    Get path to global urls.toml file.

    Priority order:
    1. $EARL_DIR/urls.toml (explicit override)
    2. ~/.config/earl/urls.toml (XDG standard location)
    3. $DOTFILES_ROOT/os/mac/bin/earl/urls.toml (backwards compatibility + migration)

    If dotfiles location exists but ~/.config/earl/urls.toml doesn't, automatically migrate.
    """
    # 1. Check EARL_DIR override
    if earl_dir := os.getenv("EARL_DIR"):
        return Path(earl_dir) / "urls.toml"

    # 2. Check ~/.config/earl/urls.toml (new default)
    config_path = Path.home() / ".config" / "earl" / "urls.toml"
    if config_path.exists():
        return config_path

    # 3. Check dotfiles (backwards compatibility)
    dotfiles_root = os.getenv("DOTFILES_ROOT", "~/Projects/PMB/dotfiles")
    dotfiles_path = Path(dotfiles_root).expanduser() / "os" / "mac" / "bin" / "earl" / "urls.toml"

    # 4. If dotfiles exists but config doesn't, migrate
    if dotfiles_path.exists():
        _migrate_from_dotfiles(dotfiles_path, config_path)
        return config_path

    # 5. Default to config location (even if doesn't exist yet)
    return config_path


#------------------------------------------------------------------------------------------------------------------------
def find_project_file() -> Path | None:
    """Search for .earl.toml in current directory or parents."""
    current = Path.cwd()

    while current != current.parent:
        project_file = current / ".earl.toml"
        if project_file.exists():
            return project_file
        current = current.parent

    return None


#------------------------------------------------------------------------------------------------------------------------
def load_toml(path: Path) -> dict:
    """Load TOML file."""
    with open(path, "rb") as f:
        return tomllib.load(f)


#------------------------------------------------------------------------------------------------------------------------
def flatten_groups(data: dict, prefix: str = "") -> list[str]:
    """
    Flatten nested TOML structure to list of group paths.

    Example:
        {"work": {"aws": {...}, "gcp": {...}}}
        -> ["work.aws", "work.gcp"]
    """
    result = []

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key

        # Check if this is a nested dict (not a URL dict)
        if isinstance(value, dict) and not any(isinstance(v, str) for v in value.values()):
            # Nested group, recurse
            result.extend(flatten_groups(value, full_key))
        else:
            # This is a group with URLs
            result.append(full_key)

    return sorted(result)


#------------------------------------------------------------------------------------------------------------------------
def get_group_urls(data: dict, group_path: str) -> dict[str, str]:
    """
    Get URLs for a specific group path.

    Args:
        data: Loaded TOML data
        group_path: Dot-separated path like "work.aws"

    Returns:
        Dictionary mapping URL names to URLs
    """
    keys = group_path.split(".")
    value = data

    for key in keys:
        if key in value:
            value = value[key]
        else:
            return {}

    # Extract name -> url mappings
    if isinstance(value, dict):
        return {name: url for name, url in value.items() if isinstance(url, str)}

    return {}
