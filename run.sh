#!/bin/bash

echo "Proxy Bot - Advanced Proxy Management System"
echo "================================================"
echo ""
echo "Starting the bot..."
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python 3.7 or newer"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run the bot
echo ""
echo "Ready to run!"
echo ""
python start_bot.py