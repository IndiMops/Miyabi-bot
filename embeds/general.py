from datetime import datetime

import discord

from utils.config import Config


def add_default_footer(embed: discord.Embed) -> discord.Embed:
    return embed.set_footer(
        text=(
            f"Mops Storage © 2020-{datetime.now().year} "
            f"Всі права захищено • {Config.PUBLIC.dev.website}"
        ),
        icon_url=Config.PUBLIC.bot.assets.avatar,
    )
