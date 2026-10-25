# Configuration

[← Back to contents](README.md)

Configuration consists of two parts:

- `.env` — secrets and the local run mode;
- [`config.json`](../config.json) — public bot and embed settings.

Both files are read when modules are imported. Restart the bot process after
any change.

## Environment variables

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `DISCORD_BOT_TOKEN` | yes | none | Secret Discord Bot token. Without it `Config.require_token()` aborts startup with an error. |
| `DEBUG` | no | `False` | Console log level and control over loading disabled cog folders. |
| `STATUS_HEARTBEAT_URL`, `STATUS_HEARTBEAT_SECRET`, and other `STATUS_*` | no | disabled | Heartbeat to the status service. See [Status monitoring](status-monitoring.md). |

A template without secrets is [`.env.example`](../.env.example).

`DEBUG` is true only when the value equals `true`, case-insensitively. The
values `1`, `yes`, or `on` mean `False` in the current implementation.

With `DEBUG=False`, the folders in `bot.disabled_cogs_folder` are skipped.
With `DEBUG=True` this list is ignored, so dev modules are loaded too.

> At the time the documentation was written, the local environment was set to
> debug mode. Before a normal or public run, explicitly set `DEBUG=False`,
> because dev commands are not restricted to the bot owner.

## `config.json` fields

### `bot`

| Field | Format | Where it is used |
|---|---|---|
| `name` | string | Name in `/info`. |
| `prefix` | string | Passed to `commands.Bot`. There are no prefix commands right now, so the field is effectively unused. |
| `version` | string | Fallback version for the presence status if the Git hash cannot be obtained; also shown in `/info`. |
| `last_update` | Unix timestamp in seconds | Relative update time in `/info`. |
| `color.default` | `#RRGGBB` | Main embed color. |
| `color.error` | `#RRGGBB` | Error color; barely used right now. |
| `color.info` | `#RRGGBB` | Info color; barely used right now. |
| `color.warn` | `#RRGGBB` | Warning embeds, e.g. "command not found". |
| `assets.avatar` | URL | Thumbnail/footer icon in responses. |
| `assets.banner` | URL | Banner in `/info`. |
| `assets.fallback_avatar` | local path | Reserved, but the current code does not apply a fallback. |
| `assets.fallback_banner` | local path | Reserved, but the current code does not apply a fallback. |
| `urls.support_server` | URL | Support server link in `/info`. |
| `urls.github` | URL | Repository link in `/info`. |
| `disabled_cogs_folder` | list of strings | Names of folders inside `cogs/` that are skipped with `DEBUG=False`. |
| `commands` | list of `{name, id}` | Discord command IDs for clickable mentions like `</help:ID>`. |

### `dev`

| Field | Format | Where it is used |
|---|---|---|
| `name` | string | Developer name in embeds. |
| `id` | numeric string | Converted to `int` and passed as the bot's `owner_id`. |
| `emoji` | Discord emoji markup | Developer icon in `/info`. |
| `website` | URL | Link in the help footer. |

`owner_id` only tells `discord.py` who the owner is. It does **not** restrict
commands automatically: a command needs its own owner/permission check for
that.

## Command IDs

The `bot.commands` array does not register commands. Registration is done by
`bot.tree.sync()`; the IDs in the JSON are only needed for nice clickable
mentions inside embeds.

If you run the code with another Discord Application or re-create the
commands:

1. Discord will assign new IDs;
2. slash commands will keep working;
3. old mentions in `/help` and other embeds may be wrong;
4. the values in `config.json` must be updated manually.

The current code does not write the sync result back to the JSON.

## Important properties

- `config.json` must stay valid UTF-8 JSON without comments.
- Colors must be valid HEX strings.
- `dev.id` must contain digits only.
- A name in `disabled_cogs_folder` is compared against folder names in the
  module path, not against an individual Python file name.
- Secrets must not be moved from `.env` into `config.json`.
- If the JSON cannot be read, the helper returns an empty object, but the next
  access such as `Config.PUBLIC.bot` will still break the import.

## Why run from the root

[`utils/config.py`](../utils/config.py) looks up `.env` and `config.json`
relative to the project root. Meanwhile [`utils/logger.py`](../utils/logger.py)
creates `logs/` and opens log files relative to the current working
directory. Running from the root guarantees a predictable log location.
