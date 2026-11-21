from typing import List
import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor

from .agents import AliceEmbed
from .routes import ALICE_ROUTE


class CharactersMainEmbeds:
    Main_placeholder = "Оберіть атрибут агента..."
    Main = discord.Embed(
        title="Агенти Zenless Zone Zero: Хто вони такі?",
        description="Агенти — це досвідчені найманці, що спеціалізуються на винищенні Ефіріалів у Холлоу. У Zenless Zone Zero вони є головними дійовими персонажами, якими Ви керуєте в бою. Кожен Агент має унікальні бойові стилі, навички та історію, що допомагають йому ефективно боротися з ворогами та розкривати таємниці Нового Еріду.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )
    Main.set_thumbnail(
        url="https://static.wikia.nocookie.net/zenless-zone-zero/images/0/0a/Icon_Agents.png/"
    )
    Main.set_image(
        url="https://res.cloudinary.com/z5ozewii/image/upload/v1794582840/8ac5568d973c9381ae29c2798dc34a97_jd5pyz.jpg"
    )

    Main.set_footer(
        text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
            curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website
        ),
        icon_url=Config.PUBLIC.bot.assets.avatar
    )

    Main_children = [
        {"label": "Фізичні агенти", "value": "PhysicalCharacters",
            "emoji": "<:Icon_Physical:1422213096117764116>"},
        {"label": "Вогняні агенти", "value": "FireCharacters",
            "emoji": "<:Icon_Fire:1422213479208845332>"},
        {"label": "Крижані агенти", "value": "IceCharacters",
            "emoji": "<:Icon_Ice:1422213464071475302>"},
        {"label": "Електричні агенти", "value": "ElectricCharacters",
            "emoji": "<:Icon_Electric:1422213503967690817>"},
        {"label": "Ефірні агенти", "value": "EtherCharacters",
            "emoji": "<:Icon_Ether:1422213491674189937>"}
    ]

    PhysicalCharacters = discord.Embed(
        title="Фізичні агенти",
        description="Фізичні агенти спеціалізуються на ближньому бою та використовують фізичні атаки для знищення ворогів. Вони відомі своєю витривалістю та здатністю завдавати значної шкоди в бою.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    ).set_thumbnail(
        url="https://res.cloudinary.com/z5ozewii/image/upload/v1794583182/Icon_Physical_ytljtg.png"
    ).set_image(
        url="https://res.cloudinary.com/z5ozewii/image/upload/c_limit,w_1536,q_auto,f_webp/v1794583115/Christmas_2023_Artwork_qboriq.png"
    ).set_footer(
        text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
            curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website
        ),
        icon_url=Config.PUBLIC.bot.assets.avatar
    ).add_field(
        name="Агенти фізичного атрибуту",
        value="Оберіть агента в меню нижче.",
        inline=False
    ).add_field(
        name="<:Agent_Alice_Thymefield_Icon:1422224006219698248> Аліса",
        value="Відкриває демонстраційні сторінки огляду, навичок і збірки.",
        inline=False
    )

    PhysicalCharacters_children = [
        {
            "label": "Аліса",
            "value": ALICE_ROUTE.key,
            "emoji": "<:Agent_Alice_Thymefield_Icon:1422224006219698248>"
        }
    ]
    PhysicalCharacters_placeholder = "Оберіть фізичного агента..."

    # Головна сторінка Alice відкриває окремі тематичні розділи.
    Alice = AliceEmbed.get_embed("Main")
    Alice_children = AliceEmbed.get_children("Main")
    Alice_pages = AliceEmbed.get_pages("Main")
    Alice_placeholder = AliceEmbed.get_placeholder(
        "Main",
        "Оберіть розділ персонажа...",
    )

    FireCharacters = discord.Embed(
        title="Вогняні агенти",
        description=(
            "Цей розділ ще не наповнений: сторінки вогняних агентів "
            "з'являться в наступних оновленнях."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    FireCharacters_children = []

    IceCharacters = discord.Embed(
        title="Крижані агенти",
        description=(
            "Цей розділ ще не наповнений: сторінки крижаних агентів "
            "з'являться в наступних оновленнях."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    IceCharacters_children = []

    ElectricCharacters = discord.Embed(
        title="Електричні агенти",
        description=(
            "Цей розділ ще не наповнений: сторінки електричних агентів "
            "з'являться в наступних оновленнях."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    ElectricCharacters_children = []

    EtherCharacters = discord.Embed(
        title="Ефірні агенти",
        description=(
            "Цей розділ ще не наповнений: сторінки ефірних агентів "
            "з'являться в наступних оновленнях."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    EtherCharacters_children = []

    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key: str) -> List[str]:
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)

    @classmethod
    def get_placeholder(cls, key: str, fallback: str) -> str:
        return getattr(cls, f"{key}_placeholder", fallback)

# Додаємо розділи Alice до спільного контракту навігації персонажів.
for alice_section in AliceEmbed.get_children("Main"):
    section_key = alice_section["value"]
    setattr(
        CharactersMainEmbeds,
        section_key,
        AliceEmbed.get_embed(section_key),
    )
    setattr(
        CharactersMainEmbeds,
        f"{section_key}_pages",
        AliceEmbed.get_pages(section_key),
    )
