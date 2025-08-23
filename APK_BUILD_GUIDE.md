# 📱 دليل إنشاء ملف APK - بوت البروكسي

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية إنشاء ملف APK للتطبيق بطرق مختلفة.

---

## 📋 المتطلبات الأساسية

### 1. تثبيت Node.js و npm:
```bash
# تحقق من التثبيت
node --version
npm --version
```

### 2. تثبيت Expo CLI:
```bash
npm install -g @expo/cli
npm install -g eas-cli
```

### 3. إنشاء حساب Expo:
- اذهب إلى: https://expo.dev/
- أنشئ حساب جديد أو سجل دخولك

---

## 🚀 الطرق المختلفة لإنشاء APK

### الطريقة الأولى: باستخدام EAS Build (الأفضل والأحدث)

#### 1. تسجيل الدخول:
```bash
eas login
```

#### 2. إعداد المشروع:
```bash
cd /path/to/your/project
eas build:configure
```

#### 3. بناء APK:
```bash
# للإنتاج
eas build --platform android --profile production

# أو للمعاينة
eas build --platform android --profile preview
```

#### 4. تنزيل APK:
- ستحصل على رابط في Terminal
- أو اذهب إلى: https://expo.dev/accounts/[username]/projects/proxy-bot-manager/builds

---

### الطريقة الثانية: باستخدام Expo Build (التقليدية)

#### 1. تسجيل الدخول:
```bash
expo login
```

#### 2. بناء APK:
```bash
expo build:android -t apk
```

#### 3. تنزيل APK:
- انتظر انتهاء البناء (قد يستغرق 10-20 دقيقة)
- ستحصل على رابط التنزيل

---

### الطريقة الثالثة: البناء المحلي (متقدم)

#### 1. تثبيت Android Studio:
- حمل من: https://developer.android.com/studio

#### 2. إعداد متغيرات البيئة:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### 3. تصدير المشروع:
```bash
expo eject
```

#### 4. بناء APK:
```bash
cd android
./gradlew assembleRelease
```

---

## 📁 ترتيب الملفات للتوزيع

### هيكل المجلد النهائي:

```
ProxyBotManager/
├── 📱 التطبيق
│   ├── ProxyBotManager.apk          # ملف APK الجاهز
│   └── app-release-signed.apk       # نسخة موقعة (إن وجدت)
│
├── 🤖 البوت
│   ├── telegram_proxy_bot.py        # البوت الرئيسي
│   ├── start_bot.py                # ملف التشغيل
│   ├── requirements.txt            # المتطلبات
│   ├── run.bat                     # تشغيل سريع (Windows)
│   └── run.sh                      # تشغيل سريع (Linux/Mac)
│
└── 📚 الوثائق
    ├── README.md                   # التعليمات الأساسية
    ├── INSTALLATION_GUIDE.md       # دليل التثبيت
    ├── APK_BUILD_GUIDE.md          # هذا الملف
    └── PROJECT_SUMMARY.md          # ملخص المشروع
```

---

## 🎯 خطوات التوزيع النهائية

### 1. إنشاء مجلد التوزيع:
```bash
mkdir ProxyBotManager
cd ProxyBotManager
```

### 2. نسخ ملفات البوت:
```bash
cp telegram_proxy_bot.py ProxyBotManager/
cp start_bot.py ProxyBotManager/
cp requirements.txt ProxyBotManager/
cp run.bat ProxyBotManager/
cp run.sh ProxyBotManager/
cp *.md ProxyBotManager/
```

### 3. إضافة APK:
```bash
# بعد بناء APK، انسخه للمجلد
cp ProxyBotManager.apk ProxyBotManager/
```

### 4. ضغط المجلد:
```bash
zip -r ProxyBotManager.zip ProxyBotManager/
```

---

## 📱 كيفية تثبيت واستخدام APK

### للمستخدم النهائي:

#### 1. تثبيت APK:
- انقل ملف APK للهاتف
- فعّل "مصادر غير معروفة" في الإعدادات
- اضغط على APK وثبت التطبيق

#### 2. تشغيل البوت:
```bash
# على الكمبيوتر
python start_bot.py
```

#### 3. استخدام التطبيق:
- افتح التطبيق على الهاتف
- اذهب لإعدادات البوت
- أدخل معرف الأدمن: `6891599955`
- اضغط "تشغيل البوت"

---

## 🔧 إعدادات متقدمة للـ APK

### تخصيص الأيقونة:
```bash
# أنشئ مجلد assets
mkdir assets

# أضف الأيقونات (يجب أن تكون PNG):
# assets/icon.png (1024x1024)
# assets/adaptive-icon.png (1024x1024)
# assets/splash.png (1242x2436)
```

### تخصيص معلومات التطبيق:
```json
// في app.json
{
  "expo": {
    "name": "Proxy Bot Manager",
    "description": "نظام إدارة البروكسيات المتقدم",
    "version": "1.0.0",
    "android": {
      "package": "com.mohamadzalaf.proxybot",
      "versionCode": 1
    }
  }
}
```

---

## ⚠️ نصائح مهمة

### 1. الأمان:
- لا تشارك ملف APK مع أشخاص غير موثوقين
- احتفظ بمعرف البوت سرياً
- استخدم كلمات مرور قوية

### 2. الأداء:
- تأكد من وجود اتصال إنترنت مستقر
- أغلق التطبيقات الأخرى لتوفير الذاكرة
- راقب استهلاك البطارية

### 3. التحديثات:
- احتفظ بنسخة من الكود المصدري
- وثق أي تغييرات تقوم بها
- اعمل نسخ احتياطية منتظمة

---

## 🛠️ استكشاف أخطاء APK

### مشاكل شائعة:

#### 1. APK لا يعمل:
```bash
# تحقق من إعدادات Android
# تأكد من تفعيل "مصادر غير معروفة"
# جرب إعادة تثبيت التطبيق
```

#### 2. لا يتصل بالبوت:
```bash
# تأكد من تشغيل البوت أولاً
python start_bot.py

# تحقق من عنوان IP
# في التطبيق، استخدم IP الفعلي بدلاً من localhost
```

#### 3. مشاكل في البناء:
```bash
# امسح cache
npm cache clean --force
rm -rf node_modules
npm install

# جرب بناء جديد
eas build --platform android --clear-cache
```

---

## 📞 الدعم الفني

### في حالة وجود مشاكل:
- 💬 **معرف الأدمن**: `6891599955`
- 📖 راجع ملف README.md
- 🔍 تحقق من INSTALLATION_GUIDE.md

### معلومات مفيدة للدعم:
- نوع المشكلة (بناء APK، تثبيت، تشغيل)
- نظام التشغيل المستخدم
- رسالة الخطأ كاملة
- خطوات إعادة إنتاج المشكلة

---

## ✅ قائمة التحقق النهائية

### قبل إنشاء APK:
- [ ] Node.js مثبت
- [ ] Expo CLI مثبت
- [ ] تم تسجيل الدخول في Expo
- [ ] تم اختبار التطبيق محلياً

### بعد إنشاء APK:
- [ ] تم تنزيل APK بنجاح
- [ ] تم اختبار التثبيت
- [ ] التطبيق يعمل بشكل صحيح
- [ ] يمكن الاتصال بالبوت

### للتوزيع:
- [ ] تم إنشاء مجلد التوزيع
- [ ] تم نسخ جميع الملفات
- [ ] تم إضافة الوثائق
- [ ] تم ضغط المجلد

---

## 🎉 تهانينا!

إذا اتبعت هذا الدليل، فلديك الآن:
- ✅ ملف APK جاهز للتوزيع
- ✅ مجلد كامل بجميع الملفات المطلوبة
- ✅ وثائق شاملة للمستخدمين

**النظام جاهز للاستخدام الفوري! 🚀**

---

*تم إعداد هذا الدليل بـ ❤️ من قبل Mohamad Zalaf ©2025*