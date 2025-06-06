#!/bin/bash

# Update and install Python & pip
sudo apt update
sudo apt install -y python3 python3-pip

# Install Python packages from requirements.txt
pip3 install -r requirements.txt
