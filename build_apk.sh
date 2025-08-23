#!/bin/bash

echo "APK Build - Proxy Bot"
echo "Developer: Mohamad Zalaf (c)2025"
echo "================================"
echo ""

# Check requirements
echo "Checking requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install it first"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install it first"
    exit 1
fi

echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"

# Install requirements
echo ""
echo "Installing requirements..."
npm install

# Check Expo CLI
if ! command -v expo &> /dev/null; then
    echo "Installing Expo CLI..."
    npm install -g @expo/cli
fi

# Check EAS CLI
if ! command -v eas &> /dev/null; then
    echo "Installing EAS CLI..."
    npm install -g eas-cli
fi

echo ""
echo "Starting APK build..."
echo ""
echo "Choose build method:"
echo "1) EAS Build (Latest and Best)"
echo "2) Expo Build (Traditional)"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Building APK using EAS Build..."
        echo ""
        echo "You need to login to Expo first:"
        eas login
        
        echo ""
        echo "Setting up project..."
        eas build:configure
        
        echo ""
        echo "Building APK for production..."
        eas build --platform android --profile production
        
        echo ""
        echo "Build process started!"
        echo "You will get a download link soon"
        echo "Or check: https://expo.dev/"
        ;;
        
    2)
        echo ""
        echo "Building APK using Expo Build..."
        echo ""
        echo "You need to login to Expo first:"
        expo login
        
        echo ""
        echo "Building APK..."
        expo build:android -t apk
        
        echo ""
        echo "Build process started!"
        echo "May take 10-20 minutes"
        echo "You will get a download link when finished"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Important notes:"
echo "• Keep the download link"
echo "• Transfer APK to your Android phone"
echo "• Enable 'Unknown sources' before installation"
echo "• Make sure to run the bot on computer first"
echo ""
echo "Thanks for using Proxy Bot!"
echo "Developer: Mohamad Zalaf (c)2025"