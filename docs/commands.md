# Discord Commands

[← Back to contents](README.md)

All existing commands are global application commands. There are no prefix
commands in the code, although the `"."` prefix is kept in the configuration.

## User commands

These modules are loaded with `DEBUG=False`.

| Command | Parameters | Response | Current state |
|---|---|---|---|
| `/info` | none | Ephemeral embed | Shows the name, version, update time, developer, support server, and GitHub. |
| `/help` | `command?`, `category?` | Ephemeral embed/menu | Main help: overview, the `information` and `wiki` categories, detailed pages for `help`, `info`, and `characters`. |
| `/characters` | `agent?` | Ephemeral embed/menu | Interactive reference with a menu or a direct jump to an agent via autocomplete. |

### `/help`

Usage:

```text
/help
/help command:info
/help category:information
/help category:wiki
```

- without parameters it shows a category select menu;
- `command` tries to open the embed of a specific command;
- `category` opens the category embed;
- if both parameters are given, `command` takes precedence.

Autocomplete for `command` and `category` is built from the help content
itself, without requests to Discord, so it only suggests commands and
categories that have a help page.

All help content lives in one place, `embeds/information/help.py`:
`COMMAND_DOCS` (description, usage, examples per command) and
`HELP_CATEGORIES` (which commands belong to which category). Usage and example
texts use `{name}` placeholders, which are replaced with clickable command
mentions when the embed is built. To document a new command, add a
`CommandDoc` and put its name into a category.

### `/characters`

Current tree:

```text
Main
├── Physical agents
│   └── Alice → Overview / Skills / Build
├── Fire agents
│   └── 35 test agents → pages of 24 + 11
├── Ice agents        # safe placeholder page
├── Electric agents   # safe placeholder page
└── Ether agents      # safe placeholder page
```

On nested levels one of the 25 available select options is reserved for
`Back`, so a single page holds at most 24 characters. The pagination buttons
switch the embed and the set of options at the same time. After viewing a
character, `Back` returns the user to the same page of the list.

The 35 fire agents are only technical placeholders demonstrating the
mechanism. Without a parameter the command opens the main menu:

```text
/characters
```

The optional `agent` parameter supports autocomplete, internal keys, and
alternative names:

```text
/characters agent:Аліса Таймфілд
/characters agent:Alice
/characters agent:FireAgent30
```

A direct jump restores the full route `Main → category → agent`, so the `Back`
option returns first to the category and then to the main menu. The registry
of keys, aliases, and routes lives in `embeds/wiki/characters/routes.py`.

## Dev commands

The `cogs/dev` folder is listed in `disabled_cogs_folder`, so these commands
are skipped only with `DEBUG=False`. With `DEBUG=True` they are synced
globally too.

| Command | Response | Purpose |
|---|---|---|
| `/ping` | Public | Shows gateway latency in milliseconds. |
| `/pagination_test` | Ephemeral | Demonstrates pagination over 10 embeds. |
| `/deep_menu` | Ephemeral | Demonstrates a nested menu and navigation to five pages. |

Dev commands have no `is_owner`, permission checks, or cooldown. The
`owner_id` in the bot constructor does not protect them automatically. So if
they are loaded, any user who can see the bot can invoke them.

## General UI behavior

- An ephemeral response is visible only to the user who invoked the command.
- Select menus and pagination time out after 600 seconds by default (the
  `bot.nav_menu_timeout` value in `config.json`).
- Pagination supports first, previous, next, and last page.
- The disabled middle button shows the current `N/M` value.
- After the timeout (counted from the last click) the select menu and buttons
  become disabled. If the interaction token has expired (15 minutes), they may
  remain on screen, but clicks are no longer handled.

## Current limitations

- The ice, electric, and ether branches have no characters yet.
- The fire agents are demo placeholders, not game data.
- `/help` does not describe the dev commands.
- Some images use signed Discord attachment URLs, which can expire.
- Custom emoji depend on the availability of specific Discord emoji.
- Alice currently has only a short introductory embed without stats, skills,
  or build information.
- No command has a rate limit, cooldown, or role-based restrictions.
