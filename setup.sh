#!/bin/bash

# Update and install Python & pip
sudo apt update
sudo apt install -y python3 python3-pip

# Install Python packages from requirements.txt 
pip3 install -r requirements.txt  --break-system-packages


SERVICE_NAME="parser"
INSTALL_DIR="/etc/parser_service"
LOG_DIR="/var/log/parser_service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo " Installing $SERVICE_NAME as a background service..."

# Create log directory
sudo mkdir -p $LOG_DIR
sudo touch $LOG_DIR/output.log $LOG_DIR/error.log
sudo chmod 666 $LOG_DIR/*.log

# Copy systemd service unit file
sudo cp "$INSTALL_DIR/service/$SERVICE_NAME.service" "$SERVICE_FILE"

# Reload systemd and enable the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo " $SERVICE_NAME installed and started successfully!"
echo "Logs:"
echo "   → $LOG_DIR/output.log"
echo "   → $LOG_DIR/error.log"
