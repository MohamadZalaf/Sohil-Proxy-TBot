@echo off
title Virtual Environment Setup for Proxy Bot
color 0B
echo Virtual Environment Setup for Proxy Bot
echo ==========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or newer from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo SUCCESS: Python found
python --version
echo.

REM Check if pip is available
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo SUCCESS: pip found
pip --version
echo.

REM Remove existing virtual environment if it exists
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
    echo Virtual environment removed
    echo.
)

REM Create new virtual environment
echo Creating new virtual environment...
echo This may take a moment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure you have sufficient permissions
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Virtual environment activated
echo.

REM Upgrade pip to latest version
echo Upgrading pip to latest version...
python -m pip install --upgrade pip
echo.

REM Check if requirements.txt exists and fix it
if not exist "requirements.txt" (
    echo Creating requirements.txt file...
    echo flask==2.3.3> requirements.txt
    echo flask-cors==4.0.0>> requirements.txt
    echo requests==2.31.0>> requirements.txt
    echo SUCCESS: requirements.txt created
    echo.
) else (
    echo Checking requirements.txt for sqlite3...
    findstr /i "sqlite3" requirements.txt >nul 2>&1
    if %errorlevel% equ 0 (
        echo WARNING: Found sqlite3 in requirements.txt
        echo sqlite3 is built into Python and should not be in requirements.txt
        echo Creating corrected requirements.txt...
        echo flask==2.3.3> requirements_fixed.txt
        echo flask-cors==4.0.0>> requirements_fixed.txt
        echo requests==2.31.0>> requirements_fixed.txt
        move requirements.txt requirements_backup.txt
        move requirements_fixed.txt requirements.txt
        echo SUCCESS: requirements.txt has been corrected
        echo Original file backed up as requirements_backup.txt
        echo.
    )
)

REM Install requirements
echo Installing requirements from requirements.txt...
echo This may take a few minutes...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install some requirements
    echo Please check the requirements.txt file and your internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Virtual Environment Setup Complete!
echo ============================================
echo.
echo The virtual environment has been created and all requirements installed successfully.
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
echo IMPORTANT NOTES:
echo • sqlite3 is built into Python - no need to install it separately
echo • All Flask dependencies have been installed successfully
echo • You can now run your Proxy Bot with: python start_bot.py
echo.
echo Press any key to exit...
pause >nul