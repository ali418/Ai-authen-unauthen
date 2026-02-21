import os
import sys
import shutil

# إضافة المجلد الرئيسي إلى مسار البحث
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User
from werkzeug.security import generate_password_hash
from config import Config

# حذف قاعدة البيانات الحالية إذا كانت موجودة
db_path = os.path.join(project_root, 'face_recognition.db')
if os.path.exists(db_path):
    print(f"حذف قاعدة البيانات الموجودة: {db_path}")
    try:
        os.remove(db_path)
    except Exception as e:
        print(f"فشل في حذف قاعدة البيانات: {str(e)}")
        sys.exit(1)

# إنشاء قاعدة بيانات جديدة
print("إنشاء قاعدة بيانات جديدة...")
engine = create_engine(Config.DATABASE_URI)
Base.metadata.create_all(engine)

# إنشاء مستخدم مسؤول
Session = sessionmaker(bind=engine)
session = Session()

try:
    # إنشاء مستخدم مسؤول باستخدام تشفير Werkzeug
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )
    session.add(admin_user)
    session.commit()
    print("تم إنشاء مستخدم مسؤول بنجاح:")
    print("اسم المستخدم: admin")
    print("البريد الإلكتروني: admin@example.com")
    print("كلمة المرور: admin123")
except Exception as e:
    session.rollback()
    print(f"فشل في إنشاء مستخدم مسؤول: {str(e)}")

session.close()
print("تم إعادة بناء قاعدة البيانات بنجاح.")