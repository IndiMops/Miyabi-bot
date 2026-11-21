"""Registry of the bot's registered slash commands and helpers for `</name:id>` mentions.

The registry is filled once at startup from the result of `tree.sync()` (or a
single `tree.fetch_commands()` when syncing is disabled); lookups never call
the Discord API.
"""
from collections.abc import Iterable

from discord import app_commands

from utils.logger import logger

_command_ids: dict[str, int] = {}
_warned_missing: set[str] = set()


class CommandInfo:
    """A slash command as known to Discord; `id()` is None when it is not registered."""

    def __init__(self, name: str, command_id: int | None = None) -> None:
        self._name = name
        self._id = command_id

    def name(self) -> str:
        return self._name

    def id(self) -> int | None:
        return self._id

    def mention(self) -> str:
        """A clickable `</name:id>` mention, or plain `/name` text when the ID is unknown."""
        if self._id is None:
            return f"`/{self._name}`"
        return f"</{self._name}:{self._id}>"

    def __str__(self) -> str:
        return self.mention()

    def __repr__(self) -> str:
        return f"CommandInfo(name={self._name!r}, id={self._id!r})"


def set_commands(commands: Iterable[app_commands.AppCommand]) -> None:
    """Replace the registry with the commands returned by Discord."""
    _command_ids.clear()
    _warned_missing.clear()
    for command in commands:
        _command_ids[command.name] = command.id
    logger.info(f"Command registry loaded: {len(_command_ids)} commands")


def get_command(name: str) -> CommandInfo:
    """Return a registered command by name; subcommands use their full name ("group sub").

    An unknown name still returns a usable `CommandInfo` (its mention falls back
    to plain text) and logs a warning once per name.
    """
    name = " ".join(name.split()).removeprefix("/")
    # Subcommands share the ID of their top-level command.
    command_id = _command_ids.get(name.split(" ", 1)[0])

    if command_id is None and name not in _warned_missing:
        _warned_missing.add(name)
        logger.warning(
            f"Slash command '/{name}' is not in the command registry; "
            "its mention falls back to plain text"
        )

    return CommandInfo(name, command_id)
