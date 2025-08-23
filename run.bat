@echo off
echo Proxy Bot - Advanced Proxy Management System
echo ================================================
echo.
echo Starting the bot...
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or newer
    pause
    exit /b 1
)

REM Install requirements if not installed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run the bot
echo.
echo Ready to run!
echo.
python start_bot.py

pause