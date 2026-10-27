# One image for both processes: the bot (default command) and status_service
# (command overridden in compose.yaml). Python 3.11 matches CI.
# The digest pins the multi-arch base image; update it deliberately
# (see docs/docker.md → "Updating the base image").
FROM python:3.11-slim-trixie@sha256:b7a9e5f6a93d6d4a31f129bbd4bdee69efccb6ded0fb230d78aafaf37af98377

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first, so code changes reuse this layer. Hash-checked, wheels
# only: the image needs no compiler and installs exactly requirements.lock.
COPY requirements.lock ./
RUN python -m pip install --require-hashes --only-binary=:all: -r requirements.lock

# Unprivileged runtime user. Only logs/ and data/ are writable for it;
# the code stays owned by root.
RUN groupadd --system --gid 10001 miyabi \
    && useradd --system --uid 10001 --gid miyabi --no-create-home \
        --home-dir /nonexistent --shell /usr/sbin/nologin miyabi \
    && mkdir -p /app/logs /app/data \
    && chown miyabi:miyabi /app/logs /app/data

# Application code (explicit allowlist; .env and other secrets are never copied).
COPY bot.py config.json ./
COPY cogs ./cogs
COPY embeds ./embeds
COPY utils ./utils
COPY views ./views
COPY status_service ./status_service

# Build metadata. The image has no Git, so BOT_VERSION is what the bot shows;
# when empty, utils.misc.get_version() falls back to config.json → bot.version.
ARG BOT_VERSION=""
ARG VCS_REF=""
ENV BOT_VERSION=${BOT_VERSION}
LABEL org.opencontainers.image.title="Miyabi Bot" \
      org.opencontainers.image.source="https://github.com/IndiMops/Miyabi-bot" \
      org.opencontainers.image.version="${BOT_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

# Numeric IDs, so runtimes can verify the user is non-root (uid 10001 = miyabi).
USER 10001:10001

CMD ["python", "bot.py"]
