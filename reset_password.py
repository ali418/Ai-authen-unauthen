import os
import sys

# إضافة المجلد الرئيسي إلى مسار البحث
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import User
from werkzeug.security import generate_password_hash
from config import Config

# إنشاء اتصال بقاعدة البيانات
engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# البحث عن المستخدم المسؤول
admin_user = session.query(User).filter(User.email == 'admin@example.com').first()

if admin_user:
    # تعيين كلمة مرور جديدة
    new_password = 'admin123'  # قم بتغيير هذا إلى كلمة المرور التي تريدها
    admin_user.password_hash = generate_password_hash(new_password)
    session.commit()
    print(f"تم تغيير كلمة مرور المستخدم {admin_user.username} بنجاح.")
    print(f"البريد الإلكتروني: {admin_user.email}")
    print(f"كلمة المرور الجديدة: {new_password}")
else:
    print("لم يتم العثور على مستخدم مسؤول!")
    # محاولة إنشاء مستخدم مسؤول جديد
    try:
        from werkzeug.security import generate_password_hash
        new_admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        session.add(new_admin)
        session.commit()
        print("تم إنشاء مستخدم مسؤول جديد:")
        print("البريد الإلكتروني: admin@example.com")
        print("كلمة المرور: admin123")
    except Exception as e:
        print(f"فشل في إنشاء مستخدم مسؤول جديد: {str(e)}")