@echo off
echo 📱 بناء APK - بوت البروكسي
echo المطور: Mohamad Zalaf ©2025
echo ================================
echo.

REM التحقق من المتطلبات
echo 🔍 التحقق من المتطلبات...

REM تحقق من Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js غير مثبت. يرجى تثبيته أولاً
    pause
    exit /b 1
)

REM تحقق من npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm غير مثبت. يرجى تثبيته أولاً
    pause
    exit /b 1
)

echo ✅ Node.js متوفر
echo ✅ npm متوفر

REM تثبيت المتطلبات
echo.
echo 📦 تثبيت المتطلبات...
npm install

REM تحقق من وجود Expo CLI
expo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 تثبيت Expo CLI...
    npm install -g @expo/cli
)

REM تحقق من وجود EAS CLI
eas --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔧 تثبيت EAS CLI...
    npm install -g eas-cli
)

echo.
echo 🚀 بدء بناء APK...
echo.
echo اختر طريقة البناء:
echo 1^) EAS Build ^(الأحدث والأفضل^)
echo 2^) Expo Build ^(التقليدية^)
echo.
set /p choice=أدخل اختيارك (1 أو 2): 

if "%choice%"=="1" (
    echo.
    echo 🔧 بناء APK باستخدام EAS Build...
    echo.
    echo تحتاج لتسجيل الدخول في Expo أولاً:
    eas login
    
    echo.
    echo إعداد المشروع...
    eas build:configure
    
    echo.
    echo بناء APK للإنتاج...
    eas build --platform android --profile production
    
    echo.
    echo ✅ تم بدء عملية البناء!
    echo 🔗 ستحصل على رابط التنزيل قريباً
    echo 📱 أو تحقق من: https://expo.dev/
    
) else if "%choice%"=="2" (
    echo.
    echo 🔧 بناء APK باستخدام Expo Build...
    echo.
    echo تحتاج لتسجيل الدخول في Expo أولاً:
    expo login
    
    echo.
    echo بناء APK...
    expo build:android -t apk
    
    echo.
    echo ✅ تم بدء عملية البناء!
    echo ⏳ قد يستغرق 10-20 دقيقة
    echo 🔗 ستحصل على رابط التنزيل عند الانتهاء
    
) else (
    echo ❌ اختيار غير صحيح
    pause
    exit /b 1
)

echo.
echo 📋 ملاحظات مهمة:
echo • احتفظ برابط التنزيل
echo • انقل APK لهاتفك الأندرويد
echo • فعّل 'مصادر غير معروفة' قبل التثبيت
echo • تأكد من تشغيل البوت على الكمبيوتر أولاً
echo.
echo 🎉 شكراً لاستخدام بوت البروكسي!
echo 👨‍💻 المطور: Mohamad Zalaf ©2025

pause