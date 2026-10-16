# Розробка й діагностика

[← До змісту](README.md)

## Основні перевірки

Встанови dev-інструменти:

```powershell
python -m pip install pytest ruff
```

Запусти перевірки, які відповідають поточному CI:

```powershell
python -m compileall -q bot.py cogs embeds utils views
python -m ruff check --select E9,F63,F7,F82 .
python -m pytest
```

На момент створення документації результат був:

```text
compileall: passed
CI Ruff subset: passed
pytest: 7 passed
```

Локальне середовище працює на Python 3.14.6, але CI використовує Python 3.11.

Повний `ruff check .` значно суворіший за CI й зараз повертає багато style та
modernization зауважень. Не запускай автоматичне виправлення всього проєкту
разом із маленькою функціональною зміною: це створить великий сторонній diff.

## Що покривають тести

[`tests/test_character_routes.py`](../tests/test_character_routes.py) перевіряє:

- пошук агента за ключем і альтернативними назвами;
- нормалізацію регістру та пробілів;
- повний history для роботи `Back`;
- відповідність Fire-маршрутів реальним embed-ключам;
- пріоритет точного autocomplete-збігу;
- обмеження autocomplete до 25 унікальних результатів.
- наявність параметра `agent` та підключеного Discord autocomplete callback.

Поки не перевіряються:

- реальне підключення до Discord;
- глобальна синхронізація команд;
- callbacks slash-команд;
- `NavView` і всі гілки `/characters`;
- структура `config.json`;
- коректність зовнішніх URL та custom emoji;
- поведінка логування.

## CI

Workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml):

- запускається для push у `main` і `dev`;
- запускається для pull request у `main` і `dev`;
- використовує Ubuntu та Python 3.11;
- встановлює runtime requirements, `pytest` і `ruff`;
- перевіряє compileall, критичний Ruff subset і pytest.

`pytest` і `ruff` не зафіксовані в окремому dev requirements або lock-файлі,
тому CI встановлює їхні актуальні версії.

Release workflow:

- запускається для тегів `v*.*.*`;
- використовує Python 3.11;
- запускає pytest;
- створює draft GitHub Release з автоматичними release notes.

Він не запускає compileall/Ruff і не перевіряє, що тег відповідає
`config.json → bot.version`.

## Логи

| Місце | Рівень | Поведінка |
|---|---|---|
| Консоль Loguru | `INFO` або `DEBUG` | `DEBUG` вмикається через `.env`. |
| `logs/bot.log` | `DEBUG` | Rotation на 10 MB, retention 10 днів, старі логи стискаються в ZIP. |
| `logs/standard.log` | `DEBUG` | Standard Python logging, без rotation. |

Каталог `logs/` ігнорується Git.

Для першої діагностики шукай у `logs/bot.log`:

- `Loaded extension: ...`;
- `Skipped disabled extension: ...`;
- `Failed to load extension: ...`;
- `Bot is ready!`;
- traceback безпосередньо перед завершенням процесу.

## Типові проблеми

### `DISCORD_BOT_TOKEN is not set`

Причина: немає `.env`, змінна названа неправильно або токен не потрапив у
середовище процесу.

Перевір наявність **назви** змінної, не друкуючи її значення в термінал чи
чат. Після виправлення перезапусти бот.

### Slash-команди не видно

Перевір:

1. чи встановлено Application на сервер зі scope `applications.commands`;
2. чи всі extensions завантажилися без помилки;
3. чи дійшов запуск до `Bot is ready!`;
4. чи не дивишся на dev-команду при `DEBUG=False`;
5. чи минув час на оновлення глобальних команд у Discord.

### Dev-команди несподівано доступні всім

Встанови в `.env`:

```dotenv
DEBUG=False
```

Після цього перезапусти бот, щоб він повторно синхронізував дерево без
`cogs/dev`.

### `Failed to load extension`

Перевір traceback. Часті причини:

- синтаксична або import-помилка;
- у файлі cog відсутній `async setup(bot)`;
- неправильна назва class attribute в дереві embeds;
- невалідний `config.json`;
- helper-файл випадково розміщено в `cogs/` і loader сприйняв його як
  extension.

### Меню відповідає `interaction failed`

Для великого списку перевір, що кількість `<Key>_pages` відповідає кількості
24-елементних зрізів `<Key>_children`. Наприклад, 35 дочірніх елементів
потребують двох embeds-сторінок: 24 та 11.

Інші можливі причини:

- протермінований URL зображення;
- недоступний custom emoji;
- порожнє або невалідне поле embed;
- `value` у select не збігається з назвою embed attribute;
- view уже досяг 120-секундного timeout.

### Логи створилися не в репозиторії

Бот був запущений з іншої робочої директорії. Перейди в корінь репозиторію й
запусти `python bot.py` ще раз.

## Безпечний цикл зміни

```text
1. Перевір git status.
2. Зміни один cog/embed/view.
3. Запусти compileall, Ruff subset і pytest.
4. Запусти бот на тестовому сервері.
5. Перевір звичайний та помилковий сценарії команди.
6. Переглянь git diff і не додавай .env або logs.
```

## Корисний backlog для наступного повернення

1. Замінити 35 вогняних заглушок справжніми ігровими даними.
2. Наповнити крижану, електричну та ефірну гілки.
3. Захистити dev-команди owner/permission checks незалежно від `DEBUG`.
4. Зробити `/help` єдиним джерелом метаданих команд.
5. Автоматично отримувати command IDs замість ручного JSON-списку.
6. Додати `.env.example` без секретів і зафіксовані dev-залежності.
7. Додати тести для `NavView`, help callbacks і всіх гілок персонажів.
8. Замінити тимчасові Discord attachment URLs на стабільні assets.
9. Визначити deployment-процес і перевірку версії перед release.
