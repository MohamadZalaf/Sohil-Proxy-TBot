@echo off
title APK Build - Proxy Bot
color 0A
echo APK Build - Proxy Bot
echo Developer: Mohamad Zalaf (c)2025
echo ================================
echo.

REM Check requirements
echo Checking requirements...
echo.

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Make sure to add Node.js to your system PATH
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo SUCCESS: Node.js is installed
node --version
echo.

REM Check npm
echo Checking npm installation...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed or not accessible
    echo npm should come with Node.js installation
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo SUCCESS: npm is available
npm --version
echo.

REM Install requirements
echo Installing project dependencies...
echo This may take a few minutes...
echo.
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install npm dependencies
    echo Please check your internet connection and try again
    echo.
    pause
    exit /b 1
)
echo.

REM Check Expo CLI
echo Checking Expo CLI...
expo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Expo CLI not found. Installing Expo CLI...
    echo This may take a few minutes...
    npm install -g @expo/cli
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Expo CLI
        echo.
        pause
        exit /b 1
    )
)

echo SUCCESS: Expo CLI is available
expo --version
echo.

REM Check EAS CLI
echo Checking EAS CLI...
eas --version >nul 2>&1
if %errorlevel% neq 0 (
    echo EAS CLI not found. Installing EAS CLI...
    echo This may take a few minutes...
    npm install -g eas-cli
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install EAS CLI
        echo.
        pause
        exit /b 1
    )
)

echo SUCCESS: EAS CLI is available
eas --version
echo.

echo ================================
echo All requirements are satisfied!
echo ================================
echo.
echo Starting APK build process...
echo.
echo Choose build method:
echo 1) EAS Build (Latest and Best)
echo 2) Expo Build (Traditional)
echo 3) Exit
echo.
set /p choice=Enter your choice (1, 2, or 3): 

if "%choice%"=="1" (
    echo.
    echo ================================
    echo Building APK using EAS Build...
    echo ================================
    echo.
    echo You need to login to Expo first:
    echo Press any key to continue to login...
    pause >nul
    eas login
    
    echo.
    echo Setting up project configuration...
    eas build:configure
    
    echo.
    echo Starting APK build for production...
    echo This process will run on Expo servers and may take 10-30 minutes
    eas build --platform android --profile production
    
    echo.
    echo ================================
    echo Build process started!
    echo ================================
    echo You will receive a download link when the build is complete
    echo You can also check your build status at: https://expo.dev/
    echo.
    
) else if "%choice%"=="2" (
    echo.
    echo ================================
    echo Building APK using Expo Build...
    echo ================================
    echo.
    echo You need to login to Expo first:
    echo Press any key to continue to login...
    pause >nul
    expo login
    
    echo.
    echo Starting APK build...
    echo This process will run on Expo servers and may take 10-30 minutes
    expo build:android -t apk
    
    echo.
    echo ================================
    echo Build process started!
    echo ================================
    echo The build may take 10-20 minutes to complete
    echo You will receive a download link when finished
    echo.
    
) else if "%choice%"=="3" (
    echo.
    echo Exiting...
    echo.
    pause
    exit /b 0
    
) else (
    echo.
    echo ERROR: Invalid choice. Please enter 1, 2, or 3
    echo.
    pause
    goto :eof
)

echo.
echo ================================
echo Important Notes:
echo ================================
echo • Keep the download link safe
echo • Transfer the APK file to your Android device
echo • Enable 'Unknown sources' in Android settings before installation
echo • Make sure the bot is running on your computer before using the app
echo • The APK will be available for download from your Expo dashboard
echo.
echo ================================
echo Thanks for using Proxy Bot!
echo Developer: Mohamad Zalaf (c)2025
echo ================================
echo.
echo Press any key to exit...
pause >nul