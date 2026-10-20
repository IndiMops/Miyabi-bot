# Запуск Miyabi Bot

[← До змісту](README.md)

## Вимоги

- Python **3.11** — рекомендована версія, бо саме її використовують CI та
  release workflow;
- Git;
- Discord Application із доданим Bot;
- токен цього бота;
- тестовий Discord-сервер.

Поточне локальне `venv` працює на Python 3.14.6 і проходить тести, але
`discord.py` уже показує deprecation warning для цієї версії. Для
відтворюваного середовища краще залишатися на Python 3.11.

## 1. Створення середовища

Запускай усі команди з кореня репозиторію.

### Windows PowerShell

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Якщо `py -3.11` недоступна, перевір установлені версії командою:

```powershell
py --list
```

### Linux або macOS

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`pytest` і `ruff` є інструментами розробки, але не входять у
[`requirements.txt`](../requirements.txt). Для роботи з кодом встанови їх
окремо:

```powershell
python -m pip install pytest ruff
```

## 2. Створення Discord Application

У [Discord Developer Portal](https://discord.com/developers/applications):

1. створи Application;
2. додай до неї Bot і отримай його токен;
3. для встановлення застосунку додай scopes `applications.commands` і `bot`;
4. дай боту мінімальні дозволи для перегляду каналу, надсилання повідомлень та
   embeds;
5. встанови застосунок на тестовий сервер.

Поточний код не використовує `members`, `presences` або `message_content`, тому
привілейовані Gateway Intents для наявних slash-команд не потрібні.

Корисні офіційні сторінки:

- [Discord: Getting Started](https://docs.discord.com/developers/quick-start/getting-started)
- [Discord: Application Commands](https://docs.discord.com/developers/interactions/application-commands)
- [Discord: Gateway Intents](https://docs.discord.com/developers/events/gateway)

## 3. Локальний `.env`

Створи файл `.env` у корені репозиторію:

```dotenv
DEBUG=False
DISCORD_BOT_TOKEN=вставити_сюди_токен
```

Правила:

- не додавай пробіли навколо назви змінної;
- не публікуй справжній токен;
- якщо токен потрапив у Git або повідомлення, негайно скинь його в Discord
  Developer Portal;
- значення `DEBUG=True` використовуй лише усвідомлено — воно відкриває
  тестові команди.

`.env` уже доданий до `.gitignore`.

## 4. Запуск

```powershell
python bot.py
```

Або без активації середовища:

```powershell
.\venv\Scripts\python.exe bot.py
```

Під час успішного старту бот:

1. читає `.env` і `config.json`;
2. знаходить і завантажує всі Python-модулі в `cogs/`;
3. глобально синхронізує slash-команди через Discord;
4. запускає оновлення статусу;
5. пише в консоль `Bot is ready!`.

Глобальні slash-команди іноді з'являються у клієнті Discord не миттєво.
Зупинити процес можна через `Ctrl+C`.

Запускай бот саме з кореня репозиторію: файлові логи створюються відносно
поточної робочої директорії.

## 5. Швидка перевірка перед роботою

```powershell
git status
python -m pytest -q
python -m compileall -q bot.py cogs embeds utils views
python -m ruff check --select E9,F63,F7,F82 .
```

Ці команди повторюють основні перевірки CI. Детальніше дивись у
[довідці для розробки](development.md).
