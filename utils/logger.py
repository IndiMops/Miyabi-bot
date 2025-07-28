"""
Logger configuration for the application.
This module sets up logging using the Loguru library. It loads environment variables 
from a .env file to determine the debug mode and log level. The logs are directed to 
both the console and a log file, with specific formatting and retention policies.
Key Features:
- Loads environment variables to configure logging behavior.
- Supports DEBUG and INFO log levels based on the DEBUG environment variable.
- Creates a 'logs' directory if it does not exist.
- Configures console logging with a specific format.
- Logs to a file with rotation, retention, and compression settings.
Environment Variables:
- DEBUG: Set to 'true' to enable DEBUG logging; otherwise, INFO logging is used.
Log File:
- Logs are stored in 'logs/bot.log' with a rotation size of 10 MB and retained for 10 days.
"""
import sys
import logging
import os

from dotenv import load_dotenv
from loguru import logger


load_dotenv() # load environment variables from .env file

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"

os.makedirs("logs", exist_ok=True)  # Ensure the logs directory exists


logger.remove()  # Remove the default logger

logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | [<level>{level}</level>] <cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

logger.add(
    "logs/bot.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{name}:{function}:{line} | {message}"
)

# Setting up a standard Python logger
standard_logger = logging.getLogger()
standard_logger.setLevel(logging.DEBUG)

# Format for standard console logs
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "%(asctime)s | [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(console_formatter)

# Format for standard in-file logs
file_handler = logging.FileHandler("logs/standard.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s | [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(file_formatter)

standard_logger.addHandler(console_handler)
standard_logger.addHandler(file_handler)
