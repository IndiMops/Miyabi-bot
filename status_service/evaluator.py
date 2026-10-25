"""
Heartbeat validation and state evaluation.

State semantics (freshness is measured with the receiver's clock, using the
time a heartbeat was received, so clock skew on the bot host does not matter):

- UNKNOWN:  no heartbeat has been seen yet and the service started less than
            `offline_after` seconds ago. Never published to Discord.
- STARTING: a fresh heartbeat says the client is not ready yet, and the bot
            process is younger than `starting_grace`.
- ONLINE:   a fresh heartbeat says the client is ready and the gateway is
            connected, with acceptable latency.
- DEGRADED: a fresh heartbeat says the client is ready, but the gateway is
            reconnecting or latency is above `degraded_latency_ms`.
- OFFLINE:  no heartbeat for more than `offline_after` seconds, the bot
            reported a graceful shutdown, or it has been not ready for longer
            than `starting_grace`.
"""

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from status_service.settings import Thresholds

SUPPORTED_SCHEMA = 1


class ServiceState(str, Enum):
    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class PayloadError(ValueError):
    """The heartbeat payload is malformed. The message is safe to return to the client."""


@dataclass(frozen=True)
class Heartbeat:
    service: str
    sent_at: float
    received_at: float
    process_started_at: float
    uptime_seconds: float
    ready: bool
    gateway_connected: bool
    latency_ms: float | None = None
    guild_count: int | None = None
    shard_count: int | None = None
    shutting_down: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(
        cls, data: Any, expected_service: str, received_at: float
    ) -> "Heartbeat":
        if not isinstance(data, dict):
            raise PayloadError("payload must be a JSON object")
        if data.get("schema") != SUPPORTED_SCHEMA:
            raise PayloadError("unsupported schema version")
        if data.get("service") != expected_service:
            raise PayloadError("unknown service")

        return cls(
            service=expected_service,
            sent_at=_timestamp(data, "sent_at"),
            received_at=received_at,
            process_started_at=_timestamp(data, "process_started_at"),
            uptime_seconds=_non_negative(data, "uptime_seconds"),
            ready=_bool(data, "ready"),
            gateway_connected=_bool(data, "gateway_connected"),
            latency_ms=_optional_non_negative(data, "latency_ms"),
            guild_count=_optional_count(data, "guild_count"),
            shard_count=_optional_count(data, "shard_count"),
            shutting_down=_bool(data, "shutting_down", default=False),
        )

    @classmethod
    def from_stored(cls, data: Any, expected_service: str) -> "Heartbeat":
        """Restore a heartbeat persisted by the state store."""
        if not isinstance(data, dict):
            raise PayloadError("stored heartbeat must be an object")
        payload = {**data, "schema": SUPPORTED_SCHEMA}
        return cls.from_payload(
            payload, expected_service, _timestamp(data, "received_at")
        )


@dataclass(frozen=True)
class Evaluation:
    state: ServiceState
    reason: str
    heartbeat: Heartbeat | None = None


def evaluate(
    heartbeat: Heartbeat | None,
    now: float,
    monitor_started_at: float,
    thresholds: Thresholds,
) -> Evaluation:
    if heartbeat is None:
        if now - monitor_started_at < thresholds.offline_after:
            return Evaluation(ServiceState.UNKNOWN, "Waiting for first heartbeat")
        return Evaluation(ServiceState.OFFLINE, "Heartbeat has never been received")

    age = now - heartbeat.received_at
    if age > thresholds.offline_after:
        return Evaluation(
            ServiceState.OFFLINE,
            f"No heartbeat received for over {int(age)} seconds",
            heartbeat,
        )
    if heartbeat.shutting_down:
        return Evaluation(
            ServiceState.OFFLINE, "Bot has shut down gracefully", heartbeat
        )
    if not heartbeat.ready:
        if heartbeat.uptime_seconds < thresholds.starting_grace:
            return Evaluation(
                ServiceState.STARTING, "Bot is connecting to Discord", heartbeat
            )
        return Evaluation(ServiceState.OFFLINE, "Bot is not ready for work", heartbeat)
    if not heartbeat.gateway_connected:
        return Evaluation(
            ServiceState.DEGRADED, "Reconnecting to Discord gateway", heartbeat
        )
    if (
        heartbeat.latency_ms is not None
        and heartbeat.latency_ms > thresholds.degraded_latency_ms
    ):
        return Evaluation(
            ServiceState.DEGRADED, "High Discord gateway latency", heartbeat
        )
    return Evaluation(ServiceState.ONLINE, "Operates normally", heartbeat)


def _number(data: dict, key: str) -> float:
    value = data.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise PayloadError(f"{key} must be a finite number")
    return float(value)


def _timestamp(data: dict, key: str) -> float:
    value = _number(data, key)
    if value <= 0:
        raise PayloadError(f"{key} must be a positive Unix timestamp")
    return value


def _non_negative(data: dict, key: str) -> float:
    value = _number(data, key)
    if value < 0:
        raise PayloadError(f"{key} must be >= 0")
    return value


def _optional_non_negative(data: dict, key: str) -> float | None:
    if data.get(key) is None:
        return None
    return _non_negative(data, key)


def _optional_count(data: dict, key: str) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PayloadError(f"{key} must be a non-negative integer")
    return value


def _bool(data: dict, key: str, default: bool | None = None) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise PayloadError(f"{key} must be a boolean")
    return value
