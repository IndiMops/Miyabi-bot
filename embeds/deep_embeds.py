from typing import List

import discord


class DeepEmbeds:
    Main = discord.Embed(
        title="Main menu",
        description="Select a submenu:",
        color=0x00ff00
    )
    Main_children = ["Submenu1", "Submenu2"]

    Submenu1 = discord.Embed(
        title="Submenu 1",
        description="You are in the submenu 1",
        color=0x00ff00
    )
    Submenu1_children = ["Subsubmenu"]

    Submenu2 = discord.Embed(
        title="Submenu 2",
        description="You are in the submenu 2",
        color=0x00ff00
    )
    Submenu2_children: List[str] = []

    Subsubmenu = discord.Embed(
        title="Nested submenu",
        description="You're in a deep level",
        color=0x00ff00
    )
    Subsubmenu_children: List[str] = []
    Subsubmenu_pages: List[discord.Embed] = [
        discord.Embed(title=f"Page {i+1}", description=f"Page {i+1}")
        for i in range(5)
    ]

    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key: str) -> List[str]:
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)
