import math
from typing import Any, Dict, List, Optional, Type

import discord
from discord.ui import Select, View

from views.pagination import PaginationView, TimeoutView

MAX_SELECT_OPTIONS = 25
BACK_OPTION_VALUE = "BACK"


def _get_visible_children(
    history: List[str],
    embed_cls: Type[Any],
) -> tuple[List[Any], bool, str]:
    """Keep a parent's tabs visible while browsing their paginated sections."""
    current = history[-1]
    children = embed_cls.get_children(current)

    if children or len(history) <= 1 or not embed_cls.get_pages(current):
        return children, False, current

    parent_children = embed_cls.get_children(history[-2])
    sibling_values = {
        child.get("value") if isinstance(child, dict) else child[1]
        for child in parent_children
        if isinstance(child, (dict, tuple))
    }
    shows_sibling_tabs = current in sibling_values
    menu_key = history[-2] if shows_sibling_tabs else current
    return parent_children, shows_sibling_tabs, menu_key


def _get_level_placeholder(
    embed_cls: Type[Any],
    key: str,
    fallback: str,
) -> str:
    """Resolve an optional placeholder declared beside a level's children."""
    get_placeholder = getattr(embed_cls, "get_placeholder", None)
    if get_placeholder is None:
        return fallback
    return get_placeholder(key, fallback)


class NavSelect(Select):
    def __init__(
        self,
        history: List[str],
        embed_cls: Type[Any],
        placeholder: str = "Select an option...",
        *,
        option_page: int = 0,
        page_state: Optional[Dict[str, int]] = None,
    ):
        self.history = history.copy()
        self.embed_cls = embed_cls
        self._placeholder = placeholder
        self.page_state = page_state if page_state is not None else {}

        current = self.history[-1]
        children, self._shows_sibling_tabs, menu_key = _get_visible_children(
            self.history,
            embed_cls,
        )
        self._placeholder = _get_level_placeholder(
            embed_cls,
            menu_key,
            placeholder,
        )
        page_size = MAX_SELECT_OPTIONS - int(len(self.history) > 1)
        page_count = max(1, math.ceil(len(children) / page_size))
        self._option_page = max(0, min(option_page, page_count - 1))

        start = self._option_page * page_size
        visible_children = children[start:start + page_size]

        options = []
        for child in visible_children:
            if isinstance(child, dict):
                options.append(discord.SelectOption(
                    label=child['label'],
                    value=child['value'],
                    description=child.get('description'),
                    emoji=child.get('emoji'),
                ))
            elif isinstance(child, tuple):
                if len(child) == 3:
                    options.append(discord.SelectOption(label=child[0], value=child[1], emoji=child[2]))
                elif len(child) == 2:
                    options.append(discord.SelectOption(label=child[0], value=child[1]))
            else:
                options.append(discord.SelectOption(label=child, value=child))

        if len(self.history) > 1:
            options.append(discord.SelectOption(
                label="Back",
                value=BACK_OPTION_VALUE,
            ))

        super().__init__(placeholder=self._placeholder,
                        min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        if choice == BACK_OPTION_VALUE:
            self.history.pop()
            await self._show_level(interaction)
            return

        if self._shows_sibling_tabs:
            self.history[-1] = choice
        else:
            self.history.append(choice)
        await self._show_level(interaction)

    async def _show_level(self, interaction: discord.Interaction):
        embed, view = build_navigation_level(
            self.history,
            self.embed_cls,
            self._placeholder,
            self.page_state,
        )
        view.bind_to_message(interaction.message)
        if self.view is not None:
            self.view.stop()
        await interaction.response.edit_message(embed=embed, view=view)


class NavView(TimeoutView):
    def __init__(
        self,
        history: List[str],
        embed_cls: Type[Any],
        placeholder: str = "Select an option...",
        timeout: Optional[float] = None,
        *,
        page_state: Optional[Dict[str, int]] = None,
    ):
        super().__init__(timeout=timeout)
        self.page_state = page_state if page_state is not None else {}
        current = history[-1]
        option_page = self.page_state.get(current, 0)
        self.add_item(NavSelect(
            history,
            embed_cls,
            placeholder,
            option_page=option_page,
            page_state=self.page_state,
        ))

def build_navigation_level(
    history: List[str],
    embed_cls: Type[Any],
    placeholder: str,
    page_state: Dict[str, int],
) -> tuple[discord.Embed, View]:
    current = history[-1]
    children, _, _ = _get_visible_children(history, embed_cls)
    pages = embed_cls.get_pages(current)
    page_size = MAX_SELECT_OPTIONS - int(len(history) > 1)

    if pages:
        initial_page = min(page_state.get(current, 0), len(pages) - 1)
        if len(children) > page_size:
            expected_page_count = math.ceil(len(children) / page_size)
            if len(pages) != expected_page_count:
                raise ValueError(
                    f"{current} requires {expected_page_count} embed pages "
                    f"for {len(children)} select options, got {len(pages)}"
                )

            history_snapshot = history.copy()

            def select_menu_factory(page_index: int) -> NavSelect:
                page_state[current] = page_index
                return NavSelect(
                    history_snapshot,
                    embed_cls,
                    placeholder,
                    option_page=page_index,
                    page_state=page_state,
                )

            view = PaginationView(
                pages,
                select_menu_factory=select_menu_factory,
                initial_page=initial_page,
            )
        else:
            view = PaginationView(
                pages,
                NavSelect(
                    history,
                    embed_cls,
                    placeholder,
                    page_state=page_state,
                ),
            )

        return view.initial, view

    embed = embed_cls.get_embed(current)
    view = NavView(
        history,
        embed_cls,
        placeholder,
        page_state=page_state,
    )
    return embed, view
