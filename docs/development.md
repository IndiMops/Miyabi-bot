# Development and Diagnostics

[← Back to contents](README.md)

## Main checks

Install the dev tools:

```powershell
python -m pip install pytest ruff
```

Run the checks that match the current CI:

```powershell
python -m compileall -q bot.py cogs embeds utils views status_service
python -m ruff check --select E9,F63,F7,F82 .
python -m pytest
```

The local environment runs on Python 3.14.6, but CI uses Python 3.11.

A full `ruff check .` is much stricter than CI and currently reports many style
and modernization issues. Do not auto-fix the whole project together with a
small functional change: it will produce a large unrelated diff.

## What the tests cover

| File | What it checks |
|---|---|
| [`tests/test_core.py`](../tests/test_core.py) | Disabled-folder extension filtering, the missing-token error, color/JSON helpers, `PaginationView` edge cases. |
| [`tests/test_character_routes.py`](../tests/test_character_routes.py) | Agent lookup by key and aliases, case/whitespace normalization, full `Back` history, Fire routes matching real embed keys, autocomplete ranking and the 25-result limit, the `agent` parameter with its autocomplete callback, Alice's paginated sections and tabs. |
| [`tests/test_status_heartbeat.py`](../tests/test_status_heartbeat.py) | Bot-side heartbeat payload, reporter settings, delivery with retry/backoff, env float parsing. |
| [`tests/test_status_service.py`](../tests/test_status_service.py) | State evaluation, payload validation, settings, the state store, the webhook publisher, the status embed, the monitor loop, and the HTTP endpoints. |

Not covered yet:

- the real connection to Discord;
- global command sync;
- slash command callbacks;
- `NavView` beyond the Alice navigation level, and the remaining branches of
  `/characters`;
- the structure of `config.json`;
- validity of external URLs and custom emoji;
- logging behavior.

## CI

The [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) workflow:

- runs on pushes to `main` and `dev`;
- runs on pull requests to `main` and `dev`;
- uses Ubuntu and Python 3.11;
- installs the runtime requirements, `pytest`, and `ruff`;
- runs compileall, the critical Ruff subset, and pytest.

`pytest` and `ruff` are not pinned in a separate dev requirements or lock
file, so CI installs their latest versions.

Release workflow:

- runs for `v*.*.*` tags;
- uses Python 3.11;
- runs pytest;
- creates a draft GitHub Release with automatic release notes.

It does not run compileall/Ruff and does not verify that the tag matches
`config.json → bot.version`.

## Logs

| Location | Level | Behavior |
|---|---|---|
| Loguru console | `INFO` or `DEBUG` | `DEBUG` is enabled via `.env`. |
| `logs/bot.log` | `DEBUG` | Rotation at 10 MB, retention 10 days, old logs compressed to ZIP. |
| `logs/standard.log` | `DEBUG` | Standard Python logging, no rotation. |

The `logs/` directory is ignored by Git.

For initial diagnostics, look in `logs/bot.log` for:

- `Loaded extension: ...`;
- `Skipped disabled extension: ...`;
- `Failed to load extension: ...`;
- `Bot is ready!`;
- the traceback right before the process exits.

## Common problems

### `DISCORD_BOT_TOKEN is not set`

Cause: there is no `.env`, the variable is misnamed, or the token did not reach
the process environment.

Check that the variable **name** is present without printing its value to the
terminal or chat. Restart the bot after fixing it.

### Slash commands are not visible

Check:

1. that the Application is installed on the server with the
   `applications.commands` scope;
2. that all extensions loaded without errors;
3. that startup reached `Bot is ready!`;
4. that you are not looking for a dev command with `DEBUG=False`;
5. that enough time has passed for Discord to update global commands.

### Dev commands are unexpectedly available to everyone

Set in `.env`:

```dotenv
DEBUG=False
```

Then restart the bot so it re-syncs the tree without `cogs/dev`.

### `Failed to load extension`

Check the traceback. Common causes:

- a syntax or import error;
- the cog file is missing `async setup(bot)`;
- a wrong class attribute name in the embed tree;
- an invalid `config.json`;
- a helper file was accidentally placed in `cogs/` and the loader treated it as
  an extension.

### The menu responds with `interaction failed`

For a large list, check that the number of `<Key>_pages` matches the number of
24-item slices of `<Key>_children`. For example, 35 children require two embed
pages: 24 and 11.

Other possible causes:

- an expired image URL;
- an unavailable custom emoji;
- an empty or invalid embed field;
- a select `value` that does not match an embed attribute name;
- the view has already reached the timeout set in `config.json` (currently
  600 seconds).

### Logs were created outside the repository

The bot was started from a different working directory. Go to the repository
root and run `python bot.py` again.

## Safe change cycle

```text
1. Check git status.
2. Change one cog/embed/view.
3. Run compileall, the Ruff subset, and pytest.
4. Run the bot on a test server.
5. Check the normal and the error path of the command.
6. Review git diff and do not add .env or logs.
```

## Useful backlog for the next return

1. Replace the 35 fire placeholders with real game data.
2. Fill in the ice, electric, and ether branches.
3. Protect dev commands with owner/permission checks regardless of `DEBUG`.
4. Make `/help` the single source of command metadata.
5. Fetch command IDs automatically instead of a manual JSON list.
6. Pin dev dependencies (`pytest`, `ruff`) in a separate requirements file.
7. Add tests for `NavView`, help callbacks, and all character branches.
8. Replace temporary Discord attachment URLs with stable assets.
9. Define a deployment process and a version check before release.
