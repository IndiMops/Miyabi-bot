#./utils/config.py
import os

from box import Box
from dotenv import load_dotenv

from utils.logger import logger
from utils.misc import load_json

load_dotenv()

json_config = load_json("config.json")


class Config:
    # environment variables
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    # public variables
    PUBLIC = Box(json_config)
