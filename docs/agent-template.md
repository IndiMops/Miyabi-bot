# Agent page template

The agreed structure and content rules for an agent's pages in `/characters`.
It is the specification for writing agent content (plan tasks B5) and for the
future data model (C1). The reference implementation is Alice:
[`embeds/wiki/characters/agents/alice/`](../embeds/wiki/characters/agents/alice/).

Ukrainian strings in quotes («…») are the exact texts users see.

## How an agent is navigated

- Choosing an agent opens its main page: the first page of «Основна інформація».
- The select menu under the embed switches between the agent's **sections**
  and stays visible on every section page.
- Pagination buttons switch the **pages** inside a section.
- Page counts are not the same for every agent. A simple mechanic can be one
  page, a complex one can be split into several. Do not pad an agent to match
  Alice, and do not force Alice's mechanics onto other agents.

## Page conventions

| Part | Rule |
|---|---|
| Title | Create pages with a short page name (`title="Огляд"`). [`section()`](../embeds/wiki/characters/sections.py) turns it into «Основна інформація: Огляд — 1/2»; the number appears only in multi-page sections. Never write page numbers by hand. |
| Tab | `section(key, label, summary, pages)` builds the select option «<summary> — N сторінок» with the real page count and the right plural form. |
| Author | Agent name in Ukrainian, the agent's message icon, and a link to the agent's Fandom page (`decorate()` in the agent's `common.py`). |
| Thumbnail, color | The agent icon and the agent's color, shared through `common.py`. |
| Footer | The project footer (`add_default_footer`). |
| Images | Upload to Cloudinary and use `res.cloudinary.com` links. Never use Discord attachment links (`media.discordapp.net`, `cdn.discordapp.com/attachments`): they are signed and expire. Alice's first pages still use `i.imgur.com`; move them when those pages are revised. |
| Fields | Inline fields for short facts (rank, attribute, …), full-width fields for explanations. |
| Unknown data | Leave the field out instead of writing «Невідомо». |
| Custom emoji | `<:Name:id>` markup of emoji the bot can use. |
| Limits | Title 256, description 4096, 25 fields, field name 256 / value 1024, 6000 characters per embed, select option texts 100. [`tests/test_navigation_tree.py`](../tests/test_navigation_tree.py) checks the whole tree, including page numbers and image links. |

## Sections and pages

### 1. «Основна інформація» (basic info)

**«Огляд»** — the agent's main page.

- 2–4 sentences: who the agent is, their faction, their story or professional
  role, and their combat role. Not a full biography.
- Fields: rank, attribute, specialty, faction, damage type (if it matters),
  combat role, signature W-Engine, release date or version, and how to obtain
  the agent (if relevant).

**«Характеристики»** (stats)

- Stats at max level with explicit conditions, for example «Рівень 60, Core
  Skill F, без W-Engine та Drive Discs».
- HP, ATK, DEF, Impact, CRIT Rate, CRIT DMG, Anomaly Mastery, Anomaly
  Proficiency, PEN Ratio, Energy Regen.
- If sources show different numbers because of Core Skill or other passive
  bonuses, explain why.

### 2. «Бойові механіки» (combat mechanics)

A separate section from skills. Skills answer "what does this button do?";
combat mechanics answer "how does the whole kit work together?".

**«Стиль гри»** — the main role, the main resource, the main damage source, and
a simple numbered rotation that a first-time player can follow.

**One page per unique mechanic** — for each important mechanic: the maximum
resource, how it is gained, what it is spent on, how much it costs, and what
happens at different charge levels. Alice has «Blade Etiquette та Starshine
Waltz» and «Polarized Assault і Disorder»; another agent's pages can be
completely different.

### 3. «Навички» (skills)

One page per standard ZZZ category: Basic Attack, Dodge, Assist, Special
Attack, Chain Attack / Ultimate, Core Skill. A complex category may be split
further.

For each skill:

- the name;
- a short description: what the agent does and what damage it deals;
- the key mechanic or condition;
- when relevant: Energy cost, resource cost, invulnerability, Perfect Dodge,
  extra effects.

Do not copy the in-game text verbatim.

Multipliers: only the key ones at max skill level, so they do not bury the
description. Format:

```text
<Skill> Lv.12:
<Stage> — <multiplier>%
```

Full tables for all 12 levels do not go into the main embed; a separate
multiplier page or submenu may come later.

The Core Skill page separates **Core Passive** and **Additional Ability**.
Always give the Additional Ability's activation condition (for example, «якщо
в загоні є інший Anomaly або Support агент»), summarize the effects, and list
the stat bonuses of Core Skill F (Base ATK, Anomaly Mastery, Impact, CRIT, …).

### 4. «Mindscape Cinema»

Three pages: «M1–M2», «M3–M4», «M5–M6». For each Mindscape:

- «M1 — <Name>»;
- the mechanical effect;
- «Практичний вплив»: one sentence on what it really changes in play, because
  official descriptions are often very technical.

M3 and M5 that only raise skill levels get one line, for example «Підвищує
рівень Basic Attack, Dodge, Assist, Special Attack та Chain Attack на 2».

### 5. «Прокачування» (progression)

Not just a list of materials, but how they are used:

| Page | Content |
|---|---|
| «Рівень агента» | EXP materials and Denny for levels 1 → 60. |
| «Promotion» | Level-cap materials, optionally split by level (Lv.10 … Lv.50). |
| Skills | Materials for all five core skills; optionally the cost of one skill 1 → 12. |
| Core Skill | Higher Dimensional Data, the weekly boss material, and Denny for A → F. |
| «Загальна вартість» | Everything needed to max the agent. One of the most useful pages. |

Pages may be merged: Alice has «Навички та Core Skill» on one page, so her
section has four pages. Write amounts as `<Material> ×N`. Agent leveling
itself costs only EXP materials, no Denny; the signature W-Engine and Drive
Discs are not part of this section.

### 6. «Профіль» (profile)

| Page | Content |
|---|---|
| «Біографія» | Origin, family, education or profession, role in the faction, personality, interests, key story links. 2–4 short paragraphs, no big spoilers. |
| «Особисті дані» | Only known fields: full name, gender, species / Thiren, breed, height, birthday, age, faction, school, profession, family, specialization. |
| «Озвучення» | Voice actors: Chinese, English, Japanese, Korean; mention actor changes. Outfits can go here if there are few (Alice: «Озвучення та костюми»). |
| «Медіа» | Official media (Agent Record, Character Teaser, Character Demo, Official Page, EP) as Discord **link buttons**, not long URLs in the text. For each: official name, type, official link. |

Build the media page as a `LinkedEmbed` (the `links=` argument of `page()` in
the agent's `common.py`): up to five `(label, url)` pairs, shown as link
buttons under the page. Check that every video is on the official channel
before adding it.

## Text style

- Ukrainian text. Official English names of skills, mechanics, materials,
  W-Engines, and so on stay in English unless there is an established Ukrainian
  translation (Blade Etiquette, Starshine Waltz, Polarized Assault, Core
  Passive, Additional Ability, Physical Anomaly, Disorder, W-Engine). Players
  can then find the same mechanic in the game. The explanations around them are
  in Ukrainian.
- Compact and informative: no wiki filler, no long copied paragraphs, no
  unnecessary spoilers.
- Take the information from the wiki, not its structure or volume: rewrite it
  in your own words.

## Sources

Priority:

1. The official Zenless Zone Zero / HoYoverse site.
2. HoYoWiki.
3. Game data and reliable databases.
4. Zenless Zone Zero Fandom Wiki.
5. Honey Hunter.
6. Prydwen, Icy Veins, and other guide sites (to explain mechanics).

Fandom is the base source, but verify the numbers: base stats, multipliers,
materials, Core Passive conditions, Mindscapes, release dates, and voice
actors. Never invent data. If sources disagree, explain why or mark the value
as uncertain.

## Adding a new agent

Content:

1. Study the agent's Fandom page and verify the key numbers in reliable
   sources.
2. Identify the unique combat mechanics and design the page tree.
3. Fill the sections: basic info → play style and mechanics → skills →
   Mindscape M1–M6 → progression materials → profile, voice actors, media.
4. Leave out unnecessary information and mark uncertain data.

Code:

1. Copy `agents/alice/` to `agents/<name>/`. Adjust `common.py` (color, icons,
   Fandom link, author name) and the section modules. Each section module
   defines `SECTION = section(...)`; the package `__init__.py` lists them in
   `SECTIONS` and builds the class with the navigation contract.
2. Export the class from `agents/__init__.py`, add the agent to its attribute
   branch (`<Attribute>Characters_children`) in `menu.py`, and attach its
   sections the way Alice's are attached there. (Plan task C3 replaces this
   manual wiring with a registry.)
3. Add an `AgentRoute` to `routes.py`: the key equals the embed attribute
   name, with Ukrainian and English aliases.
4. Run the checks: `tests/test_navigation_tree.py` covers the new agent
   automatically.
5. Check the pages in Discord.

## Data organization (towards plan task C1)

Content should eventually live apart from the Discord code (plan task C1:
models `AgentData → Section → Page → Field`). Keep multipliers apart from the
skill descriptions (by level, damage, daze), so that a multiplier page can be
added later without rewriting the descriptions. Until then each section module
holds its pages, and `Section` is the seam the model will replace.

## Alice: reference tree and status

| Section | Pages | Status |
|---|---|---|
| «Основна інформація» | «Огляд» · «Характеристики» | Filled. |
| «Бойові механіки» | «Стиль гри» · «Blade Etiquette та Starshine Waltz» · «Polarized Assault і Disorder» | Filled. |
| «Навички» | «Basic Attack» · «Dodge» · «Assist» · «Special Attack» · «Chain Attack / Ultimate» · «Core Skill» | Filled (key multipliers at Lv.12). |
| «Mindscape Cinema» | «M1–M2» · «M3–M4» · «M5–M6» | Filled. |
| «Прокачування» | «Рівень агента» · «Promotion» · «Навички та Core Skill» · «Загальна вартість» | Filled. |
| «Профіль» | «Біографія» · «Особисті дані» · «Озвучення та костюми» · «Медіа» | Filled; media as link buttons. |
