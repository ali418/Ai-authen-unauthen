from sqlalchemy import create_engine, Column, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# إنشاء اتصال بقاعدة البيانات
engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# إضافة عمود is_active إلى جدول users
try:
    engine.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1')
    print("تم إضافة عمود is_active بنجاح")
except Exception as e:
    print(f"حدث خطأ: {e}")
finally:
    session.close()