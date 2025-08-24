# إصلاحات البوت - الدوال المطلوبة

def validate_ip_address(ip: str) -> bool:
    """التحقق من صحة عنوان IP مع مرونة في عدد الأرقام"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            part = part.strip()
            if not part.isdigit():
                return False
            if len(part) < 1 or len(part) > 3:
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except:
        return False

def validate_port(port: str) -> bool:
    """التحقق من صحة رقم البورت (حد أقصى 6 أرقام)"""
    try:
        port = port.strip()
        if not port.isdigit():
            return False
        if len(port) > 6:
            return False
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False
        return True
    except:
        return False

async def handle_cancel_processing(update, context):
    """معالجة إلغاء معالجة الطلب مؤقتاً"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data.get('processing_order_id')
    if order_id:
        # الحصول على بيانات المستخدم
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة للمستخدم
            if user_language == 'ar':
                message = f"⏸️ تم توقيف معالجة طلبك مؤقتاً رقم `{order_id}`\n\nسيتم استئناف المعالجة لاحقاً من قبل الأدمن."
            else:
                message = f"⏸️ Processing of your order `{order_id}` has been temporarily stopped\n\nProcessing will resume later by admin."
            
            await context.bot.send_message(user_id, message, parse_mode='Markdown')
        
        await query.edit_message_text(f"⏸️ تم إلغاء معالجة الطلب مؤقتاً\n\nمعرف الطلب: `{order_id}`\n\nيمكن استئناف المعالجة لاحقاً", parse_mode='Markdown')
        
    return ConversationHandler.END

# Test functions
def run_tests():
    print("🧪 اختبار التحقق من IP:")
    test_ips = ["192.168.1.1", "1.1.1.1", "255.255.255.255", "256.1.1.1", "192.168.x.1"]
    for ip in test_ips:
        result = validate_ip_address(ip)
        print(f"{ip}: {'✅' if result else '❌'}")
    
    print("\n🧪 اختبار التحقق من البورت:")
    test_ports = ["80", "8080", "123456", "1234567", "abc"]
    for port in test_ports:
        result = validate_port(port)
        print(f"{port}: {'✅' if result else '❌'}")

if __name__ == "__main__":
    run_tests()
