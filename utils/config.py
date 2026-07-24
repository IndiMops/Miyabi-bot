import os
from pathlib import Path

from box import Box
from dotenv import load_dotenv

from utils.misc import load_json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    json_config = load_json(PROJECT_ROOT / "config.json")
    PUBLIC = Box(json_config)

    @classmethod
    def require_token(cls) -> str:
        if not cls.DISCORD_BOT_TOKEN:
            raise RuntimeError(
                "DISCORD_BOT_TOKEN is not set. Add it to the environment or .env file."
            )
        return cls.DISCORD_BOT_TOKEN

    @classmethod
    def get_command_id_by_name(cls, name: str) -> int | None:
        """
        Отримує ID команди за її назвою.

        Args:
            name (str): Назва команди.

        Returns:
            int | None: ID команди, якщо знайдено, або None.
        """
        commands = cls.PUBLIC.bot.get("commands", [])
        for command in commands:
            if command["name"] == name:
                return command["id"]
        return None
