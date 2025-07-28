from typing import List, Type, Optional, Any

import discord
from discord.ui import View, Select

from utils.logger import logger
from views.pagination import PagginationView


class NavSelect(Select):
    """
    NavSelect is a custom selection class that allows users to navigate through a hierarchical selection of options.
    Attributes:
        history (List[str]): A list that keeps track of the user's selection history.
        embed_cls (Type[Any]): A class used to generate the embed content for the selections.
        _placeholder (str): A placeholder text displayed in the selection menu.
    Methods:
        __init__(history: List[str], embed_cls: Type[Any], placeholder: str = "Select an option..."):
            Initializes the NavSelect instance with the provided history, embed class, and placeholder.
        callback(interaction: discord.Interaction):
            Handles the user's selection and updates the view based on the selected option.
        _show_level(interaction: discord.Interaction):
            Displays the current level of options based on the user's selection history.
    """
    def __init__(
        self,
        history: List[str],
        embed_cls: Type[Any],
        placeholder: str = "Select an option..."
    ):
        self.history = history.copy()
        self.embed_cls = embed_cls
        self._placeholder = placeholder

        current = self.history[-1]
        children = embed_cls.get_children(current)
        options = [discord.SelectOption(label=opt, value=opt)
                   for opt in children]

        if len(self.history) > 1:
            options.append(discord.SelectOption(label="Back", value="BACK"))

        super().__init__(placeholder=self._placeholder,
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        if choice == "BACK":
            self.history.pop()
            await self._show_level(interaction)
            return

        self.history.append(choice)
        # Pagination check
        pages = self.embed_cls.get_pages(choice)
        if pages:
            select_menu = NavSelect(
                self.history, self.embed_cls, self._placeholder)
            pag_view = PagginationView(pages, select_menu)
            await interaction.response.edit_message(embed=pag_view.initial, view=pag_view)
        else:
            await self._show_level(interaction)

    async def _show_level(self, interaction: discord.Interaction):
        current = self.history[-1]
        embed = self.embed_cls.get_embed(current)
        view = NavView(self.history, self.embed_cls, self._placeholder)
        await interaction.response.edit_message(embed=embed, view=view)


class NavView(View):
    def __init__(
        self,
        history: List[str],
        embed_cls: Type[Any],
        placeholder: str = "Select an option...",
        timeout: Optional[float] = 120.0
    ):
        super().__init__(timeout=timeout)
        self.add_item(NavSelect(history, embed_cls, placeholder))
