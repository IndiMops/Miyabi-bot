import discord
from discord import app_commands
from discord.ext import commands

from embeds.wiki.characters import (
    CharactersMainEmbeds as CharactersEmbeds,
    find_agent_route,
    search_agent_routes,
)
from utils.logger import logger
from views.nav import build_navigation_level


class CharactersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def agent_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(
                name=route.display_name,
                value=route.key,
            )
            for route in search_agent_routes(current)
        ]

    @app_commands.command(
        name="characters",
        description="Get information about characters.",
    )
    @app_commands.describe(
        agent="Почніть вводити ім'я агента для швидкого переходу.",
    )
    @app_commands.autocomplete(
        agent=agent_autocomplete,
    )
    async def characters(
        self,
        interaction: discord.Interaction,
        agent: str | None = None,
    ):
        history = ["Main"]

        if agent is not None:
            route = find_agent_route(agent)

            if route is None:
                await interaction.response.send_message(
                    f"Сторінку агента `{agent}` не знайдено. "
                    "Скористайтеся підказками autocomplete.",
                    ephemeral=True,
                )
                return

            history = route.history

        embed, view = build_navigation_level(
            history,
            CharactersEmbeds,
            "Виберіть елемент персонажа...",
            {},
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(CharactersCommand(bot))
    logger.info("Characters command cog loaded.")
