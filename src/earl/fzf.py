import subprocess


#------------------------------------------------------------------------------------------------------------------------
def fzf_select(items: list[str], prompt: str = "> ", header: str = "") -> str | None:
    """
    Present items in fzf for interactive selection.

    Args:
        items: List of strings to present in fzf
        prompt: Prompt text to display in fzf
        header: Optional header text

    Returns:
        Selected item string, or None if cancelled

    Raises:
        RuntimeError: If fzf is not installed
    """
    if not items:
        return None

    args = [
        "fzf",
        "--height=40%",
        "--reverse",
        "--border",
        f"--prompt={prompt}",
    ]

    if header:
        args.append(f"--header={header}")

    try:
        result = subprocess.run(
            args,
            input="\n".join(items),
            text=True,
            capture_output=True,
            check=False,
        )

        # fzf returns exit code 0 on selection, 130 on cancel
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    except FileNotFoundError:
        raise RuntimeError("fzf is not installed. Install with: brew install fzf")
