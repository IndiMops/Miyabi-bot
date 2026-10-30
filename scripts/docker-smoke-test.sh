#!/usr/bin/env bash
# Smoke-test a built Miyabi image without secrets or network access to Discord.
# Usage: bash scripts/docker-smoke-test.sh <image> <expected BOT_VERSION>
set -euo pipefail
# Git Bash on Windows rewrites POSIX paths such as /app/logs in arguments;
# Docker needs them as they are. No effect on Linux.
export MSYS_NO_PATHCONV=1

image="${1:?usage: docker-smoke-test.sh <image> <expected-version>}"
expected_version="${2:?usage: docker-smoke-test.sh <image> <expected-version>}"
status_container="miyabi-smoke-status-$$"

cleanup() {
  docker rm --force --volumes "$status_container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

step() { echo "::group::$1"; }
end_step() { echo "::endgroup::"; }

step "Runs as an unprivileged user"
uid="$(docker run --rm --network none --entrypoint id "$image" -u)"
echo "uid=$uid"
[ "$uid" != "0" ] || { echo "::error::Image runs as root"; exit 1; }
end_step

step "Contains the application files and no local or secret files"
# -i is required: without it docker does not pass the script on stdin and
# python exits 0 without checking anything.
docker run --rm -i --network none "$image" python - <<'EOF'
import shutil
import sys
from pathlib import Path

app = Path("/app")
required = ["bot.py", "config.json", "cogs", "embeds", "utils", "views", "status_service"]
forbidden = [".env", ".git", "venv", "tests", "data/status_service_state.json", "requirements-dev.lock"]
missing = [name for name in required if not (app / name).exists()]
present = [name for name in forbidden if (app / name).exists()]
if missing or present:
    sys.exit(f"missing: {missing}; must not be in the image: {present}")
if shutil.which("git"):
    sys.exit("git must not be installed in the runtime image")
print("files OK")
EOF
end_step

step "Installed dependencies are consistent"
docker run --rm --network none "$image" python -m pip check
end_step

step "Bot and status_service modules import (read-only root filesystem)"
docker run --rm --network none --read-only --tmpfs /tmp -v /app/logs "$image" \
  python -c "import bot, status_service.app, status_service.__main__; print('imports OK')"
end_step

step "Version comes from BOT_VERSION without Git"
version="$(docker run --rm --network none --read-only --tmpfs /tmp -v /app/logs "$image" \
  python -c "from utils.misc import get_version; from utils.config import Config; print(get_version(Config.PUBLIC.bot.version))" | tail -n 1)"
echo "version=$version"
[ "$version" = "$expected_version" ] || { echo "::error::Expected version $expected_version, got $version"; exit 1; }
end_step

step "Bot entry point stops with a clear error when DISCORD_BOT_TOKEN is missing"
set +e
output="$(docker run --rm --network none --read-only --tmpfs /tmp -v /app/logs "$image" 2>&1)"
code=$?
set -e
echo "$output" | tail -n 5
[ "$code" -ne 0 ] || { echo "::error::Bot started without a token"; exit 1; }
echo "$output" | grep -q "DISCORD_BOT_TOKEN is not set" || { echo "::error::Missing token error not found"; exit 1; }
end_step

step "status_service starts and its healthcheck command passes"
# Throwaway value generated for this run only; it is not a real secret.
dummy_secret="$(head -c 24 /dev/urandom | base64 | tr -d '+/=')"
docker run --detach --name "$status_container" --read-only --tmpfs /tmp \
  -v /app/logs -v /app/data \
  -e STATUS_HEARTBEAT_SECRET="$dummy_secret" \
  -e STATUS_LISTEN_HOST=0.0.0.0 \
  "$image" python -m status_service >/dev/null
healthy=0
for _ in $(seq 1 30); do
  if docker exec "$status_container" python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/health', timeout=4)" 2>/dev/null; then
    healthy=1
    break
  fi
  sleep 1
done
docker logs "$status_container" 2>&1 | tail -n 10
[ "$healthy" = 1 ] || { echo "::error::status_service /health did not return 200"; exit 1; }
docker exec "$status_container" test -s /app/logs/status_service.log \
  || { echo "::error::status_service could not write its log file"; exit 1; }
end_step

echo "Docker smoke test passed for $image"
