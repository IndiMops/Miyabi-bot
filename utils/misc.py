import os
import json
import requests
import subprocess

from discord.ext import commands

from utils.logger import logger


def load_json(file_path: str):
    """
    Load a JSON file and return its content.
    
    Args:
        file_path (str): The path to the JSON file.
        
    Returns:
        dict: The content of the JSON file as a dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            output = json.loads(file.read())
            file.close()
    except Exception as e:
        logger.error(f"Could not load json file {file_path} due to exception {e}")
        output = {}

    return output


def HEXtoColor(hex_str: str) -> int:
    return int(hex_str.lstrip('#'), 16) if hex_str.startswith('#') else int(hex_str, 16)


def HEXtoRGB(hex_str: str) -> tuple:
    """
    Convert a HEX color string to an RGB tuple.
    
    Args:
        hex_str (str): The HEX color string (e.g., '#FF5733').
        
    Returns:
        tuple: A tuple representing the RGB color (R, G, B).
    """
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def get_user(bot_token: str, user_id: int):
    headers = {"Authorization": f"Bot {bot_token}"}
    req = requests.get(f"https://discord.com/api/v9/users/{user_id}", headers=headers).json()
    return json.dumps(req, indent=4, ensure_ascii=False)


def get_version(default_version: str):
    try:
        version = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
        if version.isalnum():
            return f"dev-{version}"
        return version
    except Exception as e:
        logger.error(f"Failed to get version from git: {e}")
        return default_version
    
    
async def fetch_slash_commands(bot):
    try:
        commands = await bot.tree.fetch_commands()
        return [{"name": cmd.name, "id": cmd.id} for cmd in commands]
    except Exception as e:
        logger.error(f"Failed to fetch slash commands: {e}")
        return []

async def get_command_id_by_name(bot, name: str):
    commands = await bot.tree.fetch_commands()
    for cmd in commands:
        if cmd.name == name:
            return cmd.id
    return None
