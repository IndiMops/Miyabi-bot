import aiohttp
from discord.ext import commands, tasks

from utils.config import Config
from utils.heartbeat import (
    PROCESS_STARTED_AT,
    HeartbeatReporter,
    HeartbeatSettings,
    build_heartbeat_payload,
)
from utils.logger import logger


class StatusHeartbeat(commands.Cog):
    """Periodically reports the bot's state to the external status service."""

    def __init__(self, bot: commands.Bot, settings: HeartbeatSettings):
        self.bot = bot
        self.settings = settings
        self.session: aiohttp.ClientSession | None = None
        self.reporter: HeartbeatReporter | None = None
        self.heartbeat_loop.change_interval(seconds=settings.interval)

    async def cog_load(self) -> None:
        if not self.settings.enabled:
            logger.info(
                "Status heartbeat disabled: STATUS_HEARTBEAT_URL or STATUS_HEARTBEAT_SECRET is not set"
            )
            return

        self.session = aiohttp.ClientSession()
        self.reporter = HeartbeatReporter(self.settings, self.session)
        # Starts before the gateway is ready on purpose: "not ready yet" is
        # useful information for the status service.
        self.heartbeat_loop.start()
        logger.info(f"Status heartbeat enabled every {self.settings.interval:g}s")

    async def cog_unload(self) -> None:
        self.heartbeat_loop.cancel()
        if self.reporter is not None:
            # Bot.close() unloads extensions first, so a graceful shutdown is
            # reported immediately instead of waiting for the stale threshold.
            payload = build_heartbeat_payload(
                self.bot, self.settings.service, PROCESS_STARTED_AT, shutting_down=True
            )
            await self.reporter.send(payload, max_attempts=1)
        if self.session is not None:
            await self.session.close()

    @tasks.loop(seconds=30)
    async def heartbeat_loop(self) -> None:
        payload = build_heartbeat_payload(
            self.bot, self.settings.service, PROCESS_STARTED_AT
        )
        await self.reporter.send(payload)

    @heartbeat_loop.error
    async def heartbeat_loop_error(self, error: BaseException) -> None:
        # Should be unreachable because the reporter swallows errors, but a
        # stopped loop must never take the bot down with it.
        logger.opt(exception=error).error("Status heartbeat loop stopped unexpectedly")


async def setup(bot: commands.Bot):
    settings = HeartbeatSettings(
        url=Config.STATUS_HEARTBEAT_URL,
        secret=Config.STATUS_HEARTBEAT_SECRET,
        service=Config.STATUS_SERVICE_NAME,
        interval=Config.STATUS_HEARTBEAT_INTERVAL,
        timeout=Config.STATUS_HEARTBEAT_TIMEOUT,
    )
    await bot.add_cog(StatusHeartbeat(bot, settings))
