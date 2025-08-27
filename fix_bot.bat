@echo off
echo ========================================
echo      إصلاح مشاكل البوت
echo ========================================
echo.

:: حذف ملف القفل إذا كان موجوداً
if exist bot.lock (
    echo 🗑️ حذف ملف القفل القديم...
    del bot.lock
    echo ✅ تم حذف ملف القفل
) else (
    echo ℹ️ لا يوجد ملف قفل للحذف
)

:: إيقاف أي عمليات Python تحتوي على proxy_bot
echo 🔍 البحث عن عمليات البوت القديمة...
tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe" >nul
if not errorlevel 1 (
    echo ⚠️ تم العثور على عمليات Python، يرجى إيقافها يدوياً إذا كانت متعلقة بالبوت
    echo أو استخدم مدير المهام لإيقاف العمليات
)

:: إعادة تثبيت المتطلبات
echo 🔧 إعادة تثبيت المتطلبات...
pip install --upgrade -r requirements.txt

echo.
echo ✅ تم الانتهاء من الإصلاح
echo يمكنك الآن تشغيل البوت باستخدام start_bot.bat
pause