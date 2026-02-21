from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os
import sys

# طباعة المسار الحالي للتشخيص
print(f"المسار الحالي: {os.getcwd()}")
print(f"مسار النظام: {sys.path}")

# المسار إلى قاعدة البيانات
db_path = 'd:\\Ai  authen unauthen 0.1\\face_recognition.db'

# التحقق من وجود قاعدة البيانات
if not os.path.exists(db_path):
    print(f"قاعدة البيانات غير موجودة في المسار: {db_path}")
    exit(1)

# إنشاء اتصال بقاعدة البيانات
engine = create_engine(f'sqlite:///{db_path}')
Base = declarative_base()

# تعريف نموذج المستخدم
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# إعادة إنشاء جدول المستخدمين
try:
    # حذف الجدول القديم إذا كان موجودًا
    metadata = MetaData()
    metadata.reflect(bind=engine)
    if 'users' in metadata.tables:
        users_table = metadata.tables['users']
        users_table.drop(engine)
        print("تم حذف جدول المستخدمين القديم")
    
    # إنشاء الجدول الجديد
    Base.metadata.create_all(engine)
    print("تم إنشاء جدول المستخدمين الجديد بنجاح")
    
    # إنشاء مستخدم مسؤول افتراضي
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # تشفير كلمة المرور يدويًا (بسيط للتوضيح)
    import hashlib
    def simple_hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # إنشاء مستخدم مسؤول افتراضي
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password_hash=simple_hash_password('admin'),
        is_admin=True
    )
    
    session.add(admin_user)
    session.commit()
    print("تم إنشاء مستخدم مسؤول افتراضي")
    
    session.close()
    
except Exception as e:
    print(f"حدث خطأ: {str(e)}")