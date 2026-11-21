import discord
from discord import app_commands
from discord.ext import commands

from embeds.information import (
    COMMAND_DOCS,
    HELP_CATEGORIES,
    build_category_embed,
    build_command_embed,
    build_main_embed,
)
from utils.logger import logger
from views.pagination import TimeoutView

MAIN_OPTION_VALUE = "__main__"


class HelpCategorySelect(discord.ui.Select):
    """Switches the help message between the overview and the category pages."""

    def __init__(self) -> None:
        options = [
            discord.SelectOption(label="Усі команди", value=MAIN_OPTION_VALUE, emoji="🏠"),
            *(
                discord.SelectOption(label=category.label, value=category.key, emoji=category.emoji)
                for category in HELP_CATEGORIES
            ),
        ]
        super().__init__(placeholder="Оберіть категорію...", options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        choice = self.values[0]
        embed = build_main_embed() if choice == MAIN_OPTION_VALUE else build_category_embed(choice)
        for option in self.options:
            option.default = option.value == choice
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def auto_complete_command_name(self, interaction: discord.Interaction, current: str):
        current = current.lower().strip()
        return [
            app_commands.Choice(name=name, value=name)
            for name in COMMAND_DOCS
            if current in name
        ][:25]

    async def auto_complete_command_category(self, interaction: discord.Interaction, current: str):
        current = current.lower().strip()
        return [
            app_commands.Choice(name=f"{category.label} ({category.key})", value=category.key)
            for category in HELP_CATEGORIES
            if current in category.key or current in category.label.lower()
        ][:25]

    @app_commands.command(name="help", description="Show detailed information about the bot's commands and features.")
    @app_commands.autocomplete(command_name=auto_complete_command_name, command_category=auto_complete_command_category)
    @app_commands.describe(command_name="Get help for a specific command.", command_category="Get help for a specific category.")
    @app_commands.rename(command_name="command", command_category="category")
    async def help(self, interaction: discord.Interaction, command_name: str | None = None, command_category: str | None = None):
        if command_name:
            command_name = command_name.strip().removeprefix("/").lower()
            embed = build_command_embed(command_name)
            if embed is None:
                await interaction.response.send_message(f"Команди `{command_name}` не знайдено.", ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if command_category:
            embed = build_category_embed(command_category.strip().lower())
            if embed is None:
                await interaction.response.send_message(f"Категорію `{command_category}` не знайдено.", ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = TimeoutView()
        view.add_item(HelpCategorySelect())
        await interaction.response.send_message(embed=build_main_embed(), view=view, ephemeral=True)
        view.bind_to_interaction(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
    logger.info("Help command cog loaded.")
