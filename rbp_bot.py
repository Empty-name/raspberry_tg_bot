import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# --- Настройки ---
TOKEN = "7744280511:AAGUeHaDppq0fCdhCe2IpSq2gT3iCc5WHrM"  # Токен Telegram-бота
DB_PATH = "users.db"  # Путь к файлу базы данных
PC_MAC = "58:11:22:BD:08:DF"

# --- Определение меню интерфейса бота ---
MAIN_MENU = [["💻 Включить ПК", "🌐 IP адрес"],
             ["🕒 Uptime", "⚙️ Админ-панель"]]

ADMIN_MENU = [["➕ Добавить пользователя", "➖ Удалить пользователя"],
              ["🛠 Сменить роль", "📋 Список"],
              ["🔙 Назад"]]

# --- Хранение текущего состояния пользователей ---
user_state = {}  # key: chat_id, value: состояние (например, "main" или "admin")

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация базы данных SQLite ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Создание таблицы пользователей с ограничением ролей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        role TEXT CHECK(role IN ('admin', 'user')) NOT NULL)''')
    conn.commit()
    conn.close()

# --- Работа с пользователями в базе данных ---
def get_user_role(user_id):
    # Получаем роль пользователя по его Telegram ID
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def is_admin(user_id):
    return get_user_role(user_id) == "admin"

def add_user(user_id, username, role="user"):
    # Добавление нового пользователя в базу
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, role) VALUES (?, ?, ?)", (user_id, username, role))
    conn.commit()
    conn.close()

def remove_user(user_id):
    # Удаление пользователя по ID
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def list_users():
    # Возвращает список всех пользователей
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def change_role(user_id, new_role):
    # Обновление роли пользователя (admin/user)
    if new_role not in ("admin", "user"):
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()
    return True

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if get_user_role(user_id):
        user_state[update.effective_chat.id] = "main"
        await update.message.reply_text("Добро пожаловать!", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    else:
        await update.message.reply_text("⛔ У тебя нет доступа.")

# --- Основной обработчик текста ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    role = get_user_role(user_id)
    if role is None:
        await update.message.reply_text("⛔ У тебя нет доступа.")
        return

    state = user_state.get(chat_id, "main")  # Получаем текущее состояние пользователя

    # --- Главное меню ---
    if state == "main":
        if text == "💻 Включить ПК":
            from subprocess import run
            run(["wakeonlan", PC_MAC])  # MAC-адрес ПК
            await update.message.reply_text("ПК включён.")
        elif text == "🌐 IP адрес":
            from subprocess import check_output
            ip = check_output("hostname -I", shell=True).decode().strip()
            await update.message.reply_text(f"IP: {ip}")
        elif text == "🕒 Uptime":
            from subprocess import check_output
            uptime = check_output("uptime", shell=True).decode().strip()
            await update.message.reply_text(uptime)
        elif text == "⚙️ Админ-панель":
            if role != "admin":
                await update.message.reply_text("⛔ Только для админов.")
                return
            user_state[chat_id] = "admin"
            await update.message.reply_text("Админ-панель:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    # --- Админ-меню ---
    elif state == "admin":
        if text == "🔙 Назад":
            user_state[chat_id] = "main"
            await update.message.reply_text("Главное меню:", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
        elif text == "➕ Добавить пользователя":
            user_state[chat_id] = "awaiting_add_id"
            await update.message.reply_text("Введите ID нового пользователя:")
        elif text == "➖ Удалить пользователя":
            user_state[chat_id] = "awaiting_remove_id"
            await update.message.reply_text("Введите ID пользователя для удаления:")
        elif text == "🛠 Сменить роль":
            user_state[chat_id] = "awaiting_change_role_id"
            await update.message.reply_text("Введите ID пользователя для смены роли:")
        elif text == "📋 Список":
            users = list_users()
            reply = "\n".join([f"👤 {u[1]} (ID: {u[0]}, роль: {u[2]})" for u in users])
            await update.message.reply_text(reply or "Список пуст.")

    # --- Добавление нового пользователя ---
    elif state == "awaiting_add_id":
        context.user_data["new_id"] = int(text)
        user_state[chat_id] = "awaiting_add_username"
        await update.message.reply_text("Введите username:")

    elif state == "awaiting_add_username":
        context.user_data["new_username"] = text
        user_state[chat_id] = "awaiting_add_role"
        await update.message.reply_text("Введите роль (user/admin):")

    elif state == "awaiting_add_role":
        uid = context.user_data["new_id"]
        uname = context.user_data["new_username"]
        role = text.strip().lower()
        if role in ("user", "admin"):
            add_user(uid, uname, role)
            await update.message.reply_text(f"✅ Добавлен {uname} ({uid}) с ролью {role}")
        else:
            await update.message.reply_text("⚠️ Неверная роль.")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Админ-панель:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    # --- Удаление пользователя ---
    elif state == "awaiting_remove_id":
        remove_user(int(text))
        await update.message.reply_text("✅ Пользователь удалён")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Админ-панель:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

    # --- Смена роли пользователя ---
    elif state == "awaiting_change_role_id":
        context.user_data["change_id"] = int(text)
        user_state[chat_id] = "awaiting_new_role"
        await update.message.reply_text("Введите новую роль (user/admin):")

    elif state == "awaiting_new_role":
        uid = context.user_data["change_id"]
        role = text.strip().lower()
        if change_role(uid, role):
            await update.message.reply_text(f"Роль пользователя {uid} обновлена до {role}")
        else:
            await update.message.reply_text("⚠️ Ошибка смены роли.")
        user_state[chat_id] = "admin"
        await update.message.reply_text("Админ-панель:", reply_markup=ReplyKeyboardMarkup(ADMIN_MENU, resize_keyboard=True))

# --- Блокировка нестандартных сообщений ---
async def block_others(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Игнорируем фото, документы, голосовые и т.п.

# --- Основной запуск приложения ---
def main():
    init_db()  # Создаём базу данных при старте
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(~filters.TEXT, block_others))
    app.run_polling()

if __name__ == "__main__":
    main()
