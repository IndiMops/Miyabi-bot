"""
Discord publishing: renders the status embed and keeps exactly one webhook
message up to date.

A webhook can only edit messages it created itself, which is why the service
creates the status message on its own and remembers its ID.
"""

import asyncio
import time
from typing import Any, Protocol

import discord
from loguru import logger

from status_service.evaluator import Evaluation, ServiceState
from status_service.store import StateStore

UNKNOWN_MESSAGE = 10008
UNKNOWN_WEBHOOK = 10015

STATE_STYLE = {
    ServiceState.ONLINE: (0x41E332, "🟢", "Online"),
    ServiceState.DEGRADED: (0xFFCC4D, "🟡", "Degraded"),
    ServiceState.STARTING: (0x66C7FF, "🔵", "Starting"),
    ServiceState.OFFLINE: (0xDD2E44, "🔴", "Offline"),
    ServiceState.UNKNOWN: (0x4C5D6D, "⚪", "Unknown"),
}


class WebhookLike(Protocol):
    id: int

    async def send(self, *, embed: discord.Embed, wait: bool) -> Any: ...

    async def edit_message(self, message_id: int, *, embed: discord.Embed) -> Any: ...


class PublishError(RuntimeError):
    pass


def build_status_embed(
    evaluation: Evaluation,
    display_name: str,
    now: float,
    thumbnail_url: str = "",
) -> discord.Embed:
    color, icon, label = STATE_STYLE[evaluation.state]
    embed = discord.Embed(
        title=f"{icon} {display_name} — {label}",
        description=evaluation.reason,
        color=color,
    )
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    heartbeat = evaluation.heartbeat
    if heartbeat is not None:
        received = int(heartbeat.received_at)
        embed.add_field(
            name="Last heartbeat", value=f"<t:{received}:R> (<t:{received}:T>)"
        )
        if evaluation.state in (
            ServiceState.ONLINE,
            ServiceState.DEGRADED,
            ServiceState.STARTING,
        ):
            started = int(heartbeat.process_started_at)
            embed.add_field(
                name="Uptime",
                value=f"<t:{started}:R> (since <t:{started}:f>)",
            )
            if heartbeat.guild_count is not None:
                embed.add_field(name="Servers", value=str(heartbeat.guild_count))
            latency = (
                "—"
                if heartbeat.latency_ms is None
                else f"{heartbeat.latency_ms:.0f} ms"
            )
            embed.add_field(name="Gateway latency", value=latency)
            embed.add_field(
                name="Gateway",
                value=("connected" if heartbeat.gateway_connected else "reconnecting"),
            )
    embed.set_footer(text="Updated")
    embed.timestamp = discord.utils.utcnow()
    return embed


class StatusMessagePublisher:
    """Creates the status message once, then only edits it."""

    def __init__(
        self,
        webhook: WebhookLike,
        store: StateStore,
        configured_message_id: int | None = None,
        recreate_missing: bool = True,
        clock=time.time,
    ):
        self.webhook = webhook
        self.store = store
        self.configured_message_id = configured_message_id
        self.recreate_missing = recreate_missing
        self._clock = clock
        self._lock = asyncio.Lock()
        self.last_success_at: float | None = None
        self.consecutive_failures = 0
        self.last_error: str | None = None

    @property
    def message_id(self) -> int | None:
        # The state file wins: STATUS_MESSAGE_ID is only for adopting an
        # existing message when the state file is lost.
        return self.store.get_message_id(self.webhook.id) or self.configured_message_id

    async def publish(self, embed: discord.Embed) -> None:
        # The lock guarantees two concurrent publishes cannot both create a message.
        async with self._lock:
            try:
                await self._publish(embed)
            except Exception as error:
                self.consecutive_failures += 1
                self.last_error = _describe(error)
                raise PublishError(self.last_error) from error
            self.consecutive_failures = 0
            self.last_error = None
            self.last_success_at = self._clock()

    async def _publish(self, embed: discord.Embed) -> None:
        message_id = self.message_id
        if message_id is not None:
            try:
                await self.webhook.edit_message(message_id, embed=embed)
                self._remember(message_id)
                return
            except discord.NotFound as error:
                if error.code != UNKNOWN_MESSAGE:
                    raise
                if not self.recreate_missing:
                    raise PublishError(
                        "status message was deleted; set a new STATUS_MESSAGE_ID or enable "
                        "STATUS_RECREATE_MISSING_MESSAGE"
                    ) from error
                logger.warning(
                    f"Status message {message_id} no longer exists; creating a new one"
                )
                self.configured_message_id = None
                self.store.set_message_id(self.webhook.id, None)

        message = await self.webhook.send(embed=embed, wait=True)
        self._remember(message.id)
        logger.info(f"Created status message {message.id}")

    def _remember(self, message_id: int) -> None:
        if self.store.get_message_id(self.webhook.id) != message_id:
            self.store.set_message_id(self.webhook.id, message_id)
            self.store.save()


def _describe(error: Exception) -> str:
    """Short, secret-free description of a publishing error."""
    if isinstance(error, PublishError):
        return str(error)
    if isinstance(error, discord.NotFound) and error.code == UNKNOWN_WEBHOOK:
        return "webhook not found; check STATUS_WEBHOOK_URL"
    if isinstance(error, discord.Forbidden):
        return "webhook is not allowed to send or edit in this channel"
    if isinstance(error, discord.HTTPException):
        return f"Discord API error HTTP {error.status} (code {error.code})"
    return type(error).__name__
