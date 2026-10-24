"""
Heartbeat reporting for the external status service.

The bot only describes its own state here; deciding ONLINE/OFFLINE and
publishing to Discord is the job of `status_service`. Delivery is best-effort:
every failure is logged and swallowed so it never affects the bot itself.
"""
import asyncio
import math
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import aiohttp
import discord

from utils.logger import logger

HEARTBEAT_SCHEMA_VERSION = 1
# Recorded when the reporter module is first imported during extension loading.
PROCESS_STARTED_AT = time.time()


@dataclass(frozen=True)
class HeartbeatSettings:
    url: str
    secret: str
    service: str = "miyabi-bot"
    interval: float = 30.0
    timeout: float = 5.0
    max_attempts: int = 3
    backoff_base: float = 1.0

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.secret)


def _latency_ms(latency: float) -> float | None:
    """Return gateway latency in ms, or None while Discord has not measured it yet."""
    if latency is None or math.isnan(latency) or math.isinf(latency):
        return None
    return round(latency * 1000, 1)


def build_heartbeat_payload(
    client: discord.Client,
    service: str,
    process_started_at: float,
    now: float | None = None,
    shutting_down: bool = False,
) -> dict[str, Any]:
    """Collect a safe snapshot of the client's operational state."""
    now = time.time() if now is None else now
    ws = client.ws
    gateway_connected = bool(ws is not None and ws.open) and not shutting_down
    # is_ready() stays True during gateway reconnects, so the connection flag
    # is reported separately and the status service combines both.
    ready = client.is_ready() and not client.is_closed() and not shutting_down

    return {
        "schema": HEARTBEAT_SCHEMA_VERSION,
        "service": service,
        "sent_at": now,
        "process_started_at": process_started_at,
        "uptime_seconds": round(max(0.0, now - process_started_at), 1),
        "ready": ready,
        "gateway_connected": gateway_connected,
        "latency_ms": _latency_ms(client.latency) if gateway_connected else None,
        "guild_count": len(client.guilds) if ready else None,
        "shard_count": client.shard_count,
        "shutting_down": shutting_down,
    }


class HeartbeatReporter:
    """Sends heartbeats with timeouts and bounded retries. Never raises."""

    def __init__(
        self,
        settings: HeartbeatSettings,
        session: aiohttp.ClientSession,
        sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep,
    ):
        self.settings = settings
        self.session = session
        self._sleep = sleep
        self.consecutive_failures = 0

    async def send(self, payload: dict[str, Any], max_attempts: int | None = None) -> bool:
        max_attempts = self.settings.max_attempts if max_attempts is None else max_attempts
        headers = {"Authorization": f"Bearer {self.settings.secret}"}
        timeout = aiohttp.ClientTimeout(total=self.settings.timeout)
        last_error = "unknown error"

        for attempt in range(1, max_attempts + 1):
            try:
                async with self.session.post(
                    self.settings.url, json=payload, headers=headers, timeout=timeout
                ) as response:
                    if response.status < 300:
                        if self.consecutive_failures:
                            logger.info(
                                "Status heartbeat delivery recovered after "
                                f"{self.consecutive_failures} failed heartbeat(s)"
                            )
                        self.consecutive_failures = 0
                        return True
                    last_error = f"HTTP {response.status}"
                    if response.status in (400, 401, 403, 413, 422):
                        # Retrying will not fix bad configuration or a rejected payload.
                        logger.error(
                            f"Status service rejected heartbeat with HTTP {response.status}; "
                            "check STATUS_HEARTBEAT_SECRET and STATUS_SERVICE_NAME"
                        )
                        break
            except asyncio.CancelledError:
                raise
            except (TimeoutError, aiohttp.ClientError) as error:
                last_error = type(error).__name__
            except Exception:
                logger.exception("Unexpected error while sending status heartbeat")
                break

            logger.debug(f"Status heartbeat attempt {attempt} failed: {last_error}")
            if attempt < max_attempts:
                await self._sleep(self.settings.backoff_base * 2 ** (attempt - 1))

        self.consecutive_failures += 1
        # Warn once per outage instead of on every interval.
        log = logger.warning if self.consecutive_failures == 1 else logger.debug
        log(f"Status heartbeat not delivered ({last_error}); the bot keeps running")
        return False
