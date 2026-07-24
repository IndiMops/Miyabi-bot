from typing import List, Type, Optional, Any

import discord
from discord.ui import View, Select

from views.pagination import PaginationView


class NavSelect(Select):
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

        # Check if children contains labels, values, and emojis
        options = []
        for child in children:
            if isinstance(child, dict):  # If child is a dictionary with 'label', 'value', and optional 'emoji'
                options.append(discord.SelectOption(
                    label=child['label'],
                    value=child['value'],
                    emoji=child.get('emoji')  # Use .get() to handle optional 'emoji'
                ))
            elif isinstance(child, tuple):  # If child is a tuple (label, value, emoji)
                if len(child) == 3:  # Tuple with emoji
                    options.append(discord.SelectOption(label=child[0], value=child[1], emoji=child[2]))
                elif len(child) == 2:  # Tuple without emoji
                    options.append(discord.SelectOption(label=child[0], value=child[1]))
            else:  # Fallback for backward compatibility (child is a string)
                options.append(discord.SelectOption(label=child, value=child))

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
            pag_view = PaginationView(pages, select_menu)
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
