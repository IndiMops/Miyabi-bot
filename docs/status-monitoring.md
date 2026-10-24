# Моніторинг статусу

[← До змісту](README.md)

Бот періодично надсилає heartbeat в окремий процес `status_service`. Той за
свіжістю heartbeat визначає стан і підтримує **одне** повідомлення в
окремому текстовому каналі Discord, редагуючи його через webhook.

```text
Miyabi Bot ──POST /heartbeat (Bearer secret)──▶ status_service ──webhook edit──▶ #status
                                                    │
                                    Uptime Kuma ──GET /health
```

## Компоненти

| Файл | Відповідальність |
|---|---|
| [`utils/heartbeat.py`](../utils/heartbeat.py) | Збір стану клієнта й доставка heartbeat (timeout, retry з backoff, без винятків назовні). |
| [`cogs/core/status_heartbeat.py`](../cogs/core/status_heartbeat.py) | Цикл heartbeat у життєвому циклі бота й shutdown-heartbeat при `close()`. |
| [`status_service/evaluator.py`](../status_service/evaluator.py) | Валідація payload і правила станів. |
| [`status_service/store.py`](../status_service/store.py) | JSON state-файл: ID повідомлення й останній heartbeat (атомарний запис). |
| [`status_service/publisher.py`](../status_service/publisher.py) | Embed статусу й створення/редагування одного webhook-повідомлення. |
| [`status_service/app.py`](../status_service/app.py) | HTTP-ендпоінти, цикл оцінки, `/health`. |

Бот **не залежить** від status service: якщо змінні не задані, cog лише
пише в лог, що reporter вимкнений; якщо сервіс недоступний — heartbeat
губиться, а в лог іде одне попередження на кожну серію збоїв.

## Стани

Свіжість рахується за часом **отримання** heartbeat на стороні сервісу, тож
розсинхронізація годинника на хості бота не впливає.

| Стан | Умова |
|---|---|
| `ONLINE` | Свіжий heartbeat, `ready=true`, gateway підключений, затримка ≤ `STATUS_DEGRADED_LATENCY_MS`. |
| `DEGRADED` | Свіжий heartbeat, `ready=true`, але gateway перепідключається або затримка висока. |
| `STARTING` | Свіжий heartbeat, `ready=false`, процес молодший за `STATUS_STARTING_GRACE`. |
| `OFFLINE` | Heartbeat старший за `STATUS_OFFLINE_AFTER`; або бот штатно завершився; або `ready=false` довше за grace. |
| `UNKNOWN` | Сервіс щойно стартував і ще не має жодного heartbeat. **У Discord не публікується.** |

`ready` береться з `client.is_ready()` і `client.is_closed()`, а не з факту,
що процес живий. `is_ready()` у discord.py лишається `true` під час
reconnect, тому окремо передається `gateway_connected`. Якщо event loop бота
завис, heartbeat припиняються, і сервіс сам переходить в `OFFLINE`.

## Повідомлення в Discord

1. При першій публікації сервіс створює повідомлення через webhook
   (`?wait=true`) і записує його ID разом з ID webhook у state-файл.
2. Далі він лише редагує це повідомлення.
3. Після рестарту ID читається з state-файлу — дублікатів немає.
4. Якщо повідомлення видалили (Discord `10008 Unknown Message`), при
   `STATUS_RECREATE_MISSING_MESSAGE=true` створюється нове, і його ID
   зберігається. При `false` сервіс фіксує помилку, а `/health` стає 503.
5. Якщо змінився webhook, старий ID ігнорується (у state-файлі зберігається
   ID webhook).
6. Якщо state-файл пошкоджений, він перейменовується на
   `*.corrupt-<timestamp>`. Щоб не створювати нове повідомлення, задай
   `STATUS_MESSAGE_ID` — сервіс «усиновить» наявне повідомлення цього webhook.

Публікація відбувається одразу при зміні стану або раз на
`STATUS_PUBLISH_INTERVAL` (типово 300 с). Час останнього heartbeat і uptime
показуються Discord-мітками `<t:…:R>`, які оновлюються в клієнті самі, тож
часті редагування не потрібні. Rate limit (429) обробляє discord.py; при
інших помилках — експоненційний backoff до 300 с.

Webhook може редагувати **лише власні** повідомлення, тому вручну створювати
повідомлення не потрібно і не можна.

## Змінні середовища

Повний шаблон — у [`.env.example`](../.env.example).

| Змінна | Хто читає | Типово | Призначення |
|---|---|---|---|
| `STATUS_HEARTBEAT_SECRET` | обидва | — | Спільний секрет для `Authorization: Bearer`. Для сервісу обов'язковий, ≥ 16 символів. |
| `STATUS_SERVICE_NAME` | обидва | `miyabi-bot` | Ідентифікатор сервісу в payload. |
| `STATUS_HEARTBEAT_INTERVAL` | обидва | `30` | Інтервал heartbeat, с (сервіс лише перевіряє, що поріг більший). |
| `STATUS_HEARTBEAT_URL` | бот | порожньо | Адреса `/heartbeat`. Порожньо — reporter вимкнений. |
| `STATUS_HEARTBEAT_TIMEOUT` | бот | `5` | Timeout одного запиту, с. 3 спроби з backoff 1 і 2 с. |
| `STATUS_LISTEN_HOST` / `STATUS_LISTEN_PORT` | сервіс | `127.0.0.1` / `8787` | Адреса HTTP-сервера. |
| `STATUS_WEBHOOK_URL` | сервіс | порожньо | Webhook каналу статусу. Порожньо — публікація вимкнена. |
| `STATUS_DISPLAY_NAME` | сервіс | `Miyabi Bot` | Назва в заголовку embed. |
| `STATUS_STATE_FILE` | сервіс | `data/status_service_state.json` | State-файл (відносно кореня репо). |
| `STATUS_MESSAGE_ID` | сервіс | порожньо | Лише для відновлення після втрати state-файлу. |
| `STATUS_RECREATE_MISSING_MESSAGE` | сервіс | `true` | Створювати нове повідомлення, якщо старе видалили. |
| `STATUS_OFFLINE_AFTER` | сервіс | `90` | Поріг застарівання heartbeat, с. |
| `STATUS_STARTING_GRACE` | сервіс | `180` | Скільки процес може бути `ready=false` у стані `STARTING`. |
| `STATUS_DEGRADED_LATENCY_MS` | сервіс | `1000` | Поріг затримки для `DEGRADED`. |
| `STATUS_EVALUATE_INTERVAL` | сервіс | `10` | Як часто перевіряється свіжість, с. |
| `STATUS_PUBLISH_INTERVAL` | сервіс | `300` | Мінімальний інтервал повторної публікації без зміни стану, с. |

Некоректні значення: бот підставляє типові й пише попередження; сервіс
відмовляється стартувати з кодом 2.

## Налаштування Discord

1. Створи окремий текстовий канал, наприклад `#bot-status`, у якому
   звичайні користувачі не можуть писати.
2. **Channel Settings → Integrations → Webhooks → New Webhook**, назви його,
   скопіюй URL і поклади в `STATUS_WEBHOOK_URL` (лише в `.env` / секрети
   середовища, не в Git).
3. Більше нічого не потрібно: повідомлення створиться автоматично.

Webhook URL — це секрет: хто його має, може писати в канал. Якщо він
витік — видали webhook і створи новий; сервіс створить нове повідомлення.

## HTTP-ендпоінти

| Метод | Шлях | Відповіді |
|---|---|---|
| `POST` | `/heartbeat` | `200` прийнято; `401` без/з неправильним секретом; `400` невалідний JSON/поля; `413` > 16 KB; `422` невідомий сервіс. |
| `GET` | `/health` | `200` або `503` з JSON `{status, problems, …}`. |

`/health` описує **сам сервіс**, а не бота: чи працює цикл оцінки, чи
пишеться state-файл, чи вдається оновлювати повідомлення (503 після 3
невдач поспіль). Стан бота видно в Discord.

### Мережа

Типово сервіс слухає лише `127.0.0.1`. Якщо бот і сервіс у різних
контейнерах, став `STATUS_LISTEN_HOST=0.0.0.0` **всередині** приватної
Docker-мережі й не публікуй порт назовні; бот звертається на
`http://<ім'я-сервісу>:8787/heartbeat`. Доступ до Docker socket не потрібен.

### Uptime Kuma

Monitor type **HTTP(s)**, URL `http://<host>:8787/health`, інтервал 60 с,
accepted status codes `200-299`. Kuma має бути в тій самій приватній мережі
або на тому самому хості. Ендпоінт не потребує секрету, бо не приймає даних і
не розкриває секретів.

## Розширення на інші сервіси

Payload містить поле `service`, а state-файл зберігає heartbeat за назвою
сервісу. Зараз приймається лише `STATUS_SERVICE_NAME`; для сайту чи API
наступним кроком буде список сервісів у налаштуваннях і поле embed для
кожного з них у тому самому повідомленні.

## Локальна перевірка

Автоматичні тести (без Discord):

```powershell
python -m pytest tests/test_status_heartbeat.py tests/test_status_service.py
```

Живий сценарій (потрібні тестовий бот і тестовий канал з webhook), два
термінали з кореня репо, `.env` заповнений за `.env.example`:

```powershell
# термінал 1
python -m status_service
# термінал 2
python bot.py
```

1. У логах сервісу: `miyabi-bot: UNKNOWN -> STARTING`, потім `-> ONLINE`,
   `Created status message <id>`. У каналі з'являється одне повідомлення 🟢.
2. `curl http://127.0.0.1:8787/health` → `200`, `heartbeats_received` росте.
3. Зупини бота `Ctrl+C` → shutdown-heartbeat, повідомлення стає 🔴 одразу.
   Для перевірки «зниклого» бота вбий процес без graceful shutdown
   (`Stop-Process -Id <pid> -Force`) → 🔴 приблизно через 90–100 с.
4. Запусти бота знову → 🔵/🟢, редагується **те саме** повідомлення.
5. Перезапусти `status_service` → у логах немає `Created status message`,
   ID у `data/status_service_state.json` той самий.
6. Перевірка автентифікації:
   `curl -X POST http://127.0.0.1:8787/heartbeat -d "{}"` → `401`.
