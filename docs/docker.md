# Docker

[← Back to contents](README.md)

One image runs both processes. They share the code and the dependencies but
run as separate containers:

```text
compose project "miyabi"  (default bridge network, no published ports)
┌───────────────────────────┐   POST /heartbeat   ┌──────────────────────────────┐
│ bot                       │ ──────────────────▶ │ status                       │
│ python bot.py             │  http://status:8787 │ python -m status_service     │
│ volume bot-logs → logs/   │                     │ listens on 0.0.0.0:8787      │
│ no healthcheck            │                     │ healthcheck: GET /health     │
└───────────────────────────┘                     │ volumes status-logs → logs/  │
           │ Discord gateway                      │         status-data → data/  │
           ▼                                      └──────────────────────────────┘
        Discord ◀──────────── webhook (status message) ─────────┘
```

| File | Purpose |
|---|---|
| [`Dockerfile`](../Dockerfile) | Python 3.11 slim (pinned digest), hash-checked install of `requirements.lock`, non-root user `10001`, code copied from an explicit allowlist. |
| [`.dockerignore`](../.dockerignore) | Allowlist build context, so `.env`, `.git`, `venv/`, `logs/`, and `data/` are never sent to the builder. |
| [`compose.yaml`](../compose.yaml) | Services `bot` and `status`, volumes, restart policy, hardening, log rotation. |
| [`scripts/docker-smoke-test.sh`](../scripts/docker-smoke-test.sh) | Checks a built image without secrets. Used by CI. |

## Requirements on the host

- Docker Engine with the Compose plugin (v2.24 or newer for `env_file.required`).
- A `.env` file next to `compose.yaml` (see [`.env.example`](../.env.example)).
  It needs `DISCORD_BOT_TOKEN`, and `STATUS_HEARTBEAT_SECRET` (at least 16
  characters) for the status service. Without the secret the `status`
  container exits with code 2 and keeps restarting.
- `DEBUG=False` in `.env` for anything but a test server.

## Local build and run

```bash
# Build the image (BOT_VERSION is what the bot shows; empty = config.json version)
BOT_VERSION="dev-$(git rev-parse --short HEAD)" VCS_REF="$(git rev-parse HEAD)" docker compose build

docker compose up -d                 # start both services
docker compose ps                    # state and health (status: "healthy")
docker compose logs -f bot           # follow the bot's stdout
docker compose logs -f status
docker compose down                  # stop; volumes are kept
```

PowerShell:

```powershell
$env:BOT_VERSION = "dev-$(git rev-parse --short HEAD)"; $env:VCS_REF = "$(git rev-parse HEAD)"
docker compose build
```

Check a built image the same way CI does (Linux, WSL, or Git Bash on
Windows):

```bash
docker build --build-arg BOT_VERSION=local-test -t miyabi-bot:test .
bash scripts/docker-smoke-test.sh miyabi-bot:test local-test
```

The smoke test checks, without secrets or Discord access: a non-root user;
the application files are present and `.env`, `.git`, and `git` are absent;
`pip check`; imports on a read-only filesystem; the version; the bot's
missing-token error; and that `status_service` answers `/health`. It exits
non-zero on the first failed check.

In CI the `docker` job additionally builds with `docker compose build`,
starts `status` in a throwaway compose project (`miyabi-ci`, dummy secret)
with `docker compose up --wait`, and removes that project's containers and
volumes afterwards.

`docker compose down -v` **deletes the volumes**, including the status
message ID in `status-data`. Without it, the next start posts a new status
message (unless `STATUS_MESSAGE_ID` is set). Do not use `-v` on the server.

## Configuration in containers

- All secrets come from `.env` on the host through `env_file`. They are not
  in the image or in build arguments, and `.env` is not in the build context.
- `compose.yaml` overrides three values that differ inside Docker:
  `STATUS_HEARTBEAT_URL` (bot → `http://status:8787/heartbeat`),
  `STATUS_LISTEN_HOST=0.0.0.0` (so the bot container can reach the service),
  and `STATUS_STATE_FILE=/app/data/...`. `environment:` takes precedence over
  `.env`.
- The status port is not published. If Uptime Kuma runs on the host itself,
  uncomment `127.0.0.1:8787:8787` in `compose.yaml`; never publish it on
  `0.0.0.0`. If Uptime Kuma runs in Docker, attach it to the `miyabi_default`
  network and use `http://status:8787/health` instead.

## Version

`config.json → bot.version` is the canonical release version (the release
workflow requires the tag to match it). The bot shows, in order:

1. `BOT_VERSION` from the image (build argument);
2. `dev-<short hash>` when running from a Git checkout (queried once per
   process);
3. `config.json → bot.version`.

The image contains no Git, so without `BOT_VERSION` it shows the config
version and logs one warning at startup.

## Logs

| Where | What | Rotation |
|---|---|---|
| `docker compose logs <service>` | stdout of each process (Loguru + standard logging at INFO, DEBUG with `DEBUG=True`) | json-file driver, 5 × 10 MB per container |
| volume `bot-logs` | `bot.log` (Loguru, DEBUG), `standard.log` (discord.py/aiohttp, DEBUG) | 10 MB; `bot.log` kept 10 days and zipped, `standard.log` 10 backups |
| volume `status-logs` | `status_service.log` (DEBUG) | 10 MB, 10 days, zipped |

Each process writes only its own files, and the two services use separate
volumes, so two processes never rotate the same file. Read file logs with:

```bash
docker compose exec bot sh -c 'tail -n 100 logs/bot.log'
docker compose exec status sh -c 'tail -n 100 logs/status_service.log'
```

## Health and restarts

- Both services use `restart: unless-stopped`: they come back after a crash
  or a host reboot, but not after `docker compose stop`.
- `status` has a healthcheck on `GET /health`. It turns `unhealthy` when the
  monitor loop stalls, the state file cannot be written, or the Discord status
  message fails three times in a row. Docker does not restart unhealthy
  containers by itself; the state is for `docker compose ps` and future deploy
  checks.
- `bot` has no healthcheck on purpose: it has no local endpoint that reflects
  its state, and a check that always passes would be misleading. The bot's
  health is what `status_service` reports from heartbeats.
- Stopping (`docker compose stop`/`down`, or an update that recreates the
  containers):
  - `bot` is stopped with **SIGINT** (`stop_signal` in `compose.yaml`).
    discord.py's `Client.run()` shuts down cleanly only on SIGINT: it closes
    the client, unloads the cogs, and the heartbeat cog sends a final
    `shutting_down` heartbeat, so the status message turns OFFLINE at once.
    Docker's default SIGTERM kills the process instead (exit code 143, no
    final heartbeat); the status then stays ONLINE until
    `STATUS_OFFLINE_AFTER` (90 s) expires. Both cases were reproduced with a
    test harness that replaces only the Discord connection.
  - `status` uses the default SIGTERM, which aiohttp handles itself (saves
    the state file and exits).
  - Each service gets up to 20 s (`stop_grace_period`) before Docker kills it.
  - `docker kill` without `--signal SIGINT` skips the clean shutdown.

## Hardening

Containers run as uid `10001` with a read-only root filesystem (writable:
the volumes and a `/tmp` tmpfs), all Linux capabilities dropped, and
`no-new-privileges`. The code in the image is owned by root and is not
writable by the process.

## Updating the base image

The `FROM` line pins `python:3.11-slim-trixie` by digest. To pick up Debian or
Python patch updates, resolve the current digest, replace it in the
`Dockerfile`, and open a PR so CI rebuilds and smoke-tests the image:

```bash
docker buildx imagetools inspect python:3.11-slim-trixie --format '{{json .Manifest.Digest}}'
```

## Registry (GHCR)

Development images are published to GitHub Container Registry:

```text
ghcr.io/indimops/miyabi-bot
```

The [`docker-publish.yml`](../.github/workflows/docker-publish.yml) workflow
runs on every push to `dev` (including PR merges into `dev`), and on nothing
else: not on pull requests, other branches, or tags. It builds the image with
`BOT_VERSION=dev-<7-character SHA>` and `VCS_REF=<full SHA>`, then runs the
same image checks as the CI `docker` job against that exact image:
`scripts/docker-smoke-test.sh`, `docker compose config`, and the `status`
service started from it (`--no-build --pull never`) in a throwaway compose
project with a dummy secret until its healthcheck is `healthy`. Only then does
it log in with the built-in `GITHUB_TOKEN` (`packages: write`) and push.

| Tag | Meaning |
|---|---|
| `sha-<12-character SHA>` | The image built from that exact `dev` commit. Never moved; use it to pin a deployment. |
| `dev` | The latest published `dev` commit. Moves with every push to `dev`. |

There is no `latest` tag and no release image yet.

Only one publish runs at a time, and a running publish is never cancelled.
While it runs, GitHub keeps just the newest waiting run: if several commits
reach `dev` in quick succession, the intermediate ones are cancelled and get no
`sha-` image. Before moving `dev`, the workflow checks that its commit is still
the head of the `dev` branch; if not (for example, a re-run of an older
commit), it pushes only the `sha-` tag. After pushing, it checks that each tag
in the registry has the digest of the tested image.

> [!IMPORTANT]
> A `dev` image is a development snapshot. The workflow does not run pytest,
> so a published image does not mean the full CI is green (see
> [Known failures](development.md#known-failures)).

Pull an image built from a specific commit:

```bash
docker pull "ghcr.io/indimops/miyabi-bot:sha-$(git rev-parse --short=12 HEAD)"
docker image inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' \
  "ghcr.io/indimops/miyabi-bot:sha-$(git rev-parse --short=12 HEAD)"
```

If the package is private, log in first with a token that has `read:packages`
(`docker login ghcr.io`).

A future deployment uses the registry image instead of building, by setting
`MIYABI_IMAGE` (for example in the shell or a compose `.env` on the server):

```bash
MIYABI_IMAGE=ghcr.io/indimops/miyabi-bot:sha-<12-character SHA> docker compose up -d --no-build
```

Prefer a `sha-` tag (or a digest) over `dev`, so the server runs a known
commit.

Publishing is **not** deployment: the workflow only pushes to GHCR. It does
not connect to the home server and does not start, stop, or update the bot
there.

## Not covered yet

Deploying the image to the home server, and release (version-tagged) images,
are a separate stage.
