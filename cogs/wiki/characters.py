import discord
from discord.ext import commands
from discord import app_commands

from utils.config import Config
from utils.logger import logger

from embeds.commands_characters import CharactersMainEmbeds as CharactersEmbeds


class CharactersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="characters", description="Get information about characters.")
    async def characters(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=CharactersEmbeds.Main)


async def setup(bot: commands.Bot):
    await bot.add_cog(CharactersCommand(bot))
    logger.info("Help command cog loaded.")
