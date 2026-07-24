# embeds\commands_help.py
from typing import List
import datetime

import discord

from utils.config import Config
from utils.misc import HEXtoColor


class CommandsHelpEmbeds:
    Main = discord.Embed(
        title="Доступні команди:",
        description="Для отримання детальної інформації про будь-яку команду, скористайтесь цим форматом: {help_command} `<назва команди чи категорії>`.\nТакож ви можете обрати одну з категорій нижче, щоб переглянути всі доступні команди.".format(
            help_command=f"</help:{Config.get_command_id_by_name('help')}>"
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )

    Main.add_field(
        name="📃Інформація ({help_command} `<category: information>`)".format(
            help_command=f"</help:{Config.get_command_id_by_name('help')}>"
        ),
        value=f"</help:{Config.get_command_id_by_name('help')}> </info:{Config.get_command_id_by_name('info')}>"
    )

    Main.set_thumbnail(
        url=Config.PUBLIC.bot.assets.avatar
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

    @classmethod
    def has_embed(cls, key: str) -> bool:
        return isinstance(getattr(cls, key, None), discord.Embed)


class HelpCommands(CommandsHelpEmbeds):
    info = discord.Embed(
        title="Опис окманди:",
        description="Показує інформацію про бота, включаючи версію, розробника та інші деталі.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )
    info.set_author(
        name="Команда info"
    )
    info.add_field(
        name="Використання",
        value=f"</info:{Config.get_command_id_by_name('info')}>",
        inline=False
    )
    info.set_thumbnail(
        url=Config.PUBLIC.bot.assets.avatar
    )
    info.set_footer(
        text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
            curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website),
        icon_url=Config.PUBLIC.bot.assets.avatar
    )

    help = discord.Embed(
        title="Опис команди:",
        description="Відображає перелік усіх доступних команд бота з короткими описами для кожної команди.",
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )

    help.set_author(
        name="Команда help"
    )

    help.add_field(
        name="Використання",
        value=f"</help:{Config.get_command_id_by_name('help')}> `<command: назва команди>|<category: назва категорії>`",
        inline=False
    )
    help.add_field(
        name="Приклад 1",
        value=f"</help:{Config.get_command_id_by_name('help')}>\n↪Показує весь список команд",
        inline=False
    )
    help.add_field(
        name="Приклад 2",
        value=f"</help:{Config.get_command_id_by_name('help')}> `<command:info>`\n↪Показує детальну інформацію про команду info",
        inline=False
    )

    help.add_field(
        name="Приклад 3",
        value=f"</help:{Config.get_command_id_by_name('help')}> `category: information`\n↪Показує всі команди в категорії Інформація",
        inline=False
    )

    help.set_thumbnail(
        url=Config.PUBLIC.bot.assets.avatar
    )

    help.set_footer(
        text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
            curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website),
        icon_url=Config.PUBLIC.bot.assets.avatar
    )

    CommandsNotFound = discord.Embed(
        title="Команди не знайдено",
        description="Для обраної категорії немає доступних команд.",
        color=HEXtoColor(Config.PUBLIC.bot.color.warn)
    )


class HelpCategory(CommandsHelpEmbeds):
    infromation_commands = [
        {
            "name": "help",
            "id": Config.get_command_id_by_name("help"),
            "description": "Відображає перелік усіх доступних команд бота з короткими описами для кожної команди"
        },
        {
            "name": "info",
            "id": Config.get_command_id_by_name("info"),
            "description": "Показує інформацію про бота, включаючи версію, розробника та інші деталі."
        }
    ]

    information = discord.Embed(
        title="Доступні команди категорії 📃 Інформація",
        description="Для отримання детальної інформації про будь-яку команду, скористайтесь цим форматом: {help_command} `<назва команди чи категорії>`.".format(
            help_command=f"</help:{Config.get_command_id_by_name('help')}>"
        ),
        color=HEXtoColor(Config.PUBLIC.bot.color.default)
    )
    for command in infromation_commands:
        information.add_field(
            name=f"• </{command['name']}:{command['id']}>",
            value=f"↪{command['description']}",
            inline=False
        )

    information.set_thumbnail(
        url=Config.PUBLIC.bot.assets.avatar
    )
    
    information.set_footer(
        text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
            curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website),
        icon_url=Config.PUBLIC.bot.assets.avatar
    )
