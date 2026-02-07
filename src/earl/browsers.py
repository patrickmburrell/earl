import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

CHROME_APP_NAME = "Google Chrome"
OPEN_BIN = "open"
OSASCRIPT_BIN = "osascript"

CHROME_SUPPORT_DIR = Path.home() / "Library/Application Support/Google/Chrome"
CHROME_LOCAL_STATE_PATH = CHROME_SUPPORT_DIR / "Local State"

DEFAULT_PROFILE_DIR = "Default"
PROFILE_DIR_PREFIX = "Profile "

TAB_MENU_NAME = "Tab"
PIN_TAB_MENU_ITEM = "Pin Tab"


# =====================================================================================================================
@dataclass(frozen=True, slots=True)
class ChromeTab:
    title: str
    url: str


# ----------------------------------------------------------------------------------------------------------------------
def get_chrome_profiles() -> dict[str, str]:
    """Get Chrome profiles mapping directory name -> profile name."""
    if not CHROME_LOCAL_STATE_PATH.exists():
        return {}

    data = json.loads(CHROME_LOCAL_STATE_PATH.read_text(encoding="utf-8"))
    profiles = data.get("profile", {}).get("info_cache", {})

    result: dict[str, str] = {}
    for profile_dir, info in profiles.items():
        if not isinstance(info, dict):
            continue
        name = info.get("name")
        result[profile_dir] = name if isinstance(name, str) and name else "Unknown"

    return result


# ----------------------------------------------------------------------------------------------------------------------
def resolve_chrome_profile(profile_input: str) -> str:
    """Resolve Chrome profile name -> directory name."""
    if profile_input == DEFAULT_PROFILE_DIR or profile_input.startswith(PROFILE_DIR_PREFIX):
        return profile_input

    profiles = get_chrome_profiles()
    profile_lower = profile_input.lower()

    for profile_dir, profile_name in profiles.items():
        if profile_name.lower() == profile_lower:
            return profile_dir

    return profile_input


# ----------------------------------------------------------------------------------------------------------------------
def get_chrome_front_window_tabs() -> list[ChromeTab]:
    """Return (title, url) for tabs in Chrome's frontmost window."""
    script = """
(() => {
  try {
    const chrome = Application("Google Chrome");
    const windows = chrome.windows();
    if (windows.length === 0) {
      return JSON.stringify([]);
    }

    const tabs = windows[0].tabs().map(t => ({
      title: String(t.title()),
      url: String(t.url()),
    }));

    return JSON.stringify(tabs);
  } catch (e) {
    return JSON.stringify([]);
  }
})();
""".strip()

    result = subprocess.run(
        [OSASCRIPT_BIN, "-l", "JavaScript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        logger.warning("Failed reading Chrome tabs via osascript: {}", result.stderr.strip())
        return []

    try:
        raw = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError:
        logger.warning("Failed parsing osascript output as JSON")
        return []

    tabs: list[ChromeTab] = []

    if not isinstance(raw, list):
        return []

    for item in raw:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        url = item.get("url")
        if not isinstance(url, str) or not url:
            continue
        tabs.append(ChromeTab(title=title if isinstance(title, str) else "", url=url))

    return tabs


# ----------------------------------------------------------------------------------------------------------------------
def open_urls_chrome(urls: list[str], pinned_indices: list[int] | None = None, profile: str = "") -> None:
    """Open URLs in Chrome with optional profile and pinned tabs."""
    if not urls:
        return

    profile_dir = resolve_chrome_profile(profile) if profile else ""

    cmd = [OPEN_BIN, "-na", CHROME_APP_NAME, "--args"]
    if profile_dir:
        cmd.append(f"--profile-directory={profile_dir}")

    cmd.append("--new-window")
    cmd.extend(urls)

    subprocess.run(cmd, check=False)

    if not pinned_indices:
        return

    time.sleep(2)

    for idx in pinned_indices:
        tab_num = idx + 1

        script = f"""tell application \"{CHROME_APP_NAME}\"
            activate
            tell front window
                set active tab index to {tab_num}
            end tell
        end tell
        delay 0.5
        tell application \"System Events\"
            tell process \"{CHROME_APP_NAME}\"
                click menu item \"{PIN_TAB_MENU_ITEM}\" of menu \"{TAB_MENU_NAME}\" of menu bar 1
            end tell
        end tell
        delay 0.2"""

        pin_result = subprocess.run([OSASCRIPT_BIN, "-e", script], capture_output=True, text=True, check=False)
        if pin_result.returncode != 0:
            logger.warning("Could not pin tab {}: {}", tab_num, pin_result.stderr.strip())


# ----------------------------------------------------------------------------------------------------------------------
def open_urls_safari(urls: list[str]) -> None:
    """Open URLs in Safari in a single new window."""
    if not urls:
        return

    first_url = urls[0]
    script = f"""tell application \"Safari\"
        activate
        make new document
        set URL of document 1 to \"{first_url}\"
    end tell"""

    subprocess.run([OSASCRIPT_BIN, "-e", script], check=False)

    for url in urls[1:]:
        script = f"""tell application \"Safari\"
            tell window 1
                set current tab to (make new tab with properties {{URL:\"{url}\"}})
            end tell
        end tell"""
        subprocess.run([OSASCRIPT_BIN, "-e", script], check=False)


# ----------------------------------------------------------------------------------------------------------------------
def open_urls_default(urls: list[str]) -> None:
    """Open URLs using system default browser."""
    for url in urls:
        subprocess.run([OPEN_BIN, url], check=False)
