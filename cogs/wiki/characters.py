import discord
from discord import app_commands
from discord.ext import commands

from embeds.commands_characters import CharactersMainEmbeds as CharactersEmbeds
from utils.logger import logger
from views.nav import NavView


class CharactersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="characters", description="Get information about characters.")
    async def characters(self, interaction: discord.Interaction):
        history = ["Main"]
        embed = CharactersEmbeds.get_embed("Main")
        view = NavView(history, CharactersEmbeds, placeholder="Виберіть атрибут агента...")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CharactersCommand(bot))
    logger.info("Characters command cog loaded.")
