# وحدة تسجيل الأحداث

import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    """فئة لإدارة تسجيل الأحداث في التطبيق"""
    
    # مستويات التسجيل
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, name, log_file=None, level=logging.INFO, max_size=10*1024*1024, backup_count=5):
        """تهيئة مسجل الأحداث
        
        المعلمات:
            name (str): اسم المسجل
            log_file (str): مسار ملف السجل (اختياري)
            level (int): مستوى التسجيل الافتراضي
            max_size (int): الحجم الأقصى لملف السجل بالبايت
            backup_count (int): عدد ملفات النسخ الاحتياطية للسجل
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # تنسيق السجل
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # إضافة معالج لعرض السجلات في وحدة التحكم
        import sys
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setStream(sys.stdout)
        self.logger.addHandler(console_handler)
        
        # إضافة معالج لكتابة السجلات في ملف إذا تم تحديد ملف السجل
        if log_file:
            # التأكد من وجود مجلد السجلات
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # إنشاء معالج ملف دوار
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """تسجيل رسالة بمستوى تصحيح"""
        self.logger.debug(message)
    
    def info(self, message):
        """تسجيل رسالة بمستوى معلومات"""
        self.logger.info(message)
    
    def warning(self, message):
        """تسجيل رسالة بمستوى تحذير"""
        self.logger.warning(message)
    
    def error(self, message):
        """تسجيل رسالة بمستوى خطأ"""
        self.logger.error(message)
    
    def critical(self, message):
        """تسجيل رسالة بمستوى حرج"""
        self.logger.critical(message)
    
    def exception(self, message):
        """تسجيل استثناء مع تتبع الاستدعاء"""
        self.logger.exception(message)

# إنشاء مسجل افتراضي للتطبيق
app_logger = Logger(
    name="face_recognition_app",
    log_file="logs/app.log",
    level=logging.INFO
)

# إنشاء مسجل للأمان
security_logger = Logger(
    name="security",
    log_file="logs/security.log",
    level=logging.WARNING
)

# إنشاء مسجل للوصول
access_logger = Logger(
    name="access",
    log_file="logs/access.log",
    level=logging.INFO
)

# تصدير المسجلات للاستخدام المباشر
__all__ = ['Logger', 'app_logger', 'security_logger', 'access_logger']