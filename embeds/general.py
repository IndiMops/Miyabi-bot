from datetime import datetime
from collections.abc import Iterable, Sequence
from typing import Any

import discord

from utils.config import Config

MAX_PAGE_LINKS = 5  # one row of Discord link buttons


class LinkedEmbed(discord.Embed):
    """An embed whose page shows link buttons under it.

    `links` is a sequence of `(label, url)` pairs. Navigation and pagination
    views render them as link buttons in the bottom row (`TimeoutView.show_links`).
    """

    def __init__(self, *, links: Sequence[tuple[str, str]] = (), **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if len(links) > MAX_PAGE_LINKS:
            raise ValueError(f"A page can show at most {MAX_PAGE_LINKS} link buttons")
        self.links = tuple(links)


def add_fields(
    embed: discord.Embed,
    fields: Iterable[dict[str, Any]],
) -> discord.Embed:
    """Add data-defined fields to an embed and return the same embed."""
    for field in fields:
        embed.add_field(**field)

    return embed


def add_default_footer(embed: discord.Embed) -> discord.Embed:
    return embed.set_footer(
        text=(
            f"Mops Storage © 2020-{datetime.now().year} "
            f"Всі права захищено • {Config.PUBLIC.dev.website}"
        ),
        icon_url=Config.PUBLIC.bot.assets.avatar,
    )
