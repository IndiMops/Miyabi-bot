from typing import List
import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor

from .agents import AliceEmbed
from .routes import ALICE_ROUTE, FIRE_PLACEHOLDER_ROUTES

FIRE_CHARACTERS_PER_PAGE = 24
FIRE_PLACEHOLDER_CHARACTERS = [
    {
        "label": route.display_name,
        "value": route.key,
        "description": f"Тестовий агент №{index}",
    }
    for index, route in enumerate(FIRE_PLACEHOLDER_ROUTES, start=1)
]


def build_fire_character_pages(
    characters: list[dict[str, str]],
) -> list[discord.Embed]:
    pages = []
    page_count = (
        len(characters) + FIRE_CHARACTERS_PER_PAGE - 1
    ) // FIRE_CHARACTERS_PER_PAGE

    for page_index in range(page_count):
        start = page_index * FIRE_CHARACTERS_PER_PAGE
        page_characters = characters[
            start:start + FIRE_CHARACTERS_PER_PAGE
        ]
        end = start + len(page_characters)

        embed = discord.Embed(
            title=(
                f"Вогняні агенти — сторінка "
                f"{page_index + 1}/{page_count}"
            ),
            description=(
                "Це демонстраційний список. На кожній сторінці select-меню "
                "містить до 24 агентів і окремий option `Back`."
            ),
            color=HEXtoColor(Config.PUBLIC.bot.color.default),
        )

        for character in page_characters:
            embed.add_field(
                name=character["label"],
                value="Персонаж-заглушка",
                inline=True,
            )

        embed.set_footer(
            text=(
                f"Агенти {start + 1}–{end} із {len(characters)} • "
                "Оберіть агента в меню нижче"
            )
        )
        pages.append(embed)

    return pages


class CharactersMainEmbeds:
    Main_placeholder = "Оберіть атрибут агента..."
    Main = discord.Embed(
        title="Агенти Zenless Zone Zero: Хто вони такі?",
        description="Агенти — це досвідчені найманці, що спеціалізуються на винищенні Еферіалів у Холлоу. У Zenless Zone Zero вони є головними дійовими персонажами, якими Ви керуєте в бою. Кожен Агент має унікальні бойові стилі, навички та історію, що допомагають йому ефективно боротися з ворогами та розкривати таємниці Нового Еріду.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )
    Main.set_thumbnail(
        url="https://static.wikia.nocookie.net/zenless-zone-zero/images/0/0a/Icon_Agents.png/"
    )
    Main.set_image(
        url="https://media.discordapp.net/attachments/1419011934044291082/1419011967980667032/8ac5568d973c9381ae29c2798dc34a97.jpg?ex=68d03561&is=68cee3e1&hm=06757bc8d4db13a6f2918cff96dbbcb383a03ba4678fed705ee46c7e49522455&=&format=webp&width=1423&height=800"
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
        {"label": "Еферні агенти", "value": "EtherCharacters",
            "emoji": "<:Icon_Ether:1422213491674189937>"}
    ]

    PhysicalCharacters = discord.Embed(
        title="Фізичні агенти",
        description="Фізичні агенти спеціалізуються на ближньому бою та використовують фізичні атаки для знищення ворогів. Вони відомі своєю витривалістю та здатністю завдавати значної шкоди в бою.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    ).set_thumbnail(
        url="https://media.discordapp.net/attachments/1419011934044291082/1422192979350917211/Icon_Physical.png?ex=68dbc7ed&is=68da766d&hm=ab0ae4834894f93cfc8136444f37f88ff634b252fa93f9bc7fbd110181bc55bd&=&format=webp&quality=lossless&width=80&height=80"
    ).set_image(
        url="https://media.discordapp.net/attachments/1419011934044291082/1422216500978253905/Christmas_2023_Artwork.png?ex=68dbddd5&is=68da8c55&hm=9028c1540ba81fcad0e67a512f7943fdf349a6b7726b4107c52c598fff1cbaa6&=&format=webp&quality=lossless&width=1423&height=800"
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

    FireCharacters_children = FIRE_PLACEHOLDER_CHARACTERS
    FireCharacters_placeholder = "Оберіть вогняного агента..."
    FireCharacters_pages = build_fire_character_pages(
        FireCharacters_children
    )
    FireCharacters = FireCharacters_pages[0]

    IceCharacters = discord.Embed(
        title="Крижані агенти",
        description=(
            "Цей розділ ще не наповнений. Додайте IceCharacters_children, "
            "коли будуть готові сторінки крижаних агентів."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    IceCharacters_children = []

    ElectricCharacters = discord.Embed(
        title="Електричні агенти",
        description=(
            "Цей розділ ще не наповнений. Додайте "
            "ElectricCharacters_children, коли будуть готові сторінки "
            "електричних агентів."
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )
    ElectricCharacters_children = []

    EtherCharacters = discord.Embed(
        title="Ефірні агенти",
        description=(
            "Цей розділ ще не наповнений. Додайте EtherCharacters_children, "
            "коли будуть готові сторінки ефірних агентів."
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


for fire_character in FIRE_PLACEHOLDER_CHARACTERS:
    setattr(
        CharactersMainEmbeds,
        fire_character["value"],
        discord.Embed(
            title=fire_character["label"],
            description=(
                "Це демонстраційна сторінка вогняного агента. "
                "Пізніше тут можна розмістити справжній опис, навички "
                "та рекомендовану збірку."
            ),
            color=HEXtoColor(Config.PUBLIC.bot.color.warn),
        ).add_field(
            name="Внутрішній ключ",
            value=f"`{fire_character['value']}`",
            inline=False,
        ),
    )
