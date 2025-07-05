#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

# Dependency check
function check_dep() {
    if ! command -v "$1" &>/dev/null; then
        echo "Installing $1..."
        sudo apt update && sudo apt install -y "$1"
    fi
}

check_dep python3
check_dep python3-venv
check_dep python3-pip
check_dep wakeonlan
check_dep paramiko

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install python dependencies
pip install --upgrade pip
pip install python-telegram-bot==20.7 wakeonlan python-dotenv paramiko

# Request user settings
read -r -p "Enter Telegram Bot Token: " TOKEN
read -r -p "Enter PC MAC address for Wake-on-LAN: " PC_MAC
read -r -p "Enter PC local IP address for Wake-on-LAN: " PC_IP
read -r -p "Enter ssh User for PC services: " PC_SSH_USER
read -r -p "Enter ssh User's password for PC services: " PC_SSH_PASS
read -r -p "Enter your Telegram username (without @): " ADMIN_USERNAME

# Create .env file
cat <<EOF > .env
TOKEN="$TOKEN"
PC_MAC="$PC_MAC"
PC_IP="$PC_IP"
PC_SSH_USER = "$PC_SSH_USER"
PC_SSH_PASS = "$PC_SSH_PASS"
ADMIN_USERNAME="$ADMIN_USERNAME"
EOF

# Initialize database and add admin
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

# Make setup_start.sh executable and run it
chmod +x setup_start.sh
./setup_start.sh

# CLI menu for bot management
while true; do
    echo -e "\n${GREEN}Choose an action:${NC}"
    echo "1) Bot status"
    echo "2) Restart bot"
    echo "3) Stop bot"
    echo "4) Start bot"
    echo "0) Exit"
    read -p "> " choice
    case $choice in
        1) sudo systemctl status telegrambot --no-pager ;;
        2) sudo systemctl restart telegrambot ;;
        3) sudo systemctl stop telegrambot ;;
        4) sudo systemctl start telegrambot ;;
        0) break ;;
        *) echo "Invalid choice" ;;
    esac
done

echo -e "${GREEN}Installation complete!${NC}"
