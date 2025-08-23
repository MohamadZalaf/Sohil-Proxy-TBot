@echo off
echo 🤖 بوت البروكسي - نظام إدارة البروكسيات المتقدم
echo ================================================
echo.
echo 🚀 جاري بدء تشغيل البوت...
echo.

REM تحقق من وجود Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.7 أو أحدث
    pause
    exit /b 1
)

REM تثبيت المتطلبات إذا لم تكن مثبتة
if not exist "venv" (
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv venv
)

REM تفعيل البيئة الافتراضية
call venv\Scripts\activate.bat

REM تثبيت المتطلبات
echo 🔧 تثبيت المتطلبات...
pip install -r requirements.txt

REM تشغيل البوت
echo.
echo ✅ جاهز للتشغيل!
echo.
python start_bot.py

pause