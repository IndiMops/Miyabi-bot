from typing import List
import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor

from embeds.alice_embed import AliceEmbed


class CharactersMainEmbeds:
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
        name="Агенти фізичного атрибуту:", value="", inline=False
    ).add_field(
        name="<:Agent_Alice_Thymefield_Icon:1422224006219698248> Аліса",
        value=f"</characters:{Config.get_command_id_by_name('characters')}> `agent=alice`",
        inline=False
    )

    Alice = AliceEmbed.get_embed("Main")
    PhysicalCharacters_children = [
        {
            "label": "Аліса",
            "value": "Alice",
            "emoji": "<:Agent_Alice_Thymefield_Icon:1422224006219698248>",
        }
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
