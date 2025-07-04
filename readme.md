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
  - Add new user (by Telegram ID)
  - Remove user
  - Change user role
  - List all users
- Access control: only whitelisted users can use the bot

## 📦 Requirements

- Python 3.10+
- `python-telegram-bot` v20+
- `wakeonlan` (Linux utility)

```bash
pip install python-telegram-bot==20.7
sudo apt install wakeonlan
```

## 🛠 Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/raspberry-admin-bot.git
   cd raspberry-admin-bot
   ```

2. Replace `TOKEN = "ТВОЙ_ТОКЕН"` in `mybot.py` with your actual Telegram bot token.

3. Run the bot once to create the database:
   ```bash
   python3 mybot.py
   ```

4. Manually add yourself to the database as an admin using Python REPL:
   ```python
   import sqlite3
   conn = sqlite3.connect("users.db")
   c = conn.cursor()
   c.execute("INSERT INTO users (id, username, role) VALUES (?, ?, ?)", (123456789, 'your_username', 'admin'))
   conn.commit()
   conn.close()
   ```

5. Interact with your bot on Telegram. Only admins can open the admin panel.

## 🧾 File Structure

- `mybot.py` — main bot logic and user role management
- `users.db` — created automatically on first run

## 🔐 Access and Security

- Only users listed in `users.db` can use the bot
- Admins can manage other users via inline menu
- All roles are enforced through logic in `handle_text()`

## 🖥️ System Integration

You can extend this bot to:

- Run any script or system command
- Monitor services (e.g. Pi-hole)
- Act as a remote control panel for Raspberry Pi

## 📦 Running as a Service (optional)

Create a systemd unit file:

```ini
[Unit]
Description=Telegram Admin Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/raspberry-admin-bot/mybot.py
WorkingDirectory=/home/pi/raspberry-admin-bot
Restart=always

[Install]
WantedBy=multi-user.target
```

Save as `/etc/systemd/system/telegrambot.service` and run:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable telegrambot
sudo systemctl start telegrambot
```

## 📄 License

MIT License

---

Made with ❤️ for Raspberry Pi automation.

