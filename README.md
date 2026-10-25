<div align="center">

[![Miyabi Bot banner](assets/miyabi_arts/banner.png)](https://www.reddit.com/r/ZZZ_Official/comments/1hgzmeu/new_wallpapers_acquired/)

# Miyabi Bot

An interactive Discord companion for **Zenless Zone Zero** players.

[![CI](https://github.com/IndiMops/Miyabi-bot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/IndiMops/Miyabi-bot/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![discord.py 2.x](https://img.shields.io/badge/discord.py-2.x-5865F2?logo=discord&logoColor=white)](https://github.com/Rapptz/discord.py)
[![Support server](https://img.shields.io/badge/Discord-support%20server-5865F2?logo=discord&logoColor=white)](https://discord.gg/dvkNAdtdUR)

[Features](#features) •
[Commands](#commands) •
[Getting started](#getting-started) •
[Development](#development) •
[Documentation](#documentation)

</div>

---

Miyabi Bot is a Discord bot written in Python with [discord.py](https://github.com/Rapptz/discord.py).
It provides game information through slash commands with nested select menus,
pagination, and autocomplete. All responses are ephemeral, so they don't clutter
server channels.

> [!NOTE]
> Miyabi Bot is an unofficial community project. It is not affiliated with,
> endorsed by, or sponsored by HoYoverse or Discord.

## Features

- **Agent wiki** — browse agents by attribute, or jump straight to one with
  autocomplete (`/characters agent:Alice`).
- **Interactive navigation** — nested select menus with `Back`, plus button
  pagination for long sections.
- **Built-in help** — `/help` with per-command and per-category pages.
- **Status monitoring** — an optional companion service keeps a live status
  message in a Discord channel and exposes a `/health` endpoint for uptime
  monitors.

### Roadmap

- [ ] Complete agent data for every attribute
- [ ] Multi-language support via Crowdin
- [ ] Mini RPG system

## Commands

| Command | Description |
|---|---|
| `/characters [agent]` | Zenless Zone Zero agent wiki with menu navigation and autocomplete. |
| `/help [command] [category]` | Help for commands and categories. |
| `/info` | Bot version, developer, and useful links. |

Developer-only test commands (`/ping`, `/pagination_test`, `/deep_menu`) are
loaded only when `DEBUG=True`. See [docs/commands.md](docs/commands.md) for
details.

## Getting started

### Prerequisites

- Python **3.11** (the version used by CI)
- A Discord application with a bot user and its token
  ([Developer Portal](https://discord.com/developers/applications))

### Installation

```bash
git clone https://github.com/IndiMops/Miyabi-bot.git
cd Miyabi-bot

python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate

python -m pip install -r requirements.txt
```

### Configuration

Copy the template and fill in at least the bot token:

```bash
cp .env.example .env
```

```dotenv
DISCORD_BOT_TOKEN=<your-bot-token>
DEBUG=False
```

Public settings (colors, assets, links, command IDs) live in
[`config.json`](config.json). The full reference is in
[docs/configuration.md](docs/configuration.md).

> [!WARNING]
> Keep `DEBUG=False` outside local testing: debug mode loads the dev commands,
> which have no owner check.

### Running

Run from the repository root, since logs are written relative to the working
directory:

```bash
python bot.py
```

To also run the optional status service (configured via the `STATUS_*`
variables in `.env`):

```bash
python -m status_service
```

See [docs/status-monitoring.md](docs/status-monitoring.md) for setup.

## Development

Install the dev tools and run the same checks as CI:

```bash
python -m pip install pytest ruff

python -m compileall -q bot.py cogs embeds utils views status_service
python -m ruff check --select E9,F63,F7,F82 .
python -m pytest
```

### Project structure

```text
bot.py            Entry point: client setup, extension loading, command sync
cogs/             Slash commands (every .py file is auto-loaded as an extension)
embeds/           Static embeds and navigation trees
views/            Reusable UI: nested select menus and pagination
utils/            Config, logging, heartbeat, and helpers
status_service/   Standalone status monitoring service
tests/            Unit tests
docs/             Technical documentation
```

How to add a command or a new agent page is described in
[docs/architecture.md](docs/architecture.md).

## Documentation

| Guide | Contents |
|---|---|
| [Getting started](docs/getting-started.md) | Environment setup and the first run. |
| [Configuration](docs/configuration.md) | `.env` variables and `config.json` fields. |
| [Architecture](docs/architecture.md) | Startup lifecycle, layers, and the navigation contract. |
| [Commands](docs/commands.md) | Command reference and current limitations. |
| [Development](docs/development.md) | Checks, CI, logs, and troubleshooting. |
| [Status monitoring](docs/status-monitoring.md) | Heartbeat and the status service. |

## Support

- Questions and bug reports: [GitHub Issues](https://github.com/IndiMops/Miyabi-bot/issues)
- Community: [support server](https://discord.gg/dvkNAdtdUR)

## Legal

- [Terms of Service](docs/terms.md)
- [Privacy Policy](docs/privacy.md)

Zenless Zone Zero and all related names, characters, and images are the
property of their respective owners.

## Acknowledgements

- Banner art: [r/ZZZ_Official](https://www.reddit.com/r/ZZZ_Official/comments/1hgzmeu/new_wallpapers_acquired/)
- Built with [discord.py](https://github.com/Rapptz/discord.py)
