# Development and Diagnostics

[← Back to contents](README.md)

## Main checks

Install exactly the versions CI uses (pip verifies every package hash):

```powershell
python -m pip install --require-hashes -r requirements.lock -r requirements-dev.lock
```

Run the checks that match the current CI:

```powershell
python -m pip check
python -m compileall -q bot.py cogs embeds utils views status_service
python -m ruff check --select E9,F63,F7,F82 .
python -m pytest
```

CI and the lock files target Python 3.11, the supported version. A newer local
interpreter usually works, but a result there does not prove 3.11
compatibility; CI is the reference.

## Dependencies

| File | Edited by | Content |
|---|---|---|
| `requirements.txt` | hand | Direct runtime dependencies with version ranges. |
| `requirements.lock` | generated | Every runtime package (including transitive ones) pinned to an exact version with hashes. |
| `requirements-dev.txt` | hand | Dev/CI tools pinned to exact versions: `pytest`, `ruff`, and `uv`. |
| `requirements-dev.lock` | generated | Dev tools and their dependencies with hashes, constrained to the versions in `requirements.lock`. |

Packages are always installed with **pip**. [`uv`](https://docs.astral.sh/uv/)
is used only to generate the lock files, because it can resolve for
Python 3.11 and for both Linux and Windows (`--universal`) from any machine.
Platform- or version-specific packages (`colorama`, `win32-setctime`,
`audioop-lts`, `typing-extensions`) get environment markers, so one lock file
serves CI, a future Docker image, and local Windows development.

Regenerate the lock files after changing `requirements.txt` or
`requirements-dev.txt` (run from the repository root, with the dev lock
installed):

```powershell
python -m uv pip compile requirements.txt --universal --python-version 3.11 --generate-hashes -o requirements.lock
python -m uv pip compile requirements-dev.txt --constraint requirements.lock --universal --python-version 3.11 --generate-hashes -o requirements-dev.lock
```

uv keeps the versions already pinned in the existing lock file and changes only
what the new requirements need. To deliberately update packages:

```powershell
# one package
python -m uv pip compile requirements.txt --universal --python-version 3.11 --generate-hashes -o requirements.lock --upgrade-package aiohttp
# everything (review the diff carefully)
python -m uv pip compile requirements.txt --universal --python-version 3.11 --generate-hashes -o requirements.lock --upgrade
```

Always regenerate `requirements-dev.lock` after `requirements.lock`, then run
the checks above and commit the `.txt` and `.lock` files together. CI fails
the `Dependencies` job if a lock file does not match its requirements file.

A full `ruff check .` is much stricter than CI and currently reports many style
and modernization issues. Do not auto-fix the whole project together with a
small functional change: it will produce a large unrelated diff.

## What the tests cover

| File | What it checks |
|---|---|
| [`tests/test_core.py`](../tests/test_core.py) | Disabled-folder extension filtering, the missing-token error, color/JSON helpers, `PaginationView` edge cases. |
| [`tests/test_character_routes.py`](../tests/test_character_routes.py) | Agent lookup by key and aliases, case/whitespace normalization, full `Back` history, Fire routes matching real embed keys, autocomplete ranking and the 25-result limit, the `agent` parameter with its autocomplete callback, Alice's paginated sections and tabs. |
| [`tests/test_status_heartbeat.py`](../tests/test_status_heartbeat.py) | Bot-side heartbeat payload, reporter settings, delivery with retry/backoff, env float parsing. |
| [`tests/test_version_and_logging.py`](../tests/test_version_and_logging.py) | Version order (`BOT_VERSION` → Git → `config.json`), Git queried once, a real process without Git, `standard.log` rotation. |
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

Branch flow: task branch → PR into `dev` → PR from `dev` into `main`.

The [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) workflow runs:

- on a push to any branch (tag pushes are handled by the release workflow);
- on pull requests into `main` and `dev`;
- manually: **Actions → CI → Run workflow**, then pick a branch;
- from the release workflow (`workflow_call`).

It has three independent jobs on Ubuntu with Python 3.11. Each one shows up as
a separate check on a PR:

| Job | Steps |
|---|---|
| `Dependencies (install, consistency, lock files)` | hash-checked install of both lock files, `pip check`, lock files up to date |
| `Lint (syntax + Ruff)` | `compileall`, critical Ruff subset (`E9,F63,F7,F82`) |
| `Tests (pytest, Python 3.11)` | `pytest -ra` without `.env` or any secret |

The workflow token is read-only (`contents: read`), checkout does not keep
credentials, and all actions are pinned to full commit SHAs with the version
in a comment. A newer PR run cancels the previous run of the same PR; pushes
are never cancelled.

The tests need no Discord token, no network beyond `127.0.0.1`, and no
database. Without `.env`, `Config` falls back to its defaults.

### Known failures

`tests/test_character_routes.py` has two failing tests:
`test_alice_has_expected_paginated_sections` and
`test_alice_opens_basic_info_and_keeps_tabs_in_sections`. They expect the
planned Alice layout (three "Combat mechanics" pages, page titles without a
subtitle), while `embeds/wiki/characters/agents/alice.py` currently has one
combat page titled "… — 1/3". This is an unfinished content issue that is
tracked separately from CI, so the `Tests` job stays red until it is resolved.
Do not change these tests just to turn CI green.

## Releases

The [`.github/workflows/release.yml`](../.github/workflows/release.yml)
workflow runs when a `v*.*.*` tag is pushed:

1. `Verify tag`: the tag must equal `v` + `config.json → bot.version`, and the
   tagged commit must be on `main`;
2. `CI checks`: the full CI workflow above;
3. `Create draft GitHub Release`: only if both pass, using the `gh` CLI with
   generated notes. Only this job can write to the repository
   (`contents: write`).

Publishing the draft stays a manual step on GitHub.

Existing tags (`v0.1.0`, `v0.1.1`) are not changed or re-checked. They
predate this check, and `config.json` still says `0.0.1`. For the next
release:

1. In a task branch, set `bot.version` (for example to `0.2.0`) and
   `bot.last_update`; PR into `dev`.
2. PR `dev` into `main` once CI is green, and merge.
3. Tag the merge commit on `main`, then push the tag:

   ```powershell
   git switch main
   git pull
   git tag -a v0.2.0 -m "v0.2.0"
   git push origin v0.2.0
   ```

4. Review the draft release on GitHub and publish it.

If the tag and `bot.version` differ, the workflow stops with an error that
names both values. Delete the unpublished tag (`git push --delete origin
vX.Y.Z` and `git tag -d vX.Y.Z`), fix the version through a PR, and tag
again.

## Logs

| Location | Level | Behavior |
|---|---|---|
| Loguru console | `INFO` or `DEBUG` | `DEBUG` is enabled via `.env`. |
| `logs/bot.log` | `DEBUG` | Rotation at 10 MB, retention 10 days, old logs compressed to ZIP. |
| `logs/standard.log` | `DEBUG` | Standard Python logging (discord.py, aiohttp), rotation at 10 MB, 10 backups. |
| `logs/status_service.log` | `DEBUG` | Written only by `status_service`; rotation at 10 MB, retention 10 days. |

The `logs/` directory is ignored by Git. In Docker, see
[Docker → Logs](docker.md#logs).

Known issue (Windows, local only): log paths are relative to the working
directory, and importing `utils.logger` in tests opens the same
`logs/bot.log` and `logs/standard.log` as a bot started from the repository
root. If both run at once and a file reaches 10 MB, Windows refuses to rename
the open file: rotation fails and `--- Logging error ---` messages appear on
stderr while both processes run; records written during failed rotation
attempts may be missing from the file. The processes keep running. Docker and
CI are not affected (one process per container and per runner). Until this is
fixed separately, stop the local bot before running the tests.

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
6. Resolve the two known Alice test failures (see [Known failures](#known-failures)).
7. Add tests for `NavView`, help callbacks, and all character branches.
8. Replace temporary Discord attachment URLs with stable assets.
9. Define a deployment process and a version check before release.
