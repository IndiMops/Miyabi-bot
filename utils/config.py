#./utils/config.py
import os
import json

from box import Box
from dotenv import load_dotenv

from utils.logger import logger
from utils.misc import load_json

load_dotenv()

class Config:
    # environment variables
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    json_config = load_json("config.json")
    
    # public variables
    PUBLIC = Box(json_config)
    
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
