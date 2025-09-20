from typing import List
import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor

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
