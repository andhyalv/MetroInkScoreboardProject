#!/bin/bash

# -----------------------
# System update
# -----------------------
sudo apt update && sudo apt upgrade -y

# -----------------------
# Install system dependencies for OpenCV
# -----------------------
sudo apt install -y python3-pip python3-dev libjpeg-dev libpng-dev libtiff-dev \
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
libgtk-3-dev libatlas-base-dev gfortran ffmpeg

# -----------------------
# Setup Python virtual environment
# -----------------------
python3 -m venv ~/pi_env
source ~/pi_env/bin/activate

# -----------------------
# Upgrade pip
# -----------------------
pip install --upgrade pip

# -----------------------
# Install Python packages
# -----------------------
pip install -r ~/ScoreboardProject/requirements.txt

# -----------------------
# Permissions for camera
# -----------------------
sudo usermod -a -G video $USER

echo "✅ Raspberry Pi setup complete. Please reboot for camera permissions to take effect."
