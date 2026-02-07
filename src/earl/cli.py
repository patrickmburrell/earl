import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from earl.browsers import (
    get_chrome_front_window_tabs,
    get_chrome_profiles,
    open_urls_chrome,
    open_urls_default,
    open_urls_safari,
)
from earl.capture import (
    CHROME_PROFILE_PLACEHOLDER,
    DEFAULT_PROJECT_FILE_NAME,
    build_project_urls_from_tabs,
    render_project_toml,
    write_project_file,
)
from earl.config import find_project_file, flatten_groups, get_group_urls, get_urls_file, load_toml
from earl.fzf import fzf_select

OPEN_BIN = "open"

app = typer.Typer(help="Earl - Your friendly URL launcher", add_completion=False)
console = Console()

chrome_app = typer.Typer(help="Chrome helpers", add_completion=False)
project_app = typer.Typer(help="Project URL sets (.earl.toml)", add_completion=False)
capture_app = typer.Typer(help="Capture current browser state", add_completion=False)

app.add_typer(chrome_app, name="chrome")
app.add_typer(project_app, name="project")
app.add_typer(capture_app, name="capture")


# ----------------------------------------------------------------------------------------------------------------------
@app.callback(invoke_without_command=True)
def _default(ctx: typer.Context) -> None:
    """Default: interactive browse."""
    if ctx.invoked_subcommand:
        return

    _browse(group_filter=None)


# ----------------------------------------------------------------------------------------------------------------------
@app.command()
def browse(group_filter: str | None = typer.Argument(None, help="Filter groups by substring")) -> None:
    """Interactive: pick group, then URL."""
    _browse(group_filter=group_filter)


# ----------------------------------------------------------------------------------------------------------------------
def _browse(*, group_filter: str | None) -> None:
    urls_file = get_urls_file()
    if not urls_file.exists():
        console.print(f"[red]Error:[/red] URLs file not found at {urls_file}")
        raise typer.Exit(1)

    data = load_toml(urls_file)
    all_groups = flatten_groups(data)

    if not all_groups:
        console.print("[yellow]No URL groups found[/yellow]")
        raise typer.Exit(1)

    selected_group = _select_group(all_groups, group_filter)
    urls = get_group_urls(data, selected_group)

    if not urls:
        console.print(f"[yellow]No URLs found in group '{selected_group}'[/yellow]")
        raise typer.Exit(1)

    selected_name = fzf_select(list(urls.keys()), f"{selected_group} > ", "Select URL to open (ESC to cancel)")
    if not selected_name:
        raise typer.Exit(0)

    console.print(f"[green]Opening:[/green] {selected_name}")
    subprocess.run([OPEN_BIN, urls[selected_name]], check=False)


# ----------------------------------------------------------------------------------------------------------------------
@app.command(name="open-all")
def open_all(group: str = typer.Argument(..., help="Group name (e.g. work.aws)")) -> None:
    """Open all URLs from a global group."""
    urls_file = get_urls_file()
    if not urls_file.exists():
        console.print(f"[red]Error:[/red] URLs file not found at {urls_file}")
        raise typer.Exit(1)

    data = load_toml(urls_file)
    urls = get_group_urls(data, group)

    if not urls:
        console.print(f"[yellow]No URLs found in group '{group}'[/yellow]")
        raise typer.Exit(1)

    console.print(f"[green]Opening all URLs in group:[/green] {group}")
    for name, url in urls.items():
        console.print(f"  Opening: {name}")
        subprocess.run([OPEN_BIN, url], check=False)


# ----------------------------------------------------------------------------------------------------------------------
@chrome_app.command(name="profiles")
def chrome_profiles() -> None:
    """List Chrome profiles (directory -> name)."""
    profiles = get_chrome_profiles()

    if not profiles:
        console.print("[yellow]Chrome Local State file not found. Is Chrome installed?[/yellow]")
        raise typer.Exit(1)

    table = Table()
    table.add_column("Directory", style="cyan")
    table.add_column("Profile Name", style="green")

    for profile_dir, profile_name in sorted(profiles.items()):
        table.add_row(profile_dir, profile_name)

    console.print(table)


# ----------------------------------------------------------------------------------------------------------------------
@project_app.command(name="open")
def project_open(project_file: Path | None = typer.Argument(None, help="Explicit .earl.toml path")) -> None:
    """Open all URLs from a `.earl.toml` (explicit path or nearest parent search)."""
    resolved_project_file = project_file.expanduser() if project_file else find_project_file()

    if not resolved_project_file:
        console.print("[red]Error:[/red] No .earl.toml found in current directory or parents")
        raise typer.Exit(1)

    if not resolved_project_file.exists():
        console.print(f"[red]Error:[/red] Project file not found: {resolved_project_file}")
        raise typer.Exit(1)

    console.print(f"[green]Opening URLs from:[/green] {resolved_project_file}")
    data = load_toml(resolved_project_file)

    urls_section = data.get("urls")
    if not isinstance(urls_section, list):
        console.print("[red]Error:[/red] .earl.toml must contain [[urls]] array")
        raise typer.Exit(1)

    options = data.get("options", {})
    if not isinstance(options, dict):
        options = {}

    browser = str(options.get("browser", "default")).lower()
    chrome_profile = str(options.get("chrome_profile", ""))

    urls_to_open: list[str] = []
    pinned_indices: list[int] = []

    for entry in urls_section:
        if not isinstance(entry, dict) or "name" not in entry or "url" not in entry:
            console.print(f"[yellow]Warning:[/yellow] Skipping malformed entry: {entry}")
            continue

        name = entry["name"]
        url = entry["url"]
        is_pinned = entry.get("pinned", False)

        console.print(f"  Opening: {name}" + (" (pinned)" if is_pinned else ""))
        urls_to_open.append(str(url))

        if is_pinned:
            pinned_indices.append(len(urls_to_open) - 1)

    _open_project_urls(
        browser=browser, chrome_profile=chrome_profile, urls_to_open=urls_to_open, pinned_indices=pinned_indices
    )


# ----------------------------------------------------------------------------------------------------------------------
@capture_app.command(name="chrome")
def capture_chrome(
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output file if it exists"),
    select_profile: bool = typer.Option(
        True,
        "--select-profile/--no-select-profile",
        help="Prompt for Chrome profile (via fzf) to write into [options]",
    ),
    prompt_front_window: bool = typer.Option(
        True,
        "--prompt-front-window/--no-prompt-front-window",
        help="Prompt to bring the target Chrome window to the front before capture",
    ),
) -> None:
    """Generate a `.earl.toml` from the front Chrome window's tabs."""
    if prompt_front_window:
        typer.prompt("Bring target Chrome window to the front, then press Enter", default="", show_default=False)

    tabs = get_chrome_front_window_tabs()
    if not tabs:
        console.print("[red]Error:[/red] No Chrome tabs found in the frontmost window")
        raise typer.Exit(1)

    urls = build_project_urls_from_tabs(tabs)
    if not urls:
        console.print("[red]Error:[/red] No http(s) tabs found in the frontmost window")
        raise typer.Exit(1)

    chrome_profile = CHROME_PROFILE_PLACEHOLDER
    chrome_profile_dir_hint: str | None = None

    if select_profile:
        selected_profile = _select_chrome_profile()
        if selected_profile:
            chrome_profile, chrome_profile_dir_hint = selected_profile

    out_path = output.expanduser() if output else (Path.cwd() / DEFAULT_PROJECT_FILE_NAME)

    if out_path.exists() and not overwrite:
        overwrite = typer.confirm(f"{out_path} exists. Overwrite?", default=False)
        if not overwrite:
            raise typer.Exit(1)

    contents = render_project_toml(
        chrome_profile=chrome_profile,
        chrome_profile_dir_hint=chrome_profile_dir_hint,
        urls=urls,
    )

    write_project_file(path=out_path, contents=contents, overwrite=overwrite)
    console.print(f"[green]Wrote:[/green] {out_path}")


# ----------------------------------------------------------------------------------------------------------------------
def _select_group(all_groups: list[str], group_filter: str | None) -> str:
    if group_filter:
        filtered = [g for g in all_groups if group_filter in g]
        if not filtered:
            console.print(f"[yellow]No groups found matching '{group_filter}'[/yellow]")
            raise typer.Exit(1)

        if len(filtered) == 1:
            return filtered[0]

        selected = fzf_select(filtered, "Select group > ", "Choose a URL group (ESC to cancel)")
        if not selected:
            raise typer.Exit(0)
        return selected

    selected = fzf_select(all_groups, "Select group > ", "Choose a URL group (ESC to cancel)")
    if not selected:
        raise typer.Exit(0)
    return selected


# ----------------------------------------------------------------------------------------------------------------------
def _select_chrome_profile() -> tuple[str, str] | None:
    profiles = get_chrome_profiles()
    if not profiles:
        return None

    display_to_profile: dict[str, tuple[str, str]] = {}
    items: list[str] = []

    for profile_dir, profile_name in sorted(profiles.items(), key=lambda kv: kv[1].lower()):
        display = f"{profile_name} ({profile_dir})"
        display_to_profile[display] = (profile_name, profile_dir)
        items.append(display)

    try:
        selected = fzf_select(items, "Profile > ", "Select Chrome profile for .earl.toml (ESC for placeholder)")
    except RuntimeError:
        return None

    if not selected:
        return None

    return display_to_profile.get(selected)


# ----------------------------------------------------------------------------------------------------------------------
def _open_project_urls(
    *,
    browser: str,
    chrome_profile: str,
    urls_to_open: list[str],
    pinned_indices: list[int],
) -> None:
    if not urls_to_open:
        console.print("[yellow]No URLs found[/yellow]")
        raise typer.Exit(1)

    if browser == "chrome":
        open_urls_chrome(urls_to_open, pinned_indices if pinned_indices else None, chrome_profile)
        return

    if browser == "safari":
        open_urls_safari(urls_to_open)
        if pinned_indices:
            console.print("[yellow]Note:[/yellow] Safari does not support programmatic tab pinning")
        return

    open_urls_default(urls_to_open)


if __name__ == "__main__":
    app()
