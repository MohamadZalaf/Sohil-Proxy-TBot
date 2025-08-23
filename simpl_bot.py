#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تيليجرام لبيع البروكسيات
Simple Proxy Bot - Telegram Bot for Selling Proxies
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
    PAYMENT_METHOD_SELECTION, WITHDRAWAL_REQUEST
) = range(19)

# قواميس البيانات
STATIC_COUNTRIES = {
    'ar': {
        'US': '🇺🇸 أميركا',
        'UK': '🇬🇧 بريطانيا', 
        'DE': '🇩🇪 ألمانيا',
        'FR': '🇫🇷 فرنسا'
    },
    'en': {
        'US': '🇺🇸 United States',
        'UK': '🇬🇧 United Kingdom',
        'DE': '🇩🇪 Germany', 
        'FR': '🇫🇷 France'
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
        'AT': '🇦🇹 النمسا'
    },
    'en': {
        'US': '🇺🇸 United States',
        'UK': '🇬🇧 United Kingdom',
        'DE': '🇩🇪 Germany', 
        'FR': '🇫🇷 France',
        'CA': '🇨🇦 Canada',
        'AU': '🇦🇺 Australia',
        'AT': '🇦🇹 Austria'
    }
}

US_STATES = {
    'ar': {
        'CA': 'كاليفورنيا',
        'NY': 'نيويورك',
        'TX': 'تكساس',
        'FL': 'فلوريدا',
        'IL': 'إلينوي'
    },
    'en': {
        'CA': 'California',
        'NY': 'New York', 
        'TX': 'Texas',
        'FL': 'Florida',
        'IL': 'Illinois'
    }
}

UK_STATES = {
    'ar': {
        'ENG': 'إنجلترا',
        'SCT': 'اسكتلندا',
        'WAL': 'ويلز',
        'NIR': 'أيرلندا الشمالية'
    },
    'en': {
        'ENG': 'England',
        'SCT': 'Scotland',
        'WAL': 'Wales', 
        'NIR': 'Northern Ireland'
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
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
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
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{}`""",
        'select_country': 'اختر الدولة:',
        'select_state': 'اختر الولاية:',
        'manual_input': 'إدخال يدوي',
        'payment_methods': 'اختر طريقة الدفع:',
        'send_payment_proof': 'يرجى إرسال إثبات الدفع (صورة أو نص):',
        'order_received': 'تم استلام طلبك بنجاح! جاري معالجة الطلب يدوياً من الأدمن بأقرب وقت.',
        'main_menu_buttons': ['🔒 طلب بروكسي ستاتيك', '🧦 طلب بروكسي سوكس', '👥 إحالاتي', '⚙️ الإعدادات'],
        'admin_main_buttons': ['📋 إدارة الطلبات', '💰 إدارة الأموال', '👥 الإحالات', '⚙️ الإعدادات'],
        'language_change_success': 'تم تغيير اللغة إلى العربية ✅\nيرجى استخدام الأمر /start لإعادة تحميل القوائم',
        'admin_panel': '🔧 لوحة الأدمن',
        'manage_orders': 'إدارة الطلبات',
        'pending_orders': 'الطلبات المعلقة',
        'admin_login_prompt': 'يرجى إدخال كلمة المرور:'
    },
    'en': {
        'welcome': """🎯 Welcome to Proxy Sales Bot

Choose the required service from the buttons below:""",
        'static_package': """📦 Static Package

🔹 Prices:
- Static ISP Risk0: 3$
- Static Residential Verizon: 4$
- Static Residential AT&T: 6$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {}""",
        'socks_package': """📦 Socks Package

🔹 Prices:
- 5 Temporary Proxies Package: 0.4$
- 10 Temporary Proxies Package: 0.7$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {}""",
        'select_country': 'Select Country:',
        'select_state': 'Select State:',
        'manual_input': 'Manual Input',
        'payment_methods': 'Choose payment method:',
        'send_payment_proof': 'Please send payment proof (image or text):',
        'order_received': 'Your order has been received successfully! Admin will process it manually soon.',
        'main_menu_buttons': ['🔒 Request Static Proxy', '🧦 Request Socks Proxy', '👥 My Referrals', '⚙️ Settings'],
        'admin_main_buttons': ['📋 Manage Orders', '💰 Manage Money', '👥 Referrals', '⚙️ Settings'],
        'language_change_success': 'Language changed to English ✅\nPlease use /start command to reload menus',
        'admin_panel': '🔧 Admin Panel',
        'manage_orders': 'Manage Orders',
        'pending_orders': 'Pending Orders',
        'admin_login_prompt': 'Please enter password:'
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
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                proxy_details TEXT,
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
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def update_user_language(self, user_id: int, language: str):
        """تحديث لغة المستخدم"""
        query = "UPDATE users SET language = ? WHERE user_id = ?"
        self.execute_query(query, (language, user_id))
    
    def create_order(self, order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_method: str):
        """إنشاء طلب جديد"""
        query = '''
            INSERT INTO orders (id, user_id, proxy_type, country, state, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (order_id, user_id, proxy_type, country, state, payment_method))
    
    def update_order_payment_proof(self, order_id: str, payment_proof: str):
        """تحديث إثبات الدفع للطلب"""
        query = "UPDATE orders SET payment_proof = ? WHERE id = ?"
        self.execute_query(query, (payment_proof, order_id))
    
    def get_pending_orders(self) -> List[tuple]:
        """الحصول على الطلبات المعلقة"""
        query = "SELECT * FROM orders WHERE status = 'pending'"
        return self.execute_query(query)
    
    def log_action(self, user_id: int, action: str, details: str = ""):
        """تسجيل إجراء في السجل"""
        query = "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)"
        self.execute_query(query, (user_id, action, details))

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
    
    # إضافة مكافأة الإحالة للمحيل
    if referred_by and is_new_user:
        await add_referral_bonus(referred_by, user.id)
        
        # إشعار المحيل
        try:
            await context.bot.send_message(
                referred_by,
                f"🎉 تهانينا! لقد قام {user.first_name} بالانضمام عبر رابط الإحالة الخاص بك.\n💰 تم إضافة 0.1$ إلى رصيدك!"
            )
        except:
            pass  # في حالة عدم إمكانية إرسال الرسالة
        
        # إشعار الأدمن بانضمام عضو جديد عبر الإحالة
        await send_referral_notification(context, referred_by, user)
    
    db.log_action(user.id, "start_command")
    
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
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])]
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
    if update.message.text == ADMIN_PASSWORD:
        global ADMIN_CHAT_ID
        context.user_data['is_admin'] = True
        ADMIN_CHAT_ID = update.effective_user.id  # حفظ معرف الأدمن
        
        db.log_action(update.effective_user.id, "admin_login_success")
        
        # لوحة مفاتيح عادية للأدمن
        keyboard = [
            [KeyboardButton("📋 إدارة الطلبات")],
            [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
            [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("🔍 استعلام عن مستخدم")],
            [KeyboardButton("🔙 عودة للمستخدم")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🔧 مرحباً بك في لوحة الأدمن\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        return ADMIN_MENU
    else:
        await update.message.reply_text("كلمة المرور غير صحيحة!")
        return ConversationHandler.END

async def handle_static_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب البروكسي الستاتيك"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء معرف الطلب
    order_id = generate_order_id()
    context.user_data['current_order_id'] = order_id
    context.user_data['proxy_type'] = 'static'
    
    db.log_action(user_id, "static_proxy_request", order_id)
    
    # عرض رسالة الحزمة
    await update.message.reply_text(
        MESSAGES[language]['static_package'].format(order_id)
    )
    
    # عرض قائمة الدول للستاتيك
    keyboard = []
    for code, name in STATIC_COUNTRIES[language].items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        MESSAGES[language]['select_country'],
        reply_markup=reply_markup
    )

async def handle_socks_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب بروكسي السوكس"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء معرف الطلب
    order_id = generate_order_id()
    context.user_data['current_order_id'] = order_id
    context.user_data['proxy_type'] = 'socks'
    
    db.log_action(user_id, "socks_proxy_request", order_id)
    
    # عرض رسالة الحزمة
    await update.message.reply_text(
        MESSAGES[language]['socks_package'].format(order_id)
    )
    
    # عرض قائمة الدول للسوكس (مع دول إضافية)
    keyboard = []
    for code, name in SOCKS_COUNTRIES[language].items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    
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
    
    if query.data.startswith("country_"):
        country_code = query.data.replace("country_", "")
        context.user_data['selected_country'] = country_code
        
        # عرض قائمة الولايات بناء على الدولة
        if country_code == "US":
            states = US_STATES[language]
        elif country_code == "UK":
            states = UK_STATES[language]
        else:
            # للدول الأخرى، انتقل مباشرة لطرق الدفع
            await show_payment_methods(query, context, language)
            return
        
        keyboard = []
        for code, name in states.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"state_{code}")])
        keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_state")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            MESSAGES[language]['select_state'],
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("state_"):
        state_code = query.data.replace("state_", "")
        context.user_data['selected_state'] = state_code
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
    
    # إنشاء الطلب في قاعدة البيانات
    order_id = context.user_data['current_order_id']
    proxy_type = context.user_data['proxy_type']
    country = context.user_data.get('selected_country', 'manual')
    state = context.user_data.get('selected_state', 'manual')
    
    db.create_order(order_id, user_id, proxy_type, country, state, payment_method)
    
    await query.edit_message_text(MESSAGES[language]['send_payment_proof'])
    
    return PAYMENT_PROOF

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إثبات الدفع"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    order_id = context.user_data['current_order_id']
    
    # حفظ إثبات الدفع
    if update.message.photo:
        # إذا كانت صورة
        file_id = update.message.photo[-1].file_id
        payment_proof = f"photo:{file_id}"
        
        # إرسال رسالة بعنوان إثبات الدفع
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=file_id,
            caption=f"إثبات دفع للطلب بمعرف: {order_id}"
        )
    else:
        # إذا كان نص
        payment_proof = f"text:{update.message.text}"
        
        # إرسال رسالة بعنوان إثبات الدفع
        await update.message.reply_text(
            f"إثبات دفع للطلب بمعرف: {order_id}\n\nالتفاصيل: {update.message.text}"
        )
    
    db.update_order_payment_proof(order_id, payment_proof)
    
    # إرسال إشعار للأدمن مع زر المعالجة
    await send_admin_notification(context, order_id)
    
    await update.message.reply_text(MESSAGES[language]['order_received'])
    
    db.log_action(user_id, "payment_proof_submitted", order_id)
    
    return ConversationHandler.END

async def send_withdrawal_notification(context: ContextTypes.DEFAULT_TYPE, withdrawal_id: str, user: tuple) -> None:
    """إرسال إشعار طلب سحب للأدمن"""
    message = f"""💸 طلب سحب رصيد جديد

👤 الاسم: {user[2]} {user[3]}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user[0]}`

━━━━━━━━━━━━━━━
💰 المبلغ المطلوب: `{user[5]:.2f}$`
📊 نوع الطلب: سحب رصيد الإحالات

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{withdrawal_id}`
📅 تاريخ الطلب: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    # زر معالجة طلب السحب
    keyboard = [[InlineKeyboardButton("💸 معالجة طلب السحب", callback_data=f"process_{withdrawal_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                ADMIN_CHAT_ID, 
                message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال إشعار طلب السحب: {e}")
    
    # حفظ الإشعار في قاعدة البيانات
    db.log_action(user[0], "withdrawal_notification", f"New withdrawal: {withdrawal_id}")

async def send_referral_notification(context: ContextTypes.DEFAULT_TYPE, referrer_id: int, new_user) -> None:
    """إرسال إشعار للأدمن بانضمام عضو جديد عبر الإحالة"""
    # الحصول على بيانات المحيل
    referrer = db.get_user(referrer_id)
    
    if referrer:
        message = f"""👥 عضو جديد عبر الإحالة

🆕 العضو الجديد:
👤 الاسم: {new_user.first_name} {new_user.last_name or ''}
📱 اسم المستخدم: @{new_user.username or 'غير محدد'}
🆔 معرف المستخدم: `{new_user.id}`

━━━━━━━━━━━━━━━
👥 تم إحالته بواسطة:
👤 الاسم: {referrer[2]} {referrer[3]}
📱 اسم المستخدم: @{referrer[1] or 'غير محدد'}
🆔 معرف المحيل: `{referrer[0]}`

━━━━━━━━━━━━━━━
💰 تم إضافة `0.1$` لرصيد المحيل
📅 تاريخ الانضمام: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        if ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID, 
                    message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال إشعار الإحالة: {e}")
        
        # حفظ الإشعار في قاعدة البيانات
        db.log_action(new_user.id, "referral_notification", f"Referred by: {referrer_id}")

async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """إرسال إشعار للأدمن بطلب جديد"""
    # الحصول على تفاصيل الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if result:
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
        
        message = f"""🔔 طلب جديد

👤 الاسم: {order[7]} {order[8]}
📱 اسم المستخدم: @{order[9] or 'غير محدد'}
🆔 معرف المستخدم: {order[1]}

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🔧 نوع البروكسي: {order[2]}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: {order[0]}
📅 تاريخ الطلب: {order[9]}"""
        
        keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # حفظ رسالة إثبات الدفع مع معرف الطلب
        if order[7]:  # payment_proof
            proof_message = f"إثبات دفع للطلب بمعرف: {order_id}"
            db.execute_query(
                "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)",
                (order[1], "payment_proof_saved", proof_message)
            )
        
        # إرسال للأدمن مع زر المعالجة
        keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID, 
                    message, 
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال إشعار الأدمن: {e}")
        
        # حفظ تفاصيل الطلب في قاعدة البيانات
        db.log_action(order[1], "order_details_logged", f"Order: {order_id} - {order[2]} - {order[3]}")

async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قسم الإحالات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء رابط الإحالة
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # الحصول على رصيد الإحالة
    user = db.get_user(user_id)
    referral_balance = user[5] if user else 0.0
    
    # عدد الإحالات
    query = "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?"
    referral_count = db.execute_query(query, (user_id,))[0][0]
    
    if language == 'ar':
        message = f"""👥 نظام الإحالات

🔗 رابط الإحالة الخاص بك:
{referral_link}

💰 رصيدك: `{referral_balance:.2f}$`
👥 عدد إحالاتك: {referral_count}

━━━━━━━━━━━━━━━
شارك رابطك واحصل على `0.1$` لكل إحالة!
الحد الأدنى للسحب: `1.0$`"""
    else:
        message = f"""👥 Referral System

🔗 Your referral link:
{referral_link}

💰 Your balance: `{referral_balance:.2f}$`
👥 Your referrals: {referral_count}

━━━━━━━━━━━━━━━
Share your link and earn `0.1$` per referral!
Minimum withdrawal: `1.0$`"""
    
    keyboard = [
        [InlineKeyboardButton("💸 سحب الرصيد" if language == 'ar' else "💸 Withdraw Balance", callback_data="withdraw_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإعدادات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🌐 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🌐 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "اختر اللغة / Choose Language:",
        reply_markup=reply_markup
    )

async def handle_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تغيير اللغة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "lang_ar":
        new_language = "ar"
        message = """تم تغيير اللغة إلى العربية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم

Language changed to Arabic ✅  
Please use /start command to reload menus"""
    else:
        new_language = "en"
        message = """Language changed to English ✅
Please use /start command to reload menus

تم تغيير اللغة إلى الإنجليزية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم"""
    
    db.update_user_language(user_id, new_language)
    db.log_action(user_id, "language_change", new_language)
    
    await query.edit_message_text(message)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الاستعلامات المرسلة"""
    query = update.callback_query
    
    if query.data.startswith("country_") or query.data.startswith("state_"):
        await handle_country_selection(update, context)
    elif query.data.startswith("payment_"):
        await handle_payment_method_selection(update, context)
    elif query.data.startswith("lang_"):
        await handle_language_change(update, context)
    elif query.data.startswith("process_"):
        await handle_process_order(update, context)
    elif query.data in ["payment_success", "payment_failed"]:
        if query.data == "payment_success":
            await handle_payment_success(update, context)
        else:
            await handle_payment_failed(update, context)
    elif query.data.startswith("proxy_type_"):
        await handle_proxy_details_input(update, context)
    elif query.data.startswith("admin_country_"):
        await handle_admin_country_selection(update, context)
    elif query.data in ["manage_orders", "show_pending_orders", "admin_referrals", "user_lookup", "manage_money", "admin_settings", "reset_balance"]:
        await handle_admin_menu_actions(update, context)
    elif query.data == "withdraw_balance":
        await handle_withdrawal_request(update, context)
    elif query.data in ["send_custom_message", "no_custom_message"]:
        await handle_custom_message_choice(update, context)
    else:
        await query.answer("قيد التطوير...")

async def handle_admin_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار الدولة من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_other_country":
        context.user_data['admin_input_state'] = ENTER_COUNTRY
        await query.edit_message_text("4️⃣ يرجى إدخال اسم الدولة:")
        return ENTER_COUNTRY
    elif query.data.startswith("admin_state_"):
        state_code = query.data.replace("admin_state_", "")
        context.user_data['admin_proxy_state'] = US_STATES['ar'].get(state_code, state_code)
        context.user_data['admin_input_state'] = ENTER_USERNAME
        await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
        return ENTER_USERNAME
    elif query.data == "admin_other_state":
        context.user_data['admin_input_state'] = ENTER_STATE
        await query.edit_message_text("5️⃣ يرجى إدخال اسم الولاية:")
        return ENTER_STATE
    else:
        country_code = query.data.replace("admin_country_", "")
        context.user_data['admin_proxy_country'] = STATIC_COUNTRIES['ar'][country_code]
        
        # عرض قائمة الولايات إذا كانت متوفرة
        if country_code == "US":
            states = US_STATES['ar']
        elif country_code == "UK":
            states = UK_STATES['ar']
        else:
            # انتقل مباشرة لاسم المستخدم
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME
        
        keyboard = []
        for code, name in states.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"admin_state_{code}")])
        keyboard.append([InlineKeyboardButton("غير ذلك", callback_data="admin_other_state")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("5️⃣ اختر الولاية:", reply_markup=reply_markup)
        return ENTER_STATE

async def handle_withdrawal_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    language = get_user_language(user_id)
    
    if user and user[5] >= 1.0:  # الحد الأدنى 1 دولار
        # إنشاء معرف طلب السحب
        withdrawal_id = generate_order_id()
        
        # حفظ طلب السحب في قاعدة البيانات
        db.execute_query(
            "INSERT INTO orders (id, user_id, proxy_type, payment_amount, status) VALUES (?, ?, ?, ?, ?)",
            (withdrawal_id, user_id, 'withdrawal', user[5], 'pending')
        )
        
        if language == 'ar':
            message = f"""💸 تم إرسال طلب سحب الرصيد

💰 المبلغ المطلوب: `{user[5]:.2f}$`
🆔 معرف الطلب: `{withdrawal_id}`

تم إرسال طلبك للأدمن وسيتم معالجته في أقرب وقت ممكن."""
        else:
            message = f"""💸 Withdrawal request sent

💰 Amount: `{user[5]:.2f}$`
🆔 Request ID: `{withdrawal_id}`

Your request has been sent to admin and will be processed soon."""
        
        # إرسال إشعار طلب السحب للأدمن
        await send_withdrawal_notification(context, withdrawal_id, user)
        
        await query.edit_message_text(message, parse_mode='Markdown')
    else:
        min_amount = 1.0
        current_balance = user[5] if user else 0.0
        
        if language == 'ar':
            message = f"""❌ رصيد غير كافٍ للسحب

💰 رصيدك الحالي: `{current_balance:.2f}$`
📊 الحد الأدنى للسحب: `{min_amount:.1f}$`

يرجى دعوة المزيد من الأصدقاء لزيادة رصيدك!"""
        else:
            message = f"""❌ Insufficient balance for withdrawal

💰 Current balance: `{current_balance:.2f}$`
📊 Minimum withdrawal: `{min_amount:.1f}$`

Please invite more friends to increase your balance!"""
        
        await query.edit_message_text(message, parse_mode='Markdown')

async def handle_custom_message_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار إرسال رسالة مخصصة"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    if query.data == "send_custom_message":
        await query.edit_message_text("يرجى إدخال الرسالة المخصصة للمستخدم:")
        return CUSTOM_MESSAGE
    else:
        # عدم إرسال رسالة مخصصة
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            await context.bot.send_message(
                user_id,
                "عذراً، تم رفض طلبك. يرجى التأكد من صحة إثبات الدفع والمحاولة مرة أخرى."
            )
        
        await query.edit_message_text(f"تم إشعار المستخدم برفض الطلب.\nمعرف الطلب: {order_id}")
        return ConversationHandler.END

async def handle_custom_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال الرسالة المخصصة"""
    custom_message = update.message.text
    order_id = context.user_data['processing_order_id']
    
    # إرسال الرسالة المخصصة للمستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        await context.bot.send_message(user_id, custom_message)
    
    await update.message.reply_text(f"تم إرسال الرسالة المخصصة للمستخدم.\nمعرف الطلب: {order_id}")
    return ConversationHandler.END

# إضافة المزيد من الوظائف المساعدة
async def add_referral_bonus(user_id: int, referred_user_id: int) -> None:
    """إضافة مكافأة الإحالة"""
    # الحصول على قيمة الإحالة من الإعدادات
    referral_amount_query = "SELECT value FROM settings WHERE key = 'referral_amount'"
    result = db.execute_query(referral_amount_query)
    referral_amount = float(result[0][0]) if result else 0.1
    
    # إضافة الإحالة
    db.execute_query(
        "INSERT INTO referrals (referrer_id, referred_id, amount) VALUES (?, ?, ?)",
        (user_id, referred_user_id, referral_amount)
    )
    
    # تحديث رصيد المستخدم
    db.execute_query(
        "UPDATE users SET referral_balance = referral_balance + ? WHERE user_id = ?",
        (referral_amount, user_id)
    )

async def cleanup_old_orders() -> None:
    """تنظيف الطلبات القديمة (48 ساعة)"""
    # حذف الطلبات الفاشلة القديمة (بعد 48 ساعة كما هو مطلوب في المواصفات)
    deleted_failed = db.execute_query("""
        DELETE FROM orders 
        WHERE status = 'failed' 
        AND created_at < datetime('now', '-48 hours')
    """)
    
    # تسجيل عدد الطلبات المحذوفة
    if deleted_failed:
        print(f"تم حذف {len(deleted_failed)} طلب فاشل قديم")
    
    # يمكن الاحتفاظ بالطلبات المكتملة للإحصائيات (لا نحذفها)

# تشغيل تنظيف الطلبات كل ساعة
async def schedule_cleanup():
    """جدولة تنظيف الطلبات"""
    while True:
        await asyncio.sleep(3600)  # كل ساعة
        await cleanup_old_orders()

def create_requirements_file():
    """إنشاء ملف requirements.txt"""
    requirements = """python-telegram-bot==20.7
sqlite3"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)

async def export_database_excel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى Excel"""
    try:
        # قراءة البيانات من قاعدة البيانات
        conn = sqlite3.connect(DATABASE_FILE)
        
        # إنشاء ملف Excel مع عدة أوراق
        with pd.ExcelWriter('database_export.xlsx', engine='openpyxl') as writer:
            # جدول المستخدمين
            users_df = pd.read_sql_query("SELECT * FROM users", conn)
            users_df.to_excel(writer, sheet_name='Users', index=False)
            
            # جدول الطلبات
            orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
            
            # جدول الإحالات
            referrals_df = pd.read_sql_query("SELECT * FROM referrals", conn)
            referrals_df.to_excel(writer, sheet_name='Referrals', index=False)
            
            # جدول السجلات
            logs_df = pd.read_sql_query("SELECT * FROM logs", conn)
            logs_df.to_excel(writer, sheet_name='Logs', index=False)
        
        conn.close()
        
        # إرسال الملف
        with open('database_export.xlsx', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                caption="📊 تم تصدير قاعدة البيانات بصيغة Excel"
            )
        
        # حذف الملف المؤقت
        os.remove('database_export.xlsx')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير Excel: {str(e)}")

async def export_database_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى CSV"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        # تصدير جدول المستخدمين
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        users_df.to_csv('users_export.csv', index=False, encoding='utf-8-sig')
        
        # تصدير جدول الطلبات
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        orders_df.to_csv('orders_export.csv', index=False, encoding='utf-8-sig')
        
        conn.close()
        
        # إرسال الملفات
        with open('users_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="👥 بيانات المستخدمين - CSV"
            )
        
        with open('orders_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="📋 بيانات الطلبات - CSV"
            )
        
        # حذف الملفات المؤقتة
        os.remove('users_export.csv')
        os.remove('orders_export.csv')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير CSV: {str(e)}")

async def export_database_sqlite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير ملف قاعدة البيانات الأصلي"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"proxy_bot_backup_{timestamp}.db"
        
        # نسخ ملف قاعدة البيانات
        import shutil
        shutil.copy2(DATABASE_FILE, backup_filename)
        
        # إرسال الملف
        with open(backup_filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=backup_filename,
                caption="🗃️ نسخة احتياطية من قاعدة البيانات - SQLite"
            )
        
        # حذف الملف المؤقت
        os.remove(backup_filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير قاعدة البيانات: {str(e)}")

def create_readme_file():
    """إنشاء ملف README.md"""
    readme_content = """# بوت بيع البروكسيات - Proxy Sales Bot

## تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

## إعداد البوت

1. احصل على TOKEN من BotFather على تيليجرام
2. ضع التوكن في متغير TOKEN في الكود
3. قم بتشغيل البوت:

```bash
python simpl_bot.py
```

## الميزات

- طلب البروكسيات (Static/Socks)
- نظام دفع متعدد الطرق
- إدارة أدمن متكاملة
- نظام إحالات
- دعم اللغتين العربية والإنجليزية
- قاعدة بيانات SQLite محلية

## أوامر الأدمن

- `/admin_login` - تسجيل دخول الأدمن
- كلمة المرور: `sohilSOHIL`

## البنية

- `simpl_bot.py` - الملف الرئيسي للبوت
- `proxy_bot.db` - قاعدة البيانات (تُنشأ تلقائياً)
- `requirements.txt` - متطلبات Python
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

async def handle_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الطلب من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("process_", "")
    context.user_data['processing_order_id'] = order_id
    
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data="payment_success")],
        [InlineKeyboardButton("لا", callback_data="payment_failed")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "هل عملية الدفع ناجحة وحقيقية؟",
        reply_markup=reply_markup
    )

async def handle_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة نجاح الدفع والبدء في جمع معلومات البروكسي"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # إرسال رسالة للمستخدم أن الطلب قيد المعالجة
    order_query = "SELECT user_id, proxy_type FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if order_result:
        user_id = order_result[0][0]
        order_type = order_result[0][1]
        
        await context.bot.send_message(
            user_id,
            "جاري معالجة الطلب يدوياً من الأدمن بأقرب وقت."
        )
        
        # التحقق من نوع الطلب
        if order_type == 'withdrawal':
            # معالجة طلب السحب
            await handle_withdrawal_approval(query, context, order_id, user_id)
            return ConversationHandler.END
    
    # بدء جمع معلومات البروكسي للطلبات العادية
    keyboard = [
        [InlineKeyboardButton("ستاتيك", callback_data="proxy_type_static")],
        [InlineKeyboardButton("سوكس", callback_data="proxy_type_socks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "1️⃣ اختر نوع البروكسي:",
        reply_markup=reply_markup
    )
    
    return ENTER_PROXY_TYPE

async def handle_withdrawal_approval(query, context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int) -> None:
    """معالجة موافقة طلب السحب"""
    # الحصول على بيانات المستخدم
    user = db.get_user(user_id)
    
    if user:
        # تصفير رصيد المستخدم
        db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
        
        # تحديث حالة طلب السحب
        db.execute_query("UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
        
        # إرسال رسالة للمستخدم
        await context.bot.send_message(
            user_id,
            f"✅ تم الموافقة على طلب سحب الرصيد\n\n💰 المبلغ: `{user[5]:.2f}$`\n🆔 معرف الطلب: `{order_id}`\n\nسيتم التواصل معك قريباً لإتمام عملية التحويل.",
            parse_mode='Markdown'
        )
        
        # رسالة تأكيد للأدمن
        await query.edit_message_text(
            f"✅ تم الموافقة على طلب السحب بنجاح!\n\n👤 المستخدم: {user[2]} {user[3]}\n💰 المبلغ: `{user[5]:.2f}$`\n🆔 معرف الطلب: `{order_id}`\n\n⚠️ تم تصفير رصيد المستخدم تلقائياً.",
            parse_mode='Markdown'
        )

async def handle_payment_failed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة فشل الدفع"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # تحديث حالة الطلب
    db.execute_query("UPDATE orders SET status = 'failed' WHERE id = ?", (order_id,))
    
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data="send_custom_message")],
        [InlineKeyboardButton("لا", callback_data="no_custom_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "هل تريد إرسال رسالة مخصصة للمستخدم؟",
        reply_markup=reply_markup
    )
    
    return CUSTOM_MESSAGE

async def handle_admin_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إجراءات لوحة الأدمن"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "manage_orders":
        keyboard = [
            [InlineKeyboardButton("الطلبات المعلقة", callback_data="show_pending_orders")],
            [InlineKeyboardButton("حذف الطلبات الفاشلة", callback_data="delete_failed_orders")],
            [InlineKeyboardButton("حذف الطلبات المكتملة", callback_data="delete_completed_orders")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("إدارة الطلبات:", reply_markup=reply_markup)
    
    elif query.data == "show_pending_orders":
        pending_orders = db.get_pending_orders()
        if not pending_orders:
            await query.edit_message_text("لا توجد طلبات معلقة حالياً.")
            return
        
        message = "الطلبات المعلقة:\n\n"
        for order in pending_orders[:10]:  # عرض أول 10 طلبات
            message += f"🔸 معرف: {order[0]}\n"
            message += f"   نوع: {order[2]}\n"
            message += f"   الدولة: {order[3]}\n\n"
        
        await query.edit_message_text(message)
    
    elif query.data == "admin_referrals":
        await show_admin_referrals(query, context)
    
    elif query.data == "user_lookup":
        await query.edit_message_text("يرجى إرسال معرف المستخدم أو @username للبحث:")
        return USER_LOOKUP

async def show_admin_referrals(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات الإحالات للأدمن"""
    # إحصائيات الإحالات
    total_referrals = db.execute_query("SELECT COUNT(*) FROM referrals")[0][0]
    total_amount = db.execute_query("SELECT SUM(amount) FROM referrals")[0][0] or 0
    
    # أفضل المحيلين
    top_referrers = db.execute_query('''
        SELECT u.first_name, u.last_name, COUNT(r.id) as referral_count, SUM(r.amount) as total_earned
        FROM users u
        JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY referral_count DESC
        LIMIT 5
    ''')
    
    message = f"📊 إحصائيات الإحالات\n\n"
    message += f"إجمالي الإحالات: {total_referrals}\n"
    message += f"إجمالي المبلغ: {total_amount:.2f}$\n\n"
    message += "أفضل المحيلين:\n"
    
    for i, referrer in enumerate(top_referrers, 1):
        message += f"{i}. {referrer[0]} {referrer[1]}: {referrer[2]} إحالة ({referrer[3]:.2f}$)\n"
    
    keyboard = [
        [InlineKeyboardButton("تحديد قيمة الإحالة", callback_data="set_referral_amount")],
        [InlineKeyboardButton("تصفير رصيد مستخدم", callback_data="reset_user_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def handle_proxy_details_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال تفاصيل البروكسي خطوة بخطوة"""
    query = update.callback_query
    
    if query:
        await query.answer()
        
        if query.data.startswith("proxy_type_"):
            proxy_type = query.data.replace("proxy_type_", "")
            context.user_data['admin_proxy_type'] = proxy_type
            context.user_data['admin_input_state'] = ENTER_PROXY_ADDRESS
            
            await query.edit_message_text("2️⃣ يرجى إدخال عنوان البروكسي:")
            return ENTER_PROXY_ADDRESS
    
    else:
        # معالجة النص المدخل
        text = update.message.text
        current_state = context.user_data.get('admin_input_state', ENTER_PROXY_ADDRESS)
        
        if current_state == ENTER_PROXY_ADDRESS:
            context.user_data['admin_proxy_address'] = text
            context.user_data['admin_input_state'] = ENTER_PROXY_PORT
            await update.message.reply_text("3️⃣ يرجى إدخال البورت:")
            return ENTER_PROXY_PORT
        
        elif current_state == ENTER_PROXY_PORT:
            context.user_data['admin_proxy_port'] = text
            
            # عرض قائمة الدول
            keyboard = []
            for code, name in STATIC_COUNTRIES['ar'].items():
                keyboard.append([InlineKeyboardButton(name, callback_data=f"admin_country_{code}")])
            keyboard.append([InlineKeyboardButton("غير ذلك", callback_data="admin_other_country")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("4️⃣ اختر الدولة:", reply_markup=reply_markup)
            return ENTER_COUNTRY
        
        elif current_state == ENTER_USERNAME:
            context.user_data['admin_proxy_username'] = text
            context.user_data['admin_input_state'] = ENTER_PASSWORD
            await update.message.reply_text("7️⃣ يرجى إدخال كلمة المرور:")
            return ENTER_PASSWORD
        
        elif current_state == ENTER_PASSWORD:
            context.user_data['admin_proxy_password'] = text
            context.user_data['admin_input_state'] = ENTER_THANK_MESSAGE
            await update.message.reply_text("8️⃣ يرجى إدخال رسالة شكر قصيرة:")
            return ENTER_THANK_MESSAGE
        
        elif current_state == ENTER_THANK_MESSAGE:
            thank_message = text
            
            # إرسال البروكسي للمستخدم
            await send_proxy_to_user(update, context, thank_message)
            return ConversationHandler.END
    
    return current_state

async def send_proxy_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, thank_message: str) -> None:
    """إرسال تفاصيل البروكسي للمستخدم"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معرف المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        
        # إنشاء رسالة البروكسي
        proxy_message = f"""✅ تم تجهيز البروكسي الخاص بك

🔐 تفاصيل البروكسي:
📡 العنوان: {context.user_data['admin_proxy_address']}
🔌 البورت: {context.user_data['admin_proxy_port']}
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: {context.user_data['admin_proxy_username']}
🔑 كلمة المرور: {context.user_data['admin_proxy_password']}

━━━━━━━━━━━━━━━
💬 {thank_message}

معرف الطلب: {order_id}"""
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message)
        
        # تحديث حالة الطلب
        proxy_details = {
            'address': context.user_data['admin_proxy_address'],
            'port': context.user_data['admin_proxy_port'],
            'country': context.user_data.get('admin_proxy_country', ''),
            'state': context.user_data.get('admin_proxy_state', ''),
            'username': context.user_data['admin_proxy_username'],
            'password': context.user_data['admin_proxy_password']
        }
        
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ? WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # رسالة تأكيد للأدمن
        await update.message.reply_text(f"✅ تم إرسال البروكسي للمستخدم بنجاح!\nمعرف الطلب: {order_id}")
        
        # تنظيف البيانات المؤقتة
        admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
        for key in admin_keys:
            del context.user_data[key]

async def handle_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة البحث عن مستخدم"""
    search_term = update.message.text
    
    # البحث بالمعرف أو اسم المستخدم
    if search_term.startswith('@'):
        username = search_term[1:]
        query = "SELECT * FROM users WHERE username = ?"
        user_result = db.execute_query(query, (username,))
    else:
        try:
            user_id = int(search_term)
            query = "SELECT * FROM users WHERE user_id = ?"
            user_result = db.execute_query(query, (user_id,))
        except ValueError:
            await update.message.reply_text("معرف المستخدم غير صحيح!")
            return ConversationHandler.END
    
    if not user_result:
        await update.message.reply_text("المستخدم غير موجود!")
        return ConversationHandler.END
    
    user = user_result[0]
    user_id = user[0]
    
    # إحصائيات المستخدم
    successful_orders = db.execute_query(
        "SELECT COUNT(*), SUM(payment_amount) FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )[0]
    
    failed_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'failed'",
        (user_id,)
    )[0][0]
    
    pending_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'pending'",
        (user_id,)
    )[0][0]
    
    referral_count = db.execute_query(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
        (user_id,)
    )[0][0]
    
    last_successful_order = db.execute_query(
        "SELECT created_at FROM orders WHERE user_id = ? AND status = 'completed' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    
    report = f"""📊 تقرير المستخدم

👤 الاسم: {user[2]} {user[3]}
📝 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: {user[0]}

━━━━━━━━━━━━━━━
📈 إحصائيات الشراء:
✅ الشراءات الناجحة: {successful_orders[0]}
💰 قيمة الشراءات: {successful_orders[1] or 0:.2f}$
❌ الشراءات الفاشلة: {failed_orders}
⏳ طلبات معلقة: {pending_orders}

━━━━━━━━━━━━━━━
👥 الإحالات:
📊 عدد الإحالات: {referral_count}
💵 رصيد الإحالات: {user[5]:.2f}$

━━━━━━━━━━━━━━━
📅 آخر شراء ناجح: {last_successful_order[0][0] if last_successful_order else 'لا يوجد'}
📅 تاريخ الانضمام: {user[7]}"""
    
    await update.message.reply_text(report)
    return ConversationHandler.END

async def handle_admin_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الطلبات للأدمن"""
    keyboard = [
        [KeyboardButton("📋 الطلبات المعلقة")],
        [KeyboardButton("🗑️ حذف الطلبات الفاشلة"), KeyboardButton("🗑️ حذف الطلبات المكتملة")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📋 إدارة الطلبات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_money_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الأموال للأدمن"""
    keyboard = [
        [KeyboardButton("📊 إحصاء المبيعات")],
        [KeyboardButton("💲 إدارة الأسعار")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 إدارة الأموال\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_referrals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الإحالات للأدمن"""
    keyboard = [
        [KeyboardButton("💵 تحديد قيمة الإحالة")],
        [KeyboardButton("📊 إحصائيات المستخدمين")],
        [KeyboardButton("🗑️ تصفير رصيد مستخدم")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👥 إدارة الإحالات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إعدادات الأدمن"""
    keyboard = [
        [KeyboardButton("🌐 تغيير اللغة")],
        [KeyboardButton("🔕 ساعات الهدوء")],
        [KeyboardButton("📊 تحميل قاعدة البيانات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚙️ إعدادات الأدمن\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة استعلام عن مستخدم"""
    await update.message.reply_text(
        "🔍 استعلام عن مستخدم\n\nيرجى إرسال:\n- معرف المستخدم (رقم)\n- أو اسم المستخدم (@username)"
    )

async def return_to_user_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لوضع المستخدم العادي"""
    context.user_data['is_admin'] = False
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء الأزرار الرئيسية للمستخدم
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        MESSAGES[language]['welcome'],
        reply_markup=reply_markup
    )

async def show_pending_orders_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض الطلبات المعلقة للأدمن"""
    pending_orders = db.get_pending_orders()
    
    if not pending_orders:
        await update.message.reply_text("✅ لا توجد طلبات معلقة حالياً.")
        return
    
    message = "📋 الطلبات المعلقة:\n\n"
    for i, order in enumerate(pending_orders[:10], 1):  # عرض أول 10 طلبات
        message += f"{i}. 🆔 `{order[0]}`\n"
        message += f"   📦 النوع: {order[2]}\n"
        message += f"   🌍 الدولة: {order[3]}\n"
        message += f"   📅 التاريخ: {order[9]}\n\n"
    
    if len(pending_orders) > 10:
        message += f"... و {len(pending_orders) - 10} طلبات أخرى"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def delete_failed_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف الطلبات الفاشلة"""
    result = db.execute_query("DELETE FROM orders WHERE status = 'failed'")
    deleted_count = db.execute_query("SELECT changes()")[0][0]
    
    await update.message.reply_text(f"🗑️ تم حذف {deleted_count} طلب فاشل.")

async def delete_completed_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف الطلبات المكتملة"""
    result = db.execute_query("DELETE FROM orders WHERE status = 'completed'")
    deleted_count = db.execute_query("SELECT changes()")[0][0]
    
    await update.message.reply_text(f"🗑️ تم حذف {deleted_count} طلب مكتمل.")

async def show_sales_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات المبيعات"""
    # إحصائيات المبيعات الناجحة
    stats = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount) 
        FROM orders 
        WHERE status = 'completed' AND proxy_type != 'withdrawal'
    """)[0]
    
    # إحصائيات السحوبات
    withdrawals = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount)
        FROM orders 
        WHERE proxy_type = 'withdrawal' AND status = 'completed'
    """)[0]
    
    total_orders = stats[0] or 0
    total_revenue = stats[1] or 0.0
    withdrawal_count = withdrawals[0] or 0
    withdrawal_amount = withdrawals[1] or 0.0
    
    message = f"""📊 إحصائيات المبيعات

💰 المبيعات الناجحة:
📦 عدد الطلبات: {total_orders}
💵 إجمالي الإيرادات: `{total_revenue:.2f}$`

💸 السحوبات:
📋 عدد الطلبات: {withdrawal_count}
💰 إجمالي المسحوب: `{withdrawal_amount:.2f}$`

━━━━━━━━━━━━━━━
📈 صافي الربح: `{total_revenue - withdrawal_amount:.2f}$`"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def database_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة تصدير قاعدة البيانات"""
    keyboard = [
        [KeyboardButton("📊 Excel"), KeyboardButton("📄 CSV")],
        [KeyboardButton("🗃️ SQLite Database")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📊 تحميل قاعدة البيانات\nاختر صيغة التصدير:",
        reply_markup=reply_markup
    )

async def return_to_admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن"""
    keyboard = [
        [KeyboardButton("📋 إدارة الطلبات")],
        [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
        [KeyboardButton("⚙️ الإعدادات"), KeyboardButton("🔍 استعلام عن مستخدم")],
        [KeyboardButton("🔙 عودة للمستخدم")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل النصية"""
    text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    is_admin = context.user_data.get('is_admin', False)
    
    # أزرار الأدمن
    if is_admin:
        # القوائم الرئيسية للأدمن
        if text == "📋 إدارة الطلبات":
            await handle_admin_orders_menu(update, context)
        elif text == "💰 إدارة الأموال":
            await handle_admin_money_menu(update, context)
        elif text == "👥 الإحالات":
            await handle_admin_referrals_menu(update, context)
        elif text == "⚙️ الإعدادات":
            await handle_admin_settings_menu(update, context)
        elif text == "🔍 استعلام عن مستخدم":
            await handle_admin_user_lookup(update, context)
        elif text == "🔙 عودة للمستخدم":
            await return_to_user_mode(update, context)
        
        # إدارة الطلبات
        elif text == "📋 الطلبات المعلقة":
            await show_pending_orders_admin(update, context)
        elif text == "🗑️ حذف الطلبات الفاشلة":
            await delete_failed_orders(update, context)
        elif text == "🗑️ حذف الطلبات المكتملة":
            await delete_completed_orders(update, context)
        
        # إدارة الأموال
        elif text == "📊 إحصاء المبيعات":
            await show_sales_statistics(update, context)
        elif text == "💲 إدارة الأسعار":
            await manage_prices_menu(update, context)
        
        # إدارة الإحالات
        elif text == "💵 تحديد قيمة الإحالة":
            await set_referral_amount(update, context)
        elif text == "📊 إحصائيات المستخدمين":
            await show_user_statistics(update, context)
        elif text == "🗑️ تصفير رصيد مستخدم":
            await reset_user_balance(update, context)
        
        # إعدادات الأدمن
        elif text == "🌐 تغيير اللغة":
            await handle_settings(update, context)
        elif text == "🔕 ساعات الهدوء":
            await set_quiet_hours(update, context)
        elif text == "📊 تحميل قاعدة البيانات":
            await database_export_menu(update, context)
        
        # معالجة تصدير قاعدة البيانات
        elif text == "📊 Excel":
            await export_database_excel(update, context)
        elif text == "📄 CSV":
            await export_database_csv(update, context)
        elif text == "🗃️ SQLite Database":
            await export_database_sqlite(update, context)
        
        # العودة للقائمة الرئيسية
        elif text == "🔙 العودة للقائمة الرئيسية":
            await return_to_admin_main(update, context)
        
        return
    
    # التحقق من الأزرار الرئيسية للمستخدم
    if text == MESSAGES[language]['main_menu_buttons'][0]:  # طلب بروكسي ستاتيك
        await handle_static_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][1]:  # طلب بروكسي سوكس
        await handle_socks_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][2]:  # إحالاتي
        await handle_referrals(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][3]:  # الإعدادات
        await handle_settings(update, context)

def main() -> None:
    """الدالة الرئيسية"""
    if not TOKEN:
        print("يرجى إضافة التوكن في بداية الملف!")
        print("1. اذهب إلى @BotFather على تيليجرام")
        print("2. أنشئ بوت جديد وانسخ التوكن")
        print("3. ضع التوكن في متغير TOKEN في بداية الملف")
        return
    
    # إنشاء ملفات المساعدة
    create_requirements_file()
    create_readme_file()
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # معالج تسجيل دخول الأدمن
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin_login", admin_login)],
        states={
            ADMIN_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_password)],
            ADMIN_MENU: [CallbackQueryHandler(handle_admin_menu_actions)],
            ENTER_PROXY_TYPE: [CallbackQueryHandler(handle_proxy_details_input)],
            ENTER_PROXY_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_PROXY_PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_COUNTRY: [
                CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_country_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)
            ],
            ENTER_STATE: [
                CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_state_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)
            ],
            ENTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_THANK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            CUSTOM_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_message_input)],
            USER_LOOKUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_lookup)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    
    # معالج إثبات الدفع
    payment_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_payment_method_selection, pattern="^payment_")],
        states={
            PAYMENT_PROOF: [MessageHandler(filters.ALL & ~filters.COMMAND, handle_payment_proof)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(admin_conv_handler)
    application.add_handler(payment_conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    # تشغيل البوت
    print("🚀 بدء تشغيل البوت...")
    print("📊 قاعدة البيانات جاهزة")
    print("⚡ البوت يعمل الآن!")
    print("💡 تأكد من إضافة التوكن للبدء")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()