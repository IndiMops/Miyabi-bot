# cogs\information\help.py
import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select

from utils.config import Config
from utils.logger import logger
from utils.misc import fetch_slash_commands, HEXtoColor
from views.pagination import PagginationView

from embeds.commands_help import CommandsHelpEmbeds, HelpCommands as Commands, HelpCategory as Categories


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def auto_complete_command_name(self, interaction: discord.Interaction, current: str):
        commands_list = await fetch_slash_commands(self.bot)

        filtered_commands = [
            app_commands.Choice(name=cmd["name"], value=cmd["name"])
            for cmd in commands_list if current.lower() in cmd["name"].lower()
        ]
        return filtered_commands[:25]  # Discord allows a maximum of 25 choices

    async def auto_complete_command_category(self, interaction: discord.Interaction, current: str):
        categories = ["information"]

        filtered_categories = [
            app_commands.Choice(name=cat, value=cat)
            for cat in categories if current.lower() in cat.lower()
        ]
        return filtered_categories[:25]

    @app_commands.command(name="help", description="Show detailed information about the bot's commands and features.")
    @app_commands.autocomplete(command_name=auto_complete_command_name, command_category=auto_complete_command_category)
    @app_commands.describe(command_name="Get help for a specific command.", command_category="Get help for a specific category.")
    @app_commands.rename(command_name="command", command_category="category")
    async def help(self, interaction: discord.Interaction, command_name: str = None, command_category: str = None):
        try:
            if command_name == None and command_category == None:
                menu = Select(
                    placeholder="Оберіть категорію...",
                    options=[
                        discord.SelectOption(
                            label="Інформація",
                            value="0",
                            emoji="📃",
                        )
                    ]
                )

                async def callback(interaction: discord.Interaction):
                    category_index = int(menu.values[0])
                    category = menu.options[category_index]

                    commands = []
                    if category.value == "0":
                        commands = [
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

                    pages = []

                    for i in range(0, len(commands), 10):
                        embed = discord.Embed(
                            title=f"Доступні команди категорії {category.emoji} {category.label}",
                            description="Для отримання детальної інформації про будь-яку команду, скористайтесь цим форматом: {help_command} `<назва команди чи категорії>`.".format(
                                help_command=f"</help:{Config.get_command_id_by_name('help')}>"
                            ),
                            color=HEXtoColor(Config.PUBLIC.bot.color.default)
                        )
                        embed.set_thumbnail(
                            url=Config.PUBLIC.bot.assets.avatar
                        )
                        embed.set_footer(
                            text="Mops Storage © 2020-{curent_year} Всі права захищено • {dev_site_url}".format(
                                curent_year=datetime.datetime.now().year, dev_site_url=Config.PUBLIC.dev.website
                            ),
                            icon_url=Config.PUBLIC.bot.assets.avatar
                        )

                        for command in commands[i:i+10]:
                            embed.add_field(
                                name=f"• </{command['name']}:{command['id']}>",
                                value=f"↪{command['description']}",
                                inline=False
                            )

                        pages.append(embed)

                    if pages:
                        if len(pages) > 1:
                            menu.callback = callback
                            await interaction.response.send_message(embed=pages[0], view=PagginationView(pages, menu), ephemeral=True)
                        else:
                            view = View()
                            if menu:
                                view.add_item(menu)
                            await interaction.response.edit_message(embed=pages[0], view=view)
                    else:
                        await interaction.responce.edit_message(embed=Commands.get_embed("CommandsNotDound"))

                menu.callback = callback
                view = View()
                view.add_item(menu)
                
                await interaction.response.send_message(embed=Commands.get_embed("Main"), view=view, ephemeral=True)
            elif command_name:
                if Commands.has_embed(command_name):
                    await interaction.response.send_message(embed=Commands.get_embed(command_name), ephemeral=True)
                else:
                    await interaction.response.send_message(f"Команди {command_name} не знайдено.", ephemeral=True)
            elif command_category:
                if Categories.has_embed(command_category):
                    await interaction.response.send_message(embed=Categories.get_embed(command_category), ephemeral=True)
                else:
                    await interaction.response.send_message(f"Категорію {command_category} не знайдено.", ephemeral=True)
        except Exception as e:
            print(e)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
    logger.info("Help command cog loaded.")
