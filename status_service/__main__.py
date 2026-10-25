import logging
import os
import sys

from aiohttp import web
from dotenv import load_dotenv
from loguru import logger

from status_service.app import build_production_app
from status_service.settings import PROJECT_ROOT, SettingsError, StatusServiceSettings


def configure_logging() -> None:
    # discord.py logs full webhook URLs (including the token) at DEBUG level.
    # Keep that logger at INFO even if some import configures root logging.
    logging.getLogger("discord.webhook").setLevel(logging.INFO)

    level = "DEBUG" if os.getenv("DEBUG", "False").lower() == "true" else "INFO"
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | [<level>{level}</level>] <cyan>{name}</cyan> - <level>{message}</level>",
    )
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    # Separate file from logs/bot.log: two processes must not rotate one file.
    logger.add(
        logs_dir / "status_service.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    configure_logging()
    try:
        settings = StatusServiceSettings.from_env()
    except SettingsError as error:
        logger.error(f"Status service configuration error: {error}")
        sys.exit(2)

    logger.info(
        f"Status service for '{settings.service_name}' listening on "
        f"http://{settings.host}:{settings.port} (state file: {settings.state_file})"
    )
    web.run_app(
        build_production_app(settings),
        host=settings.host,
        port=settings.port,
        access_log=None,
        print=None,
    )


if __name__ == "__main__":
    main()
