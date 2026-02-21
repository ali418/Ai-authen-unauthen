from flask import Flask
import sys
import os

# Add the parent directory to sys.path to find the config module and other modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the config and other modules
from config import Config
from flask_login import LoginManager

# استيراد المسجلات من وحدة الأدوات المساعدة
from utils.logger import app_logger, security_logger

# إنشاء تطبيق Flask
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# تحميل الإعدادات من ملف التكوين
app.config.from_object(Config)

# إعداد مدير تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# استيراد وتسجيل المسارات
# Change relative imports to absolute imports
import backend.routes
from backend.routes import main_bp, api_bp
from backend.auth import auth_bp
from admin_dashboard import admin_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)  # تسجيل Blueprint لوحة تحكم المسؤول

# استيراد وظيفة تحميل المستخدم
from backend.auth import load_user
login_manager.user_loader(load_user)

# تهيئة قاعدة البيانات
from backend.models import init_db
init_db()

# تسجيل بدء التطبيق
app_logger.info("تم بدء تطبيق التعرف على الوجوه")

def create_app():
    """إنشاء وتهيئة تطبيق Flask"""
    app_logger.info("تم إنشاء تطبيق Flask")
    return app

# Add this for running the app directly