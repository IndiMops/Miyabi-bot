# Структура embeds

`embeds/` містить лише Discord-представлення: заголовки, описи, поля,
зображення та реєстри сторінок. Callback-логіка меню й пагінації повинна
залишатися у `views/`.

```text
embeds/
├── dev/
│   └── deep_menu.py
├── information/
│   └── help.py
└── wiki/
    └── characters/
        ├── menu.py
        ├── routes.py
        └── agents/
            └── alice.py
```

## Правила розміщення

- `information/` — embeds загальних інформаційних команд.
- `dev/` — демонстраційні та діагностичні embeds.
- `wiki/<feature>/` — окремий wiki-домен, наприклад `characters` або
  майбутній `w_engines`.
- `menu.py` — кореневий реєстр дерева навігації конкретної команди.
- `routes.py` — стабільні ключі, aliases та breadcrumbs для прямого переходу.
- `agents/<name>.py` — embeds одного персонажа.
- `views/` — універсальна поведінка select-меню, `Back` і пагінації.

Новий персонаж має отримувати власний файл:

```text
embeds/wiki/characters/agents/new_agent.py
```

Після додавання його клас експортується з `agents/__init__.py` та підключається
в `characters/menu.py`.

## Майбутній поділ із Pydantic

Коли з'являться моделі й зовнішні дані, рекомендована межа буде такою:

```text
models/     # Pydantic-схеми Character, WEngine, Skill, Build
data/       # JSON/YAML або інше джерело контенту
embeds/     # перетворення моделей на discord.Embed
views/      # Discord UI та навігація
cogs/       # slash-команди й orchestration
```

Не варто зберігати бізнес-дані або interaction callbacks безпосередньо в
embed-файлах.
