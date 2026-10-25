# Status Monitoring

[← Back to contents](README.md)

The bot periodically sends a heartbeat to a separate `status_service`
process. Based on heartbeat freshness, the service determines the state and
maintains **one** message in a dedicated Discord text channel, editing it via
a webhook.

```text
Miyabi Bot ──POST /heartbeat (Bearer secret)──▶ status_service ──webhook edit──▶ #status
                                                    │
                                    Uptime Kuma ──GET /health
```

## Components

| File | Responsibility |
|---|---|
| [`utils/heartbeat.py`](../utils/heartbeat.py) | Collecting client state and delivering the heartbeat (timeout, retry with backoff, no exceptions propagated). |
| [`cogs/core/status_heartbeat.py`](../cogs/core/status_heartbeat.py) | The heartbeat loop within the bot lifecycle and the shutdown heartbeat on `close()`. |
| [`status_service/evaluator.py`](../status_service/evaluator.py) | Payload validation and state rules. |
| [`status_service/store.py`](../status_service/store.py) | JSON state file: message ID and the last heartbeat (atomic write). |
| [`status_service/publisher.py`](../status_service/publisher.py) | The status embed and creating/editing the single webhook message. |
| [`status_service/app.py`](../status_service/app.py) | HTTP endpoints, the evaluation loop, `/health`. |

The bot **does not depend** on the status service: if the variables are not
set, the cog only logs that the reporter is disabled; if the service is
unreachable, the heartbeat is lost and one warning is logged per series of
failures.

## States

Freshness is measured by the time the heartbeat was **received** on the
service side, so clock skew on the bot host has no effect.

| State | Condition |
|---|---|
| `ONLINE` | Fresh heartbeat, `ready=true`, gateway connected, latency ≤ `STATUS_DEGRADED_LATENCY_MS`. |
| `DEGRADED` | Fresh heartbeat, `ready=true`, but the gateway is reconnecting or latency is high. |
| `STARTING` | Fresh heartbeat, `ready=false`, process younger than `STATUS_STARTING_GRACE`. |
| `OFFLINE` | Heartbeat older than `STATUS_OFFLINE_AFTER`; or the bot shut down gracefully; or `ready=false` for longer than the grace period. |
| `UNKNOWN` | The service has just started and has no heartbeat yet. **Not published to Discord.** |

`ready` is taken from `client.is_ready()` and `client.is_closed()`, not from
the fact that the process is alive. In discord.py `is_ready()` stays `true`
during a reconnect, so `gateway_connected` is sent separately. If the bot's
event loop hangs, heartbeats stop and the service moves to `OFFLINE` on its
own.

## The Discord message

1. On the first publish the service creates the message via the webhook
   (`?wait=true`) and writes its ID together with the webhook ID to the state
   file.
2. After that it only edits this message.
3. After a restart the ID is read from the state file — no duplicates.
4. If the message was deleted (Discord `10008 Unknown Message`), with
   `STATUS_RECREATE_MISSING_MESSAGE=true` a new one is created and its ID is
   saved. With `false` the service records the error and `/health` becomes
   503.
5. If the webhook changed, the old ID is ignored (the webhook ID is stored in
   the state file).
6. If the state file is corrupted, it is renamed to `*.corrupt-<timestamp>`.
   To avoid creating a new message, set `STATUS_MESSAGE_ID` — the service will
   "adopt" the existing message of this webhook.

Publishing happens immediately on a state change or once every
`STATUS_PUBLISH_INTERVAL` (300 s by default). The time of the last heartbeat
and the uptime are shown with Discord `<t:…:R>` timestamps, which the client
updates by itself, so frequent edits are not needed. Rate limits (429) are
handled by discord.py; on other errors there is exponential backoff up to
300 s.

A webhook can edit **only its own** messages, so creating the message manually
is neither needed nor possible.

## Environment variables

The full template is in [`.env.example`](../.env.example).

| Variable | Read by | Default | Purpose |
|---|---|---|---|
| `STATUS_HEARTBEAT_SECRET` | both | — | Shared secret for `Authorization: Bearer`. Required for the service, ≥ 16 characters. |
| `STATUS_SERVICE_NAME` | both | `miyabi-bot` | Service identifier in the payload. |
| `STATUS_HEARTBEAT_INTERVAL` | both | `30` | Heartbeat interval, s (the service only checks that the threshold is larger). |
| `STATUS_HEARTBEAT_URL` | bot | empty | Address of `/heartbeat`. Empty — reporter disabled. |
| `STATUS_HEARTBEAT_TIMEOUT` | bot | `5` | Timeout of a single request, s. 3 attempts with 1 and 2 s backoff. |
| `STATUS_LISTEN_HOST` / `STATUS_LISTEN_PORT` | service | `127.0.0.1` / `8787` | HTTP server address. |
| `STATUS_WEBHOOK_URL` | service | empty | Webhook of the status channel. Empty — publishing disabled. |
| `STATUS_DISPLAY_NAME` | service | `Miyabi Bot` | Name in the embed title. |
| `STATUS_THUMBNAIL_URL` | service | `bot.assets.avatar` from `config.json` | Embed thumbnail (`https://` only). Without a value and without `config.json` — embed without a thumbnail. |
| `STATUS_STATE_FILE` | service | `data/status_service_state.json` | State file (relative to the repo root). |
| `STATUS_MESSAGE_ID` | service | empty | Only for recovery after the state file was lost. |
| `STATUS_RECREATE_MISSING_MESSAGE` | service | `true` | Create a new message if the old one was deleted. |
| `STATUS_OFFLINE_AFTER` | service | `90` | Heartbeat staleness threshold, s. |
| `STATUS_STARTING_GRACE` | service | `180` | How long the process may stay `ready=false` in the `STARTING` state. |
| `STATUS_DEGRADED_LATENCY_MS` | service | `1000` | Latency threshold for `DEGRADED`. |
| `STATUS_EVALUATE_INTERVAL` | service | `10` | How often freshness is checked, s. |
| `STATUS_PUBLISH_INTERVAL` | service | `300` | Minimum interval for re-publishing without a state change, s. |

Invalid values: the bot substitutes the defaults and logs a warning; the
service refuses to start with exit code 2.

## Discord setup

1. Create a dedicated text channel, e.g. `#bot-status`, where regular users
   cannot write.
2. **Channel Settings → Integrations → Webhooks → New Webhook**, name it, copy
   the URL, and put it into `STATUS_WEBHOOK_URL` (only in `.env` / environment
   secrets, not in Git).
3. Nothing else is needed: the message is created automatically.

The webhook URL is a secret: whoever has it can post to the channel. If it
leaks, delete the webhook and create a new one; the service will create a new
message.

## HTTP endpoints

| Method | Path | Responses |
|---|---|---|
| `POST` | `/heartbeat` | `200` accepted; `401` missing/wrong secret; `400` invalid JSON/fields; `413` > 16 KB; `422` unknown service. |
| `GET` | `/health` | `200` or `503` with JSON `{status, problems, …}`. |

`/health` describes **the service itself**, not the bot: whether the
evaluation loop is running, whether the state file is being written, whether
the message can be updated (503 after 3 consecutive failures). The bot's state
is visible in Discord.

### Networking

By default the service listens on `127.0.0.1` only. If the bot and the service
run in different containers, set `STATUS_LISTEN_HOST=0.0.0.0` **inside** a
private Docker network and do not publish the port externally; the bot calls
`http://<service-name>:8787/heartbeat`. Access to the Docker socket is not
required.

### Uptime Kuma

Monitor type **HTTP(s)**, URL `http://<host>:8787/health`, interval 60 s,
accepted status codes `200-299`. Kuma must be on the same private network or
the same host. The endpoint needs no secret because it accepts no data and
exposes no secrets.

## Extending to other services

The payload contains a `service` field, and the state file stores heartbeats
by service name. Right now only `STATUS_SERVICE_NAME` is accepted; for a
website or an API the next step would be a list of services in the settings
and an embed field for each of them in the same message.

## Local verification

Automated tests (no Discord):

```powershell
python -m pytest tests/test_status_heartbeat.py tests/test_status_service.py
```

Live scenario (requires a test bot and a test channel with a webhook), two
terminals from the repo root, `.env` filled in from `.env.example`:

```powershell
# terminal 1
python -m status_service
# terminal 2
python bot.py
```

1. In the service logs: `miyabi-bot: UNKNOWN -> STARTING`, then `-> ONLINE`,
   `Created status message <id>`. A single 🟢 message appears in the channel.
2. `curl http://127.0.0.1:8787/health` → `200`, `heartbeats_received` grows.
3. Stop the bot with `Ctrl+C` → shutdown heartbeat, the message turns 🔴
   immediately. To test a "vanished" bot, kill the process without graceful
   shutdown (`Stop-Process -Id <pid> -Force`) → 🔴 after roughly 90–100 s.
4. Start the bot again → 🔵/🟢, **the same** message is edited.
5. Restart `status_service` → no `Created status message` in the logs, the ID
   in `data/status_service_state.json` stays the same.
6. Authentication check:
   `curl -X POST http://127.0.0.1:8787/heartbeat -d "{}"` → `401`.
