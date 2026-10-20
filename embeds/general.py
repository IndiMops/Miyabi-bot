from datetime import datetime
from collections.abc import Iterable
from typing import Any

import discord

from utils.config import Config


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
