import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

from earl.browsers import BrowserTab

DEFAULT_PROJECT_FILE_NAME = ".earl.toml"
CHROME_PROFILE_PLACEHOLDER = "CHROME_PROFILE_HERE"

BROWSER_CHROME = "chrome"
BROWSER_SAFARI = "safari"

TABITHA_PINNED_URL_PREFIX = "https://tabitha.smallblocksoftware.com/"

VALID_URL_SCHEMES = {"http", "https"}
WHITESPACE_RE = re.compile(r"\s+")


# =====================================================================================================================
@dataclass(frozen=True, slots=True)
class ProjectUrl:
    name: str
    url: str
    pinned: bool


# ----------------------------------------------------------------------------------------------------------------------
def build_project_urls_from_tabs(tabs: list[BrowserTab]) -> list[ProjectUrl]:
    """Convert browser tabs -> ProjectUrl list (deduped names, ignores non-http(s) URLs)."""
    used_names: dict[str, int] = {}
    urls: list[ProjectUrl] = []

    for tab in tabs:
        parsed = urlparse(tab.url)
        if parsed.scheme not in VALID_URL_SCHEMES:
            continue

        title = WHITESPACE_RE.sub(" ", tab.title or "").strip()
        base_name = title or (parsed.netloc or tab.url)

        count = used_names.get(base_name, 0) + 1
        used_names[base_name] = count

        name = base_name if count == 1 else f"{base_name} ({count})"
        pinned = tab.url.startswith(TABITHA_PINNED_URL_PREFIX)

        urls.append(ProjectUrl(name=name, url=tab.url, pinned=pinned))

    return urls


# ----------------------------------------------------------------------------------------------------------------------
def render_project_toml(
    *,
    browser: str,
    chrome_profile: str | None,
    chrome_profile_dir_hint: str | None,
    urls: list[ProjectUrl],
) -> str:
    """Render Earl project-format TOML for `.earl.toml`."""
    browser_value = browser.lower().strip()
    if browser_value not in {BROWSER_CHROME, BROWSER_SAFARI, "default"}:
        raise ValueError(f"Unsupported browser: {browser}")

    lines: list[str] = []

    lines.append("[options]")
    lines.append(f"browser = {_toml_quote(browser_value)}")

    if browser_value == BROWSER_CHROME:
        profile = chrome_profile or CHROME_PROFILE_PLACEHOLDER
        profile_line = f"chrome_profile = {_toml_quote(profile)}"
        if chrome_profile_dir_hint:
            profile_line = f"{profile_line}  # dir: {chrome_profile_dir_hint}"
        lines.append(profile_line)

    for entry in urls:
        lines.append("")
        lines.append("[[urls]]")
        lines.append(f"name = {_toml_quote(entry.name)}")
        lines.append(f"url = {_toml_quote(entry.url)}")
        if entry.pinned:
            lines.append("pinned = true")

    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------------------------------
def write_project_file(*, path: Path, contents: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(path)

    path.write_text(contents, encoding="utf-8")
    logger.info("Wrote {}", path)


# ----------------------------------------------------------------------------------------------------------------------
def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
