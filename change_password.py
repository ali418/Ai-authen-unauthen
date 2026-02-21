from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# إضافة مسار المشروع الرئيسي إلى مسارات النظام
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# استيراد وظيفة تشفير كلمة المرور من ملف المساعدات
from utils.helpers import hash_password

# طباعة المسار الحالي للتشخيص
print(f"المسار الحالي: {os.getcwd()}")

# المسار إلى قاعدة البيانات
db_path = 'd:\\Ai  authen unauthen 0.1\\face_recognition.db'

# التحقق من وجود قاعدة البيانات
if not os.path.exists(db_path):
    print(f"قاعدة البيانات غير موجودة في المسار: {db_path}")
    exit(1)

# إنشاء اتصال بقاعدة البيانات
engine = create_engine(f'sqlite:///{db_path}')


try:
    # إنشاء جلسة قاعدة البيانات
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # الحصول على المستخدم المسؤول
    from sqlalchemy import Table, MetaData, select
    metadata = MetaData()
    users_table = Table('users', metadata, autoload_with=engine)
    
    # البحث عن المستخدم المسؤول
    query = select(users_table).where(users_table.c.username == 'admin')
    result = session.execute(query).fetchone()
    
    if not result:
        print("المستخدم المسؤول غير موجود في قاعدة البيانات")
        exit(1)
    
    # طلب كلمة المرور الجديدة من المستخدم
    new_password = input("أدخل كلمة المرور الجديدة للمستخدم المسؤول: ")
    
    # تحديث كلمة المرور
    update_query = users_table.update().where(users_table.c.username == 'admin').values(password_hash=hash_password(new_password))
    session.execute(update_query)
    
    # حفظ التغييرات
    session.commit()
    print("تم تحديث كلمة المرور بنجاح")
    
    session.close()
    
except Exception as e:
    print(f"حدث خطأ: {str(e)}")