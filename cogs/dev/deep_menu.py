import discord
from discord.ext import commands
from discord import app_commands

from views.nav import NavView
from embeds.deep_embeds import DeepEmbeds


class SplitMenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="deep_menu")
    async def split_menu(self, interaction: discord.Interaction):
        history = ["Main"]
        embed = DeepEmbeds.get_embed("Main")
        view = NavView(history, DeepEmbeds, placeholder="Select menu...")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SplitMenuCog(bot))
