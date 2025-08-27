#./utils/config.py
import os

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
