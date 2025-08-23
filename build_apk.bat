@echo off
echo APK Build - Proxy Bot
echo Developer: Mohamad Zalaf (c)2025
echo ================================
echo.

REM Check requirements
echo Checking requirements...

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install it first
    pause
    exit /b 1
)

REM Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm is not installed. Please install it first
    pause
    exit /b 1
)

echo Node.js is available
echo npm is available

REM Install requirements
echo.
echo Installing requirements...
npm install

REM Check Expo CLI
expo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Expo CLI...
    npm install -g @expo/cli
)

REM Check EAS CLI
eas --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing EAS CLI...
    npm install -g eas-cli
)

echo.
echo Starting APK build...
echo.
echo Choose build method:
echo 1^) EAS Build ^(Latest and Best^)
echo 2^) Expo Build ^(Traditional^)
echo.
set /p choice=Enter your choice (1 or 2): 

if "%choice%"=="1" (
    echo.
    echo Building APK using EAS Build...
    echo.
    echo You need to login to Expo first:
    eas login
    
    echo.
    echo Setting up project...
    eas build:configure
    
    echo.
    echo Building APK for production...
    eas build --platform android --profile production
    
    echo.
    echo Build process started!
    echo You will get a download link soon
    echo Or check: https://expo.dev/
    
) else if "%choice%"=="2" (
    echo.
    echo Building APK using Expo Build...
    echo.
    echo You need to login to Expo first:
    expo login
    
    echo.
    echo Building APK...
    expo build:android -t apk
    
    echo.
    echo Build process started!
    echo May take 10-20 minutes
    echo You will get a download link when finished
    
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Important notes:
echo • Keep the download link
echo • Transfer APK to your Android phone
echo • Enable 'Unknown sources' before installation
echo • Make sure to run the bot on computer first
echo.
echo Thanks for using Proxy Bot!
echo Developer: Mohamad Zalaf (c)2025

pause