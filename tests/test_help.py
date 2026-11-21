import string
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from cogs.information.help import MAIN_OPTION_VALUE, HelpCategorySelect, HelpCommand
from embeds.information import (
    COMMAND_DOCS,
    HELP_CATEGORIES,
    build_category_embed,
    build_command_embed,
    build_main_embed,
)
from embeds.information.help import render
from utils.commands import set_commands
from utils.misc import PROJECT_ROOT, load_json

REGISTERED = {"help": 1, "info": 2, "characters": 3}


def register_all() -> None:
    set_commands(SimpleNamespace(name=name, id=command_id) for name, command_id in REGISTERED.items())


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


class HelpContentTests(unittest.TestCase):
    def test_every_categorized_command_is_documented(self) -> None:
        for category in HELP_CATEGORIES:
            for name in category.commands:
                self.assertIn(name, COMMAND_DOCS, f"{category.key} lists undocumented /{name}")

    def test_every_documented_command_is_in_a_category(self) -> None:
        categorized = {name for category in HELP_CATEGORIES for name in category.commands}
        self.assertEqual(set(COMMAND_DOCS), categorized)

    def test_placeholders_name_documented_commands(self) -> None:
        for doc in COMMAND_DOCS.values():
            texts = [doc.usage, *(example for example, _ in doc.examples)]
            for text in texts:
                self.assertLessEqual(placeholders(text), set(COMMAND_DOCS), text)

    def test_config_has_no_command_id_list(self) -> None:
        config = load_json(PROJECT_ROOT / "config.json")
        self.assertNotIn("commands", config["bot"])


class HelpEmbedTests(unittest.TestCase):
    def setUp(self) -> None:
        register_all()
        self.addCleanup(set_commands, [])

    def test_render_replaces_placeholders_with_mentions(self) -> None:
        self.assertEqual(render("{help} `command: info`"), "</help:1> `command: info`")

    def test_main_embed_lists_every_category_with_mentions(self) -> None:
        embed = build_main_embed()

        self.assertEqual(len(embed.fields), len(HELP_CATEGORIES))
        self.assertIn("</characters:3>", embed.fields[-1].value)
        self.assertIn("</help:1>", embed.description)

    def test_category_embeds(self) -> None:
        wiki = build_category_embed("wiki")

        self.assertEqual([field.name for field in wiki.fields], ["• </characters:3>"])
        self.assertIsNone(build_category_embed("missing"))

    def test_command_embeds_fit_discord_limits(self) -> None:
        for name in COMMAND_DOCS:
            embed = build_command_embed(name)
            self.assertLessEqual(len(embed), 6000)
            self.assertLessEqual(len(embed.fields), 25)
            for field in embed.fields:
                self.assertLessEqual(len(field.value), 1024)
                self.assertNotIn("{", field.value)

        self.assertIsNone(build_command_embed("missing"))

    def test_unregistered_commands_fall_back_to_plain_text(self) -> None:
        set_commands([])

        embed = build_command_embed("info")

        self.assertEqual(embed.fields[0].value, "`/info`")


class HelpCogTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        register_all()
        self.addCleanup(set_commands, [])
        self.cog = HelpCommand(MagicMock())

    async def test_command_autocomplete_uses_help_content(self) -> None:
        choices = await self.cog.auto_complete_command_name(MagicMock(), "CHAR")

        self.assertEqual([choice.value for choice in choices], ["characters"])

    async def test_category_autocomplete_matches_label(self) -> None:
        choices = await self.cog.auto_complete_command_category(MagicMock(), "вікі")

        self.assertEqual([choice.value for choice in choices], ["wiki"])

    async def test_category_select_switches_embed(self) -> None:
        select = HelpCategorySelect()
        select._values = ["wiki"]
        interaction = MagicMock()
        interaction.response.edit_message = AsyncMock()

        await select.callback(interaction)

        embed = interaction.response.edit_message.await_args.kwargs["embed"]
        self.assertIn("Вікі", embed.title)
        self.assertEqual(
            [option.value for option in select.options if option.default],
            ["wiki"],
        )

    async def test_category_select_returns_to_overview(self) -> None:
        select = HelpCategorySelect()
        select._values = [MAIN_OPTION_VALUE]
        interaction = MagicMock()
        interaction.response.edit_message = AsyncMock()

        await select.callback(interaction)

        embed = interaction.response.edit_message.await_args.kwargs["embed"]
        self.assertEqual(embed.title, "Доступні команди:")


if __name__ == "__main__":
    unittest.main()
