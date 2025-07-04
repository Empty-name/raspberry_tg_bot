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

## 🛠 Fast Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/raspberry-admin-bot.git
   cd raspberry-admin-bot
   ```

2. Run the automatic installation:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   The script will:
   - Check and install all dependencies
   - Ask for your bot token, PC MAC address, and your Telegram username
   - Create the .env file and user database, add you as admin
   - Set up autostart via systemd
   - Show a CLI menu for bot management (start/stop/status)

3. Example `.env.example` file:
   ```env
   TOKEN=""
   PC_MAC=""
   ADMIN_USERNAME=""
   ```

---

## 🛠 Manual Installation

1. Create a .env file as shown above and fill in your data.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install python-telegram-bot==20.7 wakeonlan python-dotenv
   ```
3. Start the bot:
   ```bash
   ./venv/bin/python rbp_bot.py
   ```
4. For autostart use:
   ```bash
   chmod +x setup_start.sh
   ./setup_start.sh
   ```

## 🧾 File Structure

- `rbp_bot.py` — main bot logic and user role management
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
