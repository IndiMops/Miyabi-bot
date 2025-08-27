# .\views\pagination.py
import discord
from discord.ui import View

from typing import List, Optional

from utils.logger import logger


class PagginationView(View):
    def __init__(self, embeds: List[discord.Embed], select_menu: Optional[discord.ui.Select]) -> None:
        super().__init__()

        self._embeds = embeds
        self._initial = embeds[0] # First embed
        self._len = len(embeds)
        self._current_page = 1
        self.children[0].disabled = True
        self.children[1].disabled = True
        self.children[2].label = f"{self._current_page}/{self._len}"

        if select_menu:
            self.add_item(select_menu)

    async def update_butons(self, interaction: discord.Interaction) -> None:
        try:
            self.children[0].disabled = self._current_page == 1  # Previous
            self.children[1].disabled = self._current_page == 1  # First
            self.children[2].label = f"{self._current_page}/{self._len}"
            self.children[3].disabled = self._current_page == self._len  # Last
            self.children[4].disabled = self._current_page == self._len  # Next

            await interaction.edit_original_response(view=self)
        except Exception as e:
            pass
            logger.error(f"Error updating pagination buttons: {e}")

    @discord.ui.button(emoji="⏪")
    async def first(self, interaction: discord.Interaction, _):
        self._current_page = 1
        await interaction.response.edit_message(embed=self._embeds[self._current_page - 1])
        await self.update_butons(interaction)

    @discord.ui.button(emoji="◀️")
    async def previous(self, interaction: discord.Interaction, _):
        if self._current_page > 1:
            self._current_page -= 1
            await interaction.response.edit_message(embed=self._embeds[self._current_page - 1])
            await self.update_butons(interaction)

    @discord.ui.button(style=discord.ButtonStyle.danger,  disabled=True)
    async def curent_page(self, interaction: discord.Interaction, _):
        pass

    @discord.ui.button(emoji="▶️")
    async def next(self, interaction: discord.Interaction, _):
        if self._current_page < self._len:
            self._current_page += 1
            await interaction.response.edit_message(embed=self._embeds[self._current_page - 1])
            await self.update_butons(interaction)

    @discord.ui.button(emoji="⏩")
    async def last(self, interaction: discord.Interaction, _):
        self._current_page = self._len
        await interaction.response.edit_message(embed=self._embeds[self._current_page - 1])
        await self.update_butons(interaction)

    @property
    def initial(self) -> discord.Embed:
        return self._initial
