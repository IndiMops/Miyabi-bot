import discord
from discord import app_commands
from discord.ext import commands

from utils.config import Config
from utils.logger import logger


class PingComand(commands.Cog):
    def __init__(self, bot: commands):
        self.bot = bot


    @app_commands.command(name="ping", description="Check the bot working status")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(
            f"🏓 Pong! Latency: `{round(self.bot.latency * 1000)}ms`"
        )


async def setup(bot: commands):
    await bot.add_cog(PingComand(bot))
