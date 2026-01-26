import json
import subprocess
import time
from pathlib import Path


#------------------------------------------------------------------------------------------------------------------------
def get_chrome_profiles() -> dict[str, str]:
    """
    Get Chrome profiles mapping directory name to profile name.

    Returns:
        Dictionary mapping profile directory (e.g. "Profile 2") to profile name (e.g. "Amway")
    """
    chrome_dir = Path.home() / "Library/Application Support/Google/Chrome"
    local_state = chrome_dir / "Local State"

    if not local_state.exists():
        return {}

    with open(local_state) as f:
        data = json.load(f)
        profiles = data.get("profile", {}).get("info_cache", {})
        return {profile_dir: info.get("name", "Unknown") for profile_dir, info in profiles.items()}


#------------------------------------------------------------------------------------------------------------------------
def resolve_chrome_profile(profile_input: str) -> str:
    """
    Resolve Chrome profile name to directory name.

    Args:
        profile_input: Either a profile name (e.g. "Amway") or directory (e.g. "Profile 2")

    Returns:
        Profile directory name (e.g. "Default" or "Profile 2")
    """
    # If already a directory name, return as-is
    if profile_input == "Default" or profile_input.startswith("Profile "):
        return profile_input

    # Try to map profile name to directory
    profiles = get_chrome_profiles()
    profile_lower = profile_input.lower()

    for profile_dir, profile_name in profiles.items():
        if profile_name.lower() == profile_lower:
            return profile_dir

    # Not found, use as-is and let Chrome handle it
    return profile_input


#------------------------------------------------------------------------------------------------------------------------
def open_urls_chrome(urls: list[str], pinned_indices: list[int] | None = None, profile: str = "") -> None:
    """
    Open URLs in Chrome with optional profile and pinned tabs.

    Args:
        urls: List of URLs to open
        pinned_indices: List of indices (0-based) to pin, or None
        profile: Chrome profile directory name (e.g. "Profile 2")
    """
    if not urls:
        return

    # Resolve profile if provided
    if profile:
        profile_dir = resolve_chrome_profile(profile)
    else:
        profile_dir = ""

    # Build Chrome command
    cmd = ["open", "-na", "Google Chrome", "--args"]

    if profile_dir:
        cmd.append(f"--profile-directory={profile_dir}")

    cmd.append("--new-window")
    cmd.extend(urls)

    subprocess.run(cmd)

    # Pin tabs if requested
    if pinned_indices:
        time.sleep(2)  # Wait for tabs to load

        for idx in pinned_indices:
            tab_num = idx + 1  # AppleScript uses 1-based indexing

            script = f"""tell application "Google Chrome"
                activate
                tell front window
                    set active tab index to {tab_num}
                end tell
            end tell
            delay 0.5
            tell application "System Events"
                tell process "Google Chrome"
                    click menu item "Pin Tab" of menu "Tab" of menu bar 1
                end tell
            end tell
            delay 0.2"""

            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Could not pin tab {tab_num}: {result.stderr.strip()}")


#------------------------------------------------------------------------------------------------------------------------
def open_urls_safari(urls: list[str]) -> None:
    """
    Open URLs in Safari in a single new window.

    Args:
        urls: List of URLs to open
    """
    if not urls:
        return

    # Create new window with first URL
    first_url = urls[0]
    script = f"""tell application "Safari"
        activate
        make new document
        set URL of document 1 to "{first_url}"
    end tell"""

    subprocess.run(["osascript", "-e", script])

    # Open remaining URLs as new tabs
    for url in urls[1:]:
        script = f"""tell application "Safari"
            tell window 1
                set current tab to (make new tab with properties {{URL:"{url}"}})
            end tell
        end tell"""
        subprocess.run(["osascript", "-e", script])


#------------------------------------------------------------------------------------------------------------------------
def open_urls_default(urls: list[str]) -> None:
    """
    Open URLs using system default browser.

    Args:
        urls: List of URLs to open
    """
    for url in urls:
        subprocess.run(["open", url])
