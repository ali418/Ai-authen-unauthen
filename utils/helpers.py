# دوال مساعدة للتطبيق

import os
import re
import uuid
import hashlib
import datetime
from typing import Optional, Union, List, Dict, Any


def format_datetime(dt: Optional[datetime.datetime] = None, 
                   format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """تنسيق كائن التاريخ والوقت إلى سلسلة نصية
    
    المعلمات:
        dt: كائن التاريخ والوقت (إذا كان None، يتم استخدام الوقت الحالي)
        format_str: تنسيق السلسلة النصية
        
    العائد:
        سلسلة نصية منسقة للتاريخ والوقت
    """
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime(format_str)


def generate_unique_id() -> str:
    """إنشاء معرف فريد
    
    العائد:
        سلسلة نصية تمثل معرف فريد
    """
    return str(uuid.uuid4())


def validate_email(email: str) -> bool:
    """التحقق من صحة عنوان البريد الإلكتروني
    
    المعلمات:
        email: عنوان البريد الإلكتروني للتحقق منه
        
    العائد:
        True إذا كان عنوان البريد الإلكتروني صالحًا، وإلا False
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def sanitize_input(input_str: str) -> str:
    """تنظيف المدخلات من الأحرف غير المرغوب فيها
    
    المعلمات:
        input_str: السلسلة النصية المدخلة
        
    العائد:
        السلسلة النصية بعد التنظيف
    """
    # إزالة أي أحرف HTML خاصة
    sanitized = re.sub(r'<[^>]*>', '', input_str)
    # إزالة أي أحرف تحكم
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
    return sanitized.strip()


def get_file_extension(filename: str) -> str:
    """الحصول على امتداد الملف
    
    المعلمات:
        filename: اسم الملف
        
    العائد:
        امتداد الملف (بدون النقطة)
    """
    return os.path.splitext(filename)[1][1:].lower()


def create_directory_if_not_exists(directory_path: str) -> bool:
    """إنشاء مجلد إذا لم يكن موجودًا
    
    المعلمات:
        directory_path: مسار المجلد
        
    العائد:
        True إذا تم إنشاء المجلد أو كان موجودًا بالفعل، وإلا False
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except Exception:
        return False


def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام SHA-256
    
    المعلمات:
        password: كلمة المرور المراد تشفيرها
        
    العائد:
        كلمة المرور المشفرة
    """
    return hashlib.sha256(password.encode()).hexdigest()


def is_valid_image_file(filename: str) -> bool:
    """التحقق مما إذا كان الملف صورة صالحة
    
    المعلمات:
        filename: اسم الملف
        
    العائد:
        True إذا كان الملف صورة صالحة، وإلا False
    """
    valid_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    return get_file_extension(filename) in valid_extensions


def truncate_text(text: str, max_length: int = 100) -> str:
    """اقتطاع النص إلى طول محدد
    
    المعلمات:
        text: النص المراد اقتطاعه
        max_length: الطول الأقصى
        
    العائد:
        النص المقتطع
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def format_file_size(size_bytes: int) -> str:
    """تنسيق حجم الملف إلى صيغة مقروءة
    
    المعلمات:
        size_bytes: حجم الملف بالبايت
        
    العائد:
        حجم الملف بصيغة مقروءة
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"


def get_current_timestamp() -> int:
    """الحصول على الطابع الزمني الحالي
    
    العائد:
        الطابع الزمني الحالي بالثواني
    """
    return int(datetime.datetime.now().timestamp())


def parse_boolean(value: Union[str, bool, int]) -> bool:
    """تحليل قيمة إلى قيمة منطقية
    
    المعلمات:
        value: القيمة المراد تحليلها
        
    العائد:
        القيمة المنطقية
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.lower() in ('yes', 'true', 't', 'y', '1')
    return False


def safe_list_get(lst: List[Any], idx: int, default: Any = None) -> Any:
    """الحصول على عنصر من قائمة بأمان
    
    المعلمات:
        lst: القائمة
        idx: الفهرس
        default: القيمة الافتراضية إذا كان الفهرس خارج النطاق
        
    العائد:
        العنصر في الفهرس أو القيمة الافتراضية
    """
    try:
        return lst[idx]
    except (IndexError, TypeError):
        return default


def safe_dict_get(dct: Dict[Any, Any], key: Any, default: Any = None) -> Any:
    """الحصول على قيمة من قاموس بأمان
    
    المعلمات:
        dct: القاموس
        key: المفتاح
        default: القيمة الافتراضية إذا لم يكن المفتاح موجودًا
        
    العائد:
        القيمة المرتبطة بالمفتاح أو القيمة الافتراضية
    """
    try:
        return dct.get(key, default)
    except (AttributeError, TypeError):
        return default