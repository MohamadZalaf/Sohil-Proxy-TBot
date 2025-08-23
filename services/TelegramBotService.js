import * as SQLite from 'expo-sqlite';
import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';

const BOT_TOKEN = "8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA";
const ADMIN_ID = "6891599955";
const BACKGROUND_TASK_NAME = 'telegram-bot-polling';

class TelegramBotService {
  constructor() {
    this.db = null;
    this.isRunning = false;
    this.updateOffset = 0;
    this.pollingInterval = null;
    this.initDatabase();
  }

  async initDatabase() {
    try {
      this.db = SQLite.openDatabase('proxy_bot.db');
      
      // إنشاء الجداول
      this.db.transaction(tx => {
        // جدول المستخدمين
        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_banned INTEGER DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // جدول أنواع البروكسي
        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS proxy_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            is_active INTEGER DEFAULT 1
          )
        `);

        // جدول الطلبات
        tx.executeSql(`
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
        `);

        // جدول الأرباح
        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            amount REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id)
          )
        `);

        // جدول الإعدادات
        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
          )
        `);

        // إضافة أنواع بروكسي افتراضية
        tx.executeSql(`
          INSERT OR IGNORE INTO proxy_types (id, name, description, price, is_active)
          VALUES 
            (1, 'SOCKS5', 'بروكسي SOCKS5 عالي السرعة', 5.0, 1),
            (2, 'HTTP', 'بروكسي HTTP آمن', 3.0, 1),
            (3, 'HTTPS', 'بروكسي HTTPS مشفر', 4.0, 1)
        `);
      });

      console.log('✅ تم إعداد قاعدة البيانات');
    } catch (error) {
      console.error('❌ خطأ في إعداد قاعدة البيانات:', error);
    }
  }

  async sendMessage(chatId, text, replyMarkup = null) {
    try {
      const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
      const data = {
        chat_id: chatId,
        text: text,
        parse_mode: 'HTML'
      };

      if (replyMarkup) {
        data.reply_markup = JSON.stringify(replyMarkup);
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      return await response.json();
    } catch (error) {
      console.error('خطأ في إرسال الرسالة:', error);
      return null;
    }
  }

  async getUpdates() {
    try {
      const url = `https://api.telegram.org/bot${BOT_TOKEN}/getUpdates`;
      const params = new URLSearchParams({
        offset: this.updateOffset + 1,
        timeout: 30
      });

      const response = await fetch(`${url}?${params}`);
      return await response.json();
    } catch (error) {
      console.error('خطأ في الحصول على التحديثات:', error);
      return null;
    }
  }

  createKeyboard(buttons) {
    const keyboard = [];
    for (const row of buttons) {
      const keyboardRow = [];
      for (const button of row) {
        keyboardRow.push({
          text: button.text,
          callback_data: button.callback_data
        });
      }
      keyboard.push(keyboardRow);
    }

    return {
      inline_keyboard: keyboard
    };
  }

  async handleMessage(message) {
    const chatId = message.chat.id;
    const userId = message.from.id;
    const text = message.text || '';

    // إضافة المستخدم لقاعدة البيانات
    await this.addUser({
      user_id: userId,
      username: message.from.username || '',
      first_name: message.from.first_name || '',
      last_name: message.from.last_name || ''
    });

    // التحقق من الحظر
    const isBanned = await this.isUserBanned(userId);
    if (isBanned) {
      await this.sendMessage(chatId, "❌ تم حظرك من استخدام البوت");
      return;
    }

    if (text === '/start') {
      await this.handleStart(chatId);
    }
  }

  async handleCallbackQuery(callbackQuery) {
    const chatId = callbackQuery.message.chat.id;
    const userId = callbackQuery.from.id;
    const data = callbackQuery.data;

    // التحقق من الحظر
    const isBanned = await this.isUserBanned(userId);
    if (isBanned) {
      await this.sendMessage(chatId, "❌ تم حظرك من استخدام البوت");
      return;
    }

    if (data === 'request_proxy') {
      await this.showProxyTypes(chatId);
    } else if (data.startsWith('proxy_')) {
      const proxyTypeId = parseInt(data.split('_')[1]);
      await this.handleProxyRequest(chatId, userId, proxyTypeId);
    }
  }

  async handleStart(chatId) {
    const welcomeText = `
🤖 مرحباً بك في بوت البروكسي!

يمكنك من خلال هذا البوت طلب شراء بروكسي عالي الجودة

اختر من الخيارات أدناه:
    `;

    const keyboard = this.createKeyboard([
      [{ text: '🛒 طلب شراء بروكسي', callback_data: 'request_proxy' }],
      [{ text: '📞 التواصل مع الدعم', callback_data: 'support' }]
    ]);

    await this.sendMessage(chatId, welcomeText, keyboard);
  }

  async showProxyTypes(chatId) {
    const proxyTypes = await this.getActiveProxyTypes();

    if (proxyTypes.length === 0) {
      await this.sendMessage(chatId, "❌ لا توجد أنواع بروكسي متوفرة حالياً");
      return;
    }

    let text = "🛒 اختر نوع البروكسي الذي تريد شراؤه:\n\n";
    const buttons = [];

    for (const proxy of proxyTypes) {
      text += `🔹 ${proxy.name} - $${proxy.price}\n${proxy.description}\n\n`;
      buttons.push([{
        text: `${proxy.name} - $${proxy.price}`,
        callback_data: `proxy_${proxy.id}`
      }]);
    }

    const keyboard = this.createKeyboard(buttons);
    await this.sendMessage(chatId, text, keyboard);
  }

  async handleProxyRequest(chatId, userId, proxyTypeId) {
    // الحصول على معلومات البروكسي
    const proxyType = await this.getProxyType(proxyTypeId);
    if (!proxyType) {
      await this.sendMessage(chatId, "❌ نوع البروكسي غير متوفر");
      return;
    }

    // إنشاء الطلب
    const orderId = await this.createOrder(userId, proxyTypeId);

    // إرسال رسالة للمستخدم
    const userMessage = `
✅ تم استلام طلبك بنجاح!

📋 تفاصيل الطلب:
🆔 رقم الطلب: ${orderId}
🛒 نوع البروكسي: ${proxyType.name}
📝 الوصف: ${proxyType.description}
💰 السعر: $${proxyType.price}
⏳ حالة الطلب: قيد المعالجة
📅 تاريخ الطلب: ${new Date().toLocaleString('ar-SA')}

💳 خطوات الدفع:
1️⃣ سيتم التواصل معك قريباً لتأكيد الدفع
2️⃣ بعد تأكيد الدفع سيتم تجهيز البروكسي
3️⃣ ستحصل على معلومات البروكسي كاملة

شكراً لثقتك بنا! 🙏
    `;

    await this.sendMessage(chatId, userMessage);

    // إرسال إشعار للأدمن
    const userInfo = await this.getUserInfo(userId);
    const adminText = `
🚨 طلب جديد وارد! 🚨

👤 معلومات المستخدم:
🆔 معرف المستخدم: ${userId}
👤 الاسم: ${userInfo.first_name} ${userInfo.last_name}
📱 اسم المستخدم: @${userInfo.username}

🛒 تفاصيل الطلب:
🆔 رقم الطلب: ${orderId}
🌐 نوع البروكسي: ${proxyType.name}
💰 السعر: $${proxyType.price}
📅 وقت الطلب: ${new Date().toLocaleString('ar-SA')}

⚡ يرجى معالجة الطلب من خلال التطبيق
    `;

    await this.sendMessage(ADMIN_ID, adminText);
  }

  // دوال قاعدة البيانات
  async addUser(userData) {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          `INSERT OR REPLACE INTO users 
           (user_id, username, first_name, last_name, is_banned, join_date)
           VALUES (?, ?, ?, ?, 0, datetime('now'))`,
          [userData.user_id, userData.username, userData.first_name, userData.last_name],
          (_, result) => resolve(result),
          (_, error) => reject(error)
        );
      });
    });
  }

  async isUserBanned(userId) {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT is_banned FROM users WHERE user_id = ?',
          [userId],
          (_, result) => {
            const banned = result.rows.length > 0 ? result.rows.item(0).is_banned === 1 : false;
            resolve(banned);
          },
          (_, error) => reject(error)
        );
      });
    });
  }

  async getActiveProxyTypes() {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT * FROM proxy_types WHERE is_active = 1',
          [],
          (_, result) => {
            const types = [];
            for (let i = 0; i < result.rows.length; i++) {
              types.push(result.rows.item(i));
            }
            resolve(types);
          },
          (_, error) => reject(error)
        );
      });
    });
  }

  async getProxyType(id) {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT * FROM proxy_types WHERE id = ?',
          [id],
          (_, result) => {
            const proxyType = result.rows.length > 0 ? result.rows.item(0) : null;
            resolve(proxyType);
          },
          (_, error) => reject(error)
        );
      });
    });
  }

  async createOrder(userId, proxyTypeId) {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          `INSERT INTO orders (user_id, proxy_type_id, status, created_at)
           VALUES (?, ?, 'pending', datetime('now'))`,
          [userId, proxyTypeId],
          (_, result) => resolve(result.insertId),
          (_, error) => reject(error)
        );
      });
    });
  }

  async getUserInfo(userId) {
    return new Promise((resolve, reject) => {
      this.db.transaction(tx => {
        tx.executeSql(
          'SELECT * FROM users WHERE user_id = ?',
          [userId],
          (_, result) => {
            const user = result.rows.length > 0 ? result.rows.item(0) : {};
            resolve(user);
          },
          (_, error) => reject(error)
        );
      });
    });
  }

  async startPolling() {
    if (this.isRunning) {
      console.log('البوت يعمل بالفعل');
      return;
    }

    console.log('🚀 بدء تشغيل البوت...');
    this.isRunning = true;

    // إرسال إشعار بدء التشغيل
    await this.sendMessage(ADMIN_ID, `
🚀 تم بدء البوت بنجاح!

📊 معلومات البوت:
🤖 حالة البوت: نشط ويعمل
🕐 وقت البدء: ${new Date().toLocaleString('ar-SA')}
🌐 الخادم: هاتف أندرويد
👤 الأدمن المسؤول: ${ADMIN_ID}

✅ البوت جاهز لاستقبال الطلبات
📱 يمكن للمستخدمين التفاعل مع البوت الآن
    `);

    // بدء الـ polling
    this.poll();

    // تسجيل مهمة الخلفية
    await this.registerBackgroundTask();
  }

  async stopPolling() {
    if (!this.isRunning) {
      console.log('البوت متوقف بالفعل');
      return;
    }

    console.log('⏹️ إيقاف البوت...');
    this.isRunning = false;

    if (this.pollingInterval) {
      clearTimeout(this.pollingInterval);
      this.pollingInterval = null;
    }

    // إلغاء مهمة الخلفية
    await BackgroundFetch.unregisterTaskAsync(BACKGROUND_TASK_NAME);

    // إرسال إشعار بالإيقاف
    await this.sendMessage(ADMIN_ID, `
⏹️ تم إيقاف البوت

📊 معلومات الإيقاف:
🤖 حالة البوت: متوقف
🕐 وقت الإيقاف: ${new Date().toLocaleString('ar-SA')}
👤 تم الإيقاف بواسطة: الأدمن

⚠️ البوت لن يستقبل طلبات جديدة
    `);
  }

  async poll() {
    if (!this.isRunning) return;

    try {
      const updates = await this.getUpdates();

      if (updates && updates.ok) {
        for (const update of updates.result) {
          this.updateOffset = update.update_id;

          if (update.message) {
            await this.handleMessage(update.message);
          } else if (update.callback_query) {
            await this.handleCallbackQuery(update.callback_query);
          }
        }
      }
    } catch (error) {
      console.error('خطأ في الـ polling:', error);
    }

    // جدولة الـ poll التالي
    if (this.isRunning) {
      this.pollingInterval = setTimeout(() => this.poll(), 1000);
    }
  }

  async registerBackgroundTask() {
    try {
      // تسجيل مهمة الخلفية
      TaskManager.defineTask(BACKGROUND_TASK_NAME, async () => {
        if (this.isRunning) {
          await this.poll();
          return BackgroundFetch.BackgroundFetchResult.NewData;
        }
        return BackgroundFetch.BackgroundFetchResult.NoData;
      });

      // تسجيل المهمة
      await BackgroundFetch.registerTaskAsync(BACKGROUND_TASK_NAME, {
        minimumInterval: 15, // 15 ثانية كحد أدنى
        stopOnTerminate: false,
        startOnBoot: true,
      });

      console.log('✅ تم تسجيل مهمة الخلفية');
    } catch (error) {
      console.error('❌ خطأ في تسجيل مهمة الخلفية:', error);
    }
  }

  getStatus() {
    return this.isRunning;
  }
}

export default new TelegramBotService();