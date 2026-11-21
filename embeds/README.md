# Embeds layout

`embeds/` holds only the Discord presentation: titles, descriptions, fields,
images, and page registries. Menu and pagination callbacks stay in `views/`.

```text
embeds/
├── general.py                # shared helpers (fields, default footer)
├── dev/
│   └── deep_menu.py
├── information/
│   └── help.py
└── wiki/
    └── characters/
        ├── menu.py           # root tree registry of /characters
        ├── routes.py         # stable keys, aliases, and breadcrumbs
        ├── sections.py       # Section: a select tab with its pages
        └── agents/
            └── alice/        # one package per agent
                ├── __init__.py    # AliceEmbed: sections -> navigation contract
                ├── common.py      # color, icons, author, footer
                ├── basic_info.py  # one module per section
                ├── combat.py
                ├── skills.py
                ├── mindscape.py
                ├── progression.py
                └── profile.py
```

## Placement rules

- `information/` — embeds of general information commands.
- `dev/` — demo and diagnostic embeds.
- `wiki/<feature>/` — a separate wiki domain, for example `characters` or a
  future `w_engines`.
- `menu.py` — the root registry of one command's navigation tree.
- `routes.py` — stable keys, aliases, and breadcrumbs for a direct jump.
- `agents/<name>/` — the pages of one agent, one module per section. Each
  module defines a `Section` (tab label, short summary, pages); the tab
  description gets the real page count automatically.
- `views/` — generic behavior of select menus, `Back`, and pagination.

A new agent gets its own package next to `alice/`. Its class is exported from
`agents/__init__.py`, wired into `characters/menu.py`, and gets an
`AgentRoute` in `routes.py`.

## Future split with Pydantic

Once models and external data appear, the recommended boundary is:

```text
models/     # Pydantic schemas: Character, WEngine, Skill, Build
data/       # JSON/YAML or another content source
embeds/     # turning models into discord.Embed
views/      # Discord UI and navigation
cogs/       # slash commands and orchestration
```

Do not keep business data or interaction callbacks directly in embed files.
