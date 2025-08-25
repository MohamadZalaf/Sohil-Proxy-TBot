# بوت بيع البروكسيات - Proxy Sales Bot

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
