#!/usr/bin/env python3
"""
اختبار دوال التحقق للبوت
"""

def validate_ip_address(ip: str) -> bool:
    """التحقق من صحة عنوان IP مع مرونة في عدد الأرقام"""
    try:
        # إزالة المسافات الزائدة
        ip = ip.strip()
        
        # تقسيم العنوان إلى أجزاء
        parts = ip.split('.')
        
        # يجب أن يكون هناك 4 أجزاء بالضبط
        if len(parts) != 4:
            return False
        
        # التحقق من كل جزء
        for part in parts:
            # إزالة المسافات من الجزء
            part = part.strip()
            
            # يجب أن يكون رقماً (لا يقبل النصوص)
            if not part.isdigit():
                return False
            
            # يجب أن يكون بين 1-3 أرقام (حد أدنى 1 رقم، حد أقصى 3 أرقام)
            if len(part) < 1 or len(part) > 3:
                return False
            
            # يقبل أي قيمة رقمية (مثل 62.1.2.1)
        
        return True
    except:
        return False

def validate_port(port: str) -> bool:
    """التحقق من صحة رقم البورت (حد أقصى 6 أرقام)"""
    try:
        # تجاهل المسافات
        port = port.strip()
        
        # يجب أن يكون رقم
        if not port.isdigit():
            return False
        
        # يجب أن يكون حد أقصى 6 أرقام
        if len(port) > 6:
            return False
        
        # يجب أن يكون بين 1-65535
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False
        
        return True
    except:
        return False

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 اختبار دوال التحقق للبوت")
    print("=" * 50)
    
    # اختبارات عناوين IP
    print("\n📍 اختبار التحقق من عناوين IP:")
    test_ips = [
        ("192.168.1.1", True, "عنوان IP عادي"),
        ("62.1.2.1", True, "العنوان المطلوب في المثال"),
        ("255.255.255.255", True, "أقصى قيمة"),
        ("1.1.1.1", True, "أرقام مفردة"),
        ("10.0.0.1", True, "مع أصفار"),
        ("300.1.1.1", True, "قيمة أكبر من 255 (مقبولة)"),
        ("256.1.1.1", False, "4 أرقام (مرفوض)"),
        ("192.168.1", False, "ناقص جزء"),
        ("192.168.1.1.1", False, "جزء زائد"),
        ("192.168.x.1", False, "يحتوي على حرف"),
        ("192.168..1", False, "جزء فارغ"),
        (" 192.168.1.1 ", True, "مع مسافات (ستُزال)"),
    ]
    
    for ip, expected, description in test_ips:
        result = validate_ip_address(ip)
        status = "✅" if result == expected else "❌"
        print(f"{status} {ip:<15} | {description}")
    
    # اختبارات البورت
    print("\n🔌 اختبار التحقق من البورت:")
    test_ports = [
        ("80", True, "بورت HTTP"),
        ("443", True, "بورت HTTPS"),
        ("8080", True, "بورت Proxy"),
        ("65535", True, "أقصى بورت"),
        ("1", True, "أقل بورت"),
        ("123456", True, "6 أرقام (الحد الأقصى)"),
        ("1234567", False, "7 أرقام (مرفوض)"),
        ("0", False, "صفر (مرفوض)"),
        ("65536", False, "أكبر من المسموح"),
        ("abc", False, "نص (مرفوض)"),
        ("80a", False, "رقم مع حرف"),
        (" 8080 ", True, "مع مسافات (ستُزال)"),
    ]
    
    for port, expected, description in test_ports:
        result = validate_port(port)
        status = "✅" if result == expected else "❌"
        print(f"{status} {port:<10} | {description}")
    
    print("\n" + "=" * 50)
    print("✅ انتهاء الاختبارات")

if __name__ == "__main__":
    run_tests()