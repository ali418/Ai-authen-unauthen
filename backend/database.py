from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import sys
import numpy as np
import pickle
import datetime

# إضافة مسار المشروع الرئيسي إلى مسارات النظام
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# استيراد المسجلات والدوال المساعدة
from utils.logger import app_logger, security_logger
from utils.helpers import hash_password, format_datetime

# استيراد الإعدادات
from config import Config

# استيراد النماذج
from backend.models import User, FaceImage, AccessLog, Base

class Database:
    """فئة لإدارة قاعدة البيانات وعمليات المستخدمين وصور الوجوه وسجلات الوصول"""
    
    def __init__(self):
        """تهيئة اتصال قاعدة البيانات"""
        try:
            # إنشاء محرك قاعدة البيانات
            self.engine = create_engine(Config.DATABASE_URI)
            
            # إنشاء جلسة قاعدة البيانات
            self.session_factory = sessionmaker(bind=self.engine)
            self.session = scoped_session(self.session_factory)
            
            app_logger.info("تم تهيئة اتصال قاعدة البيانات بنجاح")
        except Exception as e:
            app_logger.error(f"فشل في تهيئة اتصال قاعدة البيانات: {str(e)}")
            raise
    
    def add_user(self, username, email, password, is_admin=False):
        """إضافة مستخدم جديد إلى قاعدة البيانات"""
        try:
            # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
            existing_user = self.session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                app_logger.warning(f"محاولة إنشاء مستخدم موجود بالفعل: {username} / {email}")
                return None, "اسم المستخدم أو البريد الإلكتروني موجود بالفعل"
            
            # تشفير كلمة المرور
            hashed_password = hash_password(password)
            
            # إنشاء مستخدم جديد
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                is_admin=is_admin
            )
            
            # إضافة المستخدم إلى قاعدة البيانات
            self.session.add(new_user)
            self.session.commit()
            
            app_logger.info(f"تم إنشاء مستخدم جديد: {username}")
            security_logger.info(f"تم إنشاء مستخدم جديد: {username}, المسؤول: {is_admin}")
            
            return new_user, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في إضافة مستخدم جديد: {str(e)}")
            return None, str(e)
    
    def get_user_by_id(self, user_id):
        """الحصول على مستخدم بواسطة المعرف"""
        try:
            return self.session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم بالمعرف {user_id}: {str(e)}")
            return None
    
    def get_user_by_username(self, username):
        """الحصول على مستخدم بواسطة اسم المستخدم"""
        try:
            return self.session.query(User).filter(User.username == username).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم باسم المستخدم {username}: {str(e)}")
            return None
    
    def get_user_by_email(self, email):
        """الحصول على مستخدم بواسطة البريد الإلكتروني"""
        try:
            return self.session.query(User).filter(User.email == email).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم بالبريد الإلكتروني {email}: {str(e)}")
            return None
    
    def get_all_users(self):
        """الحصول على جميع المستخدمين"""
        try:
            return self.session.query(User).all()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على جميع المستخدمين: {str(e)}")
            return []
    
    def update_user(self, user_id, username=None, email=None, password=None, is_admin=None, is_active=None):
        """تحديث معلومات المستخدم"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                app_logger.warning(f"محاولة تحديث مستخدم غير موجود بالمعرف: {user_id}")
                return False, "المستخدم غير موجود"
            
            # تحديث المعلومات المقدمة فقط
            if username is not None:
                user.username = username
            
            if email is not None:
                user.email = email
            
            if password is not None:
                user.password_hash = hash_password(password)
            
            if is_admin is not None:
                user.is_admin = is_admin
                
            if is_active is not None:
                user.is_active = is_active
            
            self.session.commit()
            
            app_logger.info(f"تم تحديث معلومات المستخدم بالمعرف: {user_id}")
            security_logger.info(f"تم تحديث معلومات المستخدم: {user.username}")
            
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في تحديث معلومات المستخدم بالمعرف {user_id}: {str(e)}")
            return False, str(e)
    
    def delete_user(self, user_id):
        """حذف مستخدم"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                app_logger.warning(f"محاولة حذف مستخدم غير موجود بالمعرف: {user_id}")
                return False, "المستخدم غير موجود"
            
            # حذف صور الوجوه المرتبطة بالمستخدم
            self.session.query(FaceImage).filter(FaceImage.user_id == user_id).delete()
            
            # حذف المستخدم
            self.session.delete(user)
            self.session.commit()
            
            app_logger.info(f"تم حذف المستخدم بالمعرف: {user_id}")
            security_logger.info(f"تم حذف المستخدم: {user.username}")
            
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في حذف المستخدم بالمعرف {user_id}: {str(e)}")
            return False, str(e)
    
    def add_face_image(self, user_id, image_path, embedding):
        """إضافة صورة وجه جديدة لمستخدم"""
        try:
            # التحقق من وجود المستخدم
            user = self.get_user_by_id(user_id)
            if not user:
                app_logger.warning(f"محاولة إضافة صورة وجه لمستخدم غير موجود بالمعرف: {user_id}")
                return False, "المستخدم غير موجود"
            
            # تحويل المتجه المضمن إلى بيانات ثنائية
            embedding_binary = pickle.dumps(embedding)
            
            # إنشاء صورة وجه جديدة
            new_face_image = FaceImage(
                user_id=user_id,
                image_path=image_path,
                embedding=embedding_binary,
                created_at=datetime.datetime.utcnow()
            )
            
            # إضافة صورة الوجه إلى قاعدة البيانات
            self.session.add(new_face_image)
            self.session.commit()
            
            app_logger.info(f"تم إضافة صورة وجه جديدة للمستخدم بالمعرف: {user_id}")
            
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في إضافة صورة وجه للمستخدم بالمعرف {user_id}: {str(e)}")
            return False, str(e)
    
    def get_face_images(self, user_id=None):
        """الحصول على صور الوجوه لمستخدم معين أو جميع المستخدمين"""
        try:
            query = self.session.query(FaceImage)
            
            if user_id is not None:
                query = query.filter(FaceImage.user_id == user_id)
            
            return query.all()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على صور الوجوه: {str(e)}")
            return []
    
    def get_face_embeddings(self):
        """الحصول على متجه وجه ممثل لكل مستخدم"""
        try:
            face_images = self.session.query(FaceImage).all()
            user_embeddings = {}
            for face_image in face_images:
                if face_image.embedding is None:
                    continue
                embedding = pickle.loads(face_image.embedding)
                if face_image.user_id not in user_embeddings:
                    user_embeddings[face_image.user_id] = []
                user_embeddings[face_image.user_id].append(embedding)
            embeddings_dict = {}
            for user_id, embeddings in user_embeddings.items():
                try:
                    stacked = np.stack(embeddings, axis=0)
                    avg_embedding = stacked.mean(axis=0)
                    embeddings_dict[user_id] = avg_embedding
                except Exception as e:
                    app_logger.error(f"فشل في تجميع متجهات المستخدم {user_id}: {str(e)}")
            return embeddings_dict
        except Exception as e:
            app_logger.error(f"فشل في الحصول على متجهات الوجوه المضمنة: {str(e)}")
            return {}
    
    def delete_face_image(self, face_image_id):
        """حذف صورة وجه"""
        try:
            face_image = self.session.query(FaceImage).filter(FaceImage.id == face_image_id).first()
            if not face_image:
                app_logger.warning(f"محاولة حذف صورة وجه غير موجودة بالمعرف: {face_image_id}")
                return False, "صورة الوجه غير موجودة"
            
            # حذف صورة الوجوه
            self.session.delete(face_image)
            self.session.commit()
            
            app_logger.info(f"تم حذف صورة الوجه بالمعرف: {face_image_id} للمستخدم بالمعرف: {face_image.user_id}")
            
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في حذف صورة الوجه بالمعرف {face_image_id}: {str(e)}")
            return False, str(e)
    
    def log_access_attempt(self, user_id, access_granted, confidence=None, image_path=None, notes=None):
        """تسجيل محاولة وصول"""
        try:
            # إنشاء سجل وصول جديد
            access_log = AccessLog(
                user_id=user_id,
                timestamp=datetime.datetime.utcnow(),
                access_granted=access_granted,
                confidence=confidence,
                image_path=image_path,
                notes=notes
            )
            
            # إضافة سجل الوصول إلى قاعدة البيانات
            self.session.add(access_log)
            self.session.commit()
            
            app_logger.info(f"تم تسجيل محاولة وصول للمستخدم بالمعرف: {user_id}, الوصول مسموح: {access_granted}")
            
            return access_log
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في تسجيل محاولة وصول: {str(e)}")
            return None
    
    def get_access_logs(self, user_id=None, limit=50):
        """الحصول على سجلات الوصول"""
        try:
            query = self.session.query(AccessLog).order_by(AccessLog.timestamp.desc())
            
            if user_id is not None:
                query = query.filter(AccessLog.user_id == user_id)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على سجلات الوصول: {str(e)}")
            return []
    
    def get_access_stats(self, days=30):
        """الحصول على إحصائيات الوصول"""
        try:
            # حساب تاريخ البداية (قبل عدد الأيام المحدد)
            start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
            
            # إجمالي محاولات الوصول
            total_attempts = self.session.query(func.count(AccessLog.id)).\
                filter(AccessLog.timestamp >= start_date).scalar()
            
            # محاولات الوصول الناجحة
            successful_attempts = self.session.query(func.count(AccessLog.id)).\
                filter(AccessLog.timestamp >= start_date).\
                filter(AccessLog.access_granted == True).scalar()
            
            # محاولات الوصول الفاشلة
            failed_attempts = total_attempts - successful_attempts
            
            # معدل النجاح
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # إحصائيات حسب المستخدم
            user_stats = self.session.query(
                AccessLog.user_id,
                func.count(AccessLog.id).label('total'),
                func.sum(func.cast(AccessLog.access_granted, type_=Integer)).label('successful')
            ).filter(AccessLog.timestamp >= start_date).\
            group_by(AccessLog.user_id).all()
            
            user_stats_dict = {}
            for user_id, total, successful in user_stats:
                user = self.get_user_by_id(user_id) if user_id else None
                username = user.username if user else "غير معروف"
                
                user_stats_dict[user_id] = {
                    'username': username,
                    'total_attempts': total,
                    'successful_attempts': successful,
                    'failed_attempts': total - successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
            
            return {
                'total_attempts': total_attempts,
                'successful_attempts': successful_attempts,
                'failed_attempts': failed_attempts,
                'success_rate': success_rate,
                'user_stats': user_stats_dict
            }
        except Exception as e:
            app_logger.error(f"فشل في الحصول على إحصائيات الوصول: {str(e)}")
            return {
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0,
                'success_rate': 0,
                'user_stats': {}
            }
