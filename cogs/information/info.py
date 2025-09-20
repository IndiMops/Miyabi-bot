import discord
from discord import app_commands
from discord.ext import commands

from utils.config import Config
from utils.logger import logger
from utils.misc import HEXtoColor


class InfoCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot

    @app_commands.command(name="info", description="Show information about the bot.")
    async def info(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title=Config.PUBLIC.bot.name,
                description="Вітаю. Я — ***Хошімі Міябі***, і цей бот служить довідником для тих, хто прагне пізнати Zenless Zone Zero.",
                color=HEXtoColor(Config.PUBLIC.bot.color.default)
            ).set_thumbnail(
                url=Config.PUBLIC.bot.assets.avatar
            ).set_image(
                url=Config.PUBLIC.bot.assets.banner
            ).add_field(
                name="Збірка",
                value="{bot_version} (<t:{last_update_Unix_time}:R>)".format(
                    bot_version=Config.PUBLIC.bot.version, last_update_Unix_time=Config.PUBLIC.bot.last_update),
            ).add_field(
                name="Мій розробник",
                value="{dev_emoji} [{dev_name}](https://discord.com/users/{dev_id})".format(
                    dev_emoji=Config.PUBLIC.dev.emoji, dev_name=Config.PUBLIC.dev.name, dev_id=Config.PUBLIC.dev.id),
            ).add_field(
                name="⠀",  # This empty field is needed to align all the fields, or if you ever have additional information, you can add it here
                value="⠀"
            ).add_field(
                name="⠀",
                value="- [Сервер підтримки]({bot_support_server_url})\n- [GitHub репозиторій]({bot_guthub_url})".format(
                    bot_support_server_url=Config.PUBLIC.bot.urls.support_server, bot_guthub_url=Config.PUBLIC.bot.urls.github),
            )
            embed.set_footer(
                text="Цей бот створено фанатами для фанатів. Він не пов’язаний із HoYoverse, усі права на гру залишаються за їх власниками."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in info command: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCommand(bot))
    logger.info("Info command cog loaded.")
