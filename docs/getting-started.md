# Running Miyabi Bot

[← Back to contents](README.md)

## Requirements

- Python **3.11** — the recommended version, since it is what the CI and
  release workflows use;
- Git;
- a Discord Application with a Bot added;
- the token of that bot;
- a test Discord server.

The current local `venv` runs on Python 3.14.6 and passes the tests, but
`discord.py` already shows a deprecation warning for that version. For a
reproducible environment, stick with Python 3.11.

## 1. Creating the environment

Run all commands from the repository root.

### Windows PowerShell

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `py -3.11` is not available, list the installed versions with:

```powershell
py --list
```

### Linux or macOS

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`pytest` and `ruff` are development tools and are not part of
[`requirements.txt`](../requirements.txt). Install them separately to work on
the code:

```powershell
python -m pip install pytest ruff
```

## 2. Creating the Discord Application

In the [Discord Developer Portal](https://discord.com/developers/applications):

1. create an Application;
2. add a Bot to it and get its token;
3. to install the application, add the `applications.commands` and `bot`
   scopes;
4. give the bot the minimum permissions to view channels, send messages, and
   embed links;
5. install the application on the test server.

The current code does not use `members`, `presences`, or `message_content`, so
privileged Gateway Intents are not required for the existing slash commands.

Useful official pages:

- [Discord: Getting Started](https://docs.discord.com/developers/quick-start/getting-started)
- [Discord: Application Commands](https://docs.discord.com/developers/interactions/application-commands)
- [Discord: Gateway Intents](https://docs.discord.com/developers/events/gateway)

## 3. Local `.env`

Create a `.env` file in the repository root:

```dotenv
DEBUG=False
DISCORD_BOT_TOKEN=paste_your_token_here
```

Rules:

- do not put spaces around the variable name;
- never publish the real token;
- if the token ends up in Git or a message, reset it immediately in the
  Discord Developer Portal;
- use `DEBUG=True` only deliberately — it exposes the test commands.

`.env` is already listed in `.gitignore`.

## 4. Running

```powershell
python bot.py
```

Or without activating the environment:

```powershell
.\venv\Scripts\python.exe bot.py
```

On a successful start the bot:

1. reads `.env` and `config.json`;
2. discovers and loads all Python modules in `cogs/`;
3. globally syncs slash commands with Discord;
4. starts the presence status updates;
5. prints `Bot is ready!` to the console.

Global slash commands sometimes take a while to appear in the Discord client.
Stop the process with `Ctrl+C`.

Always run the bot from the repository root: log files are created relative to
the current working directory.

## 5. Quick check before working

```powershell
git status
python -m pytest -q
python -m compileall -q bot.py cogs embeds utils views status_service
python -m ruff check --select E9,F63,F7,F82 .
```

These commands mirror the main CI checks. See the
[development guide](development.md) for details.
