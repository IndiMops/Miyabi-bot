import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOT_CONFIG_FILE = PROJECT_ROOT / "config.json"
MIN_SECRET_LENGTH = 16


class SettingsError(ValueError):
    """Raised when the status service is misconfigured. The service refuses to start."""


@dataclass(frozen=True)
class Thresholds:
    offline_after: float = 90.0
    starting_grace: float = 180.0
    degraded_latency_ms: float = 1000.0


@dataclass(frozen=True)
class StatusServiceSettings:
    heartbeat_secret: str
    service_name: str = "miyabi-bot"
    display_name: str = "Miyabi Bot"
    host: str = "127.0.0.1"
    port: int = 8787
    webhook_url: str = ""
    message_id: int | None = None
    state_file: Path = PROJECT_ROOT / "data" / "status_service_state.json"
    thresholds: Thresholds = Thresholds()
    evaluate_interval: float = 10.0
    publish_interval: float = 300.0
    recreate_missing_message: bool = True
    thumbnail_url: str = ""

    @property
    def publishing_enabled(self) -> bool:
        return bool(self.webhook_url)

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "StatusServiceSettings":
        env = os.environ if environ is None else environ

        secret = env.get("STATUS_HEARTBEAT_SECRET", "").strip()
        if len(secret) < MIN_SECRET_LENGTH:
            raise SettingsError(
                f"STATUS_HEARTBEAT_SECRET must be set and at least {MIN_SECRET_LENGTH} characters long"
            )

        webhook_url = env.get("STATUS_WEBHOOK_URL", "").strip()
        if webhook_url and not webhook_url.startswith("https://"):
            raise SettingsError(
                "STATUS_WEBHOOK_URL must be an https:// Discord webhook URL"
            )

        thumbnail_url = env.get("STATUS_THUMBNAIL_URL", "").strip()
        if thumbnail_url and not thumbnail_url.startswith("https://"):
            raise SettingsError("STATUS_THUMBNAIL_URL must be an https:// URL")

        state_file = Path(env.get("STATUS_STATE_FILE", "").strip() or cls.state_file)
        if not state_file.is_absolute():
            state_file = PROJECT_ROOT / state_file

        offline_after = _number(
            env, "STATUS_OFFLINE_AFTER", Thresholds.offline_after, 10
        )
        heartbeat_interval = _number(env, "STATUS_HEARTBEAT_INTERVAL", 30.0, 5)
        if offline_after <= heartbeat_interval:
            raise SettingsError(
                "STATUS_OFFLINE_AFTER must be greater than STATUS_HEARTBEAT_INTERVAL"
            )

        return cls(
            heartbeat_secret=secret,
            service_name=env.get("STATUS_SERVICE_NAME", "").strip() or cls.service_name,
            display_name=env.get("STATUS_DISPLAY_NAME", "").strip() or cls.display_name,
            host=env.get("STATUS_LISTEN_HOST", "").strip() or cls.host,
            port=int(_number(env, "STATUS_LISTEN_PORT", cls.port, 1)),
            webhook_url=webhook_url,
            message_id=_optional_id(env, "STATUS_MESSAGE_ID"),
            state_file=state_file,
            thresholds=Thresholds(
                offline_after=offline_after,
                starting_grace=_number(
                    env, "STATUS_STARTING_GRACE", Thresholds.starting_grace, 0
                ),
                degraded_latency_ms=_number(
                    env, "STATUS_DEGRADED_LATENCY_MS", Thresholds.degraded_latency_ms, 1
                ),
            ),
            evaluate_interval=_number(
                env, "STATUS_EVALUATE_INTERVAL", cls.evaluate_interval, 1
            ),
            publish_interval=_number(
                env, "STATUS_PUBLISH_INTERVAL", cls.publish_interval, 30
            ),
            recreate_missing_message=_flag(
                env, "STATUS_RECREATE_MISSING_MESSAGE", True
            ),
            thumbnail_url=thumbnail_url or read_bot_avatar_url(BOT_CONFIG_FILE),
        )


def _number(env, name: str, default: float, minimum: float) -> float:
    raw_value = env.get(name, "").strip()
    if not raw_value:
        return float(default)
    try:
        value = float(raw_value)
    except ValueError:
        value = math.nan
    if not math.isfinite(value):
        raise SettingsError(f"{name} must be a finite number")
    if value < minimum:
        raise SettingsError(f"{name} must be >= {minimum}")
    return value


def _optional_id(env, name: str) -> int | None:
    raw_value = env.get(name, "").strip()
    if not raw_value:
        return None
    if not raw_value.isdigit():
        raise SettingsError(f"{name} must be a numeric Discord ID")
    return int(raw_value)


def _flag(env, name: str, default: bool) -> bool:
    raw_value = env.get(name, "").strip().lower()
    if not raw_value:
        return default
    return raw_value == "true"


def read_bot_avatar_url(config_file: Path) -> str:
    """
    Read `bot.assets.avatar` from the bot's config.json.

    Plain `json` on purpose: importing `utils.config` would also import
    `utils.logger`, which sends DEBUG logs of every library (including
    discord.py webhook URLs with their tokens) to logs/standard.log.
    A missing or invalid value only means the embed has no thumbnail.
    """
    try:
        data = json.loads(Path(config_file).read_text(encoding="utf-8"))
        avatar = data["bot"]["assets"]["avatar"]
    except (OSError, ValueError, KeyError, TypeError):
        return ""
    return avatar if isinstance(avatar, str) and avatar.startswith("https://") else ""
