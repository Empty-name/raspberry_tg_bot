#!/bin/bash

# This script creates a startup systemd service for the Telegram bot

SERVICE_NAME=telegrambot
BOT_PATH="$(pwd)"
SCRIPT_NAME=start_bot
SCRIPT_PATH="$BOT_PATH/$SCRIPT_NAME"

# Create launcher script with correct venv execution
cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
cd "$BOT_PATH"
$BOT_PATH/venv/bin/python rbp_bot.py
EOF
chmod +x "$SCRIPT_PATH"

# Create systemd service
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Telegram Admin Bot
After=network.target

[Service]
ExecStart=$SCRIPT_PATH
WorkingDirectory=$BOT_PATH
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ Bot is now set to run at system startup as '$SERVICE_NAME'."
