# .\views\pagination.py
import discord
from discord.ui import View

from collections.abc import Sequence
from typing import Optional

from utils.logger import logger


class PaginationView(View):
    def __init__(
        self,
        embeds: Sequence[discord.Embed],
        select_menu: Optional[discord.ui.Select] = None,
        timeout: float | None = 120.0,
    ) -> None:
        if not embeds:
            raise ValueError("PaginationView requires at least one embed")

        super().__init__(timeout=timeout)
        self._embeds = list(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self._update_buttons()

        if select_menu:
            self.add_item(select_menu)

    def _update_buttons(self) -> None:
        self.first.disabled = self._current_page == 1
        self.previous.disabled = self._current_page == 1
        self.current_page.label = f"{self._current_page}/{self._len}"
        self.next.disabled = self._current_page == self._len
        self.last.disabled = self._current_page == self._len

    async def _show_page(self, interaction: discord.Interaction) -> None:
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self._embeds[self._current_page - 1],
            view=self,
        )

    @discord.ui.button(emoji="⏪")
    async def first(self, interaction: discord.Interaction, _):
        self._current_page = 1
        await self._show_page(interaction)

    @discord.ui.button(emoji="◀️")
    async def previous(self, interaction: discord.Interaction, _):
        if self._current_page > 1:
            self._current_page -= 1
            await self._show_page(interaction)

    @discord.ui.button(style=discord.ButtonStyle.danger,  disabled=True)
    async def current_page(self, interaction: discord.Interaction, _):
        pass

    @discord.ui.button(emoji="▶️")
    async def next(self, interaction: discord.Interaction, _):
        if self._current_page < self._len:
            self._current_page += 1
            await self._show_page(interaction)

    @discord.ui.button(emoji="⏩")
    async def last(self, interaction: discord.Interaction, _):
        self._current_page = self._len
        await self._show_page(interaction)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item,
    ) -> None:
        logger.opt(exception=error).error(
            f"Pagination interaction failed for {item!r}"
        )
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Не вдалося змінити сторінку. Спробуйте ще раз.",
                ephemeral=True,
            )

    @property
    def initial(self) -> discord.Embed:
        return self._initial


# Temporary compatibility alias for older imports.
PagginationView = PaginationView
