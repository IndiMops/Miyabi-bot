import discord
from discord import app_commands
from discord.ext import commands

from utils.logger import logger

GENERIC_ERROR_MESSAGE = "Не вдалося виконати команду. Спробуйте ще раз пізніше."
CHECK_FAILURE_MESSAGE = "У вас немає доступу до цієї команди."
BOT_MISSING_PERMISSIONS_MESSAGE = "Мені бракує прав на цьому сервері, щоб виконати команду."
COOLDOWN_MESSAGE = "Команду можна буде використати знову через {retry_after:.0f} с."
TRANSFORMER_ERROR_MESSAGE = "Не вдалося розпізнати значення параметра. Перевірте введені дані."


def get_error_message(error: app_commands.AppCommandError) -> str:
    """Return the Ukrainian message shown to the user for an app command error."""
    if isinstance(error, app_commands.CommandOnCooldown):
        return COOLDOWN_MESSAGE.format(retry_after=error.retry_after)
    if isinstance(error, app_commands.BotMissingPermissions):
        return BOT_MISSING_PERMISSIONS_MESSAGE
    if isinstance(error, app_commands.CheckFailure):
        return CHECK_FAILURE_MESSAGE
    if isinstance(error, app_commands.TransformerError):
        return TRANSFORMER_ERROR_MESSAGE
    return GENERIC_ERROR_MESSAGE


def is_expected_error(error: app_commands.AppCommandError) -> bool:
    """Expected errors are user-facing conditions, not bugs: no traceback is logged."""
    return isinstance(
        error,
        (
            app_commands.CommandOnCooldown,
            app_commands.CheckFailure,
            app_commands.TransformerError,
        ),
    )


async def send_error_message(interaction: discord.Interaction, message: str) -> None:
    """Send an ephemeral error reply, whether or not the interaction was answered."""
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException as error:
        # The interaction token may have expired or the message was deleted.
        logger.opt(exception=error).warning("Could not send the error message to the user")


class ErrorHandler(commands.Cog):
    """Global error handler for all slash commands (`CommandTree.on_error`)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._previous_on_error = None

    async def cog_load(self) -> None:
        tree = self.bot.tree
        self._previous_on_error = tree.on_error
        tree.on_error = self.on_app_command_error

    async def cog_unload(self) -> None:
        if self._previous_on_error is not None:
            self.bot.tree.on_error = self._previous_on_error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        command_name = interaction.command.qualified_name if interaction.command else "unknown"

        if is_expected_error(error):
            logger.info(f"/{command_name} rejected for user {interaction.user.id}: {error}")
        else:
            original = error.original if isinstance(error, app_commands.CommandInvokeError) else error
            logger.opt(exception=original).error(f"Unhandled error in /{command_name}")

        await send_error_message(interaction, get_error_message(error))


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
    logger.info("Error handler cog loaded.")
