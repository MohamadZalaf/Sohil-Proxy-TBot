#!/usr/bin/env python3

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# التوكن (استخدام التوكن الموجود)
TOKEN = "8408804784:AAGlBg9kGYwRhPXmvFr9mJpvTJLGWB3wABez7LA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأمر /start"""
    await update.message.reply_text('مرحباً! البوت يعمل بشكل صحيح!')

async def main():
    """الدالة الرئيسية"""
    print("🤖 اختبار البوت...")
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة معالج
    application.add_handler(CommandHandler("start", start))
    
    print("🚀 تشغيل البوت...")
    
    # تشغيل البوت
    try:
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == '__main__':
    asyncio.run(main())