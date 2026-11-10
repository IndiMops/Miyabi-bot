import contextlib
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord

import utils.commands as command_registry
from bot import register_commands
from utils.commands import CommandInfo, get_command, set_commands
from utils.config import Config


def app_command(name: str, command_id: int) -> SimpleNamespace:
    return SimpleNamespace(name=name, id=command_id)


@contextlib.contextmanager
def capture_warnings():
    """Collect loguru WARNING messages logged by the command registry."""
    messages: list[str] = []
    handler_id = command_registry.logger.add(messages.append, level="WARNING", format="{message}")
    try:
        yield messages
    finally:
        command_registry.logger.remove(handler_id)


class CommandRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        set_commands([app_command("help", 111), app_command("characters", 222)])
        self.addCleanup(set_commands, [])

    def test_known_command_returns_name_id_and_mention(self) -> None:
        command = get_command("help")

        self.assertEqual(command.name(), "help")
        self.assertEqual(command.id(), 111)
        self.assertEqual(command.mention(), "</help:111>")
        self.assertEqual(str(command), "</help:111>")

    def test_leading_slash_and_extra_spaces_are_ignored(self) -> None:
        self.assertEqual(get_command(" /help ").mention(), "</help:111>")

    def test_subcommand_uses_parent_id(self) -> None:
        self.assertEqual(
            get_command("characters  agent").mention(),
            "</characters agent:222>",
        )

    def test_unknown_command_falls_back_to_name_and_warns_once(self) -> None:
        with capture_warnings() as messages:
            first = get_command("missing")
            get_command("missing")

        self.assertEqual(first.name(), "missing")
        self.assertIsNone(first.id())
        self.assertEqual(first.mention(), "`/missing`")
        self.assertEqual(len(messages), 1)
        self.assertIn("/missing", messages[0])

    def test_set_commands_replaces_previous_registry(self) -> None:
        set_commands([app_command("info", 333)])

        self.assertIsNone(get_command("help").id())
        self.assertEqual(get_command("info").id(), 333)


class CommandInfoTests(unittest.TestCase):
    def test_without_id_mention_is_plain_text(self) -> None:
        self.assertEqual(CommandInfo("help").mention(), "`/help`")


class RegisterCommandsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        original = Config.SYNC_COMMANDS
        self.addCleanup(setattr, Config, "SYNC_COMMANDS", original)
        self.addCleanup(set_commands, [])
        self.bot = MagicMock()
        self.bot.tree.sync = AsyncMock(return_value=[app_command("help", 1)])
        self.bot.tree.fetch_commands = AsyncMock(return_value=[app_command("help", 2)])

    async def test_sync_enabled_uses_sync_result(self) -> None:
        Config.SYNC_COMMANDS = True

        await register_commands(self.bot)

        self.bot.tree.sync.assert_awaited_once()
        self.bot.tree.fetch_commands.assert_not_awaited()
        self.assertEqual(get_command("help").id(), 1)

    async def test_sync_disabled_only_fetches_ids(self) -> None:
        Config.SYNC_COMMANDS = False

        await register_commands(self.bot)

        self.bot.tree.sync.assert_not_awaited()
        self.assertEqual(get_command("help").id(), 2)

    async def test_fetch_failure_does_not_stop_startup(self) -> None:
        Config.SYNC_COMMANDS = False
        self.bot.tree.fetch_commands.side_effect = discord.HTTPException(
            MagicMock(status=500, reason="Server Error"), "boom"
        )

        await register_commands(self.bot)

        self.assertIsNone(get_command("help").id())


if __name__ == "__main__":
    unittest.main()
