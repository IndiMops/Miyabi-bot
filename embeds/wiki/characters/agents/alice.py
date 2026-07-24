"""Embed pages for Alice Thymefield."""

from typing import List
from datetime import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor
from embeds.general import add_default_footer


class AliceEmbed:
    footer = "Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(curent_year=datetime.now().year, dev_site_url=Config.PUBLIC.dev.website)
    
    
    Main = discord.Embed(
        title="Аліса Таймфілд — огляд",
        description=(
            "Це демонстраційна головна сторінка агента. Тут можна розмістити "
            "атрибут, спеціальність, фракцію та короткий опис персонажа."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    ).set_thumbnail(
        url=Config.PUBLIC.bot.assets.avatar
    ).add_field(
        name="Атрибут",
        value="Фізичний",
        inline=True
    ).add_field(
        name="Статус сторінки",
        value="Демонстраційний приклад",
        inline=True
    ).set_footer(
        text=footer,
        icon_url=Config.PUBLIC.bot.assets.avatar
    )
    
    set_default_footer = add_default_footer(Main)

    Skills = discord.Embed(
        title="Аліса Таймфілд — навички",
        description=(
            "Друга сторінка показує, як розділити великий опис агента "
            "на кілька embeds."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    ).add_field(
        name="Базова атака",
        value="Тут буде опис базової атаки.",
        inline=False
    ).add_field(
        name="Особлива атака",
        value="Тут буде опис особливої атаки.",
        inline=False
    ).add_field(
        name="Суперздібність",
        value="Тут буде опис суперздібності.",
        inline=False
    )
    
    set_default_footer = add_default_footer(Skills)

    Build = discord.Embed(
        title="Аліса Таймфілд — приклад збірки",
        description=(
            "Третя сторінка є шаблоном. Замінити демонстраційні значення "
            "можна після додавання перевірених ігрових даних."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    ).add_field(
        name="W-Engine",
        value="Тут буде рекомендований W-Engine.",
        inline=False
    ).add_field(
        name="Drive Discs",
        value="Тут буде рекомендований набір Drive Discs.",
        inline=False
    ).add_field(
        name="Пріоритет характеристик",
        value="Тут буде порядок основних і додаткових характеристик.",
        inline=False
    )
    
    set_default_footer = add_default_footer(Build)

    # NavView відкриє пагінацію, коли знайде <key>_pages.
    Main_pages = [Main, Skills, Build]

    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key: str) -> List[str]:
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)
