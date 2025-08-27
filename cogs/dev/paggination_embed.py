import discord
from discord.ext import commands
from discord import app_commands

from views.pagination import PagginationView
from utils.logger import logger


class EmbedTest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pagination_test", description="Test pagination with embeds")
    async def pagination_test(self, interaction: discord.Interaction):
        try:
            embeds = [
                discord.Embed(title="Page 1",
                              description="This is the first page"),
                discord.Embed(title="Page 2",
                              description="This is the second page"),
                discord.Embed(title="Page 3",
                              description="This is the third page"),
                discord.Embed(title="Page 4",
                              description="This is the fourth page"),
                discord.Embed(title="Page 5",
                              description="This is the fifth page"),
                discord.Embed(title="Page 6",
                              description="This is the sixth page"),
                discord.Embed(title="Page 7",
                              description="This is the seventh page"),
                discord.Embed(title="Page 8",
                              description="This is the eighth page"),
                discord.Embed(title="Page 9",
                              description="This is the ninth page"),
                discord.Embed(title="Page 10",
                              description="This is the tenth page"),
            ]

            view = PagginationView(embeds, select_menu=None)
            await interaction.response.send_message(embed=view.initial, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"An error occurred in embed_test command: {e}")
            await interaction.response.send_message(
                content="An error occurred while processing your request. Please try again later.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedTest(bot))
