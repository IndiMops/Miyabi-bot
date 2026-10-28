import functools
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_json(file_path: str | Path) -> dict[str, Any] | list[Any]:
    """
    Load a JSON file and return its content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            output = json.load(file)
    except Exception as e:
        logger.error(f"Could not load JSON file {file_path} due to exception: {e}")
        output = {}

    return output


def save_json(value: Any, filename: str | Path) -> None:
    """
    Save a dictionary or list to a JSON file.
    """
    try:
        with open(filename, 'w', encoding="utf-8") as file:
            json.dump(value, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Could not save JSON file {filename} due to exception: {e}")

def hex_to_color(hex_str: str) -> int:
    return int(hex_str.lstrip('#'), 16) if hex_str.startswith('#') else int(hex_str, 16)


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """
    Convert a HEX color string to an RGB tuple.
    
    Args:
        hex_str (str): The HEX color string (e.g., '#FF5733').
        
    Returns:
        tuple: A tuple representing the RGB color (R, G, B).
    """
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


# Backwards-compatible aliases; migrate callers to snake_case gradually.
HEXtoColor = hex_to_color
HEXtoRGB = hex_to_rgb


@functools.cache
def _git_revision() -> str | None:
    """Return the short Git commit hash of the checkout, or None without Git metadata.

    Cached: Git is queried at most once per process.
    """
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).strip().decode("utf-8")
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning(f"Git revision is unavailable ({type(e).__name__}); using the configured version")
        return None
    return revision if revision.isalnum() else None


def get_version(default_version: str) -> str:
    """
    Return the version string shown to users.

    Order: the `BOT_VERSION` environment variable (set when a Docker image is
    built), then `dev-<git hash>` for a local checkout, then `default_version`
    (`config.json → bot.version`, the canonical release version).
    """
    build_version = os.getenv("BOT_VERSION", "").strip()
    if build_version:
        return build_version

    revision = _git_revision()
    if revision:
        return f"dev-{revision}"
    return default_version
    
    
async def fetch_slash_commands(bot):
    try:
        commands = await bot.tree.fetch_commands()
        return [{"name": cmd.name, "id": cmd.id} for cmd in commands]
    except Exception as e:
        logger.error(f"Failed to fetch slash commands: {e}")
        return []
