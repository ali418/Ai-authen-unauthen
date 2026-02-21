# وحدة الأدوات المساعدة (Utils)

توفر هذه الوحدة مجموعة من الأدوات المساعدة التي يمكن استخدامها في مختلف أجزاء التطبيق، وتشمل:

## تسجيل الأحداث (Logger)

توفر وحدة `logger.py` فئة `Logger` لتسجيل الأحداث في التطبيق، مع دعم لتسجيل الأحداث في ملفات وفي وحدة التحكم.

### المسجلات المتاحة

- `app_logger`: مسجل عام للتطبيق
- `security_logger`: مسجل للأحداث المتعلقة بالأمان
- `access_logger`: مسجل لأحداث الوصول

### مثال الاستخدام

```python
from utils.logger import app_logger, security_logger, access_logger

# تسجيل معلومات عامة
app_logger.info("تم بدء التطبيق")

# تسجيل تحذير أمني
security_logger.warning("محاولة وصول غير مصرح بها")

# تسجيل حدث وصول
access_logger.info(f"تم منح الوصول للمستخدم {user_id}")

# تسجيل خطأ
app_logger.error("حدث خطأ أثناء معالجة الطلب")
```

### إنشاء مسجل مخصص

```python
from utils.logger import Logger

# إنشاء مسجل مخصص
my_logger = Logger(
    name="custom_module",
    log_file="logs/custom.log",
    level=Logger.DEBUG
)

my_logger.debug("رسالة تصحيح")
my_logger.info("معلومات")
my_logger.warning("تحذير")
my_logger.error("خطأ")
my_logger.critical("خطأ حرج")
```

## الدوال المساعدة (Helpers)

توفر وحدة `helpers.py` مجموعة من الدوال المساعدة للاستخدام العام في التطبيق.

### دوال التاريخ والوقت

```python
from utils.helpers import format_datetime, get_current_timestamp

# تنسيق التاريخ والوقت الحالي
current_time = format_datetime()
print(current_time)  # مثال: 2023-01-01 12:34:56

# تنسيق مخصص
custom_format = format_datetime(format_str="%d/%m/%Y")
print(custom_format)  # مثال: 01/01/2023

# الحصول على الطابع الزمني الحالي
timestamp = get_current_timestamp()
print(timestamp)  # مثال: 1672567890
```

### دوال التحقق والتنظيف

```python
from utils.helpers import validate_email, sanitize_input, is_valid_image_file

# التحقق من صحة البريد الإلكتروني
is_valid = validate_email("user@example.com")
print(is_valid)  # True

# تنظيف المدخلات
clean_input = sanitize_input("<script>alert('XSS');</script>")
print(clean_input)  # alert('XSS');

# التحقق من صحة ملف الصورة
is_image = is_valid_image_file("image.jpg")
print(is_image)  # True
```

### دوال الملفات والمجلدات

```python
from utils.helpers import get_file_extension, create_directory_if_not_exists, format_file_size

# الحصول على امتداد الملف
extension = get_file_extension("document.pdf")
print(extension)  # pdf

# إنشاء مجلد إذا لم يكن موجودًا
success = create_directory_if_not_exists("uploads/images")
print(success)  # True

# تنسيق حجم الملف
size = format_file_size(1024 * 1024)
print(size)  # 1.00 MB
```

### دوال أخرى

```python
from utils.helpers import generate_unique_id, hash_password, truncate_text

# إنشاء معرف فريد
unique_id = generate_unique_id()
print(unique_id)  # مثال: 550e8400-e29b-41d4-a716-446655440000

# تشفير كلمة المرور
hashed = hash_password("password123")
print(hashed)  # تشفير SHA-256 لكلمة المرور

# اقتطاع النص
short_text = truncate_text("هذا نص طويل جدًا سيتم اقتطاعه", max_length=10)
print(short_text)  # هذا نص ط...
```

## الاستيراد المباشر

يمكن استيراد جميع الدوال والفئات المتاحة مباشرة من حزمة `utils`:

```python
from utils import (
    # من logger.py
    Logger, app_logger, security_logger, access_logger,
    
    # من helpers.py
    format_datetime, generate_unique_id, validate_email,
    sanitize_input, get_file_extension, create_directory_if_not_exists,
    hash_password, is_valid_image_file, truncate_text,
    format_file_size, get_current_timestamp
)
```