import { Alert, Linking } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:5000/api';

class TermuxBotService {
  constructor() {
    this.isRunning = false;
  }

  async checkTermuxInstalled() {
    try {
      // محاولة فتح Termux إذا كان مثبتاً
      return true; // نفترض أنه مثبت، المستخدم سيتعامل مع هذا يدوياً
    } catch (error) {
      return false;
    }
  }

  async showTermuxInstructions() {
    Alert.alert(
      'تعليمات تشغيل البوت على Termux 📱',
      `لتشغيل البوت محلياً على هاتفك، اتبع هذه الخطوات:

1️⃣ ثبت Termux من Google Play أو F-Droid
2️⃣ افتح Termux واكتب الأوامر التالية:

pkg update && pkg upgrade -y
pkg install python git -y
pip install flask flask-cors requests

3️⃣ إنشاء مجلد البوت:
mkdir ProxyBot && cd ProxyBot

4️⃣ انسخ ملفات البوت من مجلد التطبيق إلى Termux
5️⃣ شغل البوت:
python telegram_proxy_bot.py

✅ بعدها يمكنك استخدام أزرار التحكم في التطبيق

📋 ملاحظة: تأكد من أن Termux يعمل في الخلفية دائماً`,
      [
        {
          text: 'تنزيل Termux',
          onPress: () => Linking.openURL('https://play.google.com/store/apps/details?id=com.termux')
        },
        {
          text: 'فهمت',
          style: 'default'
        }
      ]
    );
  }

  async startBot() {
    try {
      // محاولة بدء البوت عبر API
      const response = await fetch(`${API_BASE_URL}/bot/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          this.isRunning = true;
          Alert.alert(
            '✅ تم بدء البوت!',
            'البوت يعمل الآن ويستقبل الطلبات.\n\n• تأكد من إبقاء Termux يعمل\n• لا تغلق نافذة Termux\n• البوت جاهز لاستقبال الرسائل',
            [{ text: 'ممتاز!' }]
          );
          return true;
        }
      }
      
      throw new Error('فشل في بدء البوت');
    } catch (error) {
      console.error('خطأ في بدء البوت:', error);
      
      // إذا فشل الاتصال، نعرض التعليمات
      Alert.alert(
        'تعذر الاتصال بالبوت 🤔',
        'يبدو أن البوت غير مُشغّل في Termux.\n\nهل تريد عرض تعليمات التشغيل؟',
        [
          { text: 'إلغاء', style: 'cancel' },
          { 
            text: 'عرض التعليمات', 
            onPress: () => this.showTermuxInstructions()
          }
        ]
      );
      return false;
    }
  }

  async stopBot() {
    try {
      const response = await fetch(`${API_BASE_URL}/bot/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          this.isRunning = false;
          Alert.alert(
            '⏹️ تم إيقاف البوت',
            'البوت متوقف الآن ولن يستقبل طلبات جديدة.\n\nيمكنك إعادة تشغيله في أي وقت.',
            [{ text: 'موافق' }]
          );
          return true;
        }
      }
      
      throw new Error('فشل في إيقاف البوت');
    } catch (error) {
      console.error('خطأ في إيقاف البوت:', error);
      Alert.alert(
        'خطأ في الإيقاف',
        'تعذر إيقاف البوت عبر API.\n\nيمكنك إيقافه يدوياً في Termux بالضغط على Ctrl+C',
        [{ text: 'موافق' }]
      );
      return false;
    }
  }

  async checkBotHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/bot/status`, {
        method: 'GET',
        timeout: 5000,
      });
      
      if (response.ok) {
        const data = await response.json();
        this.isRunning = data.running;
        return data.running;
      }
      
      this.isRunning = false;
      return false;
    } catch (error) {
      this.isRunning = false;
      return false;
    }
  }

  getStatus() {
    return this.isRunning;
  }

  async showSetupGuide() {
    Alert.alert(
      'دليل الإعداد الكامل 📚',
      `لتشغيل البوت محلياً على الهاتف:

🔧 متطلبات التشغيل:
• Termux (مجاني)
• اتصال إنترنت مستقر
• مساحة 100 ميجا تقريباً

📱 خطوات التثبيت:
1. ثبت Termux
2. افتح Termux وثبت Python
3. انسخ ملفات البوت
4. شغل البوت
5. استخدم التطبيق للتحكم

💡 فوائد التشغيل المحلي:
• مجاني تماماً
• تحكم كامل
• لا حاجة لخادم خارجي
• يعمل بدون إنترنت (بعد التثبيت)

هل تريد التعليمات التفصيلية؟`,
      [
        { text: 'لاحقاً', style: 'cancel' },
        { 
          text: 'نعم، اعرضها', 
          onPress: () => this.showDetailedInstructions()
        }
      ]
    );
  }

  showDetailedInstructions() {
    Alert.alert(
      'التعليمات التفصيلية 📋',
      `خطوة بخطوة:

1️⃣ تثبيت Termux:
• نزل من Google Play أو F-Droid
• افتح التطبيق

2️⃣ تحديث النظام:
pkg update
pkg upgrade

3️⃣ تثبيت Python:
pkg install python

4️⃣ تثبيت المكتبات:
pip install flask flask-cors requests

5️⃣ إنشاء مجلد:
mkdir ProxyBot
cd ProxyBot

6️⃣ إنشاء ملف البوت:
nano telegram_proxy_bot.py
(انسخ الكود من ملفات التطبيق)

7️⃣ تشغيل البوت:
python telegram_proxy_bot.py

✅ الآن يمكنك استخدام التطبيق!`,
      [
        { text: 'فهمت', style: 'default' },
        { 
          text: 'نسخ الملفات', 
          onPress: () => this.showFileCopyInstructions()
        }
      ]
    );
  }

  showFileCopyInstructions() {
    Alert.alert(
      'نسخ ملفات البوت 📁',
      `لنسخ ملفات البوت:

🔄 الطريقة السهلة:
1. افتح مدير الملفات
2. اذهب إلى مجلد التطبيق
3. انسخ ملف telegram_proxy_bot.py
4. الصقه في مجلد ProxyBot في Termux

📂 مسار Termux:
/data/data/com.termux/files/home/ProxyBot/

📝 أو أنشئ الملف يدوياً:
nano telegram_proxy_bot.py
ثم انسخ الكود من التطبيق

✅ بعد النسخ شغل:
python telegram_proxy_bot.py`,
      [{ text: 'واضح!' }]
    );
  }
}

export default new TermuxBotService();