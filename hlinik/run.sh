#!/bin/bash

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

echo "[IRIS] Booting System..."
source venv/bin/activate

# Check for .env (Optional but helpful to remind user)
# if [ ! -f ".env" ]; then
#     echo "[WARNING] .env file not found. System will run with defaults."
# fi

# Cleanup Port 8000
if fuser 8000/tcp >/dev/null 2>&1; then
    echo "[IRIS] Port 8000 in use. Killing old process..."
    fuser -k 8000/tcp >/dev/null 2>&1
    sleep 1
fi

python run.py
