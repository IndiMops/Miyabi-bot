# Архітектура

[← До змісту](README.md)

Проєкт є невеликим монолітним Discord-ботом. Окремого серверного API, бази
даних або фонового worker-процесу немає.

## Карта проєкту

```text
Miyabi-bot/
├── bot.py                    # точка входу та composition root
├── config.json               # публічна конфігурація
├── requirements.txt          # runtime-залежності
├── cogs/
│   ├── information/          # /help і /info
│   ├── wiki/                 # /characters
│   └── dev/                  # тестові команди
├── embeds/                   # представлення, згруповані за доменами
│   ├── information/          # embeds для /help
│   ├── dev/                  # демонстраційний deep-menu
│   └── wiki/
│       └── characters/
│           ├── menu.py       # кореневий реєстр дерева
│           ├── routes.py     # ключі, aliases і breadcrumbs
│           └── agents/       # окремі файли персонажів
├── views/
│   ├── nav.py                # вкладені select-меню
│   └── pagination.py         # кнопкова пагінація
├── utils/
│   ├── config.py             # .env + config.json
│   ├── logger.py             # Loguru і standard logging
│   └── misc.py               # JSON, кольори, версія, fetch commands
├── tests/                    # локальні unit-тести
└── docs/                     # документація
```

`embeds/` тепер є явною ієрархією Python-пакетів з `__init__.py` та
контрольованими exports. Папки `cogs`, `utils` і `views` поки залишаються
implicit namespace packages.

## Життєвий цикл запуску

1. Під час імпорту `Config` читаються `.env` і `config.json`.
2. Під час імпорту логера створюється `logs/` та підключаються файлові
   handlers.
3. Створюється екземпляр `MiyabiBot` зі стандартними intents.
4. `bot.run(Config.require_token())` перевіряє токен і підключається до
   Discord.
5. `setup_hook()` рекурсивно знаходить усі `.py` у `cogs/`.
6. При `DEBUG=False` loader пропускає папки з `disabled_cogs_folder`.
7. Кожний модуль завантажується як extension через його `async setup(bot)`.
8. `tree.sync()` глобально синхронізує всі завантажені slash-команди.
9. Стартує 30-секундний цикл статусу.
10. Після готовності подія `on_ready` пише повідомлення в лог.

Якщо будь-який cog кидає `ExtensionError`, loader записує traceback і повторно
піднімає помилку. Через це весь запуск зупиняється — бот не продовжує роботу з
частковим набором модулів.

Статус раз на 30 секунд перемикається між:

- `/help | dev-<короткий Git hash>`;
- `<кількість> servers`.

Якщо Git недоступний, використовується `bot.version` із `config.json`.

## Межі відповідальності

| Шар | Відповідальність |
|---|---|
| `bot.py` | Створення клієнта, intents, завантаження extensions, sync і presence. |
| `cogs/` | Вхідні Discord-команди та orchestration відповіді. |
| `embeds/` | Статичні Discord Embed і дерево доступного контенту. |
| `views/` | Повторно використовувані UI-компоненти Discord. |
| `utils/` | Конфігурація, логування й невеликі загальні helpers. |

Весь wiki-контент зараз жорстко записаний в `embeds/`. Залежність `requests`
встановлюється, але поточний Python-код її не використовує.

## Як додати slash-команду

Створи файл, наприклад `cogs/information/example.py`:

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

Після перезапуску loader знайде файл автоматично. Не називай звичайний helper
усередині `cogs/` окремим `.py`, якщо він не є валідним Discord extension:
loader намагатиметься завантажити кожний файл, назва якого не починається з
`__`.

Після першої синхронізації додай ID до `config.json` лише тоді, коли команду
потрібно згадувати в embed як `</example:ID>`. Для самої реєстрації цей запис не
потрібний.

## Контракт навігаційних embeds

[`NavView`](../views/nav.py) очікує клас із трьома class methods:

| Метод | Результат |
|---|---|
| `get_embed(key)` | Один `discord.Embed` для поточного вузла. |
| `get_children(key)` | Список дочірніх пунктів або порожній список. |
| `get_pages(key)` | Список embeds для пагінації або `None`. |

Для ключа `Main` клас зазвичай має:

```python
Main = discord.Embed(title="Головна")
Main_children = [
    {"label": "Деталі", "value": "Details", "emoji": "ℹ️"},
]

Details = discord.Embed(title="Деталі")
Details_children = []
```

Значення `value` повинно точно збігатися з назвою відповідного class
attribute. Дочірні елементи також можуть бути рядками або tuple, але словники
з явними `label` і `value` читати та підтримувати простіше.

Навігація зберігає історію в пам'яті view, а після першого рівня додає `Back`.
Якщо для вузла є `<Key>_pages`, вона переходить у
[`PaginationView`](../views/pagination.py).

Обидва view за замовчуванням мають timeout 120 секунд. Після timeout старі
компоненти можуть залишатися видимими в Discord, але більше не обробляють
натискання. Після перезапуску бота старі views також не відновлюються.

Для вкладених вузлів `NavSelect` показує максимум 24 дочірні елементи та
додає 25-м option `Back`. Якщо дочірніх елементів більше, `<Key>_pages`
повинен містити відповідну кількість embeds. Пагінація одночасно перемикає
embed і зріз select-options, а номер сторінки зберігається під час переходу до
елемента та повернення через `Back`.

## Технічні нюанси

- Усі поточні команди є slash-командами. Значення prefix `"."` поки не дає
  користувацької функціональності.
- `message_content` intent не ввімкнений.
- Глобальний `tree.sync()` виконується на кожному старті.
- `AllowedMentions` забороняє масові згадки `@everyone` і ролей, але дозволяє
  згадки користувачів.
- Embed-об'єкти створюються на рівні класу й повторно використовуються. Не
  мутуй отриманий embed для одного користувача без створення копії.
- У проєкті немає постійного сховища: історія меню існує лише всередині
  конкретного активного view.
