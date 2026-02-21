import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# إعدادات المشروع
class Config:
    # إعدادات عامة
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    
    # إعدادات قاعدة البيانات
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///face_recognition.db')
    
    # إعدادات التعرف على الوجه
    FACE_RECOGNITION_MODEL = os.getenv('FACE_RECOGNITION_MODEL', 'simple')
    FACE_DETECTION_MODEL = os.getenv('FACE_DETECTION_MODEL', 'opencv')
    FACE_SIMILARITY_THRESHOLD = float(os.getenv('FACE_SIMILARITY_THRESHOLD', '0.65'))
    FACE_SIMILARITY_METHOD = os.getenv('FACE_SIMILARITY_METHOD', 'hybrid')
    
    # إعدادات الكاميرا
    CAMERA_SOURCE = int(os.getenv('CAMERA_SOURCE', 0))  # 0 للكاميرا الافتراضية
    CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', 640))  # عرض الكاميرا
    CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', 480))  # ارتفاع الكاميرا
    
    # إعدادات التنبيهات
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False') == 'True'
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    
    ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv('ENABLE_TELEGRAM_NOTIFICATIONS', 'False') == 'True'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # إعدادات التحكم في الباب
    DOOR_RELAY_PIN = int(os.getenv('DOOR_RELAY_PIN', '17'))  # رقم الـ GPIO pin للمرحل
    DOOR_OPEN_DURATION = float(os.getenv('DOOR_OPEN_DURATION', '5.0'))  # مدة فتح الباب بالثواني