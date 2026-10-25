import os
from pathlib import Path

import discord
from discord.ext import commands, tasks

from utils.config import Config
from utils.logger import logger
from utils.misc import get_version


def is_disabled_extension(module: str, disabled_folders: list[str]) -> bool:
    """Return whether an extension belongs to a disabled cog folder."""
    module_parts = set(module.split(".")[1:-1])
    return bool(module_parts.intersection(disabled_folders))


class MiyabiBot(commands.Bot):
    async def setup_hook(self) -> None:
        await load_extensions(self)
        await self.tree.sync()

        if not change_status.is_running():
            change_status.start()


intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = MiyabiBot(
    command_prefix=Config.PUBLIC.bot.prefix,
    intents=intents,
    help_command=None,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(
        everyone=False,
        roles=False,
        users=True,
    ),
    owner_id=int(Config.PUBLIC.dev.id),
)


@bot.event
async def on_ready() -> None:
    logger.info(f"Bot is ready! Logged in as {bot.user}")


@tasks.loop(seconds=30)
async def change_status():
    statuses = (
        discord.Game(name=f"/help | {get_version(Config.PUBLIC.bot.version)}"),
        discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servers",
        ),
    )
    status = statuses[change_status.current_loop % len(statuses)]
    await bot.change_presence(status=discord.Status.online, activity=status)


@change_status.before_loop
async def before_change_status() -> None:
    await bot.wait_until_ready()


async def load_extensions(target_bot: commands.Bot) -> None:
    cogs_path = Path(__file__).resolve().parent / "cogs"
    disabled_folders = list(Config.PUBLIC.bot.disabled_cogs_folder)

    for root, _, files in os.walk(cogs_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), cogs_path)
                module = f"cogs.{rel_path}".replace(os.sep, ".").removesuffix(".py")

                if not Config.DEBUG and is_disabled_extension(module, disabled_folders):
                    logger.info(f"Skipped disabled extension: {module}")
                    continue

                try:
                    await target_bot.load_extension(module)
                    logger.info(f"Loaded extension: {module}")
                except commands.ExtensionError:
                    logger.exception(f"Failed to load extension: {module}")
                    raise


if __name__ == "__main__":
    bot.run(Config.require_token(), log_handler=None)
