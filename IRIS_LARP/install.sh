#!/bin/bash

echo "[IRIS] Starting Installation..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 could not be found."
    exit 1
fi

# Create Virtual Environment if not exists
if [ ! -d "venv" ]; then
    echo "[IRIS] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[IRIS] Virtual environment found."
fi

# Activate
echo "[IRIS] Activating virtual environment..."
source venv/bin/activate

# Install Requirements
if [ -f "requirements.txt" ]; then
    echo "[IRIS] Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[ERROR] requirements.txt not found!"
    exit 1
fi

echo "[IRIS] Installation Complete."
echo "[IRIS] Use './run.sh' to start the system."
