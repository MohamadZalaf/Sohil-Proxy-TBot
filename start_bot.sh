#!/bin/bash

echo "🚀 بدء تشغيل بوت بيع البروكسيات..."
echo "📦 التحقق من المتطلبات..."

# تحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python3 أولاً."
    exit 1
fi

# تحقق من وجود pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip غير مثبت. يرجى تثبيت pip أولاً."
    exit 1
fi

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
pip3 install --break-system-packages -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ تم تثبيت المتطلبات بنجاح"
else
    echo "❌ فشل في تثبيت المتطلبات"
    exit 1
fi

# التحقق من وجود التوكن
if grep -q "TOKEN = \"\"" simpl_bot.py; then
    echo "⚠️  تحذير: لم يتم تعيين TOKEN في الملف. يرجى إضافة توكن البوت."
    echo "قم بتحرير الملف simpl_bot.py وضع التوكن في السطر الذي يحتوي على:"
    echo 'TOKEN = "YOUR_BOT_TOKEN_HERE"'
    echo ""
    read -p "هل تريد المتابعة؟ (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🎯 تشغيل البوت..."
echo "📝 لإيقاف البوت، اضغط Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# تشغيل البوت
python3 simpl_bot.py