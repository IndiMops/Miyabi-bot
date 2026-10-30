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

In CI the `docker` job builds the image once, smoke-tests it, then starts
`status` from that same image (`docker compose up --no-build --pull never
--wait`) in a throwaway compose project (`miyabi-ci`, dummy secret), and
removes that project's containers and volumes afterwards.

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

Images are published to GitHub Container Registry, all in one package:

```text
ghcr.io/indimops/miyabi-bot
```

The [`docker-publish.yml`](../.github/workflows/docker-publish.yml) workflow
("CI and Docker publish") runs on every push to `dev` or `main` (including PR
merges), and on nothing else: not on pull requests, other branches, or tags.
It first runs the full CI (`ci.yml`: dependencies, lint, pytest, Docker
checks); the publish job starts only if every CI job succeeded.

The image is built **once**, in the CI `docker` job, with
`BOT_VERSION=<config.json bot.version>+<7-character SHA>` and
`VCS_REF=<full SHA>`. That job runs `scripts/docker-smoke-test.sh`, `docker
compose config`, and the `status` service started from the same image until
its healthcheck is `healthy`. Only after these checks pass, and only when
called by the publish workflow, it saves the image with `docker save` and
uploads it as an artifact of the run (`miyabi-image-<run ID>-<commit SHA>`,
kept for 1 day). Pull request runs export nothing.

The publish job does not build. It downloads that artifact from the same run,
checks the archive's SHA-256, runs `docker load`, and checks that the loaded
image ID, the `org.opencontainers.image.revision` label and the version label
match what CI tested. Only then does it log in with the built-in
`GITHUB_TOKEN` (`packages: write`, publish job only) and push. After pushing,
it checks that the registry image is the tested image (same config digest, or
same manifest digest with Docker's containerd image store).

| Tag | Set by | Meaning |
|---|---|---|
| `sha-<12-character SHA>` | push to `dev` or `main` | The image of that exact commit. Never moved or overwritten; use it to pin a deployment. |
| `beta`, `dev` | push to `dev` | Development environment: the latest published `dev` commit. Both always point to the same image. |
| `stable`, `latest` | push to `main` | Stable environment: the latest published `main` commit. Both always point to the same image. |
| `vX.Y.Z` | `vX.Y.Z` Git tag ([release workflow](development.md#releases)) | Official release: the `sha-` image of the tagged `main` commit. Never moved. |

A `dev` run never touches `stable`/`latest`, and a `main` run never touches
`beta`/`dev`. Moving tags are re-pointed by digest (`docker buildx imagetools
create`), so the old image stays available under its `sha-` tag; nothing is
deleted. If a `sha-` tag already exists, it is never overwritten: it is reused
only when it is exactly the image this run tested (for example, after
**Re-run failed jobs** for the publish job). Otherwise the publish fails. A
full re-run, or the same commit pushed to both `dev` and `main` (a
fast-forward merge), builds a new image that is not byte-identical, so its
publish fails with a clear error; use merge commits for `dev` → `main`.

Only one publish per branch runs at a time, and a running publish is never
cancelled. While it runs, GitHub keeps just the newest waiting publish for that
branch: if several commits reach a branch in quick succession, the
intermediate ones are cancelled and get no `sha-` image. Before moving the
channel tags, the workflow checks that its commit is still the head of the
branch; if not (for example, a re-run of an older commit), it pushes only the
`sha-` tag. After pushing, it checks that each tag in the registry has the
digest of the source image.

The [release workflow](development.md#releases) never builds an image. For a
`vX.Y.Z` tag it finds `sha-<12-character SHA>` of the tagged commit (waiting
up to 20 minutes for a running publish), adds `vX.Y.Z` to that manifest by
digest, and checks that both tags have the same digest. If the `sha-` image is
missing, or `vX.Y.Z` already points to a different image, the release fails.

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

Prefer a `sha-` or `vX.Y.Z` tag (or a digest) over a moving tag (`beta`,
`dev`, `stable`, `latest`), so the server runs a known commit.

Publishing is **not** deployment: the workflow only pushes to GHCR. It does
not connect to the home server and does not start, stop, or update the bot
there.

## Not covered yet

Deploying the image to the home server is a separate stage.
