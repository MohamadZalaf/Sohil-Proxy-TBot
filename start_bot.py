#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import time

def install_requirements():
    """تثبيت المتطلبات"""
    print("🔧 جاري تثبيت المتطلبات...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت المتطلبات بنجاح")
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المتطلبات")
        return False
    return True

def start_bot_server():
    """تشغيل خادم البوت"""
    print("🚀 جاري تشغيل خادم البوت...")
    try:
        import telegram_proxy_bot
        print("✅ تم تشغيل البوت بنجاح")
        print("🌐 الخادم يعمل على: http://localhost:5000")
        print("📱 يمكنك الآن استخدام تطبيق الإدارة")
        print("🔧 معرف الأدمن: 6891599955")
        print("\n" + "="*50)
        print("📋 معلومات مهمة:")
        print("• البوت يعمل على سيرفر محلي")
        print("• تأكد من اتصال الإنترنت")
        print("• لإيقاف البوت اضغط Ctrl+C")
        print("="*50 + "\n")
        
        # تشغيل البوت تلقائياً عند بدء الخادم
        time.sleep(2)
        print("🤖 جاري بدء البوت تلقائياً...")
        
        # إرسال طلب لبدء البوت
        import requests
        try:
            response = requests.post('http://localhost:5000/api/bot/start', 
                                   json={'admin_id': '6891599955'})
            if response.json().get('success'):
                print("✅ تم بدء البوت تلقائياً")
            else:
                print("⚠️ البوت يعمل بالفعل")
        except:
            print("⚠️ سيتم بدء البوت يدوياً من التطبيق")
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد البوت: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        return False
    
    return True

def main():
    """الدالة الرئيسية"""
    print("🤖 مرحباً بك في بوت البروكسي!")
    print("📱 نظام إدارة البروكسيات المتقدم")
    print("\n" + "="*50)
    
    # تثبيت المتطلبات
    if not install_requirements():
        print("❌ فشل في التحضير. يرجى المحاولة مرة أخرى.")
        return
    
    print("\n🔄 جاري التحضير...")
    time.sleep(1)
    
    # تشغيل الخادم
    if start_bot_server():
        print("🎉 تم تشغيل النظام بنجاح!")
    else:
        print("❌ فشل في تشغيل النظام")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم إيقاف البوت بواسطة المستخدم")
        print("👋 شكراً لاستخدام بوت البروكسي!")
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        print("🔧 يرجى التحقق من الإعدادات والمحاولة مرة أخرى")