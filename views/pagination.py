# .\views\pagination.py
from collections.abc import Callable, Sequence
from typing import Optional

import discord
from discord.ui import View

from utils.logger import logger


class PagginationView(View):
    def __init__(
        self,
        embeds: Sequence[discord.Embed],
        select_menu: Optional[discord.ui.Select] = None,
        *,
        select_menu_factory: Optional[
            Callable[[int], discord.ui.Select]
        ] = None,
        initial_page: int = 0,
        timeout: Optional[float] = 120.0,
    ) -> None:
        if not embeds:
            raise ValueError("PagginationView requires at least one embed")

        super().__init__(timeout=timeout)

        self._embeds = list(embeds)
        self._len = len(embeds)
        self._current_page = max(0, min(initial_page, self._len - 1))
        self._static_select_menu = select_menu
        self._select_menu_factory = select_menu_factory

        self._update_items()

    def _update_items(self) -> None:
        self.first.disabled = self._current_page == 0
        self.previous.disabled = self._current_page == 0
        self.curent_page.label = f"{self._current_page + 1}/{self._len}"
        self.next.disabled = self._current_page == self._len - 1
        self.last.disabled = self._current_page == self._len - 1

        for item in list(self.children):
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)

        select_menu = self._static_select_menu
        if self._select_menu_factory is not None:
            select_menu = self._select_menu_factory(self._current_page)

        if select_menu is not None:
            self.add_item(select_menu)

    async def _show_page(self, interaction: discord.Interaction) -> None:
        try:
            self._update_items()
            await interaction.response.edit_message(
                embed=self._embeds[self._current_page],
                view=self,
            )
        except Exception as error:
            logger.opt(exception=error).error(
                "Error updating pagination page"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Не вдалося змінити сторінку.",
                    ephemeral=True,
                )

    @discord.ui.button(emoji="⏪")
    async def first(self, interaction: discord.Interaction, _):
        self._current_page = 0
        await self._show_page(interaction)

    @discord.ui.button(emoji="◀️")
    async def previous(self, interaction: discord.Interaction, _):
        if self._current_page > 0:
            self._current_page -= 1
            await self._show_page(interaction)

    @discord.ui.button(style=discord.ButtonStyle.danger,  disabled=True)
    async def curent_page(self, interaction: discord.Interaction, _):
        pass

    @discord.ui.button(emoji="▶️")
    async def next(self, interaction: discord.Interaction, _):
        if self._current_page < self._len - 1:
            self._current_page += 1
            await self._show_page(interaction)

    @discord.ui.button(emoji="⏩")
    async def last(self, interaction: discord.Interaction, _):
        self._current_page = self._len - 1
        await self._show_page(interaction)

    @property
    def initial(self) -> discord.Embed:
        return self._embeds[self._current_page]
