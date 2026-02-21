from flask import Blueprint

# إنشاء Blueprint للوحة تحكم المسؤول
admin_bp = Blueprint('admin', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/admin')

# استيراد المسارات
from . import views