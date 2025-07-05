import sqlite3
import logging
import paramiko
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from subprocess import run, check_output
import platform
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# --- Settings ---
load_dotenv()
TOKEN = os.getenv("TOKEN")
DB_PATH = "users.db"  # Path to the database file
PC_MAC = os.getenv("PC_MAC")
PC_IP = os.getenv("PC_IP")
PC_SSH_USER = os.getenv("PC_SSH_USER")
PC_SSH_PASS = os.getenv("PC_SSH_PASS")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
PARAM_OS = "w" if platform.system().lower() == "windows" else "l"

# --- Menu definitions ---
MAIN_MENU = [["💻 PC control", "🌐 IP address"],
             ["🕒 Uptime", "⚙️ Admin panel"]]
PC_CONTROL = [["💻 Turn on PC", "💻 Turn off PC"],
             ["🌐 IP address", "🔙 Back"]]
ADMIN_MENU = [["➕ Add user", "➖ Remove user"],
              ["🛠 Change role", "🔄 Change MAC address"],
              ["📋 List", "🔙 Back"]]

# --- User state storage ---
user_state = {}  # key: chat_id, value: state (e.g., "main" or "admin")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SQLite database initialization ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create users table with role restrictions
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        role TEXT CHECK(role IN ('admin', 'user')) NOT NULL)''')
    conn.commit()
    conn.close()

# --- User management in the database ---
def get_user_role(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def is_admin(username):
    return get_user_role(username) == "admin"

def add_user(username, role="user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", (username, role))
    conn.commit()
    conn.close()

def remove_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

def list_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def change_role(username, new_role):
    if new_role not in ("admin", "user"):
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
    conn.commit()
    conn.close()
    return True

async def ping_pc():
    global PC_IP
    try:
        ping_cmd = ["ping", "-c", "3", PC_IP]
        ping = check_output(ping_cmd, shell=True).decode().strip()
        return "100%" not in ping
    except Exception as e:
        logger.error(f"Error pinging PC: {e}")
        return False

async def handle_pc(update: Update, action: str, pc_on: bool):
    global PC_IP, PC_MAC
    if action == "on":
        if pc_on:
            await update.message.reply_text("PC is already on.")
            return
        else:
            run(["wakeonlan", PC_MAC])
            await update.message.reply_text("PC is being turned on.")
            return
    else:
        if not pc_on:
            await update.message.reply_text("PC is already off or unreachable.")
            return
        else:
            run(["wakeonlan", "-p", "off", PC_MAC])
            await update.message.reply_text("PC is being turned off.")
            return

async def handle_pc_uptime(update: Update, pc_on: bool):
    global PC_IP, PC_SSH_PASS, PC_SSH_USER, PARAM_OS
    if not pc_on:
        await update.message.reply_text("PC is off or unreachable.")
        return
    try:
        if not (PC_IP and PC_SSH_USER and PC_SSH_PASS):
            await update.message.reply_text("⛔ Set PC_IP, PC_SSH_USER or PC_SSH_PASS variables in .env")
            return
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PC_IP, username=PC_SSH_USER, password=PC_SSH_PASS)
        if PARAM_OS == "w":
            stdin, stdout, stderr = ssh.exec_command('systeminfo | findstr /C:"System Boot Time"')
            uptime = stdout.read().decode().strip()
        else:
            stdin, stdout, stderr = ssh.exec_command('uptime -p')
            uptime = stdout.read().decode().strip()
        ssh.close()
        await update.message.reply_text(f"PC uptime is: {uptime}")
    except Exception as e:
        logger.error(f"Error getting PC uptime: {e}")
        await update.message.reply_text("⛔ Error getting PC uptime.")


# --- Command /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if get_user_role(username):
        user_state[update.effective_chat.id] = "main"
        await update.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    else:
        await update.message.reply_text("⛔ You do not have access.")

# --- Main text handler ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PC_MAC, PC_IP, PARAM_OS
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    role = get_user_role(username)
    if role is None:
        await update.message.reply_text("⛔ You do not have access.")
        return

    state = user_state.get(chat_id, "main")

    if state == "main":
        if text == "💻 PC control":
            if role != "admin":
                await update.message.reply_text("⛔ Admins only.")
                return
            if not (PC_IP and PC_MAC):
                await update.message.reply_text("⛔ Set PC_IP, or PC_MAC variables in .env")
                return
            user_state[chat_id] = "pc_control"
            await update.message.reply_text("PC control menu:", reply_markup=ReplyKeyboardMarkup(PC_CONTROL, resize_keyboard=True))
        elif text == "🌐 IP address":
            from subprocess import check_output
            ip = check_output("hostname -I", shell=True).decode().strip()
            await update.message.reply_text(f"IP: {ip}")
        elif text == "🕒 Uptime":
            from subprocess import check_output
            uptime = check_output("uptime", shell=True).decode().strip()
            await update.message.reply_text(uptime)
        elif text == "⚙️ Admin panel":
            if role != "admin":
                await update.message.reply_text("⛔ Admins only.")
                return
            user_state[chat_id] = "admin"
            await update.message.reply_text("Admin panel:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    elif state == "pc_control":
        pc_on = await ping_pc()
        if text == "💻 Turn on PC":
            await handle_pc(update, 'on', pc_on)
        elif text == "💻 Turn off PC":
            await handle_pc(update, 'off', pc_on)
        elif text == "🕒 Uptime":
            await handle_pc_uptime(update, pc_on)
        elif text == "🔙 Back":
            user_state[chat_id] = "main"
            await update.message.reply_text("Main menu:", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))

    elif state == "admin":
        if text == "🔙 Back":
            user_state[chat_id] = "main"
            await update.message.reply_text("Main menu:", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
        elif text == "➕ Add user":
            user_state[chat_id] = "awaiting_add_username"
            await update.message.reply_text("Enter the username of the new user:")
        elif text == "➖ Remove user":
            user_state[chat_id] = "awaiting_remove_username"
            await update.message.reply_text("Enter the username of the user to remove:")
        elif text == "🛠 Change role":
            user_state[chat_id] = "awaiting_change_role_username"
            await update.message.reply_text("Enter the username of the user to change role:")
        elif text == "🔄 Change MAC address":
            user_state[chat_id] = "awaiting_new_mac"
            await update.message.reply_text("Enter new MAC address for Wake-on-LAN:")
        elif text == "📋 List":
            users = list_users()
            reply = "\n".join([f"👤 {u[0]} (role: {u[1]})" for u in users])
            await update.message.reply_text(reply or "List is empty.")

    elif state == "awaiting_add_username":
        context.user_data["new_username"] = text
        user_state[chat_id] = "awaiting_add_role"
        await update.message.reply_text("Enter role (user/admin):")

    elif state == "awaiting_add_role":
        uname = context.user_data["new_username"]
        role = text.strip().lower()
        if role in ("user", "admin"):
            add_user(uname, role)
            await update.message.reply_text(f"✅ Added {uname} with role {role}")
        else:
            await update.message.reply_text("⚠️ Invalid role.")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Admin panel:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    elif state == "awaiting_remove_username":
        remove_user(text)
        await update.message.reply_text("✅ User removed")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Admin panel:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    elif state == "awaiting_change_role_username":
        context.user_data["change_username"] = text
        user_state[chat_id] = "awaiting_new_role"
        await update.message.reply_text("Enter new role (user/admin):")

    elif state == "awaiting_new_role":
        uname = context.user_data["change_username"]
        role = text.strip().lower()
        if change_role(uname, role):
            await update.message.reply_text(f"Role for user {uname} updated to {role}")
        else:
            await update.message.reply_text("⚠️ Failed to change role.")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Admin panel:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    elif state == "awaiting_new_mac":
        from dotenv import set_key
        PC_MAC = text.strip()
        set_key('.env', 'PC_MAC', PC_MAC)
        await update.message.reply_text(f"MAC address updated to {PC_MAC}")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Admin panel:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

# --- Blocking non-text messages ---
async def block_others(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Ignore photos, documents, voice messages, etc.

# --- Main application entry point ---
def main():
    init_db()  # Create database on startup
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(~filters.TEXT, block_others))
    app.run_polling()

if __name__ == "__main__":
    main()
