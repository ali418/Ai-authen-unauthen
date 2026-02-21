import sqlite3
import os
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

# المسار إلى قاعدة البيانات
db_path = 'd:\\Ai  authen unauthen 0.1\\face_recognition.db'

# التحقق من وجود قاعدة البيانات
if not os.path.exists(db_path):
    print(f"قاعدة البيانات غير موجودة في المسار: {db_path}")
    exit(1)

# محاولة الاتصال بقاعدة البيانات باستخدام sqlite3
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # فحص الجداول الموجودة
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("الجداول الموجودة في قاعدة البيانات:")
    for table in tables:
        print(f"- {table[0]}")
        
    # فحص هيكل جدول المستخدمين
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print("\nهيكل جدول المستخدمين:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    conn.close()
except Exception as e:
    print(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")

# محاولة الاتصال بقاعدة البيانات باستخدام SQLAlchemy
try:
    engine = create_engine(f'sqlite:///{db_path}')
    inspector = inspect(engine)
    
    print("\nالجداول الموجودة (SQLAlchemy):")
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        
    print("\nأعمدة جدول المستخدمين (SQLAlchemy):")
    for column in inspector.get_columns('users'):
        print(f"- {column['name']} ({column['type']})")
        
    # إذا كان عمود username غير موجود، سنقوم بإضافته
    if 'username' not in [col['name'] for col in inspector.get_columns('users')]:
        print("\nعمود username غير موجود في جدول المستخدمين. سيتم إضافته...")
        
        # إنشاء الجدول الجديد مع العمود المفقود
        Base = declarative_base()
        
        class User(Base):
            __tablename__ = 'users_new'
            
            id = Column(Integer, primary_key=True)
            username = Column(String(50), unique=True, nullable=False)
            email = Column(String(100), unique=True, nullable=False)
            password_hash = Column(String(128), nullable=False)
            is_admin = Column(Boolean, default=False)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            last_login = Column(DateTime, nullable=True)
        
        # إنشاء الجدول الجديد
        Base.metadata.create_all(engine)
        
        # نقل البيانات من الجدول القديم إلى الجدول الجديد
        with engine.connect() as conn:
            # الحصول على البيانات من الجدول القديم
            result = conn.execute("SELECT id, email, password_hash, is_admin, created_at, last_login FROM users")
            users_data = result.fetchall()
            
            # إدخال البيانات في الجدول الجديد مع إضافة اسم مستخدم افتراضي
            for user in users_data:
                user_id, email, password_hash, is_admin, created_at, last_login = user
                # استخدام البريد الإلكتروني كاسم مستخدم افتراضي
                username = email.split('@')[0]
                
                conn.execute(
                    f"INSERT INTO users_new (id, username, email, password_hash, is_admin, created_at, last_login) "
                    f"VALUES ({user_id}, '{username}', '{email}', '{password_hash}', {is_admin}, '{created_at}', '{last_login or 'NULL'}');"
                )
            
            # حذف الجدول القديم وإعادة تسمية الجدول الجديد
            conn.execute("DROP TABLE users;")
            conn.execute("ALTER TABLE users_new RENAME TO users;")
            
        print("تم إصلاح جدول المستخدمين بنجاح!")
        
except Exception as e:
    print(f"خطأ في استخدام SQLAlchemy: {str(e)}")