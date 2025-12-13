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

python run.py
