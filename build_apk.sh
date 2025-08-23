#!/bin/bash

echo "📱 بناء APK - بوت البروكسي"
echo "المطور: Mohamad Zalaf ©2025"
echo "================================"
echo ""

# التحقق من المتطلبات
echo "🔍 التحقق من المتطلبات..."

# تحقق من Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js غير مثبت. يرجى تثبيته أولاً"
    exit 1
fi

# تحقق من npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm غير مثبت. يرجى تثبيته أولاً"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"

# تثبيت المتطلبات
echo ""
echo "📦 تثبيت المتطلبات..."
npm install

# تحقق من وجود Expo CLI
if ! command -v expo &> /dev/null; then
    echo "🔧 تثبيت Expo CLI..."
    npm install -g @expo/cli
fi

# تحقق من وجود EAS CLI
if ! command -v eas &> /dev/null; then
    echo "🔧 تثبيت EAS CLI..."
    npm install -g eas-cli
fi

echo ""
echo "🚀 بدء بناء APK..."
echo ""
echo "اختر طريقة البناء:"
echo "1) EAS Build (الأحدث والأفضل)"
echo "2) Expo Build (التقليدية)"
echo ""
read -p "أدخل اختيارك (1 أو 2): " choice

case $choice in
    1)
        echo ""
        echo "🔧 بناء APK باستخدام EAS Build..."
        echo ""
        echo "تحتاج لتسجيل الدخول في Expo أولاً:"
        eas login
        
        echo ""
        echo "إعداد المشروع..."
        eas build:configure
        
        echo ""
        echo "بناء APK للإنتاج..."
        eas build --platform android --profile production
        
        echo ""
        echo "✅ تم بدء عملية البناء!"
        echo "🔗 ستحصل على رابط التنزيل قريباً"
        echo "📱 أو تحقق من: https://expo.dev/"
        ;;
        
    2)
        echo ""
        echo "🔧 بناء APK باستخدام Expo Build..."
        echo ""
        echo "تحتاج لتسجيل الدخول في Expo أولاً:"
        expo login
        
        echo ""
        echo "بناء APK..."
        expo build:android -t apk
        
        echo ""
        echo "✅ تم بدء عملية البناء!"
        echo "⏳ قد يستغرق 10-20 دقيقة"
        echo "🔗 ستحصل على رابط التنزيل عند الانتهاء"
        ;;
        
    *)
        echo "❌ اختيار غير صحيح"
        exit 1
        ;;
esac

echo ""
echo "📋 ملاحظات مهمة:"
echo "• احتفظ برابط التنزيل"
echo "• انقل APK لهاتفك الأندرويد"
echo "• فعّل 'مصادر غير معروفة' قبل التثبيت"
echo "• تأكد من تشغيل البوت على الكمبيوتر أولاً"
echo ""
echo "🎉 شكراً لاستخدام بوت البروكسي!"
echo "👨‍💻 المطور: Mohamad Zalaf ©2025"