@echo off
echo ========================================
echo       تشغيل بوت البروكسي
echo ========================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python من: https://python.org
    pause
    exit /b 1
)

:: التحقق من وجود المتطلبات
echo 🔍 فحص المتطلبات...
python -c "import telegram" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ المتطلبات غير مثبتة، جاري التثبيت...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ فشل في تثبيت المتطلبات
        pause
        exit /b 1
    )
)

:: تشغيل البوت
echo 🚀 تشغيل البوت...
python proxy_bot.py

:: انتظار قبل الإغلاق
echo.
echo 📝 تم إيقاف البوت
pause