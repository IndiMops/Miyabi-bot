import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
from discord import app_commands
from discord.ext import commands

from cogs.core.errors import (
    BOT_MISSING_PERMISSIONS_MESSAGE,
    CHECK_FAILURE_MESSAGE,
    GENERIC_ERROR_MESSAGE,
    ErrorHandler,
    get_error_message,
    send_error_message,
)


def make_interaction(*, response_done: bool = False) -> MagicMock:
    interaction = MagicMock()
    interaction.response.is_done.return_value = response_done
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.command = SimpleNamespace(qualified_name="info")
    interaction.user = SimpleNamespace(id=1)
    return interaction


class ErrorMessageTests(unittest.TestCase):
    def test_cooldown_shows_retry_time(self) -> None:
        cooldown = app_commands.Cooldown(1, 30)
        error = app_commands.CommandOnCooldown(cooldown, 12.4)

        self.assertIn("12", get_error_message(error))

    def test_missing_bot_permissions_has_own_message(self) -> None:
        error = app_commands.BotMissingPermissions(["send_messages"])

        self.assertEqual(get_error_message(error), BOT_MISSING_PERMISSIONS_MESSAGE)

    def test_check_failure(self) -> None:
        self.assertEqual(
            get_error_message(app_commands.CheckFailure()),
            CHECK_FAILURE_MESSAGE,
        )

    def test_unexpected_error_uses_generic_message(self) -> None:
        command = MagicMock()
        error = app_commands.CommandInvokeError(command, RuntimeError("boom"))

        self.assertEqual(get_error_message(error), GENERIC_ERROR_MESSAGE)


class SendErrorMessageTests(unittest.IsolatedAsyncioTestCase):
    async def test_replies_when_interaction_was_not_answered(self) -> None:
        interaction = make_interaction(response_done=False)

        await send_error_message(interaction, "text")

        interaction.response.send_message.assert_awaited_once_with("text", ephemeral=True)
        interaction.followup.send.assert_not_awaited()

    async def test_uses_followup_when_interaction_was_answered(self) -> None:
        interaction = make_interaction(response_done=True)

        await send_error_message(interaction, "text")

        interaction.followup.send.assert_awaited_once_with("text", ephemeral=True)
        interaction.response.send_message.assert_not_awaited()

    async def test_http_errors_are_swallowed(self) -> None:
        interaction = make_interaction(response_done=False)
        interaction.response.send_message.side_effect = discord.HTTPException(
            MagicMock(status=404, reason="Not Found"), "Unknown interaction"
        )

        await send_error_message(interaction, "text")


class ErrorHandlerCogTests(unittest.IsolatedAsyncioTestCase):
    async def test_installs_and_restores_tree_error_handler(self) -> None:
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        original = bot.tree.on_error
        cog = ErrorHandler(bot)

        await cog.cog_load()
        self.assertEqual(bot.tree.on_error, cog.on_app_command_error)

        await cog.cog_unload()
        self.assertEqual(bot.tree.on_error, original)

    async def test_unexpected_error_sends_generic_message(self) -> None:
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        cog = ErrorHandler(bot)
        interaction = make_interaction(response_done=False)
        error = app_commands.CommandInvokeError(MagicMock(), RuntimeError("boom"))

        await cog.on_app_command_error(interaction, error)

        interaction.response.send_message.assert_awaited_once_with(
            GENERIC_ERROR_MESSAGE, ephemeral=True
        )


if __name__ == "__main__":
    unittest.main()
