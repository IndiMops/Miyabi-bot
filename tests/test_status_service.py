import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import discord
from aiohttp.test_utils import TestClient, TestServer

from status_service.app import StatusMonitor, create_app
from status_service.evaluator import Heartbeat, PayloadError, ServiceState, evaluate
from status_service.publisher import (
    UNKNOWN_MESSAGE,
    UNKNOWN_WEBHOOK,
    PublishError,
    StatusMessagePublisher,
    build_status_embed,
)
from status_service.settings import SettingsError, StatusServiceSettings, Thresholds
from status_service.store import StateStore

SECRET = "0123456789abcdef-test"
THRESHOLDS = Thresholds(offline_after=90, starting_grace=180, degraded_latency_ms=1000)


def payload(**overrides):
    data = {
        "schema": 1,
        "service": "miyabi-bot",
        "sent_at": 1000.0,
        "process_started_at": 900.0,
        "uptime_seconds": 100.0,
        "ready": True,
        "gateway_connected": True,
        "latency_ms": 42.0,
        "guild_count": 5,
        "shard_count": None,
        "shutting_down": False,
    }
    data.update(overrides)
    return data


def heartbeat(received_at=1000.0, **overrides):
    return Heartbeat.from_payload(payload(**overrides), "miyabi-bot", received_at)


class Clock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


def discord_error(cls, status, code):
    response = SimpleNamespace(status=status, reason="error")
    return cls(response, {"code": code, "message": "error"})


class FakeWebhook:
    def __init__(self, webhook_id=111):
        self.id = webhook_id
        self.messages: dict[int, discord.Embed] = {}
        self.sent = 0
        self.edits = 0
        self.next_id = 5000
        self.fail_with: Exception | None = None

    async def send(self, *, embed, wait):
        if self.fail_with:
            raise self.fail_with
        self.sent += 1
        self.next_id += 1
        self.messages[self.next_id] = embed
        return SimpleNamespace(id=self.next_id)

    async def edit_message(self, message_id, *, embed):
        if self.fail_with:
            raise self.fail_with
        if message_id not in self.messages:
            raise discord_error(discord.NotFound, 404, UNKNOWN_MESSAGE)
        self.edits += 1
        self.messages[message_id] = embed
        return SimpleNamespace(id=message_id)


class EvaluateTests(unittest.TestCase):
    def check(self, hb, now, expected, monitor_started_at=1000.0):
        self.assertEqual(evaluate(hb, now, monitor_started_at, THRESHOLDS).state, expected)

    def test_fresh_ready_heartbeat_is_online(self) -> None:
        self.check(heartbeat(), 1030, ServiceState.ONLINE)

    def test_stale_heartbeat_is_offline(self) -> None:
        self.check(heartbeat(), 1090, ServiceState.ONLINE)
        self.check(heartbeat(), 1091, ServiceState.OFFLINE)

    def test_missing_heartbeat_is_unknown_then_offline(self) -> None:
        self.check(None, 1050, ServiceState.UNKNOWN)
        self.check(None, 1091, ServiceState.OFFLINE)

    def test_not_ready_is_starting_only_during_grace(self) -> None:
        self.check(heartbeat(ready=False, uptime_seconds=20), 1000, ServiceState.STARTING)
        self.check(heartbeat(ready=False, uptime_seconds=500), 1000, ServiceState.OFFLINE)

    def test_shutdown_is_offline_immediately(self) -> None:
        self.check(heartbeat(ready=False, shutting_down=True), 1000, ServiceState.OFFLINE)

    def test_reconnect_and_high_latency_are_degraded(self) -> None:
        self.check(heartbeat(gateway_connected=False, latency_ms=None), 1000, ServiceState.DEGRADED)
        self.check(heartbeat(latency_ms=2500.0), 1000, ServiceState.DEGRADED)

    def test_unmeasured_latency_on_connected_gateway_is_online(self) -> None:
        self.check(heartbeat(latency_ms=None), 1000, ServiceState.ONLINE)


class PayloadValidationTests(unittest.TestCase):
    def test_rejects_malformed_payloads(self) -> None:
        bad_payloads = [
            [],
            payload(schema=2),
            payload(service="other"),
            payload(ready="true"),
            payload(sent_at="now"),
            payload(sent_at=float("nan")),
            payload(guild_count=-1),
            payload(guild_count=True),
            payload(latency_ms=-5),
        ]
        for data in bad_payloads:
            with self.subTest(data=data), self.assertRaises(PayloadError):
                Heartbeat.from_payload(data, "miyabi-bot", 1000.0)

    def test_receiver_clock_is_used_for_freshness(self) -> None:
        hb = Heartbeat.from_payload(payload(sent_at=1.0), "miyabi-bot", 2000.0)
        self.assertEqual(hb.received_at, 2000.0)

    def test_stored_heartbeat_round_trip(self) -> None:
        hb = heartbeat(received_at=1234.0)
        self.assertEqual(Heartbeat.from_stored(hb.to_dict(), "miyabi-bot"), hb)


class SettingsTests(unittest.TestCase):
    def test_secret_is_required(self) -> None:
        with self.assertRaises(SettingsError):
            StatusServiceSettings.from_env({})
        with self.assertRaises(SettingsError):
            StatusServiceSettings.from_env({"STATUS_HEARTBEAT_SECRET": "short"})

    def test_defaults_and_overrides(self) -> None:
        settings = StatusServiceSettings.from_env(
            {
                "STATUS_HEARTBEAT_SECRET": SECRET,
                "STATUS_OFFLINE_AFTER": "120",
                "STATUS_MESSAGE_ID": "123456789012345678",
            }
        )
        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.thresholds.offline_after, 120)
        self.assertEqual(settings.message_id, 123456789012345678)
        self.assertFalse(settings.publishing_enabled)

    def test_offline_threshold_must_exceed_interval(self) -> None:
        with self.assertRaises(SettingsError):
            StatusServiceSettings.from_env(
                {"STATUS_HEARTBEAT_SECRET": SECRET, "STATUS_OFFLINE_AFTER": "30"}
            )

    def test_rejects_non_finite_numbers(self) -> None:
        for name in ("STATUS_OFFLINE_AFTER", "STATUS_LISTEN_PORT"):
            for raw in ("nan", "inf", "abc"):
                with self.subTest(name=name, raw=raw), self.assertRaises(SettingsError):
                    StatusServiceSettings.from_env({"STATUS_HEARTBEAT_SECRET": SECRET, name: raw})

    def test_rejects_non_https_webhook(self) -> None:
        with self.assertRaises(SettingsError):
            StatusServiceSettings.from_env(
                {"STATUS_HEARTBEAT_SECRET": SECRET, "STATUS_WEBHOOK_URL": "http://example.invalid"}
            )


class StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "state" / "status.json"

    def test_message_id_survives_restart(self) -> None:
        store = StateStore(self.path)
        store.set_message_id(111, 42)
        self.assertTrue(store.save())

        restarted = StateStore(self.path)
        restarted.load()
        self.assertEqual(restarted.get_message_id(111), 42)

    def test_message_id_from_another_webhook_is_ignored(self) -> None:
        store = StateStore(self.path)
        store.set_message_id(111, 42)
        self.assertIsNone(store.get_message_id(222))

    def test_corrupt_file_is_moved_aside(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")

        store = StateStore(self.path)
        store.load()

        self.assertIsNone(store.get_message_id(111))
        self.assertFalse(self.path.exists())
        self.assertEqual(len(list(self.path.parent.glob("status.json.corrupt-*"))), 1)


class PublisherTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "status.json"
        self.webhook = FakeWebhook()
        self.embed = discord.Embed(title="status")

    async def asyncTearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_publisher(self, **kwargs) -> StatusMessagePublisher:
        store = StateStore(self.path)
        store.load()
        return StatusMessagePublisher(self.webhook, store, **kwargs)

    async def test_creates_message_once_then_edits(self) -> None:
        publisher = self.make_publisher()

        for _ in range(3):
            await publisher.publish(self.embed)

        self.assertEqual(self.webhook.sent, 1)
        self.assertEqual(self.webhook.edits, 2)
        self.assertEqual(len(self.webhook.messages), 1)

    async def test_restart_reuses_persisted_message(self) -> None:
        await self.make_publisher().publish(self.embed)
        message_id = next(iter(self.webhook.messages))

        restarted = self.make_publisher()
        await restarted.publish(self.embed)

        self.assertEqual(self.webhook.sent, 1)
        self.assertEqual(restarted.message_id, message_id)
        self.assertEqual(json.loads(self.path.read_text())["message"]["id"], message_id)

    async def test_configured_message_id_is_adopted(self) -> None:
        self.webhook.messages[777] = discord.Embed()
        publisher = self.make_publisher(configured_message_id=777)

        await publisher.publish(self.embed)

        self.assertEqual(self.webhook.sent, 0)
        self.assertEqual(self.make_publisher().message_id, 777)

    async def test_deleted_message_is_recreated(self) -> None:
        publisher = self.make_publisher()
        await publisher.publish(self.embed)
        self.webhook.messages.clear()

        await publisher.publish(self.embed)
        await publisher.publish(self.embed)

        self.assertEqual(self.webhook.sent, 2)
        self.assertEqual(len(self.webhook.messages), 1)

    async def test_deleted_message_without_recreate_fails(self) -> None:
        publisher = self.make_publisher(configured_message_id=999, recreate_missing=False)

        with self.assertRaises(PublishError):
            await publisher.publish(self.embed)
        self.assertEqual(self.webhook.sent, 0)
        self.assertEqual(publisher.consecutive_failures, 1)

    async def test_unknown_webhook_is_not_treated_as_deleted_message(self) -> None:
        publisher = self.make_publisher()
        await publisher.publish(self.embed)
        self.webhook.fail_with = discord_error(discord.NotFound, 404, UNKNOWN_WEBHOOK)

        with self.assertRaisesRegex(PublishError, "STATUS_WEBHOOK_URL"):
            await publisher.publish(self.embed)
        self.assertEqual(self.webhook.sent, 1)

    async def test_failure_then_recovery(self) -> None:
        publisher = self.make_publisher()
        self.webhook.fail_with = discord_error(discord.Forbidden, 403, 50013)

        with self.assertRaises(PublishError):
            await publisher.publish(self.embed)
        self.assertEqual(publisher.consecutive_failures, 1)

        self.webhook.fail_with = None
        await publisher.publish(self.embed)
        self.assertEqual(publisher.consecutive_failures, 0)
        self.assertIsNone(publisher.last_error)


class EmbedTests(unittest.TestCase):
    def test_online_embed_contains_operational_fields(self) -> None:
        evaluation = evaluate(heartbeat(), 1000.0, 1000.0, THRESHOLDS)
        embed = build_status_embed(evaluation, "Miyabi Bot", 1000.0)

        names = [field.name for field in embed.fields]
        self.assertIn("Онлайн", embed.title)
        self.assertIn("Останній heartbeat", names)
        self.assertIn("Сервери", names)
        self.assertIn("Затримка gateway", names)

    def test_offline_embed_omits_live_metrics(self) -> None:
        evaluation = evaluate(heartbeat(), 2000.0, 1000.0, THRESHOLDS)
        embed = build_status_embed(evaluation, "Miyabi Bot", 2000.0)

        self.assertIn("Офлайн", embed.title)
        self.assertEqual([field.name for field in embed.fields], ["Останній heartbeat"])


class MonitorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "status.json"
        self.clock = Clock()
        self.webhook = FakeWebhook()
        self.settings = StatusServiceSettings(
            heartbeat_secret=SECRET,
            state_file=self.path,
            thresholds=THRESHOLDS,
            evaluate_interval=10,
            publish_interval=300,
        )

    async def asyncTearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_monitor(self) -> StatusMonitor:
        store = StateStore(self.path)
        monitor = StatusMonitor(
            self.settings,
            store,
            StatusMessagePublisher(self.webhook, store, clock=self.clock),
            clock=self.clock,
        )
        monitor.restore()
        return monitor

    def last_title(self) -> str:
        return list(self.webhook.messages.values())[-1].title

    async def test_full_lifecycle_online_offline_online(self) -> None:
        monitor = self.make_monitor()

        await monitor.tick()
        self.assertEqual(self.webhook.sent, 0, "UNKNOWN must not be published")

        monitor.record_heartbeat(payload())
        await monitor.tick()
        self.assertEqual(self.webhook.sent, 1)
        self.assertIn("Онлайн", self.last_title())

        # Heartbeats stop: the bot cannot report this itself.
        self.clock.now += 91
        await monitor.tick()
        self.assertIn("Офлайн", self.last_title())

        self.clock.now += 30
        monitor.record_heartbeat(payload())
        await monitor.tick()
        self.assertIn("Онлайн", self.last_title())
        self.assertEqual(self.webhook.sent, 1)
        self.assertEqual(len(self.webhook.messages), 1)

    async def test_unchanged_state_is_not_republished_until_interval(self) -> None:
        monitor = self.make_monitor()
        monitor.record_heartbeat(payload())
        await monitor.tick()

        for _ in range(5):
            self.clock.now += 30
            monitor.record_heartbeat(payload())
            await monitor.tick()
        self.assertEqual(self.webhook.edits, 0)

        self.clock.now += 150
        monitor.record_heartbeat(payload())
        await monitor.tick()
        self.assertEqual(self.webhook.edits, 1)

    async def test_restart_restores_heartbeat_and_message(self) -> None:
        monitor = self.make_monitor()
        monitor.record_heartbeat(payload())
        await monitor.tick()

        self.clock.now += 20
        restarted = self.make_monitor()
        self.assertEqual(restarted.evaluate().state, ServiceState.ONLINE)
        await restarted.tick()

        self.assertEqual(self.webhook.sent, 1)
        self.assertEqual(self.webhook.edits, 1)

    async def test_restart_after_long_downtime_reports_offline(self) -> None:
        monitor = self.make_monitor()
        monitor.record_heartbeat(payload())
        await monitor.tick()

        self.clock.now += 3600
        restarted = self.make_monitor()
        await restarted.tick()

        self.assertIn("Офлайн", self.last_title())
        self.assertEqual(self.webhook.sent, 1)

    async def test_publish_failure_backs_off_and_recovers(self) -> None:
        monitor = self.make_monitor()
        monitor.record_heartbeat(payload())
        self.webhook.fail_with = discord_error(discord.HTTPException, 500, 0)

        await monitor.tick()
        self.assertEqual(monitor.next_publish_attempt_at, self.clock.now + 10)
        await monitor.tick()
        self.assertEqual(monitor.publisher.consecutive_failures, 1, "must wait for backoff")

        self.webhook.fail_with = None
        self.clock.now += 10
        await monitor.tick()
        self.assertEqual(self.webhook.sent, 1)
        self.assertEqual(monitor.last_published_state, ServiceState.ONLINE)

    async def test_health_reflects_own_state_not_bot_state(self) -> None:
        monitor = self.make_monitor()
        healthy, _ = monitor.health()
        self.assertFalse(healthy, "loop has not ticked yet")

        await monitor.tick()
        self.clock.now += 3600  # bot is long gone
        await monitor.tick()
        healthy, body = monitor.health()
        self.assertTrue(healthy)
        self.assertNotIn("state", body)

        self.webhook.fail_with = discord_error(discord.Forbidden, 403, 50013)
        for _ in range(3):
            monitor.next_publish_attempt_at = 0
            monitor.last_published_state = None
            await monitor.tick()
        healthy, body = monitor.health()
        self.assertFalse(healthy)
        self.assertIn("Discord status message cannot be updated", body["problems"])


class HttpEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        settings = StatusServiceSettings(
            heartbeat_secret=SECRET,
            state_file=Path(self.temp_dir.name) / "status.json",
        )
        self.monitor = StatusMonitor(settings, StateStore(settings.state_file), publisher=None)
        self.client = TestClient(TestServer(create_app(self.monitor)))
        await self.client.start_server()

    async def asyncTearDown(self) -> None:
        await self.client.close()
        self.temp_dir.cleanup()

    async def post(self, body, token=SECRET):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        if not isinstance(body, (str, bytes)):
            body = json.dumps(body)
        return await self.client.post("/heartbeat", data=body, headers=headers)

    async def test_valid_heartbeat_is_accepted(self) -> None:
        response = await self.post(payload())

        self.assertEqual(response.status, 200)
        self.assertEqual(await response.json(), {"accepted": True, "state": "ONLINE"})
        self.assertEqual(self.monitor.heartbeats_received, 1)

    async def test_missing_or_wrong_secret_is_rejected(self) -> None:
        for token in (None, "wrong-secret"):
            with self.subTest(token=token):
                response = await self.post(payload(), token=token)
                self.assertEqual(response.status, 401)
        self.assertIsNone(self.monitor.heartbeat)

    async def test_malformed_body_is_rejected(self) -> None:
        self.assertEqual((await self.post("{not json")).status, 400)
        self.assertEqual((await self.post(payload(ready="yes"))).status, 400)
        self.assertEqual((await self.post(payload(service="website"))).status, 422)
        self.assertIsNone(self.monitor.heartbeat)

    async def test_oversized_body_is_rejected(self) -> None:
        response = await self.post("x" * (32 * 1024))
        self.assertEqual(response.status, 413)

    async def test_only_expected_routes_exist(self) -> None:
        self.assertEqual((await self.client.get("/heartbeat")).status, 405)
        self.assertEqual((await self.client.get("/admin")).status, 404)

    async def test_health_endpoint(self) -> None:
        response = await self.client.get("/health")
        self.assertEqual(response.status, 503)

        await self.monitor.tick()
        response = await self.client.get("/health")
        self.assertEqual(response.status, 200)
        self.assertEqual((await response.json())["status"], "ok")
