#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تيليجرام مبسط لبيع البروكسيات
Simple Proxy Bot - Simplified Version
"""

import os
import asyncio
import logging
import sqlite3
import json
import random
import string
import pandas as pd
import io
import csv
import openpyxl
import atexit
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

# تكوين اللوجينج
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الإعدادات الثابتة
ADMIN_PASSWORD = "sohilSOHIL"
TOKEN = "8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA"
DATABASE_FILE = "proxy_bot.db"
ADMIN_CHAT_ID = None  # سيتم تحديده عند أول تسجيل دخول للأدمن

# حالات المحادثة
(
    ADMIN_LOGIN, ADMIN_MENU, PROCESS_ORDER, 
    ENTER_PROXY_TYPE, ENTER_PROXY_ADDRESS, ENTER_PROXY_PORT,
    ENTER_COUNTRY, ENTER_STATE, ENTER_USERNAME, ENTER_PASSWORD,
    ENTER_THANK_MESSAGE, PAYMENT_PROOF, CUSTOM_MESSAGE,
    REFERRAL_AMOUNT, USER_LOOKUP, QUIET_HOURS, LANGUAGE_SELECTION,
    PAYMENT_METHOD_SELECTION, WITHDRAWAL_REQUEST, SET_PRICE_STATIC,
    SET_PRICE_SOCKS, ADMIN_ORDER_INQUIRY, BROADCAST_MESSAGE,
    BROADCAST_USERS, BROADCAST_CONFIRM, PACKAGE_MESSAGE, PACKAGE_CONFIRMATION,
    PACKAGE_ACTION_CHOICE, ADMIN_MESSAGE_INPUT

) = range(29)

# قواميس البيانات
STATIC_COUNTRIES = {
    'ar': {
        'DE': '🇩🇪 ألمانيا',
        'US': '🇺🇸 أميركا',
        'UK': '🇬🇧 بريطانيا',
        'FR': '🇫🇷 فرنسا'
    },
    'en': {
        'FR': '🇫🇷 France',
        'DE': '🇩🇪 Germany',
        'UK': '🇬🇧 United Kingdom',
        'US': '🇺🇸 United States'
    }
}

SOCKS_COUNTRIES = {
    'ar': {
        'US': '🇺🇸 أميركا',
        'UK': '🇬🇧 بريطانيا',
        'DE': '🇩🇪 ألمانيا',
        'FR': '🇫🇷 فرنسا',
        'CA': '🇨🇦 كندا',
        'AU': '🇦🇺 أستراليا',
        'AT': '🇦🇹 النمسا',
        'AL': '🇦🇱 ألبانيا',
        'UA': '🇺🇦 أوكرانيا',
        'IE': '🇮🇪 أيرلندا',
        'IS': '🇮🇸 أيسلندا',
        'EE': '🇪🇪 إستونيا',
        'ES': '🇪🇸 إسبانيا',
        'IT': '🇮🇹 إيطاليا',
        'AE': '🇦🇪 الإمارات العربية المتحدة'
    },
    'en': {
        'US': '🇺🇸 United States',
        'UK': '🇬🇧 United Kingdom',
        'DE': '🇩🇪 Germany',
        'FR': '🇫🇷 France',
        'CA': '🇨🇦 Canada',
        'AU': '🇦🇺 Australia',
        'AT': '🇦🇹 Austria',
        'AL': '🇦🇱 Albania',
        'UA': '🇺🇦 Ukraine',
        'IE': '🇮🇪 Ireland',
        'IS': '🇮🇸 Iceland',
        'EE': '🇪🇪 Estonia',
        'ES': '🇪🇸 Spain',
        'IT': '🇮🇹 Italy',
        'AE': '🇦🇪 United Arab Emirates'
    }
}

# رسائل النظام
MESSAGES = {
    'ar': {
        'welcome': """🎯 مرحباً بك في بوت بيع البروكسيات

اختر الخدمة المطلوبة من الأزرار أدناه:""",
        'static_package': """📦 Static Package

🔹 الأسعار:
- Static ISP Risk0: `3$`
- Static Residential Verizon: `4$`  
- Static Residential AT&T: `6$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع (صورة فقط) للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{}`""",
        'socks_package': """📦 Socks Package
كافة دول العالم مع ميزة اختيار الولاية والمزود للبكج

🔹 الأسعار:
- باكج 5 بروكسيات مؤقتة: `0.4$`
- باكج 10 بروكسيات مؤقتة: `0.7$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع (صورة فقط) للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{}`""",
        'select_country': 'اختر الدولة:',
        'select_state': 'اختر الولاية:',
        'manual_input': 'إدخال يدوي',
        'payment_methods': 'اختر طريقة الدفع:',
        'send_payment_proof': 'يرجى إرسال إثبات الدفع (صورة فقط):',
        'order_received': '✅ تم استلام طلبك بنجاح!\n\n📋 سيتم معالجة الطلب يدوياً من الأدمن بأقرب وقت.\n\n📧 ستصلك تحديثات الحالة تلقائياً.',
        'main_menu_buttons': ['🔒 طلب بروكسي ستاتيك', '📡 طلب بروكسي سوكس', '👥 إحالاتي', '📋 تذكير بطلباتي', '⚙️ الإعدادات'],
        'admin_main_buttons': ['📋 إدارة الطلبات', '💰 إدارة الأموال', '👥 الإحالات', '📢 البث', '⚙️ الإعدادات'],
        'admin_panel': '🔧 لوحة الأدمن',
        'manage_orders': 'إدارة الطلبات',
        'pending_orders': 'الطلبات المعلقة',
        'admin_login_prompt': 'يرجى إدخال كلمة المرور:',
        'about_bot': """🤖 حول البوت

📦 بوت بيع البروكسي وإدارة البروكسي
🔢 الإصدار: 1.0.0

━━━━━━━━━━━━━━━
🧑‍💻 طُور بواسطة: Mohamad Zalaf

📞 معلومات الاتصال:
📱 تليجرام: @MohamadZalaf
📧 البريد الإلكتروني: 
   • MohamadZalaf@outlook.com
   • Mohamadzalaf2017@gmail.com

━━━━━━━━━━━━━━━
© Mohamad Zalaf 2025"""
    }
}

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'ar',
                referral_balance REAL DEFAULT 0.0,
                referred_by INTEGER,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # جدول الطلبات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                proxy_type TEXT,
                country TEXT,
                state TEXT,
                payment_method TEXT,
                payment_amount REAL,
                payment_proof TEXT,
                quantity TEXT DEFAULT 'واحد',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                proxy_details TEXT,
                truly_processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                amount REAL DEFAULT 0.1,
                activated BOOLEAN DEFAULT FALSE,
                activated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str, referred_by: int = None):
        """إضافة مستخدم جديد"""
        query = '''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, referred_by)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (user_id, username, first_name, last_name, referred_by))
    
    def get_user(self, user_id: int) -> Optional[tuple]:
        """الحصول على بيانات المستخدم"""
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create_order(self, order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_method: str, payment_amount: float = 0.0, quantity: str = "واحد"):
        """إنشاء طلب جديد"""
        query = '''
            INSERT INTO orders (id, user_id, proxy_type, country, state, payment_method, payment_amount, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (order_id, user_id, proxy_type, country, state, payment_method, payment_amount, quantity))
    
    def update_order_payment_proof(self, order_id: str, payment_proof: str):
        """تحديث إثبات الدفع للطلب"""
        query = "UPDATE orders SET payment_proof = ? WHERE id = ?"
        self.execute_query(query, (payment_proof, order_id))
    
    def get_pending_orders(self) -> List[tuple]:
        """الحصول على الطلبات المعلقة"""
        query = "SELECT * FROM orders WHERE status = 'pending'"
        return self.execute_query(query)

# إنشاء مدير قاعدة البيانات
db = DatabaseManager(DATABASE_FILE)

def generate_order_id() -> str:
    """إنشاء معرف طلب فريد مكون من 16 خانة"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_user_language(user_id: int) -> str:
    """الحصول على لغة المستخدم"""
    user = db.get_user(user_id)
    return user[4] if user else 'ar'  # اللغة في العمود الخامس

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر البداية"""
    user = update.effective_user
    
    # التحقق من وجود المستخدم مسبقاً
    existing_user = db.get_user(user.id)
    is_new_user = existing_user is None
    
    # إضافة المستخدم إلى قاعدة البيانات
    referred_by = None
    if context.args and is_new_user:
        try:
            referred_by = int(context.args[0])
            # التأكد من أن المحيل موجود
            referrer = db.get_user(referred_by)
            if not referrer:
                referred_by = None
        except ValueError:
            pass
    
    db.add_user(user.id, user.username, user.first_name, user.last_name, referred_by)
    
    language = get_user_language(user.id)
    
    # رسالة ترحيب للمستخدمين الجدد
    if is_new_user:
        welcome_message = MESSAGES[language]['welcome']
        if referred_by:
            welcome_message += f"\n\n🎁 مرحباً بك! لقد انضممت عبر رابط إحالة وحصل صديقك على مكافأة!"
    else:
        welcome_message = f"مرحباً بعودتك {user.first_name}! 😊\n\n" + MESSAGES[language]['welcome']
    
    # إنشاء الأزرار الرئيسية
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][3]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تسجيل دخول الأدمن"""
    language = get_user_language(update.effective_user.id)
    await update.message.reply_text(MESSAGES[language]['admin_login_prompt'])
    return ADMIN_LOGIN

async def handle_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """التحقق من كلمة مرور الأدمن"""
    global ADMIN_PASSWORD
    if update.message.text == ADMIN_PASSWORD:
        global ADMIN_CHAT_ID
        context.user_data['is_admin'] = True
        ADMIN_CHAT_ID = update.effective_user.id  # حفظ معرف الأدمن
        
        # حذف رسالة كلمة المرور من المحادثة لأسباب أمنية
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except Exception as e:
            print(f"تعذر حذف رسالة كلمة المرور: {e}")
        
        # لوحة مفاتيح عادية للأدمن
        keyboard = [
            [KeyboardButton("📋 عرض الطلبات المعلقة")],
            [KeyboardButton("💬 إرسال رسالة للمستخدم")],
            [KeyboardButton("🚪 تسجيل الخروج")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🔧 مرحباً بك في لوحة الأدمن المبسطة\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("كلمة المرور غير صحيحة!")
        return ConversationHandler.END

async def handle_static_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب البروكسي الستاتيك"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'static'
    
    # عرض رسالة الحزمة بدون معرف الطلب
    package_message = MESSAGES[language]['static_package'].replace('معرف الطلب: `{}`', 'سيتم إنشاء معرف الطلب بعد إرسال إثبات الدفع')
    await update.message.reply_text(package_message, parse_mode='Markdown')
    
    # عرض أزرار اختيار الدولة مباشرة
    countries = STATIC_COUNTRIES.get(language, STATIC_COUNTRIES['ar'])
    
    keyboard = []
    for code, name in countries.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_user_proxy_request")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        MESSAGES[language]['select_country'],
        reply_markup=reply_markup
    )

async def handle_socks_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب بروكسي السوكس"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'socks'
    
    # عرض رسالة الحزمة بدون معرف الطلب
    package_message = MESSAGES[language]['socks_package'].replace('معرف الطلب: `{}`', 'سيتم إنشاء معرف الطلب بعد إرسال إثبات الدفع')
    await update.message.reply_text(package_message, parse_mode='Markdown')
    
    # عرض أزرار اختيار الدولة مباشرة
    countries = SOCKS_COUNTRIES.get(language, SOCKS_COUNTRIES['ar'])
    
    keyboard = []
    for code, name in countries.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_user_proxy_request")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        MESSAGES[language]['select_country'],
        reply_markup=reply_markup
    )

async def handle_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار الدولة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    if query.data == "manual_country":
        # الإدخال اليدوي للدولة
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="cancel_manual_input")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("يرجى إدخال اسم الدولة يدوياً:", reply_markup=reply_markup)
        context.user_data['waiting_for'] = 'manual_country'
        return
    
    elif query.data.startswith("country_"):
        country_code = query.data.replace("country_", "")
        # حفظ اسم الدولة الكامل مع العلم بدلاً من الرمز فقط
        proxy_type = context.user_data.get('proxy_type', 'static')
        if proxy_type == 'socks':
            country_name = SOCKS_COUNTRIES[language].get(country_code, country_code)
        else:
            country_name = STATIC_COUNTRIES[language].get(country_code, country_code)
        context.user_data['selected_country'] = country_name
        
        # الانتقال مباشرة لطرق الدفع (تبسيط)
        await show_payment_methods(query, context, language)

async def show_payment_methods(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """عرض طرق الدفع"""
    keyboard = [
        [InlineKeyboardButton("💳 شام كاش", callback_data="payment_shamcash")],
        [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="payment_syriatel")],
        [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
        [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
        [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        MESSAGES[language]['payment_methods'],
        reply_markup=reply_markup
    )

async def handle_payment_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار طريقة الدفع"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    payment_method = query.data.replace("payment_", "")
    context.user_data['payment_method'] = payment_method
    
    # إضافة زر الإلغاء
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="cancel_payment_proof")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[language]['send_payment_proof'],
        reply_markup=reply_markup
    )
    
    return PAYMENT_PROOF

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إثبات الدفع - صور فقط"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من وجود البيانات المطلوبة
    if 'proxy_type' not in context.user_data:
        await update.message.reply_text(
            "❌ خطأ: لم يتم العثور على نوع البروكسي. يرجى البدء من جديد بالضغط على /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # التحقق من أن الرسالة تحتوي على صورة
    if not update.message.photo:
        # رفض أي نوع آخر غير الصورة
        await update.message.reply_text(
            "❌ يُسمح بإرسال الصور فقط كإثبات للدفع!\n\n📸 يرجى إرسال صورة واضحة لإثبات الدفع\n\n⏳ البوت ينتظر صورة إثبات الدفع أو يمكنك الإلغاء",
            parse_mode='Markdown'
        )
        return PAYMENT_PROOF  # البقاء في نفس الحالة

    # إنشاء معرف الطلب الآن فقط عند إرسال إثبات الدفع
    order_id = generate_order_id()
    context.user_data['current_order_id'] = order_id
    
    # إنشاء الطلب في قاعدة البيانات
    proxy_type = context.user_data.get('proxy_type', 'static')
    country = context.user_data.get('selected_country', 'manual')
    state = context.user_data.get('selected_state', 'manual')
    payment_method = context.user_data.get('payment_method', 'unknown')
    
    # حساب سعر البروكسي
    payment_amount = 3.0 if proxy_type == 'static' else 0.4  # أسعار بسيطة
    
    # إنشاء الطلب في قاعدة البيانات
    db.create_order(order_id, user_id, proxy_type, country, state, payment_method, payment_amount, "واحد")
    
    # معالجة إثبات الدفع (صورة)
    file_id = update.message.photo[-1].file_id
    payment_proof = f"photo:{file_id}"
    
    # حفظ إثبات الدفع في قاعدة البيانات
    db.update_order_payment_proof(order_id, payment_proof)
    
    # إرسال نسخة للمستخدم
    await update.message.reply_photo(
        photo=file_id,
        caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`\n\n✅ تم حفظ إثبات الدفع بنجاح",
        parse_mode='Markdown'
    )
    
    # إرسال إشعار مبسط للأدمن
    await send_simple_admin_notification(context, order_id, payment_proof)
    
    # إرسال رسالة تأكيد للمستخدم
    await update.message.reply_text(MESSAGES[language]['order_received'], parse_mode='Markdown')
    
    # تنظيف البيانات المؤقتة
    context.user_data.clear()
    
    return ConversationHandler.END

async def send_simple_admin_notification(context: ContextTypes.DEFAULT_TYPE, order_id: str, payment_proof: str = None) -> None:
    """إرسال إشعار بسيط للأدمن بطلب جديد"""
    if not ADMIN_CHAT_ID:
        return
    
    # إرسال إشعار بسيط
    message = f"🔔 لديك طلب جديد\n\n🆔 معرف الطلب: `{order_id}`"
    
    keyboard = [[InlineKeyboardButton("📋 عرض الطلب", callback_data=f"view_order_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            ADMIN_CHAT_ID, 
            message, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"خطأ في إرسال إشعار الأدمن: {e}")

async def show_pending_orders_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض الطلبات المعلقة للأدمن"""
    pending_orders = db.get_pending_orders()
    
    if not pending_orders:
        await update.message.reply_text("✅ لا توجد طلبات معلقة حالياً.")
        return
    
    message = f"📋 **الطلبات المعلقة** - المجموع: {len(pending_orders)} طلب\n\n"
    
    # عرض أول 10 طلبات
    for i, order in enumerate(pending_orders[:10], 1):
        message += f"{i}. 🆔 `{order[0]}`\n"
        message += f"   📦 النوع: {order[2]}\n"
        message += f"   🌍 الدولة: {order[3]}\n"
        message += f"   💰 المبلغ: {order[6]}$\n"
        message += f"   📅 التاريخ: {order[9]}\n\n"
    
    # إنشاء أزرار للطلبات
    keyboard = []
    for order in pending_orders[:5]:  # أول 5 طلبات
        keyboard.append([InlineKeyboardButton(f"📋 طلب {order[0][:8]}...", callback_data=f"view_order_{order[0]}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_view_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض تفاصيل الطلب مع التوثيق"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("view_order_", "")
    
    # الحصول على تفاصيل الطلب
    order_query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(order_query, (order_id,))
    
    if not result:
        await query.edit_message_text("❌ لم يتم العثور على الطلب")
        return
    
    order = result[0]
    
    # تحديد طريقة الدفع باللغة العربية
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    
    payment_method_ar = payment_methods_ar.get(order[5], order[5])
    
    message = f"""📋 تفاصيل الطلب

👤 الاسم: `{order[14]} {order[15] or ''}`
📱 اسم المستخدم: @{order[16] or 'غير محدد'}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🔧 نوع البروكسي: {order[2]}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
💵 قيمة الطلب: `{order[6]}$`
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order_id}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""

    # إنشاء أزرار الإجراءات
    keyboard = [
        [InlineKeyboardButton("💬 إرسال رسالة للمستخدم", callback_data=f"send_message_{order_id}")],
        [InlineKeyboardButton("✅ قبول الطلب", callback_data=f"accept_order_{order_id}")],
        [InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_order_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # إرسال إثبات الدفع كرد على رسالة الطلب
    if order[7] and order[7].startswith("photo:"):
        file_id = order[7].replace("photo:", "")
        await context.bot.send_photo(
            update.effective_chat.id,
            photo=file_id,
            caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
            parse_mode='Markdown',
            reply_to_message_id=query.message.message_id
        )

async def handle_send_message_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء إرسال رسالة للمستخدم"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("send_message_", "")
    context.user_data['target_order_id'] = order_id
    
    keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="cancel_admin_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💬 إرسال رسالة للمستخدم\n\nاكتب الرسالة التي تريد إرسالها:",
        reply_markup=reply_markup
    )
    
    return ADMIN_MESSAGE_INPUT

async def handle_admin_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة الأدمن"""
    admin_message = update.message.text
    order_id = context.user_data.get('target_order_id')
    
    if not order_id:
        await update.message.reply_text("❌ خطأ: لم يتم العثور على معرف الطلب")
        return ConversationHandler.END
    
    # الحصول على معرف المستخدم من الطلب
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        
        # إرسال الرسالة للمستخدم
        user_message = f"""📩 رسالة من الإدارة

{admin_message}

━━━━━━━━━━━━━━━
🆔 بخصوص الطلب: `{order_id}`"""
        
        try:
            await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
            await update.message.reply_text(f"✅ تم إرسال الرسالة للمستخدم بنجاح!\n\n📋 الطلب: `{order_id}`", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ فشل في إرسال الرسالة: {str(e)}")
    else:
        await update.message.reply_text("❌ لم يتم العثور على المستخدم")
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('target_order_id', None)
    
    return ConversationHandler.END

async def handle_accept_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قبول الطلب"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("accept_order_", "")
    
    # تحديث حالة الطلب
    db.execute_query("UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
    
    # الحصول على معرف المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user_language = get_user_language(user_id)
        
        # إرسال رسالة للمستخدم
        user_message = f"""✅ تم قبول طلبك!

🆔 معرف الطلب: `{order_id}`

سيتم إرسال تفاصيل البروكسي قريباً."""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
    
    await query.edit_message_text(f"✅ تم قبول الطلب `{order_id}` بنجاح!", parse_mode='Markdown')

async def handle_reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رفض الطلب"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("reject_order_", "")
    
    # تحديث حالة الطلب
    db.execute_query("UPDATE orders SET status = 'failed', processed_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
    
    # الحصول على معرف المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user_language = get_user_language(user_id)
        
        # إرسال رسالة للمستخدم
        user_message = f"""❌ تم رفض طلبك

🆔 معرف الطلب: `{order_id}`

📞 يرجى التواصل مع الدعم: @Static_support"""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
    
    await query.edit_message_text(f"❌ تم رفض الطلب `{order_id}`", parse_mode='Markdown')

async def handle_about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة أمر /about"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # رسالة حول البوت
    about_message = MESSAGES[language]['about_bot']
    
    # إنشاء زر للمطور يعمل بشكل صحيح
    keyboard = [[InlineKeyboardButton("🧑‍💻 معلومات المطور", url="https://t.me/MohamadZalaf")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال الرسالة مع الزر
    await update.message.reply_text(
        about_message, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_cancel_user_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إلغاء طلب البروكسي من قبل المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # تنظيف البيانات المؤقتة
    context.user_data.clear()
    
    await query.edit_message_text("❌ تم إلغاء طلب البروكسي")
    
    # إرسال القائمة الرئيسية مرة أخرى
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][3]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await context.bot.send_message(
        user_id,
        MESSAGES[language]['welcome'],
        reply_markup=reply_markup
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الاستعلامات المرسلة"""
    query = update.callback_query
    
    try:
        await query.answer()
    except:
        pass
    
    if query.data.startswith("country_") or query.data == "manual_country":
        await handle_country_selection(update, context)
    elif query.data.startswith("payment_"):
        await handle_payment_method_selection(update, context)
    elif query.data == "cancel_user_proxy_request":
        await handle_cancel_user_proxy_request(update, context)
    elif query.data.startswith("view_order_"):
        await handle_view_order(update, context)
    elif query.data.startswith("send_message_"):
        await handle_send_message_to_user(update, context)
    elif query.data.startswith("accept_order_"):
        await handle_accept_order(update, context)
    elif query.data.startswith("reject_order_"):
        await handle_reject_order(update, context)

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل النصية"""
    text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    is_admin = context.user_data.get('is_admin', False)
    
    # معالجة الإدخال اليدوي للدول
    waiting_for = context.user_data.get('waiting_for')
    if waiting_for == 'manual_country':
        context.user_data['selected_country'] = text
        context.user_data.pop('waiting_for', None)
        await update.message.reply_text(f"تم اختيار الدولة: {text}")
        
        # الانتقال لطرق الدفع
        keyboard = [
            [InlineKeyboardButton("💳 شام كاش", callback_data="payment_shamcash")],
            [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="payment_syriatel")],
            [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
            [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
            [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            MESSAGES[language]['payment_methods'],
            reply_markup=reply_markup
        )
        return
    
    # أزرار الأدمن
    if is_admin:
        if text == "📋 عرض الطلبات المعلقة":
            await show_pending_orders_admin(update, context)
        elif text == "💬 إرسال رسالة للمستخدم":
            await update.message.reply_text("يرجى اختيار طلب من قائمة الطلبات المعلقة لإرسال رسالة للمستخدم")
        elif text == "🚪 تسجيل الخروج":
            context.user_data.clear()
            await update.message.reply_text("✅ تم تسجيل الخروج من لوحة الأدمن")
            await start(update, context)
        return
    
    # التحقق من الأزرار الرئيسية للمستخدم
    if text == MESSAGES[language]['main_menu_buttons'][0]:  # طلب بروكسي ستاتيك
        await handle_static_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][1]:  # طلب بروكسي سوكس
        await handle_socks_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][2]:  # إحالاتي
        await update.message.reply_text("🔧 قسم الإحالات قيد التطوير...")
    elif text == MESSAGES[language]['main_menu_buttons'][3]:  # تذكير بطلباتي
        await update.message.reply_text("🔧 قسم تذكير الطلبات قيد التطوير...")
    elif text == MESSAGES[language]['main_menu_buttons'][4]:  # الإعدادات
        await update.message.reply_text("🔧 قسم الإعدادات قيد التطوير...")

def main() -> None:
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", handle_about_command))
    
    # معالج تسجيل دخول الأدمن
    admin_login_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_login)],
        states={
            ADMIN_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_password)],
        },
        fallbacks=[]
    )
    application.add_handler(admin_login_handler)
    
    # معالج إثبات الدفع
    payment_proof_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_payment_method_selection, pattern="^payment_")],
        states={
            PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO | filters.TEXT, handle_payment_proof),
            ],
        },
        fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^cancel_")]
    )
    application.add_handler(payment_proof_handler)
    
    # معالج رسائل الأدمن
    admin_message_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_send_message_to_user, pattern="^send_message_")],
        states={
            ADMIN_MESSAGE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message_input)],
        },
        fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^cancel_")]
    )
    application.add_handler(admin_message_handler)
    
    # معالجات الاستعلامات والرسائل
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    # تشغيل البوت
    print("🚀 بدء تشغيل البوت المبسط...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()