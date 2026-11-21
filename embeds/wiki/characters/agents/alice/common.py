"""Shared look of Alice's pages: color, icons, author and footer."""

import discord

from embeds.general import add_default_footer
from utils.misc import HEXtoColor

COLOR = "243A63"
ICON_URL = (
    "https://res.cloudinary.com/z5ozewii/image/upload/"
    "v1785057256/Agent_Alice_Thymefield_Icon_ojp90y.png"
)
AUTHOR_ICON_URL = (
    "https://res.cloudinary.com/z5ozewii/image/upload/"
    "v1785055164/Message_Alice_Thymefield_Icon_webp_vr2vav.png"
)
WIKI_URL = "https://zenless-zone-zero.fandom.com/wiki/Alice_Thymefield"


def decorate(embed: discord.Embed) -> discord.Embed:
    """Apply the shared Alice author, thumbnail, and project footer."""
    embed.set_author(
        name="Аліса Таймфілд",
        icon_url=AUTHOR_ICON_URL,
        url=WIKI_URL,
    )
    embed.set_thumbnail(url=ICON_URL)
    return add_default_footer(embed)


def placeholder_pages(section_title: str, page_count: int) -> list[discord.Embed]:
    """Create temporary paginated embeds for a section without content yet."""
    return [
        decorate(
            discord.Embed(
                title=f"{section_title} — {page}/{page_count}",
                description=(
                    f"Заглушка для сторінки {page} розділу "
                    f"«{section_title}». Тут пізніше буде додано вміст."
                ),
                color=HEXtoColor(COLOR),
            )
        )
        for page in range(1, page_count + 1)
    ]
