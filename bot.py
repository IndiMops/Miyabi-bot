import asyncio
import os

import discord
from discord.ext import commands, tasks

from utils.config import Config
from utils.logger import logger
from utils.misc import get_version, fetch_slash_commands


bot = commands.Bot(
    command_prefix=Config.PUBLIC.bot.prefix,
    intents=discord.Intents.all(),
    help_command=None,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    owner_id=Config.PUBLIC.dev.id,
)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        change_status.start()
        logger.info(f"Bot is ready! Logged in as {bot.user}")
        bot.slash_commands = await fetch_slash_commands(bot)
        
    except Exception as e:
        logger.error(f"Error during bot startup: {e}")


@tasks.loop(seconds=10)
async def change_status():
    """
    Changes the status and activity of the bot.
    This function iterates through the guilds the bot is a member of and counts the unique non-bot
    members.
    It then sets the bot's status and activity using the count of unique members.
    Parameters:
        None
    Returns:
        None
    """
    unique_members = set()

    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                unique_members.add(member.id)

    statuses = [
        discord.Game(
            name=f"/help | {get_version('v0.0.1')}",),
        discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(unique_members)} members"
        )
    ]

    for status in statuses:
        await bot.change_presence(status=discord.Status.online, activity=status)
        await asyncio.sleep(25)


async def load_extentions():
    for root, _, files in os.walk("./cogs"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), "cogs")
                module = f"cogs.{rel_path}".replace(os.sep, ".").removesuffix(".py")
                
                if not Config.DEBUG and module in Config.PUBLIC.bot.disabled_cogs_folder:
                    continue
                
                try:
                    await bot.load_extension(module)
                    logger.info(f"✅ Loaded extension: {module}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {module}: {e}")

if __name__ == "__main__":
    async def main():
        await load_extentions()
        await bot.start(Config.DISCORD_BOT_TOKEN)
    
    asyncio.run(main())
