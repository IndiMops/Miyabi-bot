#./utils/misc.py
import json

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