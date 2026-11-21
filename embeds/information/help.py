"""Help content: command categories, per-command docs and the embeds built from them.

Embeds are built at response time, so command mentions use the IDs that the
command registry (`utils.commands`) received from Discord on startup.
Usage lines and examples may contain `{help}`-style placeholders: each
`{name}` is replaced with the mention of that command.
"""

import datetime
import string
from dataclasses import dataclass

import discord

from utils.commands import get_command
from utils.config import Config
from utils.misc import hex_to_color


@dataclass(frozen=True)
class CommandDoc:
    name: str
    description: str
    usage: str
    examples: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class HelpCategory:
    key: str
    label: str
    emoji: str
    commands: tuple[str, ...]


COMMAND_DOCS: dict[str, CommandDoc] = {
    doc.name: doc
    for doc in (
        CommandDoc(
            name="help",
            description="Відображає перелік усіх доступних команд бота з короткими описами для кожної команди.",
            usage="{help} `<command: назва команди>|<category: назва категорії>`",
            examples=(
                ("{help}", "Показує весь список команд"),
                (
                    "{help} `command: info`",
                    "Показує детальну інформацію про команду info",
                ),
                (
                    "{help} `category: information`",
                    "Показує всі команди в категорії Інформація",
                ),
            ),
        ),
        CommandDoc(
            name="info",
            description="Показує інформацію про бота, включаючи версію, розробника та інші деталі.",
            usage="{info}",
        ),
        CommandDoc(
            name="characters",
            description="Вікі агентів Zenless Zone Zero: навігація за стихіями та сторінки агентів.",
            usage="{characters} `<agent: ім'я агента>`",
            examples=(
                ("{characters}", "Відкриває меню агентів за стихіями"),
                ("{characters} `agent: Alice`", "Одразу відкриває сторінку агента"),
            ),
        ),
    )
}

HELP_CATEGORIES: tuple[HelpCategory, ...] = (
    HelpCategory(
        key="information", label="Інформація", emoji="📃", commands=("help", "info")
    ),
    HelpCategory(key="wiki", label="Вікі", emoji="📚", commands=("characters",)),
)

_CATEGORIES_BY_KEY = {category.key: category for category in HELP_CATEGORIES}


def get_category(key: str) -> HelpCategory | None:
    return _CATEGORIES_BY_KEY.get(key)


def render(text: str) -> str:
    """Replace every `{command}` placeholder with that command's mention."""
    names = {name for _, name, _, _ in string.Formatter().parse(text) if name}
    return text.format(**{name: get_command(name).mention() for name in names})


def _new_embed(title: str, description: str | None = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=hex_to_color(Config.PUBLIC.bot.color.default),
    )
    embed.set_thumbnail(url=Config.PUBLIC.bot.assets.avatar)
    embed.set_footer(
        text=f"Mops Storage © 2020-{datetime.datetime.now().year} Всі права захищено • {Config.PUBLIC.dev.website}",
        icon_url=Config.PUBLIC.bot.assets.avatar,
    )
    return embed


def _details_hint() -> str:
    return render(
        "Для отримання детальної інформації про будь-яку команду, скористайтесь цим форматом: "
        "{help} `<назва команди чи категорії>`."
    )


def build_main_embed() -> discord.Embed:
    """Overview: every category with mentions of its commands."""
    embed = _new_embed(
        "Доступні команди:",
        _details_hint()
        + "\nТакож ви можете обрати одну з категорій нижче, щоб переглянути всі доступні команди.",
    )
    help_mention = get_command("help").mention()
    for category in HELP_CATEGORIES:
        embed.add_field(
            name=f"{category.emoji} {category.label} ({help_mention} `<category: {category.key}>`)",
            value=" ".join(get_command(name).mention() for name in category.commands),
            inline=False,
        )
    return embed


def build_category_embed(key: str) -> discord.Embed | None:
    """All commands of one category with their short descriptions."""
    category = get_category(key)
    if category is None:
        return None

    embed = _new_embed(
        f"Доступні команди категорії {category.emoji} {category.label}",
        _details_hint(),
    )
    for name in category.commands:
        embed.add_field(
            name=f"• {get_command(name).mention()}",
            value=f"↪{COMMAND_DOCS[name].description}",
            inline=False,
        )
    return embed


def build_command_embed(name: str) -> discord.Embed | None:
    """Description, usage and examples of one command."""
    doc = COMMAND_DOCS.get(name)
    if doc is None:
        return None

    embed = _new_embed("Опис команди:", doc.description)
    embed.set_author(name=f"Команда {doc.name}")
    embed.add_field(name="Використання", value=render(doc.usage), inline=False)
    for index, (example, explanation) in enumerate(doc.examples, start=1):
        embed.add_field(
            name=f"Приклад {index}",
            value=f"{render(example)}\n↪{explanation}",
            inline=False,
        )
    return embed
