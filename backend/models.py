from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import os
from flask_login import UserMixin  # إضافة استيراد UserMixin

# استيراد المسجلات والدوال المساعدة
from utils.logger import app_logger, security_logger
from utils.helpers import hash_password, create_directory_if_not_exists

# استيراد الإعدادات
from config import Config

# إنشاء قاعدة للنماذج
Base = declarative_base()

class User(Base, UserMixin):  # إضافة UserMixin هنا
    """نموذج المستخدم"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # إضافة عمود is_active
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # العلاقات
    face_images = relationship('FaceImage', back_populates='user', cascade='all, delete-orphan')
    access_logs = relationship('AccessLog', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', is_admin={self.is_admin})>"

class FaceImage(Base):
    """نموذج صورة الوجه"""
    __tablename__ = 'face_images'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    image_path = Column(String(255), nullable=False)
    embedding = Column(LargeBinary, nullable=True)  # تخزين متجه الوجه المضمن
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    user = relationship('User', back_populates='face_images')
    
    def __repr__(self):
        return f"<FaceImage(id={self.id}, user_id={self.user_id}, image_path='{self.image_path}')>"

class AccessLog(Base):
    """نموذج سجل الوصول"""
    __tablename__ = 'access_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # يمكن أن يكون فارغًا للمستخدمين غير المعروفين
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    access_granted = Column(Boolean, default=False)
    confidence = Column(Integer, nullable=True)  # نسبة الثقة في التعرف على الوجه
    image_path = Column(String(255), nullable=True)  # مسار الصورة المستخدمة في محاولة الوصول
    notes = Column(String(255), nullable=True)  # ملاحظات إضافية
    
    # العلاقات
    user = relationship('User', back_populates='access_logs')
    
    def __repr__(self):
        return f"<AccessLog(id={self.id}, user_id={self.user_id}, timestamp='{self.timestamp}', access_granted={self.access_granted})>"

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    try:
        # التأكد من وجود مجلد قاعدة البيانات
        db_dir = os.path.dirname(Config.DATABASE_URI.replace('sqlite:///', ''))
        create_directory_if_not_exists(db_dir)
        
        # إنشاء محرك قاعدة البيانات
        engine = create_engine(Config.DATABASE_URI)
        
        # إنشاء الجداول
        Base.metadata.create_all(engine)
        
        # إنشاء جلسة
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # التحقق من وجود مستخدم مسؤول
        admin_exists = session.query(User).filter(User.is_admin == True).first() is not None
        
        # إنشاء مستخدم مسؤول افتراضي إذا لم يكن موجودًا
        if not admin_exists:
            admin_password_hash = hash_password('admin')
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=admin_password_hash,
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            security_logger.info("تم إنشاء مستخدم مسؤول افتراضي")
        
        session.close()
        app_logger.info("تم تهيئة قاعدة البيانات بنجاح")
        
        return True
    except Exception as e:
        app_logger.error(f"فشل في تهيئة قاعدة البيانات: {str(e)}")
        return False