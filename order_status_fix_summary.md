# إصلاح حالات الطلبات - Order Status Fix

## المشكلة
- عند اختيار زر الإلغاء أثناء معالجة البروكسي، تظهر رسالة أن الطلب محفوظ ولم يتم تعديله
- لكن عند الاستعلام عن الطلب، يظهر أنه "تم معالجته بالفعل"
- السبب: يتم تحديث حالة الطلب إلى 'completed' فور قبول الدفع

## الحل المطبق

### 1. إضافة حالات جديدة للطلبات
- **pending**: معلق (الحالة الافتراضية)
- **processing**: قيد المعالجة (بعد قبول الدفع، قبل إرسال البروكسي)
- **successful**: تم بنجاح (تم إرسال البروكسي)
- **failed**: فاشل (دفع غير حقيقي)
- **completed**: مكتمل (للتوافق مع الإصدارات القديمة)

### 2. تحديث دالة `update_order_status`
```python
def update_order_status(order_id: str, status: str):
    if status == 'processing':
        # قيد المعالجة بعد قبول الدفع
        db.execute_query('''
            UPDATE orders 
            SET status = 'processing', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))
    elif status == 'successful':
        # تم بنجاح - تم إرسال البروكسي
        db.execute_query('''
            UPDATE orders 
            SET status = 'successful', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))
    elif status == 'failed':
        # فاشل - دفع غير حقيقي
        db.execute_query('''
            UPDATE orders 
            SET status = 'failed', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))
```

### 3. تحديث `handle_payment_success`
- تم تغيير `update_order_status(order_id, 'completed')` إلى `update_order_status(order_id, 'processing')`
- تم تغيير `save_transaction(..., 'completed')` إلى `save_transaction(..., 'processing')`

### 4. تحديث إرسال البروكسي
عند إرسال البروكسي للمستخدم، يتم تحديث الحالة إلى 'successful':
```python
db.execute_query(
    "UPDATE orders SET status = 'successful', processed_at = CURRENT_TIMESTAMP, proxy_details = ?, truly_processed = TRUE WHERE id = ?",
    (json.dumps(proxy_details), order_id)
)
```

### 5. تحديث معالج الإلغاء
- `handle_cancel_proxy_processing` لا يؤثر على حالة الطلب
- يظل الطلب في حالة 'processing' ويمكن معالجته لاحقاً

### 6. تحديث الاستعلام عن الطلبات
سيتم تحديث `handle_order_inquiry` لإظهار الحالات الجديدة:
- **pending**: "⏳ معلق"
- **processing**: "🔄 قيد المعالجة"
- **successful**: "✅ تم بنجاح"
- **failed**: "❌ فاشل"

## النتيجة
- زر الإلغاء لا يؤثر على حالة الطلب بعد قبول الدفع
- الطلبات تظهر بحالات واضحة ومفهومة
- يمكن معالجة الطلبات المتوقفة لاحقاً
- تتبع أفضل لحالة الطلبات في النظام