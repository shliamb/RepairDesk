# 🛠 RepairDesk Bot

**Telegram-бот для автоматизации ремонтной мастерской**  
*Telegram bot for repair shop automation*

[English](## 🇬🇧 English) | [Русский](## 🇷🇺 Русский)

---

## 🇷🇺 Русский

### О проекте

RepairDesk — это open-source Telegram бот, созданный **ремонтником для ремонтников**.

Бот полностью закрывает потребности небольшой мастерской:
- 📦 Приём заказов
- 👥 Клиентская база с историей
- 💰 Финансовый учёт
- 🧾 Печать квитанций (PDF)
- 🔍 Умный поиск

**Никакой ежемесячной подписки. Твой сервер — твои данные.**

---

### ✅ Тестировалось на

**Ubuntu 22.04 LTS**  
Python 3.10+  
PostgreSQL 15 (в Docker)

---

### 🚀 Быстрый старт

#### 1. Подготовка

Установи Docker и Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
```

Клонируй репозиторий:
```bash
git clone https://github.com/твой-логин/RepairDesk.git
cd RepairDesk
```

#### 2. Создай бота

Напиши [@BotFather](https://t.me/botfather), создай бота, получи токен.

Узнай свой `telegram_id` — напиши [@userinfobot](https://t.me/userinfobot).

#### 3. Настройка окружения

Скопируй и заполни `.env`:

```bash
cp .env.example .env
nano .env
```

```env
# Telegram Bot
telegram_bot_token=7254634566:AAHkldfjghdfkjghdfkjg
admin_id=123456789              # Твой Telegram ID (обязательно!)

# PostgreSQL
user_db=repair_user
password_db=secure_password
db_name=repair_db
db_host=postgres
db_port=5432

# Прокси (только если в РФ)
proxy="socks5://user:pass@host:port"

# DeepSeek API (опционально)
key_api_deepseek=sk-...
```

#### 4. Настройка конфига бота

```bash
cp app/config.test.py app/config.py
nano app/config.py
```

**Обязательно укажи:**
- 📞 Номер телефона мастерской
- 📍 Адрес
- 💻 Список устройств
- 🖨️ Пути для сохранения PDF

#### 5. Запуск

```bash
sudo docker-compose up --build -d
```

Бот и PostgreSQL запустятся в контейнерах.  
Готово! 🎉

---

### 🎛 Админ-панель

Доступна **только** пользователю с `admin_id` из `.env`.

| Команда       | Описание                          |
|---------------|-----------------------------------|
| **📊 Статистика**  |                                   |
| `/allUs`      | Список всех пользователей        |
| `/allPay`     | Финансовая отчётность            |
| **📝 Логи**       |                                   |
| `/logs`       | Получить файл логов бота         |
| **🗳 Backup**     |                                   |
| `/crTabDb`    | 🔧 **Создать таблицы БД** (обязательно перед первым запуском!) |
| `/dnlUsers`   | Скачать users.json               |
| `/resUs`      | Восстановить клиентов из JSON    |
| `/dnlOrd`     | Скачать orders.json              |
| `/resOrd`     | Восстановить заказы из JSON      |
| `/Skl`        | Импорт из Livesklad (Excel)      |
| **🗑 Очистка**    |                                   |
| `/allDel`     | ❗ Удалить ВСЕ таблицы (необратимо) |
| `/dLogs`      | Очистить логи                    |

> ⚠️ **Важно!**  
> После первого запуска бота **обязательно** выполни `/crTabDb` — это создаст все необходимые таблицы в PostgreSQL.

---

### 🔄 Миграция с Livesklad

Если ты раньше вёл учёт в Excel (формат Livesklad) — бот умеет импортировать твои старые данные.

**Пошаговая инструкция:**

1. **Экспорт из Livesklad**
   - Открой свою базу в Excel
   - Сохрани как `.xlsx`

2. **Загрузка в бота**
   - Отправь команду `/Skl`
   - Загрузи Excel-файл
   - Бот автоматически создаст два JSON-файла:
     - `users_export.json` — клиенты
     - `orders_export.json` — заказы

3. **Восстановление клиентов**
   - Отправь команду `/resUs`
   - Загрузи `users_export.json`
   - ✅ Клиенты импортированы

4. **Восстановление заказов**
   - Отправь команду `/resOrd`
   - Загрузи `orders_export.json`
   - ✅ Заказы импортированы

**Важно:** Сначала всегда загружай клиентов, потом заказы (из-за внешних ключей).

---

### 🌍 Язык

Язык определяется **автоматически** по языку интерфейса Telegram пользователя.

Поддерживаются:
- 🇷🇺 Русский
- 🇬🇧 Английский

Никакой ручной настройки не требуется.

---

### 🌐 Прокси (для пользователей из РФ)

Если Telegram замедляется или блокируется — просто укажи прокси в `.env`:

```env
proxy="socks5://user:pass@host:port"
```

Бот сам настроит сессию.  
Проверено с iproyal.com и Tor (localhost:9050).

---

### ❓ Частые вопросы

**Q: У меня нет Docker. Могу запустить без него?**  
A: Да. Установи PostgreSQL локально, укажи в `.env` `db_host=localhost`, установи зависимости через `pip install -r requirements.txt` и запусти бота командой `python3 app/run_bot.py`.

**Q: После запуска бот не отвечает на команды админа.**  
A: Проверь `admin_id` в `.env` — должен быть твой числовой Telegram ID.

**Q: Бот пишет "no such table".**  
A: Забыл выполнить `/crTabDb`. Сделай — таблицы создадутся.

**Q: Как сделать бекап?**  
A: Используй `/dnlUsers` и `/dnlOrd`. Полученные JSON храни в надёжном месте.

**Q: А если я не админ, а простой мастер?**  
A: Админ даст тебе роль мастера. Ты сможешь создавать заказы и смотреть клиентов, но не увидишь админ-панель.

---

### 📄 Лицензия

MIT — делай что хочешь, но упомяни автора.

---

**Автор:** Alex Prowler  
**Статус:** ✅ Production ready  
**Open source:** с 2026 года


---

[⬆ Наверх](#-repairdesk-bot)

---

## 🇬🇧 English

### About

RepairDesk is an open-source Telegram bot built **by a repair technician for repair technicians**.

**No monthly subscriptions. Your server — your data.**

---

### ✅ Tested on

**Ubuntu 22.04 LTS**  
Python 3.10+  
PostgreSQL 15 (Docker)

---

### 🚀 Quick Start

#### 1. Prerequisites

Install Docker and Docker Compose:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
```

```bash
git clone https://github.com/your-username/RepairDesk.git
cd RepairDesk
```

#### 2. Create a bot

Message [@BotFather](https://t.me/botfather), create a bot, get the token.

Get your `telegram_id` — message [@userinfobot](https://t.me/userinfobot).

#### 3. Environment setup

```bash
cp .env.example .env
nano .env
```

```env
# Telegram Bot
telegram_bot_token=7254634566:AAHkldfjghdfkjghdfkjg
admin_id=123456789              # Your Telegram ID (required!)

# PostgreSQL
user_db=repair_user
password_db=secure_password
db_name=repair_db
db_host=postgres
db_port=5432

# Proxy (only for censored regions)
proxy="socks5://user:pass@host:port"

# DeepSeek API (optional)
key_api_deepseek=sk-...
```

#### 4. Bot configuration

```bash
cp app/config.test.py app/config.py
nano app/config.py
```

**Set your:**
- 📞 Shop phone number
- 📍 Address
- 💻 Accepted device types
- 🖨️ PDF save paths

#### 5. Run

```bash
sudo docker-compose up --build -d
```

Bot and PostgreSQL start in containers.  
Done! 🎉

---

### 🎛 Admin Panel

Accessible **only** to the user with `admin_id` from `.env`.

| Command       | Description                      |
|---------------|----------------------------------|
| **📊 Stats**      |                                  |
| `/allUs`      | List all users                 |
| `/allPay`     | Financial statistics           |
| **📝 Logs**       |                                  |
| `/logs`       | Download bot logs              |
| **🗳 Backup**     |                                  |
| `/crTabDb`    | 🔧 **Create DB tables** (required before first use!) |
| `/dnlUsers`   | Download users.json            |
| `/resUs`      | Restore users from JSON        |
| `/dnlOrd`     | Download orders.json           |
| `/resOrd`     | Restore orders from JSON       |
| `/Skl`        | Import from Livesklad (Excel)  |
| **🗑 Cleanup**    |                                  |
| `/allDel`     | ❗ Delete ALL tables (irreversible) |
| `/dLogs`      | Clear logs                     |

> ⚠️ **Important!**  
> After first launch, **you must run** `/crTabDb` to create all database tables.

---

### 🔄 Migrating from Livesklad

**Step by step:**

1. **Export from Livesklad**
   - Open your Excel database
   - Save as `.xlsx`

2. **Upload to bot**
   - Send `/Skl` command
   - Upload your Excel file
   - Bot creates two JSON files:
     - `users_export.json` — customers
     - `orders_export.json` — orders

3. **Restore customers**
   - Send `/resUs`
   - Upload `users_export.json`
   - ✅ Customers imported

4. **Restore orders**
   - Send `/resOrd`
   - Upload `orders_export.json`
   - ✅ Orders imported

**Important:** Always restore customers first, then orders.

---

### 🌍 Language

Language is **automatically detected** from user's Telegram interface.

Supported:
- 🇷🇺 Russian
- 🇬🇧 English

No manual configuration needed.

---

### 🌐 Proxy (for censored regions)

Just set proxy in `.env`:

```env
proxy="socks5://user:pass@host:port"
```

Bot will handle the rest.  
Tested with iproyal.com and Tor (localhost:9050).

---

### ❓ FAQ

**Q: I don't have Docker. Can I run without it?**  
A: Yes. Install PostgreSQL locally, set `db_host=localhost` in `.env`, install dependencies with `pip install -r requirements.txt`, run bot with `python3 app/run_bot.py`.

**Q: Bot doesn't respond to admin commands.**  
A: Check `admin_id` in `.env` — must be your numeric Telegram ID.

**Q: Bot says "no such table".**  
A: You forgot `/crTabDb`. Run it — tables will be created.

**Q: How to backup?**  
A: Use `/dnlUsers` and `/dnlOrd`. Keep the JSON files safe.

---

### 📄 License

MIT — do whatever you want, but give credit.

---

**Author:** Alex Prowler  
**Status:** ✅ Production ready  
**Open source:** since 2026


---

[⬆ Back to top](#-repairdesk-bot)