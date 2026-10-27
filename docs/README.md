# Miyabi Bot Technical Documentation

This directory is a short practical reference for quickly recalling, after a
break, how the project is structured, how to run it, and where to change a
given behavior.

The documentation describes the implementation as of **July 24, 2026**. The
code always remains the source of truth.

## Where to start

1. [First run and getting back to work](getting-started.md)
2. [Configuration](configuration.md)
3. [Architecture and extension](architecture.md)
4. [Available Discord commands](commands.md)
5. [Development, checks, and diagnostics](development.md)
6. [Status monitoring](status-monitoring.md)
7. [Docker](docker.md)

The directory also contains the
[Privacy Policy](privacy.md) and [Terms of Service](terms.md).

## The project in a minute

Miyabi Bot is a small Discord bot for **Zenless Zone Zero** communities. It is
written in Python using `discord.py` and currently works as a static
interactive reference:

- [`bot.py`](../bot.py) starts the Discord client, loads modules, and
  syncs slash commands;
- [`cogs/`](../cogs) contains the commands;
- [`embeds/`](../embeds) contains the text and layout of responses;
- [`views/`](../views) implements select menus and pagination;
- [`utils/`](../utils) handles configuration, logging, and helper functions;
- `.env` holds local environment variables and the secret token;
- [`config.json`](../config.json) holds public settings.

The project does not yet have a database, its own HTTP API, persisted user
state, or real loading of wiki data. Command content is stored directly in
Python files with embeds.

## What already works

In normal mode (`DEBUG=False`) the following are loaded:

- `/info`;
- `/help`;
- `/characters` — contains Alice's pages, demo pagination for 35 placeholder
  fire agents, and safe placeholders for the other attributes.

In debug mode the test commands `/ping`, `/pagination_test`, and `/deep_menu`
are loaded as well. They **have no owner check**, so with global sync they are
available to every user of the bot. Keep `DEBUG=False` for normal runs.

Localization and the mini-RPG system planned in the root README are not yet
implemented.

## Getting back to the project quickly

If the existing local `venv` has not been deleted:

```powershell
cd D:\Code\Miyabi-bot
.\venv\Scripts\Activate.ps1
python -m pytest -q
python bot.py
```

Before running, check:

- that `.env` exists in the root;
- that `DISCORD_BOT_TOKEN` is set;
- whether you need the debug commands;
- that there are no important uncommitted changes, via `git status`.

Never add `.env` or the token to Git, documentation, issues, or logs.
