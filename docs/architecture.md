# Architecture

[← Back to contents](README.md)

The project is a small monolithic Discord bot. There is no database and no
public API. Next to it runs a separate [`status_service`](status-monitoring.md)
process that receives the bot's heartbeats and updates the status message in
Discord.

## Project map

```text
Miyabi-bot/
├── bot.py                    # entry point and composition root
├── config.json               # public configuration
├── requirements.txt          # runtime dependencies
├── cogs/
│   ├── core/                 # status heartbeat (no commands)
│   ├── information/          # /help and /info
│   ├── wiki/                 # /characters
│   └── dev/                  # test commands
├── embeds/                   # presentation, grouped by domain
│   ├── information/          # embeds for /help
│   ├── dev/                  # demo deep-menu
│   └── wiki/
│       └── characters/
│           ├── menu.py       # root tree registry
│           ├── routes.py     # keys, aliases, and breadcrumbs
│           └── agents/       # one file per character
├── views/
│   ├── nav.py                # nested select menus
│   └── pagination.py         # button pagination
├── utils/
│   ├── config.py             # .env + config.json
│   ├── logger.py             # Loguru and standard logging
│   ├── heartbeat.py          # heartbeat payload and delivery
│   └── misc.py               # JSON, colors, version, fetch commands
├── status_service/           # separate status monitoring process
├── tests/                    # local unit tests
└── docs/                     # documentation
```

`embeds/` is now an explicit hierarchy of Python packages with `__init__.py`
and controlled exports. The `cogs`, `utils`, and `views` folders remain
implicit namespace packages for now.

## Startup lifecycle

1. When `Config` is imported, `.env` and `config.json` are read.
2. When the logger is imported, `logs/` is created and file handlers are
   attached.
3. A `MiyabiBot` instance is created with the configured intents.
4. `bot.run(Config.require_token())` validates the token and connects to
   Discord.
5. `setup_hook()` recursively discovers every `.py` in `cogs/`.
6. With `DEBUG=False`, the loader skips folders listed in
   `disabled_cogs_folder`.
7. Each module is loaded as an extension through its `async setup(bot)`.
8. `tree.sync()` globally syncs all loaded slash commands.
9. The 30-second presence status loop starts.
10. Once ready, the `on_ready` event writes a message to the log.

If any cog raises `ExtensionError`, the loader logs the traceback and re-raises
the error. As a result the whole startup stops — the bot does not keep running
with a partial set of modules.

Every 30 seconds the presence status alternates between:

- `/help | dev-<short Git hash>`;
- `<count> servers`.

If Git is unavailable, `bot.version` from `config.json` is used.

## Responsibility boundaries

| Layer | Responsibility |
|---|---|
| `bot.py` | Creating the client, intents, loading extensions, sync, and presence. |
| `cogs/` | Incoming Discord commands and response orchestration. |
| `embeds/` | Static Discord embeds and the tree of available content. |
| `views/` | Reusable Discord UI components. |
| `utils/` | Configuration, logging, and small shared helpers. |

All wiki content is currently hardcoded in `embeds/`. The `requests`
dependency is installed, but the current Python code does not use it.

## How to add a slash command

Create a file, for example `cogs/information/example.py`:

```python
import discord
from discord import app_commands
from discord.ext import commands


class ExampleCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="example",
        description="Short description for Discord.",
    )
    async def example(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Example response",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCommand(bot))
```

After a restart the loader finds the file automatically. Do not put a plain
helper inside `cogs/` as a separate `.py` file unless it is a valid Discord
extension: the loader will try to load every file whose name does not start
with `__`.

After the first sync, add the ID to `config.json` only if the command needs to
be mentioned in an embed as `</example:ID>`. The entry is not required for the
registration itself.

## Navigation embed contract

[`NavView`](../views/nav.py) expects a class with three class methods:

| Method | Result |
|---|---|
| `get_embed(key)` | A single `discord.Embed` for the current node. |
| `get_children(key)` | A list of child items, or an empty list. |
| `get_pages(key)` | A list of embeds for pagination, or `None`. |

For the `Main` key the class usually has:

```python
Main = discord.Embed(title="Main")
Main_children = [
    {"label": "Details", "value": "Details", "emoji": "ℹ️"},
]

Details = discord.Embed(title="Details")
Details_children = []
```

The `value` must exactly match the name of the corresponding class attribute.
Children may also be strings or tuples, but dictionaries with explicit `label`
and `value` are easier to read and maintain.

Navigation keeps its history in the view's memory and adds `Back` after the
first level. If a node has `<Key>_pages`, it switches to
[`PaginationView`](../views/pagination.py).

Both views time out after 120 seconds by default. After the timeout old
components may stay visible in Discord but no longer handle clicks. Old views
are also not restored after a bot restart.

For nested nodes `NavSelect` shows at most 24 children and adds `Back` as the
25th option. If there are more children, `<Key>_pages` must contain the
matching number of embeds. Pagination switches both the embed and the slice of
select options at once, and the page number is preserved when navigating into
an item and returning via `Back`.

## Technical notes

- All current commands are slash commands. The `"."` prefix provides no
  user-facing functionality yet.
- The `message_content` intent is not enabled.
- A global `tree.sync()` runs on every startup.
- `AllowedMentions` forbids mass `@everyone` and role mentions but allows user
  mentions.
- Embed objects are created at class level and reused. Do not mutate a
  retrieved embed for a single user without making a copy.
- The project has no persistent storage: menu history exists only inside a
  specific active view.
