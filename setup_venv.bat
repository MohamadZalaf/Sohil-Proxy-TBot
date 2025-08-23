@echo off
echo Virtual Environment Setup for Proxy Bot
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or newer from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip found:
pip --version
echo.

REM Remove existing virtual environment if it exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
    echo.
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    echo Make sure you have sufficient permissions
    pause
    exit /b 1
)

echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Upgrade pip to latest version
echo Upgrading pip to latest version...
python -m pip install --upgrade pip

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Warning: requirements.txt not found in current directory
    echo Creating a basic requirements.txt file...
    echo flask==2.3.3> requirements.txt
    echo flask-cors==4.0.0>> requirements.txt
    echo requests==2.31.0>> requirements.txt
    echo.
)

REM Install requirements
echo Installing requirements from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install some requirements
    echo Please check the requirements.txt file and your internet connection
    pause
    exit /b 1
)

echo.
echo ============================================
echo Virtual Environment Setup Complete!
echo ============================================
echo.
echo The virtual environment has been created and requirements installed.
echo.
echo To use the virtual environment:
echo 1. Run: call venv\Scripts\activate.bat
echo 2. Your prompt will show (venv) when activated
echo 3. Run your Python scripts normally
echo 4. To deactivate: run "deactivate"
echo.
echo Virtual environment location: %cd%\venv
echo Python executable: %cd%\venv\Scripts\python.exe
echo.
echo You can now run your Proxy Bot with: python start_bot.py
echo.

pause