#!/bin/bash

set -e

# Цвета для вывода
GREEN='\033[0;32m'
NC='\033[0m'

# Проверка зависимостей
function check_dep() {
    if ! command -v "$1" &>/dev/null; then
        echo "Устанавливаю $1..."
        sudo apt update && sudo apt install -y "$1"
    fi
}

check_dep python3
check_dep python3-venv
check_dep python3-pip
check_dep wakeonlan

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Установка python-зависимостей
pip install --upgrade pip
pip install python-telegram-bot==20.7 wakeonlan python-dotenv

# Запрос настроек у пользователя
read -p "Введите Telegram Bot Token: " TOKEN
read -p "Введите MAC-адрес ПК для Wake-on-LAN: " PC_MAC
read -p "Введите ваш Telegram username (без @): " ADMIN_USERNAME

# Создание .env файла
cat <<EOF > .env
TOKEN="$TOKEN"
PC_MAC="$PC_MAC"
ADMIN_USERNAME="$ADMIN_USERNAME"
EOF

# Инициализация базы и добавление админа
source venv/bin/activate
python3 <<END
import sqlite3, os
from dotenv import load_dotenv
load_dotenv('.env')
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, role TEXT CHECK(role IN ("admin", "user")) NOT NULL)''')
c.execute('INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)', (os.getenv('ADMIN_USERNAME'), 'admin'))
conn.commit()
conn.close()
END

# Делаем setup_start.sh исполняемым и запускаем его
chmod +x setup_start.sh
./setup_start.sh

# CLI-меню управления ботом
while true; do
    echo -e "\n${GREEN}Выберите действие:${NC}"
    echo "1) Статус бота"
    echo "2) Перезапустить бота"
    echo "3) Остановить бота"
    echo "4) Запустить бота"
    echo "0) Выйти"
    read -p "> " choice
    case $choice in
        1) sudo systemctl status telegrambot --no-pager ;;
        2) sudo systemctl restart telegrambot ;;
        3) sudo systemctl stop telegrambot ;;
        4) sudo systemctl start telegrambot ;;
        0) break ;;
        *) echo "Неверный выбор" ;;
    esac
done

echo -e "${GREEN}Установка завершена!${NC}"
