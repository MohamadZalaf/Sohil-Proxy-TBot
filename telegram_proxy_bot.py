#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

# Telegram Bot API
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعدادات البوت
BOT_TOKEN = "8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA"
ADMIN_ID = "6891599955"  # معرف الأدمن
BOT_RUNNING = False

# إعداد Flask للتطبيق
app = Flask(__name__)
CORS(app)

@dataclass
class ProxyType:
    id: int
    name: str
    description: str
    price: float
    is_active: bool

@dataclass
class User:
    user_id: int
    username: str
    first_name: str
    last_name: str
    is_banned: bool
    join_date: datetime

@dataclass
class Order:
    id: int
    user_id: int
    proxy_type_id: int
    status: str  # pending, completed, cancelled
    created_at: datetime
    completed_at: Optional[datetime]
    proxy_info: Optional[Dict[str, Any]]

class DatabaseManager:
    def __init__(self, db_path="proxy_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_banned INTEGER DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول أنواع البروكسي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxy_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # جدول الطلبات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                proxy_type_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                proxy_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (proxy_type_id) REFERENCES proxy_types (id)
            )
        ''')
        
        # جدول إعدادات البوت
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # جدول الأرباح
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_data):
        """إضافة مستخدم جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, is_banned, join_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data.get('username', ''),
            user_data.get('first_name', ''),
            user_data.get('last_name', ''),
            0,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """الحصول على جميع المستخدمين"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def ban_user(self, user_id):
        """حظر مستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def unban_user(self, user_id):
        """إلغاء حظر مستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def is_user_banned(self, user_id):
        """التحقق من حظر المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0] == 1
    
    def add_proxy_type(self, name, description, price):
        """إضافة نوع بروكسي جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO proxy_types (name, description, price, is_active)
            VALUES (?, ?, ?, 1)
        ''', (name, description, price))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_active_proxy_types(self):
        """الحصول على أنواع البروكسي النشطة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proxy_types WHERE is_active = 1')
        proxy_types = cursor.fetchall()
        
        conn.close()
        return proxy_types
    
    def create_order(self, user_id, proxy_type_id):
        """إنشاء طلب جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, proxy_type_id, status, created_at)
            VALUES (?, ?, 'pending', ?)
        ''', (user_id, proxy_type_id, datetime.now()))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id
    
    def get_pending_orders(self):
        """الحصول على الطلبات المعلقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, u.username, u.first_name, p.name as proxy_name, p.price
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN proxy_types p ON o.proxy_type_id = p.id
            WHERE o.status = 'pending'
            ORDER BY o.created_at DESC
        ''')
        
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def get_completed_orders(self):
        """الحصول على الطلبات المكتملة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, u.username, u.first_name, p.name as proxy_name, p.price
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN proxy_types p ON o.proxy_type_id = p.id
            WHERE o.status = 'completed'
            ORDER BY o.completed_at DESC
        ''')
        
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def complete_order(self, order_id, proxy_info):
        """إكمال طلب"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # تحديث الطلب
        cursor.execute('''
            UPDATE orders 
            SET status = 'completed', completed_at = ?, proxy_info = ?
            WHERE id = ?
        ''', (datetime.now(), json.dumps(proxy_info), order_id))
        
        # الحصول على معلومات الطلب لحساب الأرباح
        cursor.execute('''
            SELECT p.price FROM orders o
            JOIN proxy_types p ON o.proxy_type_id = p.id
            WHERE o.id = ?
        ''', (order_id,))
        
        price = cursor.fetchone()[0]
        
        # إضافة الأرباح
        cursor.execute('''
            INSERT INTO earnings (order_id, amount, date)
            VALUES (?, ?, ?)
        ''', (order_id, price, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_total_earnings(self):
        """الحصول على إجمالي الأرباح"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM earnings')
        total = cursor.fetchone()[0]
        
        conn.close()
        return total
    
    def set_setting(self, key, value):
        """حفظ إعداد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key, default=None):
        """الحصول على إعداد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM bot_settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else default
    
    def get_user_info(self, user_id):
        """الحصول على معلومات المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'is_banned': bool(result[4]),
                'join_date': result[5]
            }
        return {}

# إنشاء مدير قاعدة البيانات
db = DatabaseManager()

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.running = False
        self.update_offset = 0
    
    def send_message(self, chat_id, text, reply_markup=None):
        """إرسال رسالة"""
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة: {e}")
            return None
    
    def create_keyboard(self, buttons):
        """إنشاء لوحة مفاتيح"""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append({
                    'text': button['text'],
                    'callback_data': button['callback_data']
                })
            keyboard.append(keyboard_row)
        
        return {
            'inline_keyboard': keyboard
        }
    
    def get_updates(self):
        """الحصول على التحديثات"""
        url = f"{self.api_url}/getUpdates"
        params = {
            'offset': self.update_offset + 1,
            'timeout': 30
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"خطأ في الحصول على التحديثات: {e}")
            return None
    
    def handle_message(self, message):
        """معالجة الرسائل"""
        chat_id = message['chat']['id']
        user_data = {
            'user_id': message['from']['id'],
            'username': message['from'].get('username', ''),
            'first_name': message['from'].get('first_name', ''),
            'last_name': message['from'].get('last_name', '')
        }
        
        # إضافة المستخدم لقاعدة البيانات
        db.add_user(user_data)
        
        # التحقق من الحظر
        if db.is_user_banned(user_data['user_id']):
            self.send_message(chat_id, "❌ تم حظرك من استخدام البوت")
            return
        
        text = message.get('text', '')
        
        if text == '/start':
            self.handle_start(chat_id)
        
    def handle_callback_query(self, callback_query):
        """معالجة الضغط على الأزرار"""
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        
        # التحقق من الحظر
        if db.is_user_banned(user_id):
            self.send_message(chat_id, "❌ تم حظرك من استخدام البوت")
            return
        
        if data == 'request_proxy':
            self.show_proxy_types(chat_id)
        elif data.startswith('proxy_'):
            proxy_type_id = int(data.split('_')[1])
            self.handle_proxy_request(chat_id, user_id, proxy_type_id)
    
    def handle_start(self, chat_id):
        """معالجة أمر البداية"""
        welcome_text = """
🤖 مرحباً بك في بوت البروكسي!

يمكنك من خلال هذا البوت طلب شراء بروكسي عالي الجودة

اختر من الخيارات أدناه:
        """
        
        keyboard = self.create_keyboard([
            [{'text': '🛒 طلب شراء بروكسي', 'callback_data': 'request_proxy'}],
            [{'text': '📞 التواصل مع الدعم', 'callback_data': 'support'}]
        ])
        
        self.send_message(chat_id, welcome_text, keyboard)
    
    def show_proxy_types(self, chat_id):
        """عرض أنواع البروكسي المتوفرة"""
        proxy_types = db.get_active_proxy_types()
        
        if not proxy_types:
            self.send_message(chat_id, "❌ لا توجد أنواع بروكسي متوفرة حالياً")
            return
        
        text = "🛒 اختر نوع البروكسي الذي تريد شراؤه:\n\n"
        buttons = []
        
        for proxy in proxy_types:
            text += f"🔹 {proxy[1]} - ${proxy[3]}\n{proxy[2]}\n\n"
            buttons.append([{
                'text': f"{proxy[1]} - ${proxy[3]}",
                'callback_data': f'proxy_{proxy[0]}'
            }])
        
        keyboard = self.create_keyboard(buttons)
        self.send_message(chat_id, text, keyboard)
    
    def handle_proxy_request(self, chat_id, user_id, proxy_type_id):
        """معالجة طلب البروكسي"""
        # الحصول على معلومات نوع البروكسي
        proxy_types = db.get_active_proxy_types()
        selected_proxy = None
        for proxy in proxy_types:
            if proxy[0] == proxy_type_id:
                selected_proxy = proxy
                break
        
        if not selected_proxy:
            self.send_message(chat_id, "❌ نوع البروكسي غير متوفر")
            return
        
        # إنشاء الطلب
        order_id = db.create_order(user_id, proxy_type_id)
        
        # إرسال رسالة مفصلة للمستخدم
        user_message = f"""
✅ تم استلام طلبك بنجاح!

📋 تفاصيل الطلب:
🆔 رقم الطلب: {order_id}
🛒 نوع البروكسي: {selected_proxy[1]}
📝 الوصف: {selected_proxy[2]}
💰 السعر: ${selected_proxy[3]}
⏳ حالة الطلب: قيد المعالجة
📅 تاريخ الطلب: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💳 خطوات الدفع:
1️⃣ سيتم التواصل معك قريباً لتأكيد الدفع
2️⃣ بعد تأكيد الدفع سيتم تجهيز البروكسي
3️⃣ ستحصل على معلومات البروكسي كاملة

شكراً لثقتك بنا! 🙏

للاستفسار تواصل مع الدعم: @support
        """
        
        self.send_message(chat_id, user_message)
        
        # الحصول على معلومات المستخدم
        user_info = db.get_user_info(user_id)
        
        # إرسال إشعار مفصل للأدمن
        admin_text = f"""
🚨 طلب جديد وارد! 🚨

👤 معلومات المستخدم:
🆔 معرف المستخدم: {user_id}
👤 الاسم: {user_info.get('first_name', 'غير محدد')} {user_info.get('last_name', '')}
📱 اسم المستخدم: @{user_info.get('username', 'غير محدد')}

🛒 تفاصيل الطلب:
🆔 رقم الطلب: {order_id}
🌐 نوع البروكسي: {selected_proxy[1]}
📝 الوصف: {selected_proxy[2]}
💰 السعر: ${selected_proxy[3]}
📅 وقت الطلب: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ يرجى معالجة الطلب من خلال تطبيق الإدارة

💡 لمعالجة الطلب:
1️⃣ افتح تطبيق إدارة البوت
2️⃣ انتقل لقسم "الطلبات المعلقة"
3️⃣ اضغط على "معالجة الطلب"
        """
        
        # إرسال للأدمن المحدد
        self.send_message(ADMIN_ID, admin_text)
        
        # إرسال للأدمن المحفوظ في قاعدة البيانات (إن وجد)
        saved_admin_id = db.get_setting('admin_id')
        if saved_admin_id and saved_admin_id != ADMIN_ID:
            self.send_message(saved_admin_id, admin_text)
    
    def start_polling(self):
        """بدء البوت"""
        self.running = True
        logger.info("تم بدء البوت...")
        
        while self.running:
            try:
                updates = self.get_updates()
                
                if updates and updates.get('ok'):
                    for update in updates['result']:
                        self.update_offset = update['update_id']
                        
                        if 'message' in update:
                            self.handle_message(update['message'])
                        elif 'callback_query' in update:
                            self.handle_callback_query(update['callback_query'])
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"خطأ في البوت: {e}")
                time.sleep(5)
    
    def stop_polling(self):
        """إيقاف البوت"""
        self.running = False
        logger.info("تم إيقاف البوت")

# إنشاء البوت
bot = TelegramBot(BOT_TOKEN)
bot_thread = None

# API endpoints للتطبيق الأندرويد

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """بدء البوت"""
    global bot_thread, BOT_RUNNING
    
    data = request.json
    admin_id = data.get('admin_id')
    
    if admin_id:
        db.set_setting('admin_id', admin_id)
    
    if not BOT_RUNNING:
        bot_thread = threading.Thread(target=bot.start_polling)
        bot_thread.daemon = True
        bot_thread.start()
        BOT_RUNNING = True
        
        # إشعار الأدمن ببدء البوت
        start_message = f"""
🚀 تم بدء البوت بنجاح!

📊 معلومات البوت:
🤖 حالة البوت: نشط ويعمل
🕐 وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 الخادم: محلي (Local Server)
👤 الأدمن المسؤول: {ADMIN_ID}

✅ البوت جاهز لاستقبال الطلبات
📱 يمكن للمستخدمين التفاعل مع البوت الآن

🔧 لإدارة البوت استخدم تطبيق الإدارة
        """
        
        bot.send_message(ADMIN_ID, start_message)
        
        return jsonify({'success': True, 'message': 'تم بدء البوت بنجاح مع إرسال الإشعار'})
    else:
        return jsonify({'success': False, 'message': 'البوت يعمل بالفعل'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """إيقاف البوت"""
    global BOT_RUNNING
    
    if BOT_RUNNING:
        # إشعار الأدمن بإيقاف البوت
        stop_message = f"""
⏹️ تم إيقاف البوت

📊 معلومات الإيقاف:
🤖 حالة البوت: متوقف
🕐 وقت الإيقاف: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 تم الإيقاف بواسطة: الأدمن

⚠️ البوت لن يستقبل طلبات جديدة
🔧 لإعادة تشغيل البوت استخدم تطبيق الإدارة
        """
        
        bot.send_message(ADMIN_ID, stop_message)
        
        bot.stop_polling()
        BOT_RUNNING = False
        return jsonify({'success': True, 'message': 'تم إيقاف البوت مع إرسال الإشعار'})
    else:
        return jsonify({'success': False, 'message': 'البوت متوقف بالفعل'})

@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """حالة البوت"""
    return jsonify({'running': BOT_RUNNING})

@app.route('/api/users', methods=['GET'])
def get_users():
    """الحصول على قائمة المستخدمين"""
    users = db.get_all_users()
    users_list = []
    
    for user in users:
        users_list.append({
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'is_banned': bool(user[4]),
            'join_date': user[5]
        })
    
    return jsonify(users_list)

@app.route('/api/users/<int:user_id>/ban', methods=['POST'])
def ban_user(user_id):
    """حظر مستخدم"""
    # الحصول على معلومات المستخدم قبل الحظر
    user_info = db.get_user_info(user_id)
    
    db.ban_user(user_id)
    
    # إرسال إشعار للمستخدم المحظور
    ban_message = """
🚫 تم حظرك من استخدام البوت

للاستفسار عن سبب الحظر أو طلب إلغاء الحظر، يرجى التواصل مع الإدارة.

📞 للتواصل: @support
    """
    
    try:
        bot.send_message(user_id, ban_message)
    except:
        pass  # في حالة عدم إمكانية الإرسال
    
    # إشعار الأدمن
    admin_message = f"""
🚫 تم حظر مستخدم

👤 معلومات المستخدم المحظور:
🆔 معرف المستخدم: {user_id}
👤 الاسم: {user_info.get('first_name', 'غير محدد')} {user_info.get('last_name', '')}
📱 اسم المستخدم: @{user_info.get('username', 'غير محدد')}
📅 تاريخ الحظر: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ تم إرسال إشعار للمستخدم بالحظر
    """
    
    bot.send_message(ADMIN_ID, admin_message)
    
    return jsonify({'success': True, 'message': 'تم حظر المستخدم مع إرسال الإشعارات'})

@app.route('/api/users/<int:user_id>/unban', methods=['POST'])
def unban_user(user_id):
    """إلغاء حظر مستخدم"""
    # الحصول على معلومات المستخدم
    user_info = db.get_user_info(user_id)
    
    db.unban_user(user_id)
    
    # إرسال إشعار للمستخدم بإلغاء الحظر
    unban_message = """
✅ تم إلغاء حظرك من البوت!

يمكنك الآن استخدام البوت بشكل طبيعي.

🛒 لطلب بروكسي جديد اضغط /start

مرحباً بك مرة أخرى! 🙏
    """
    
    try:
        bot.send_message(user_id, unban_message)
    except:
        pass  # في حالة عدم إمكانية الإرسال
    
    # إشعار الأدمن
    admin_message = f"""
✅ تم إلغاء حظر مستخدم

👤 معلومات المستخدم:
🆔 معرف المستخدم: {user_id}
👤 الاسم: {user_info.get('first_name', 'غير محدد')} {user_info.get('last_name', '')}
📱 اسم المستخدم: @{user_info.get('username', 'غير محدد')}
📅 تاريخ إلغاء الحظر: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ تم إرسال إشعار للمستخدم بإلغاء الحظر
    """
    
    bot.send_message(ADMIN_ID, admin_message)
    
    return jsonify({'success': True, 'message': 'تم إلغاء حظر المستخدم مع إرسال الإشعارات'})

@app.route('/api/proxy-types', methods=['GET'])
def get_proxy_types():
    """الحصول على أنواع البروكسي"""
    proxy_types = db.get_active_proxy_types()
    types_list = []
    
    for proxy in proxy_types:
        types_list.append({
            'id': proxy[0],
            'name': proxy[1],
            'description': proxy[2],
            'price': proxy[3],
            'is_active': bool(proxy[4])
        })
    
    return jsonify(types_list)

@app.route('/api/proxy-types', methods=['POST'])
def add_proxy_type():
    """إضافة نوع بروكسي"""
    data = request.json
    proxy_id = db.add_proxy_type(
        data['name'],
        data['description'],
        data['price']
    )
    
    # إشعار الأدمن بإضافة نوع بروكسي جديد
    admin_message = f"""
🆕 تم إضافة نوع بروكسي جديد!

📋 تفاصيل البروكسي الجديد:
🆔 المعرف: {proxy_id}
🏷️ الاسم: {data['name']}
📝 الوصف: {data['description']}
💰 السعر: ${data['price']}
📅 تاريخ الإضافة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ البروكسي متوفر الآن للمستخدمين
🛒 يمكن للمستخدمين طلبه من البوت
    """
    
    bot.send_message(ADMIN_ID, admin_message)
    
    return jsonify({'success': True, 'id': proxy_id, 'message': 'تم إضافة نوع البروكسي مع إرسال الإشعار'})

@app.route('/api/orders/pending', methods=['GET'])
def get_pending_orders():
    """الحصول على الطلبات المعلقة"""
    orders = db.get_pending_orders()
    orders_list = []
    
    for order in orders:
        orders_list.append({
            'id': order[0],
            'user_id': order[1],
            'proxy_type_id': order[2],
            'status': order[3],
            'created_at': order[4],
            'username': order[6],
            'first_name': order[7],
            'proxy_name': order[8],
            'price': order[9]
        })
    
    return jsonify(orders_list)

@app.route('/api/orders/completed', methods=['GET'])
def get_completed_orders():
    """الحصول على الطلبات المكتملة"""
    orders = db.get_completed_orders()
    orders_list = []
    
    for order in orders:
        orders_list.append({
            'id': order[0],
            'user_id': order[1],
            'proxy_type_id': order[2],
            'status': order[3],
            'created_at': order[4],
            'completed_at': order[5],
            'proxy_info': json.loads(order[6]) if order[6] else None,
            'username': order[7],
            'first_name': order[8],
            'proxy_name': order[9],
            'price': order[10]
        })
    
    return jsonify(orders_list)

@app.route('/api/orders/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """إكمال طلب"""
    data = request.json
    proxy_info = data['proxy_info']
    
    # إكمال الطلب
    db.complete_order(order_id, proxy_info)
    
    # الحصول على معلومات المستخدم لإرسال الرسالة
    orders = db.get_completed_orders()
    for order in orders:
        if order[0] == order_id:
            user_id = order[1]
            username = order[7]
            first_name = order[8]
            proxy_name = order[9]
            price = order[10]
            
            # تنسيق رسالة البروكسي للمستخدم
            user_message = f"""
🎉 تم تجهيز البروكسي الخاص بك بنجاح! 🎉

📋 معلومات البروكسي:
🆔 رقم الطلب: {order_id}
🌐 العنوان: {proxy_info['host']}
🔌 البورت: {proxy_info['port']}
🔐 اسم المستخدم: {proxy_info['username']}
🗝️ كلمة المرور: {proxy_info['password']}
🌍 الدولة: {proxy_info['country']}
📍 المنطقة: {proxy_info['region']}
⚡ نوع البروكسي: {proxy_name}
📅 تاريخ الانتهاء: {proxy_info['expiry_date']}
⏰ وقت الانتهاء: {proxy_info['expiry_time']}

✅ حالة الطلب: مكتمل
💰 المبلغ المدفوع: ${price}

📖 تعليمات الاستخدام:
1️⃣ استخدم المعلومات أعلاه في إعدادات البروكسي
2️⃣ تأكد من صحة البيانات قبل الاستخدام
3️⃣ في حالة وجود مشاكل تواصل معنا فوراً

⚠️ مهم: احتفظ بهذه المعلومات في مكان آمن

شكراً لاختيارك خدماتنا! 🙏
للدعم الفني: @support
            """
            
            # إرسال الرسالة للمستخدم
            bot.send_message(user_id, user_message)
            
            # إرسال إشعار للأدمن بإكمال الطلب
            admin_notification = f"""
✅ تم إكمال الطلب بنجاح!

📋 تفاصيل الطلب المكتمل:
🆔 رقم الطلب: {order_id}
👤 المستخدم: {first_name} (@{username})
🆔 معرف المستخدم: {user_id}
🌐 نوع البروكسي: {proxy_name}
💰 المبلغ: ${price}
📅 تاريخ الإكمال: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 البروكسي المرسل:
• العنوان: {proxy_info['host']}:{proxy_info['port']}
• الدولة: {proxy_info['country']}
• المنطقة: {proxy_info['region']}
• تاريخ الانتهاء: {proxy_info['expiry_date']} {proxy_info['expiry_time']}

💰 تم إضافة ${price} للأرباح الإجمالية
            """
            
            # إرسال للأدمن
            bot.send_message(ADMIN_ID, admin_notification)
            
            # إرسال للأدمن المحفوظ في قاعدة البيانات (إن وجد)
            saved_admin_id = db.get_setting('admin_id')
            if saved_admin_id and saved_admin_id != ADMIN_ID:
                bot.send_message(saved_admin_id, admin_notification)
            
            break
    
    return jsonify({'success': True, 'message': 'تم إكمال الطلب وإرسال البروكسي مع إشعار الأدمن'})

@app.route('/api/earnings', methods=['GET'])
def get_earnings():
    """الحصول على الأرباح"""
    total = db.get_total_earnings()
    return jsonify({'total_earnings': total})

if __name__ == '__main__':
    # إضافة بعض أنواع البروكسي الافتراضية
    if not db.get_active_proxy_types():
        db.add_proxy_type("SOCKS5", "بروكسي SOCKS5 عالي السرعة", 5.0)
        db.add_proxy_type("HTTP", "بروكسي HTTP آمن", 3.0)
        db.add_proxy_type("HTTPS", "بروكسي HTTPS مشفر", 4.0)
    
    print("🚀 بدء تشغيل خادم البوت...")
    print("📱 يمكنك الآن استخدام التطبيق للتحكم في البوت")
    
    # تشغيل الخادم
    app.run(host='0.0.0.0', port=5000, debug=False)