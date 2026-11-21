"""Alice Thymefield: her sections assembled into the navigation embed contract.

Each section lives in its own module (see docs/agent-template.md), so pages
can be filled in independently.
"""

import discord

from . import basic_info, combat, mindscape, profile, progression, skills

SECTIONS = (
    basic_info.SECTION,
    combat.SECTION,
    skills.SECTION,
    mindscape.SECTION,
    progression.SECTION,
    profile.SECTION,
)


class AliceEmbed:
    Main_placeholder = "Оберіть розділ про Алісу..."
    Main_children = [section.tab for section in SECTIONS]

    # Entering Alice immediately opens the first section while keeping all
    # section tabs available in the select menu.
    Main_pages = list(basic_info.SECTION.pages)
    Main = Main_pages[0]

    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key: str) -> list:
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)

    @classmethod
    def get_placeholder(cls, key: str, fallback: str) -> str:
        return getattr(cls, f"{key}_placeholder", fallback)


# A regular embed (the first page) is kept for the navigation contract;
# pagination uses the matching ``<key>_pages`` list when a section is opened.
for _section in SECTIONS:
    setattr(AliceEmbed, _section.key, _section.pages[0])
    setattr(AliceEmbed, f"{_section.key}_pages", list(_section.pages))
del _section

__all__ = ["AliceEmbed", "SECTIONS"]
