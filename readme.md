# Telegram Bot Admin Panel with SQLite and System Commands

This project implements a Telegram bot that runs on a Raspberry Pi (or any Linux machine) and allows remote system control and user management via SQLite roles.

## 🚀 Features

- User roles (admin/user) stored in SQLite database
- Admin panel with inline menu interface
- Remote execution:
  - Wake-on-LAN
  - Show local IP address
  - Show system uptime
- Admin commands:
  - Add new user (by Telegram username)
  - Remove user (by Telegram username)
  - Change user role (by Telegram username)
  - List all users
- Access control: only whitelisted users can use the bot

## 📦 Requirements

- Python 3.10+
- `python-telegram-bot` v20+
- `wakeonlan` (Linux utility)

```bash
sudo apt update
sudo apt install python3-venv python3-pip wakeonlan
```

## 🛠 Быстрая установка (автоматизация)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/raspberry-admin-bot.git
   cd raspberry-admin-bot
   ```

2. Запустите автоматическую установку:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   Скрипт сам:
   - Проверит и установит зависимости
   - Попросит ввести токен бота, MAC-адрес ПК, ваш Telegram ID и username
   - Создаст .env и базу пользователей, добавит вас как админа
   - Настроит автозапуск через systemd
   - Покажет CLI-меню для управления ботом (старт/стоп/статус)

3. Пример файла настроек `.env.example`:
   ```env
   TOKEN=""
   PC_MAC=""
   ADMIN_USERNAME=""
   ```

---

## 🛠 Ручная установка (альтернатива)

1. Создайте .env по примеру выше и заполните свои данные.
2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install python-telegram-bot==20.7 wakeonlan python-dotenv
   ```
3. Запустите бота:
   ```bash
   ./venv/bin/python rbp_bot.py
   ```
4. Для автозапуска используйте:
   ```bash
   chmod +x setup_start.sh
   ./setup_start.sh
   ```

## 🧾 File Structure

- `mybot.py` — main bot logic and user role management
- `setup_start.sh` — script that sets up auto-start on boot
- `users.db` — created automatically on first run
- `venv/` — virtual environment

## 🔐 Access and Security

- Only users listed in `users.db` (по username) can use the bot
- Admins can manage other users via inline menu (по username)
- All roles are enforced through logic in `handle_text()`

## 🖥️ System Integration

You can extend this bot to:

- Run any script or system command
- Monitor services (e.g. Pi-hole)
- Act as a remote control panel for Raspberry Pi

## 🧠 Ideas for the Future

These are planned or potential features to enhance the bot:

- 📁 File browser: list files and perform actions (view, delete, download)
- 📊 System monitoring: CPU, RAM, disk usage graphs
- 🔐 Two-factor authentication (code via email or app)
- 🧪 Interactive diagnostics: check Pi-hole status, ping, DNS tests
- 📤 Upload config files via Telegram and apply them
- 🔔 Notification system: alerts if something goes offline
- 🗂️ Modular script launcher: auto-discover and run `.sh` scripts
- 📌 Scheduler: allow running tasks on a schedule (e.g., via `cron`)
- 🌍 Public status page with uptime and stats
- 🧾 Logging system: send logs to Telegram or store them by user

## 📄 License

MIT License

---

Made with ❤️ for Raspberry Pi automation.
