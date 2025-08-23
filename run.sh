#!/bin/bash

echo "🤖 بوت البروكسي - نظام إدارة البروكسيات المتقدم"
echo "================================================"
echo ""
echo "🚀 جاري بدء تشغيل البوت..."
echo ""

# تحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python3 غير مثبت"
    echo "يرجى تثبيت Python 3.7 أو أحدث"
    exit 1
fi

# إنشاء البيئة الافتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تثبيت المتطلبات
echo "🔧 تثبيت المتطلبات..."
pip install -r requirements.txt

# تشغيل البوت
echo ""
echo "✅ جاهز للتشغيل!"
echo ""
python start_bot.py