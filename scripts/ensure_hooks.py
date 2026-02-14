#!/usr/bin/env python3
"""
Script to ensure pre-commit hooks are installed.
This can be run automatically or manually to verify hooks are set up.
"""
import subprocess
import sys
from pathlib import Path


def is_git_repo() -> bool:
    """Check if we're in a git repository."""
    return (Path.cwd() / ".git").is_dir()


def are_hooks_installed() -> bool:
    """Check if pre-commit hooks are already installed."""
    hook_path = Path.cwd() / ".git" / "hooks" / "pre-commit"
    if not hook_path.exists():
        return False

    # Check if it's a pre-commit managed hook
    content = hook_path.read_text()
    return "pre-commit" in content and "hook-impl" in content


def install_hooks() -> bool:
    """Install pre-commit hooks."""
    try:
        # Try using uv run first (recommended for this project)
        result = subprocess.run(
            ["uv", "run", "pre-commit", "install"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except FileNotFoundError:
        # Fall back to direct pre-commit command
        try:
            result = subprocess.run(
                ["pre-commit", "install"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except FileNotFoundError:
            print("Error: pre-commit is not installed. Run 'uv sync --dev' first.", file=sys.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error installing pre-commit hooks: {e.stderr}", file=sys.stderr)
        return False


def main() -> int:
    """Main function."""
    if not is_git_repo():
        print("Error: Not in a git repository.", file=sys.stderr)
        return 1

    if are_hooks_installed():
        print("✓ Pre-commit hooks are already installed.")
        return 0

    print("Pre-commit hooks are not installed. Installing now...")
    if install_hooks():
        print("✓ Pre-commit hooks installed successfully.")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
