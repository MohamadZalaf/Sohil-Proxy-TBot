# 🚀 دليل البدء السريع - بوت البروكسي

**المطور: Mohamad Zalaf ©2025**

---

## 📱 لإنشاء ملف APK

### الطريقة السهلة:

#### Windows:
```cmd
# انقر نقرة مزدوجة على الملف
build_apk.bat
```

#### Linux/Mac:
```bash
./build_apk.sh
```

### الطريقة اليدوية:
```bash
# 1. تثبيت المتطلبات
npm install -g @expo/cli eas-cli

# 2. تسجيل الدخول
eas login

# 3. بناء APK
eas build --platform android --profile production
```

---

## 🤖 لتشغيل البوت

### Windows:
```cmd
run.bat
```

### Linux/Mac:
```bash
./run.sh
```

### يدوياً:
```bash
python start_bot.py
```

---

## 📁 ترتيب الملفات للمستخدم النهائي

```
ProxyBotManager/
├── ProxyBotManager.apk     # التطبيق للهاتف
├── telegram_proxy_bot.py   # البوت للكمبيوتر
├── start_bot.py           # ملف التشغيل
├── requirements.txt       # المتطلبات
├── run.bat               # تشغيل سريع (Windows)
├── run.sh                # تشغيل سريع (Linux/Mac)
└── README.md             # التعليمات
```

---

## 🎯 خطوات الاستخدام للمستخدم النهائي

### 1️⃣ على الكمبيوتر:
```bash
# تشغيل البوت
python start_bot.py
# أو
run.bat  # Windows
./run.sh # Linux/Mac
```

### 2️⃣ على الهاتف:
- ثبت `ProxyBotManager.apk`
- افتح التطبيق
- اذهب لإعدادات البوت
- أدخل معرف الأدمن: `6891599955`
- اضغط "تشغيل البوت"

### 3️⃣ اختبار النظام:
- أرسل `/start` للبوت في التيليغرام
- اطلب بروكسي من البوت
- عالج الطلب من التطبيق

---

## ⚙️ الإعدادات المهمة

- **معرف البوت**: `8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA`
- **معرف الأدمن**: `6891599955`
- **عنوان الخادم**: `http://localhost:5000`

---

## 🔔 الإشعارات

النظام يرسل إشعارات تلقائية:
- للمستخدمين: تأكيد الطلبات، معلومات البروكسي
- للأدمن: طلبات جديدة، حالة البوت

---

## 📞 الدعم

**معرف الأدمن**: `6891599955`

---

## 🎉 مبروك!

النظام جاهز للاستخدام الفوري! 

**المطور: Mohamad Zalaf ©2025**