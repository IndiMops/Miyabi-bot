"""
HTTP endpoints and the monitor loop.

Only two routes exist:
- POST /heartbeat  authenticated with `Authorization: Bearer <secret>`;
- GET  /health     the status service's own health, for Uptime Kuma.
"""
import asyncio
import hmac
import json
import time
from typing import Any

import aiohttp
import discord
from aiohttp import web
from loguru import logger

from status_service.evaluator import (
    Evaluation,
    Heartbeat,
    PayloadError,
    ServiceState,
    evaluate,
)
from status_service.publisher import (
    PublishError,
    StatusMessagePublisher,
    build_status_embed,
)
from status_service.settings import StatusServiceSettings
from status_service.store import StateStore

MAX_BODY_BYTES = 16 * 1024
MAX_PUBLISH_BACKOFF = 300.0
UNHEALTHY_PUBLISH_FAILURES = 3

MONITOR_KEY = web.AppKey("monitor", "StatusMonitor")


class StatusMonitor:
    """Tracks the latest heartbeat and decides when the Discord message needs an update."""

    def __init__(
        self,
        settings: StatusServiceSettings,
        store: StateStore,
        publisher: StatusMessagePublisher | None,
        clock=time.time,
    ):
        self.settings = settings
        self.store = store
        self.publisher = publisher
        self._clock = clock
        self.started_at = clock()
        self.heartbeat: Heartbeat | None = None
        self.heartbeats_received = 0
        self.last_tick_at: float | None = None
        self.last_published_state: ServiceState | None = None
        self.last_published_at: float | None = None
        self.next_publish_attempt_at = 0.0
        self.wake = asyncio.Event()

    def restore(self) -> None:
        self.store.load()
        stored = self.store.get_heartbeat(self.settings.service_name)
        if stored is None:
            return
        try:
            self.heartbeat = Heartbeat.from_stored(stored, self.settings.service_name)
        except PayloadError:
            logger.warning("Ignoring invalid stored heartbeat")

    def evaluate(self, now: float | None = None) -> Evaluation:
        now = self._clock() if now is None else now
        return evaluate(self.heartbeat, now, self.started_at, self.settings.thresholds)

    def record_heartbeat(self, data: Any) -> Evaluation:
        now = self._clock()
        previous_state = self.evaluate(now).state
        self.heartbeat = Heartbeat.from_payload(data, self.settings.service_name, now)
        self.heartbeats_received += 1
        self.store.set_heartbeat(self.settings.service_name, self.heartbeat.to_dict())
        self.store.save()

        evaluation = self.evaluate(now)
        if evaluation.state != previous_state:
            logger.info(f"{self.settings.service_name}: {previous_state.value} -> {evaluation.state.value}")
            self.wake.set()
        return evaluation

    def should_publish(self, evaluation: Evaluation, now: float) -> bool:
        if self.publisher is None or evaluation.state == ServiceState.UNKNOWN:
            return False
        if now < self.next_publish_attempt_at:
            return False
        if evaluation.state != self.last_published_state:
            return True
        return now - (self.last_published_at or 0) >= self.settings.publish_interval

    async def tick(self) -> Evaluation:
        now = self._clock()
        self.last_tick_at = now
        evaluation = self.evaluate(now)
        if not self.should_publish(evaluation, now):
            return evaluation

        embed = build_status_embed(
            evaluation, self.settings.display_name, now, self.settings.thumbnail_url
        )
        try:
            await self.publisher.publish(embed)
        except PublishError as error:
            failures = self.publisher.consecutive_failures
            delay = min(MAX_PUBLISH_BACKOFF, self.settings.evaluate_interval * 2 ** (failures - 1))
            self.next_publish_attempt_at = now + delay
            logger.error(f"Could not update status message: {error}; retrying in {delay:.0f}s")
            return evaluation

        if evaluation.state != self.last_published_state:
            logger.info(f"Published status {evaluation.state.value}")
        self.last_published_state = evaluation.state
        self.last_published_at = now
        self.next_publish_attempt_at = 0.0
        return evaluation

    async def run(self) -> None:
        while True:
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Status monitor tick failed")
            self.wake.clear()
            try:
                await asyncio.wait_for(self.wake.wait(), timeout=self.settings.evaluate_interval)
            except TimeoutError:
                pass

    def health(self) -> tuple[bool, dict[str, Any]]:
        now = self._clock()
        problems = []
        if self.last_tick_at is None or now - self.last_tick_at > 3 * self.settings.evaluate_interval + 5:
            problems.append("monitor loop is not running")
        if not self.store.last_save_ok:
            problems.append("state file is not writable")
        publisher_info: dict[str, Any] = {"enabled": self.publisher is not None}
        if self.publisher is not None:
            publisher_info.update(
                last_success_at=self.publisher.last_success_at,
                consecutive_failures=self.publisher.consecutive_failures,
                last_error=self.publisher.last_error,
            )
            if self.publisher.consecutive_failures >= UNHEALTHY_PUBLISH_FAILURES:
                problems.append("Discord status message cannot be updated")

        body = {
            "status": "ok" if not problems else "error",
            "problems": problems,
            "uptime_seconds": round(now - self.started_at, 1),
            "heartbeats_received": self.heartbeats_received,
            "publisher": publisher_info,
        }
        return not problems, body


def _is_authorized(request: web.Request, secret: str) -> bool:
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return False
    return hmac.compare_digest(token.strip().encode(), secret.encode())


async def handle_heartbeat(request: web.Request) -> web.Response:
    monitor: StatusMonitor = request.app[MONITOR_KEY]
    if not _is_authorized(request, monitor.settings.heartbeat_secret):
        logger.warning(f"Rejected unauthenticated heartbeat from {request.remote}")
        return web.json_response({"error": "unauthorized"}, status=401)

    try:
        data = json.loads(await request.read())
    except web.HTTPRequestEntityTooLarge:
        raise
    except (ValueError, UnicodeDecodeError):
        return web.json_response({"error": "body must be valid JSON"}, status=400)

    try:
        evaluation = monitor.record_heartbeat(data)
    except PayloadError as error:
        status = 422 if str(error) == "unknown service" else 400
        return web.json_response({"error": str(error)}, status=status)
    return web.json_response({"accepted": True, "state": evaluation.state.value})


async def handle_health(request: web.Request) -> web.Response:
    healthy, body = request.app[MONITOR_KEY].health()
    return web.json_response(body, status=200 if healthy else 503)


def create_app(monitor: StatusMonitor) -> web.Application:
    app = web.Application(client_max_size=MAX_BODY_BYTES)
    app[MONITOR_KEY] = monitor
    app.router.add_post("/heartbeat", handle_heartbeat)
    app.router.add_get("/health", handle_health)
    return app


def build_production_app(settings: StatusServiceSettings) -> web.Application:
    """Wire the real webhook, state file and background loop into the app."""
    store = StateStore(settings.state_file)
    monitor = StatusMonitor(settings, store, publisher=None)
    monitor.restore()
    app = create_app(monitor)

    async def lifecycle(app: web.Application):
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
        if settings.publishing_enabled:
            webhook = discord.Webhook.from_url(settings.webhook_url, session=session)
            monitor.publisher = StatusMessagePublisher(
                webhook,
                store,
                configured_message_id=settings.message_id,
                recreate_missing=settings.recreate_missing_message,
            )
        else:
            logger.warning("STATUS_WEBHOOK_URL is not set; Discord publishing is disabled")
        task = asyncio.create_task(monitor.run())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        store.save()
        await session.close()

    app.cleanup_ctx.append(lifecycle)
    return app
