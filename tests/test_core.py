import json
import tempfile
import unittest
from pathlib import Path

import discord

from bot import is_disabled_extension
from utils.config import Config
from utils.misc import hex_to_color, hex_to_rgb, load_json, save_json
from views.pagination import PaginationView


class ExtensionLoadingTests(unittest.TestCase):
    def test_dev_extension_is_disabled_by_folder_name(self) -> None:
        self.assertTrue(
            is_disabled_extension("cogs.dev.ping", ["dev"])
        )

    def test_regular_extension_is_not_disabled(self) -> None:
        self.assertFalse(
            is_disabled_extension("cogs.wiki.characters", ["dev"])
        )


class ConfigTests(unittest.TestCase):
    def test_require_token_fails_with_clear_message(self) -> None:
        original_token = Config.DISCORD_BOT_TOKEN
        Config.DISCORD_BOT_TOKEN = None
        self.addCleanup(setattr, Config, "DISCORD_BOT_TOKEN", original_token)

        with self.assertRaisesRegex(RuntimeError, "DISCORD_BOT_TOKEN"):
            Config.require_token()


class MiscTests(unittest.TestCase):
    def test_color_conversions(self) -> None:
        self.assertEqual(hex_to_color("#4c5d6d"), 0x4C5D6D)
        self.assertEqual(hex_to_rgb("#4c5d6d"), (76, 93, 109))

    def test_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            expected = {"bot": {"name": "Miyabi"}}

            save_json(expected, path)

            self.assertEqual(load_json(path), expected)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                expected,
            )


class PaginationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_empty_embed_list(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one embed"):
            PaginationView([])

    async def test_single_page_disables_navigation(self) -> None:
        view = PaginationView([discord.Embed(title="Only page")])

        self.assertTrue(view.first.disabled)
        self.assertTrue(view.previous.disabled)
        self.assertTrue(view.next.disabled)
        self.assertTrue(view.last.disabled)
        self.assertEqual(view.current_page.label, "1/1")
