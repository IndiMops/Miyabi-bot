import math
import os
from pathlib import Path

from box import Box
from dotenv import load_dotenv

from utils.logger import logger
from utils.misc import load_json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _env_float(name: str, default: float, minimum: float = 0.0) -> float:
    """Read a float from the environment, falling back to the default on bad input."""
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        value = float(raw_value)
    except ValueError:
        value = math.nan
    if not math.isfinite(value):
        logger.warning(f"{name} is not a finite number; using default {default}")
        return default
    if value < minimum:
        logger.warning(f"{name} must be >= {minimum}; using default {default}")
        return default
    return value


class Config:
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    # Sync slash commands with Discord on startup; when disabled, the existing
    # registrations are only fetched to learn the command IDs.
    SYNC_COMMANDS = os.getenv("SYNC_COMMANDS", "True").lower() == "true"

    # Status heartbeat reporter. Disabled unless both URL and secret are set.
    STATUS_HEARTBEAT_URL = os.getenv("STATUS_HEARTBEAT_URL", "").strip()
    STATUS_HEARTBEAT_SECRET = os.getenv("STATUS_HEARTBEAT_SECRET", "").strip()
    STATUS_SERVICE_NAME = os.getenv("STATUS_SERVICE_NAME", "miyabi-bot").strip()
    STATUS_HEARTBEAT_INTERVAL = _env_float("STATUS_HEARTBEAT_INTERVAL", 30.0, minimum=5.0)
    STATUS_HEARTBEAT_TIMEOUT = _env_float("STATUS_HEARTBEAT_TIMEOUT", 5.0, minimum=1.0)

    json_config = load_json(PROJECT_ROOT / "config.json")
    PUBLIC = Box(json_config)

    @classmethod
    def require_token(cls) -> str:
        if not cls.DISCORD_BOT_TOKEN:
            raise RuntimeError(
                "DISCORD_BOT_TOKEN is not set. Add it to the environment or .env file."
            )
        return cls.DISCORD_BOT_TOKEN
