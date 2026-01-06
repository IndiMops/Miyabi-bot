import datetime
from typing import List

import discord

from utils.config import Config
from utils.misc import HEXtoColor


class AliceEmbed:
    Main = discord.Embed(
        title="Аліса - Віртуальний Асистент Zenless Zone Zero",
        description="Аліса - це віртуальний асистент, розроблений для допомоги гравцям у Zenless Zone Zero. Вона надає інформацію про гру, допомагає з навігацією та відповідає на запитання гравців.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )
    
    
    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)
    
    @classmethod
    def get_children(cls, key: str) -> List[str]:
        return getattr(cls, f"{key}_children", [])
    
    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)
    
    
