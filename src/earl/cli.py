import subprocess
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from earl.browsers import get_chrome_profiles, open_urls_chrome, open_urls_default, open_urls_safari
from earl.config import find_project_file, flatten_groups, get_group_urls, get_urls_file, load_toml
from earl.fzf import fzf_select

app = typer.Typer(help="Earl - Your friendly URL launcher")
console = Console()


#------------------------------------------------------------------------------------------------------------------------
@app.command()
def main(
    group_filter: Optional[str] = typer.Argument(None, help="Filter to specific group(s)"),
    open_all: bool = typer.Option(False, "--open-all", "-a", help="Open all URLs in group"),
    open_project: bool = typer.Option(False, "--open-project", "-p", help="Open project URLs from .earl.toml"),
    list_profiles: bool = typer.Option(False, "--list-profiles", help="List Chrome profiles"),
) -> None:
    """
    Organize and quickly launch URLs by group.

    Examples:
        earl                     # Interactive: select group, then URL
        earl work                # Filter to work.* groups
        earl -a work.aws         # Open all URLs in work.aws group
        earl -p                  # Open all URLs from .earl.toml
        earl --list-profiles     # Show Chrome profile directory → name mapping
    """
    # Handle list-profiles mode
    if list_profiles:
        _list_chrome_profiles()
        return

    # Handle project mode
    if open_project:
        _open_project_urls()
        return

    # Load global URLs
    urls_file = get_urls_file()
    if not urls_file.exists():
        console.print(f"[red]Error:[/red] URLs file not found at {urls_file}")
        raise typer.Exit(1)

    data = load_toml(urls_file)
    all_groups = flatten_groups(data)

    if not all_groups:
        console.print("[yellow]No URL groups found[/yellow]")
        raise typer.Exit(1)

    # Filter groups if filter provided
    if group_filter:
        filtered_groups = [g for g in all_groups if group_filter in g]

        if not filtered_groups:
            console.print(f"[yellow]No groups found matching '{group_filter}'[/yellow]")
            raise typer.Exit(1)

        # If only one group matches, use it directly
        if len(filtered_groups) == 1:
            selected_group = filtered_groups[0]
        else:
            # Multiple matches, let user pick
            selected_group = fzf_select(filtered_groups, "Select group > ", "Choose a URL group (ESC to cancel)")
            if not selected_group:
                raise typer.Exit(0)
    else:
        # No filter, show all groups
        selected_group = fzf_select(all_groups, "Select group > ", "Choose a URL group (ESC to cancel)")
        if not selected_group:
            raise typer.Exit(0)

    # Get URLs for selected group
    urls = get_group_urls(data, selected_group)

    if not urls:
        console.print(f"[yellow]No URLs found in group '{selected_group}'[/yellow]")
        raise typer.Exit(1)

    # If open-all mode, open all URLs
    if open_all:
        console.print(f"[green]Opening all URLs in group:[/green] {selected_group}")
        for name, url in urls.items():
            console.print(f"  Opening: {name}")
            subprocess.run(["open", url])
        return

    # Interactive mode: select specific URL
    url_names = list(urls.keys())
    selected_name = fzf_select(url_names, f"{selected_group} > ", "Select URL to open (ESC to cancel)")

    if selected_name:
        url = urls[selected_name]
        console.print(f"[green]Opening:[/green] {selected_name}")
        subprocess.run(["open", url])


#------------------------------------------------------------------------------------------------------------------------
def _list_chrome_profiles() -> None:
    """List Chrome profiles with directory → name mapping."""
    profiles = get_chrome_profiles()

    if not profiles:
        console.print("[yellow]Chrome Local State file not found. Is Chrome installed?[/yellow]")
        raise typer.Exit(1)

    console.print("\n[bold]Chrome Profiles:[/bold]")

    table = Table()
    table.add_column("Directory", style="cyan")
    table.add_column("Profile Name", style="green")

    for profile_dir, profile_name in sorted(profiles.items()):
        table.add_row(profile_dir, profile_name)

    console.print(table)

    console.print("\n[dim]Use the directory name (e.g., \"Profile 2\") in your .earl.toml:[/dim]")
    console.print("[dim]  [options][/dim]")
    console.print("[dim]  browser = \"chrome\"[/dim]")
    console.print("[dim]  chrome_profile = \"Profile 2\"[/dim]\n")


#------------------------------------------------------------------------------------------------------------------------
def _open_project_urls() -> None:
    """Open all URLs from .earl.toml in current/parent directory."""
    project_file = find_project_file()

    if not project_file:
        console.print("[red]Error:[/red] No .earl.toml found in current directory or parents")
        raise typer.Exit(1)

    console.print(f"[green]Opening URLs from:[/green] {project_file}")

    data = load_toml(project_file)

    if "urls" not in data:
        console.print("[red]Error:[/red] .earl.toml must contain [[urls]] array")
        raise typer.Exit(1)

    urls_section = data["urls"]
    if not isinstance(urls_section, list):
        console.print("[red]Error:[/red] [[urls]] must be an array")
        raise typer.Exit(1)

    # Get optional browser settings
    options = data.get("options", {})
    browser = options.get("browser", "default").lower()
    chrome_profile = options.get("chrome_profile", "")

    # Collect URLs and pinned indices
    urls_to_open = []
    pinned_indices = []

    for entry in urls_section:
        if not isinstance(entry, dict) or "name" not in entry or "url" not in entry:
            console.print(f"[yellow]Warning:[/yellow] Skipping malformed entry: {entry}")
            continue

        name = entry["name"]
        url = entry["url"]
        is_pinned = entry.get("pinned", False)

        console.print(f"  Opening: {name}" + (" (pinned)" if is_pinned else ""))
        urls_to_open.append(url)

        if is_pinned:
            pinned_indices.append(len(urls_to_open) - 1)

    # Open URLs based on browser settings
    if browser == "chrome":
        if chrome_profile:
            # Resolve profile name if provided
            from earl.browsers import resolve_chrome_profile

            resolved = resolve_chrome_profile(chrome_profile)
            console.print(f"[dim]Using Chrome profile: {chrome_profile} -> {resolved}[/dim]")

        open_urls_chrome(urls_to_open, pinned_indices if pinned_indices else None, chrome_profile)
    elif browser == "safari":
        open_urls_safari(urls_to_open)
        if pinned_indices:
            console.print("[yellow]Note:[/yellow] Safari does not support programmatic tab pinning")
    else:
        open_urls_default(urls_to_open)


if __name__ == "__main__":
    app()
