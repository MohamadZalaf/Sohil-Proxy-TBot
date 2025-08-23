import { exec } from 'react-native-exec';
import * as FileSystem from 'expo-file-system';
import { Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BOT_FILES_DIR = FileSystem.documentDirectory + 'ProxyBot/';

class CloudServerService {
  constructor() {
    this.isConnected = false;
    this.serverConfig = null;
  }

  async saveServerConfig(config) {
    try {
      await AsyncStorage.setItem('ssh_server_config', JSON.stringify(config));
      this.serverConfig = config;
      console.log('✅ تم حفظ إعدادات الخادم');
    } catch (error) {
      console.error('❌ خطأ في حفظ إعدادات الخادم:', error);
    }
  }

  async loadServerConfig() {
    try {
      const config = await AsyncStorage.getItem('ssh_server_config');
      if (config) {
        this.serverConfig = JSON.parse(config);
        return this.serverConfig;
      }
      return null;
    } catch (error) {
      console.error('❌ خطأ في تحميل إعدادات الخادم:', error);
      return null;
    }
  }

  async testSSHConnection(config) {
    try {
      const { host, port, username, password, privateKey } = config;
      
      let sshCommand;
      if (privateKey) {
        // إنشاء ملف مفتاح خاص مؤقت
        const keyPath = BOT_FILES_DIR + 'temp_key';
        await FileSystem.writeAsStringAsync(keyPath, privateKey);
        await exec(`chmod 600 ${keyPath}`);
        sshCommand = `ssh -i ${keyPath} -p ${port} -o StrictHostKeyChecking=no ${username}@${host} "echo 'SSH Connection Test Successful'"`;
      } else {
        sshCommand = `sshpass -p '${password}' ssh -p ${port} -o StrictHostKeyChecking=no ${username}@${host} "echo 'SSH Connection Test Successful'"`;
      }

      const result = await exec(sshCommand);
      return result.includes('SSH Connection Test Successful');
    } catch (error) {
      console.error('❌ خطأ في اختبار الاتصال:', error);
      return false;
    }
  }

  async installSSHClient() {
    try {
      console.log('📦 تثبيت عميل SSH...');
      
      // تحديث قوائم الحزم وتثبيت SSH
      await exec('pkg update -y');
      await exec('pkg install openssh sshpass -y');
      
      console.log('✅ تم تثبيت عميل SSH');
      return true;
    } catch (error) {
      console.error('❌ خطأ في تثبيت SSH:', error);
      return false;
    }
  }

  async createBotFiles() {
    try {
      console.log('📁 إنشاء ملفات البوت...');
      
      // إنشاء مجلد البوت
      await FileSystem.makeDirectoryAsync(BOT_FILES_DIR, { intermediates: true });

      // إنشاء ملف البوت Python (نفس الكود السابق)
      const botCode = `#!/usr/bin/env python3
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
ADMIN_ID = "6891599955"
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
        
        text = "🛒 اختر نوع البروكسي الذي تريد شراؤه:\\n\\n"
        buttons = []
        
        for proxy in proxy_types:
            text += f"🔹 {proxy[1]} - ${proxy[3]}\\n{proxy[2]}\\n\\n"
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
        """
        
        # إرسال للأدمن المحدد
        self.send_message(ADMIN_ID, admin_text)
    
    def start_polling(self):
        """بدء البوت"""
        self.running = True
        logger.info("تم بدء البوت...")
        
        # إرسال إشعار بدء التشغيل
        self.send_message(ADMIN_ID, f"""
🚀 تم بدء البوت بنجاح!

📊 معلومات البوت:
🤖 حالة البوت: نشط ويعمل
🕐 وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 الخادم: خادم سحابي عبر SSH
👤 الأدمن المسؤول: {ADMIN_ID}

✅ البوت جاهز لاستقبال الطلبات
📱 يمكن للمستخدمين التفاعل مع البوت الآن
        """)
        
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
        
        # إرسال إشعار بالإيقاف
        self.send_message(ADMIN_ID, f"""
⏹️ تم إيقاف البوت

📊 معلومات الإيقاف:
🤖 حالة البوت: متوقف
🕐 وقت الإيقاف: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 تم الإيقاف بواسطة: الأدمن

⚠️ البوت لن يستقبل طلبات جديدة
        """)

# إنشاء البوت
bot = TelegramBot(BOT_TOKEN)
bot_thread = None

# API endpoints للتطبيق الأندرويد
@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """بدء البوت"""
    global bot_thread, BOT_RUNNING
    
    if not BOT_RUNNING:
        bot_thread = threading.Thread(target=bot.start_polling)
        bot_thread.daemon = True
        bot_thread.start()
        BOT_RUNNING = True
        
        return jsonify({'success': True, 'message': 'تم بدء البوت بنجاح على الخادم السحابي'})
    else:
        return jsonify({'success': False, 'message': 'البوت يعمل بالفعل'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """إيقاف البوت"""
    global BOT_RUNNING
    
    if BOT_RUNNING:
        bot.stop_polling()
        BOT_RUNNING = False
        return jsonify({'success': True, 'message': 'تم إيقاف البوت'})
    else:
        return jsonify({'success': False, 'message': 'البوت متوقف بالفعل'})

@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """حالة البوت"""
    return jsonify({'running': BOT_RUNNING})

# باقي API endpoints...
[API endpoints code continues...]

if __name__ == '__main__':
    # إضافة بعض أنواع البروكسي الافتراضية
    if not db.get_active_proxy_types():
        db.add_proxy_type("SOCKS5", "بروكسي SOCKS5 عالي السرعة", 5.0)
        db.add_proxy_type("HTTP", "بروكسي HTTP آمن", 3.0)
        db.add_proxy_type("HTTPS", "بروكسي HTTPS مشفر", 4.0)
    
    print("🚀 بدء تشغيل خادم البوت على الخادم السحابي...")
    print("📱 يمكنك الآن استخدام التطبيق للتحكم في البوت")
    print("المطور: Mohamad Zalaf ©2025")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
`;

      await FileSystem.writeAsStringAsync(
        BOT_FILES_DIR + 'telegram_proxy_bot.py',
        botCode
      );

      // إنشاء ملف requirements.txt
      const requirements = `flask==2.3.3
flask-cors==4.0.0
requests==2.31.0`;

      await FileSystem.writeAsStringAsync(
        BOT_FILES_DIR + 'requirements.txt',
        requirements
      );

      // إنشاء ملف setup.sh للخادم
      const setupScript = `#!/bin/bash
echo "🚀 إعداد بوت البروكسي على الخادم السحابي..."
echo "المطور: Mohamad Zalaf ©2025"
echo "================================"

# تحديث النظام
sudo apt update -y
sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3 python3-pip python3-venv -y

# إنشاء مجلد البوت
mkdir -p ~/ProxyBot
cd ~/ProxyBot

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

echo "✅ تم إعداد البيئة بنجاح!"
echo "🚀 بدء تشغيل البوت..."

# تشغيل البوت
python3 telegram_proxy_bot.py
`;

      await FileSystem.writeAsStringAsync(
        BOT_FILES_DIR + 'setup.sh',
        setupScript
      );

      console.log('✅ تم إنشاء ملفات البوت بنجاح');
      return true;
    } catch (error) {
      console.error('❌ خطأ في إنشاء ملفات البوت:', error);
      return false;
    }
  }

  async deployToCloudServer(config) {
    try {
      console.log('🚀 نشر البوت على الخادم السحابي...');
      
      const { host, port, username, password, privateKey } = config;
      
      // إنشاء ملفات البوت محلياً
      await this.createBotFiles();
      
      let sshCommand;
      let scpCommand;
      
      if (privateKey) {
        // استخدام المفتاح الخاص
        const keyPath = BOT_FILES_DIR + 'temp_key';
        await FileSystem.writeAsStringAsync(keyPath, privateKey);
        await exec(`chmod 600 ${keyPath}`);
        
        sshCommand = `ssh -i ${keyPath} -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
        scpCommand = `scp -i ${keyPath} -P ${port} -o StrictHostKeyChecking=no`;
      } else {
        // استخدام كلمة المرور
        sshCommand = `sshpass -p '${password}' ssh -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
        scpCommand = `sshpass -p '${password}' scp -P ${port} -o StrictHostKeyChecking=no`;
      }

      console.log('📁 رفع الملفات إلى الخادم...');
      
      // رفع ملفات البوت
      await exec(`${scpCommand} ${BOT_FILES_DIR}telegram_proxy_bot.py ${username}@${host}:~/ProxyBot/`);
      await exec(`${scpCommand} ${BOT_FILES_DIR}requirements.txt ${username}@${host}:~/ProxyBot/`);
      await exec(`${scpCommand} ${BOT_FILES_DIR}setup.sh ${username}@${host}:~/ProxyBot/`);

      console.log('🔧 إعداد البيئة على الخادم...');
      
      // إعداد وتشغيل البوت على الخادم
      await exec(`${sshCommand} "cd ~/ProxyBot && chmod +x setup.sh && nohup ./setup.sh > bot.log 2>&1 &"`);

      this.isConnected = true;
      console.log('✅ تم نشر البوت بنجاح على الخادم السحابي');

      Alert.alert(
        'تم النشر بنجاح! 🚀',
        `البوت يعمل الآن على الخادم السحابي:\n\n🌐 الخادم: ${host}:${port}\n👤 المستخدم: ${username}\n\n• البوت يعمل في الخلفية\n• يمكنك إغلاق التطبيق بأمان\n• البوت سيبقى يعمل 24/7`,
        [{ text: 'ممتاز!' }]
      );

      return true;
    } catch (error) {
      console.error('❌ خطأ في نشر البوت:', error);
      Alert.alert('خطأ في النشر', error.message || 'فشل في نشر البوت على الخادم');
      return false;
    }
  }

  async stopCloudBot(config) {
    try {
      console.log('⏹️ إيقاف البوت على الخادم السحابي...');
      
      const { host, port, username, password, privateKey } = config;
      
      let sshCommand;
      if (privateKey) {
        const keyPath = BOT_FILES_DIR + 'temp_key';
        await FileSystem.writeAsStringAsync(keyPath, privateKey);
        await exec(`chmod 600 ${keyPath}`);
        sshCommand = `ssh -i ${keyPath} -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
      } else {
        sshCommand = `sshpass -p '${password}' ssh -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
      }

      // إيقاف البوت
      await exec(`${sshCommand} "pkill -f telegram_proxy_bot.py"`);

      this.isConnected = false;
      console.log('✅ تم إيقاف البوت على الخادم السحابي');

      Alert.alert(
        'تم الإيقاف ⏹️',
        'تم إيقاف البوت على الخادم السحابي.\n\nيمكنك إعادة تشغيله في أي وقت.',
        [{ text: 'موافق' }]
      );

      return true;
    } catch (error) {
      console.error('❌ خطأ في إيقاف البوت:', error);
      Alert.alert('خطأ', error.message || 'فشل في إيقاف البوت');
      return false;
    }
  }

  async checkCloudBotStatus(config) {
    try {
      const { host, port, username, password, privateKey } = config;
      
      let sshCommand;
      if (privateKey) {
        const keyPath = BOT_FILES_DIR + 'temp_key';
        await FileSystem.writeAsStringAsync(keyPath, privateKey);
        await exec(`chmod 600 ${keyPath}`);
        sshCommand = `ssh -i ${keyPath} -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
      } else {
        sshCommand = `sshpass -p '${password}' ssh -p ${port} -o StrictHostKeyChecking=no ${username}@${host}`;
      }

      // التحقق من تشغيل البوت
      const result = await exec(`${sshCommand} "pgrep -f telegram_proxy_bot.py"`);
      return result.trim().length > 0;
    } catch (error) {
      console.error('❌ خطأ في التحقق من حالة البوت:', error);
      return false;
    }
  }

  getConnectionStatus() {
    return this.isConnected;
  }

  async clearTempFiles() {
    try {
      // حذف الملفات المؤقتة
      await exec(`rm -f ${BOT_FILES_DIR}temp_key`);
    } catch (error) {
      console.error('❌ خطأ في حذف الملفات المؤقتة:', error);
    }
  }
}

export default new CloudServerService();