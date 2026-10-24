import math
import os
import unittest
from types import SimpleNamespace
from unittest import mock

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer

from utils.config import _env_float
from utils.heartbeat import (
    HeartbeatReporter,
    HeartbeatSettings,
    build_heartbeat_payload,
)


class FakeClient:
    def __init__(self, ready=True, closed=False, ws_open=True, latency=0.05, guilds=3):
        self._ready = ready
        self._closed = closed
        self.ws = None if ws_open is None else SimpleNamespace(open=ws_open)
        self.latency = latency
        self.guilds = [object()] * guilds
        self.shard_count = None

    def is_ready(self):
        return self._ready

    def is_closed(self):
        return self._closed


class HeartbeatPayloadTests(unittest.TestCase):
    def test_ready_client_reports_operational_data(self) -> None:
        payload = build_heartbeat_payload(FakeClient(), "miyabi-bot", 1000.0, now=1060.0)

        self.assertEqual(payload["schema"], 1)
        self.assertEqual(payload["service"], "miyabi-bot")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["gateway_connected"])
        self.assertEqual(payload["latency_ms"], 50.0)
        self.assertEqual(payload["guild_count"], 3)
        self.assertEqual(payload["uptime_seconds"], 60.0)
        self.assertEqual(payload["sent_at"], 1060.0)
        self.assertFalse(payload["shutting_down"])

    def test_not_ready_client_is_not_reported_ready(self) -> None:
        payload = build_heartbeat_payload(
            FakeClient(ready=False, ws_open=None, latency=math.nan), "miyabi-bot", 1000.0, now=1001.0
        )

        self.assertFalse(payload["ready"])
        self.assertFalse(payload["gateway_connected"])
        self.assertIsNone(payload["latency_ms"])
        self.assertIsNone(payload["guild_count"])

    def test_closed_client_is_not_ready_even_if_ready_flag_is_set(self) -> None:
        payload = build_heartbeat_payload(FakeClient(closed=True), "miyabi-bot", 1000.0, now=1001.0)
        self.assertFalse(payload["ready"])

    def test_reconnecting_gateway_is_reported_separately(self) -> None:
        payload = build_heartbeat_payload(FakeClient(ws_open=False), "miyabi-bot", 1000.0, now=1001.0)

        self.assertTrue(payload["ready"])
        self.assertFalse(payload["gateway_connected"])
        self.assertIsNone(payload["latency_ms"])

    def test_infinite_latency_is_reported_as_unknown(self) -> None:
        payload = build_heartbeat_payload(FakeClient(latency=math.inf), "miyabi-bot", 1000.0, now=1001.0)
        self.assertIsNone(payload["latency_ms"])

    def test_shutdown_payload_is_not_ready(self) -> None:
        payload = build_heartbeat_payload(
            FakeClient(), "miyabi-bot", 1000.0, now=1001.0, shutting_down=True
        )
        self.assertFalse(payload["ready"])
        self.assertTrue(payload["shutting_down"])

    def test_settings_require_url_and_secret(self) -> None:
        self.assertFalse(HeartbeatSettings(url="", secret="x").enabled)
        self.assertFalse(HeartbeatSettings(url="http://127.0.0.1/heartbeat", secret="").enabled)
        self.assertTrue(HeartbeatSettings(url="http://127.0.0.1/heartbeat", secret="x").enabled)


class EnvFloatTests(unittest.TestCase):
    def read(self, raw):
        with mock.patch.dict(os.environ, {"TEST_HEARTBEAT_VALUE": raw}):
            return _env_float("TEST_HEARTBEAT_VALUE", 30.0, minimum=5.0)

    def test_valid_value_is_used(self) -> None:
        self.assertEqual(self.read("12.5"), 12.5)

    def test_invalid_values_fall_back_to_default(self) -> None:
        for raw in ("", "abc", "nan", "inf", "-inf", "1"):
            with self.subTest(raw=raw):
                self.assertEqual(self.read(raw), 30.0)


class HeartbeatReporterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.responses: list[int] = []
        self.requests: list[tuple[str, dict]] = []

        async def handler(request: web.Request) -> web.Response:
            self.requests.append((request.headers.get("Authorization"), await request.json()))
            return web.json_response({}, status=self.responses.pop(0) if self.responses else 200)

        app = web.Application()
        app.router.add_post("/heartbeat", handler)
        self.server = TestServer(app)
        await self.server.start_server()
        self.session = aiohttp.ClientSession()
        self.sleeps: list[float] = []

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.server.close()

    def make_reporter(self, url=None) -> HeartbeatReporter:
        settings = HeartbeatSettings(
            url=url or str(self.server.make_url("/heartbeat")),
            secret="test-secret",
            timeout=2,
        )

        async def fake_sleep(delay):
            self.sleeps.append(delay)

        return HeartbeatReporter(settings, self.session, sleep=fake_sleep)

    async def test_successful_delivery_sends_bearer_secret(self) -> None:
        reporter = self.make_reporter()

        self.assertTrue(await reporter.send({"service": "miyabi-bot"}))
        self.assertEqual(self.requests[0], ("Bearer test-secret", {"service": "miyabi-bot"}))
        self.assertEqual(reporter.consecutive_failures, 0)

    async def test_server_errors_are_retried_with_backoff(self) -> None:
        self.responses = [503, 500, 200]
        reporter = self.make_reporter()

        self.assertTrue(await reporter.send({}))
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(self.sleeps, [1.0, 2.0])

    async def test_rejected_heartbeat_is_not_retried(self) -> None:
        self.responses = [401]
        reporter = self.make_reporter()

        self.assertFalse(await reporter.send({}))
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(reporter.consecutive_failures, 1)

    async def test_unreachable_service_does_not_raise_and_recovers(self) -> None:
        reporter = self.make_reporter()

        def refuse(*args, **kwargs):
            raise aiohttp.ClientConnectionError("connection refused")

        reporter.session = SimpleNamespace(post=refuse)
        self.assertFalse(await reporter.send({}))
        self.assertFalse(await reporter.send({}))
        self.assertEqual(reporter.consecutive_failures, 2)
        self.assertEqual(self.sleeps, [1.0, 2.0, 1.0, 2.0])

        reporter.session = self.session
        self.assertTrue(await reporter.send({}))
        self.assertEqual(reporter.consecutive_failures, 0)

    async def test_single_attempt_override(self) -> None:
        self.responses = [503]
        reporter = self.make_reporter()

        self.assertFalse(await reporter.send({}, max_attempts=1))
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.sleeps, [])
