from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import sys
import numpy as np
import pickle
import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.logger import app_logger, security_logger
from utils.helpers import hash_password, format_datetime
from config import Config
from backend.models import User, FaceImage, AccessLog, Base


class Database:
    """فئة لإدارة قاعدة البيانات"""

    def __init__(self):
        try:
            self.engine = create_engine(Config.DATABASE_URI)
            self.session_factory = sessionmaker(bind=self.engine)
            self.session = scoped_session(self.session_factory)
            app_logger.info("تم تهيئة اتصال قاعدة البيانات بنجاح")
        except Exception as e:
            app_logger.error(f"فشل في تهيئة اتصال قاعدة البيانات: {str(e)}")
            raise

    # ─── Users ────────────────────────────────────────────────

    def add_user(self, username, email, password, is_admin=False):
        try:
            existing = self.session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing:
                return None, "اسم المستخدم أو البريد الإلكتروني موجود بالفعل"

            from werkzeug.security import generate_password_hash
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=is_admin,
                is_active=True
            )
            self.session.add(new_user)
            self.session.commit()
            app_logger.info(f"تم إنشاء مستخدم جديد: {username}")
            return new_user, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في إضافة مستخدم: {str(e)}")
            return None, str(e)

    def get_user_by_id(self, user_id):
        try:
            return self.session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم {user_id}: {str(e)}")
            return None

    def get_user_by_username(self, username):
        try:
            return self.session.query(User).filter(User.username == username).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم {username}: {str(e)}")
            return None

    def get_user_by_email(self, email):
        try:
            return self.session.query(User).filter(User.email == email).first()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدم {email}: {str(e)}")
            return None

    def get_all_users(self):
        try:
            return self.session.query(User).all()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على المستخدمين: {str(e)}")
            return []

    def update_user(self, user_id, username=None, email=None, password=None,
                    is_admin=None, is_active=None):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "المستخدم غير موجود"

            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            if password is not None:
                from werkzeug.security import generate_password_hash
                user.password_hash = generate_password_hash(password)
            if is_admin is not None:
                user.is_admin = is_admin
            if is_active is not None:
                user.is_active = is_active

            self.session.commit()
            app_logger.info(f"تم تحديث المستخدم: {user_id}")
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في تحديث المستخدم {user_id}: {str(e)}")
            return False, str(e)

    def delete_user(self, user_id):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "المستخدم غير موجود"

            self.session.query(FaceImage).filter(FaceImage.user_id == user_id).delete()
            self.session.delete(user)
            self.session.commit()
            app_logger.info(f"تم حذف المستخدم: {user_id}")
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في حذف المستخدم {user_id}: {str(e)}")
            return False, str(e)

    # ─── Face Images ──────────────────────────────────────────

    def add_face_image(self, user_id, image_path, embedding, image_data=None):
        """
        إضافة صورة وجه - تُخزَّن الصورة (image_data) في قاعدة البيانات مباشرة
        بحيث تبقى ثابتة بعد كل Deploy على Railway.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "المستخدم غير موجود"

            embedding_binary = pickle.dumps(embedding)

            new_face_image = FaceImage(
                user_id=user_id,
                image_path=image_path,      # اختياري - قد يكون None على Cloud
                image_data=image_data,       # ثنائي مخزون في PostgreSQL
                embedding=embedding_binary,
                created_at=datetime.datetime.utcnow()
            )
            self.session.add(new_face_image)
            self.session.commit()
            app_logger.info(f"تم إضافة صورة وجه للمستخدم: {user_id}")
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في إضافة صورة وجه: {str(e)}")
            return False, str(e)

    def get_face_images(self, user_id=None):
        try:
            query = self.session.query(FaceImage)
            if user_id is not None:
                query = query.filter(FaceImage.user_id == user_id)
            return query.all()
        except Exception as e:
            app_logger.error(f"فشل في الحصول على صور الوجوه: {str(e)}")
            return []

    def get_face_embeddings(self):
        """الحصول على متجه وجه ممثل (متوسط) لكل مستخدم"""
        try:
            face_images = self.session.query(FaceImage).all()
            user_embeddings = {}
            for fi in face_images:
                if fi.embedding is None:
                    continue
                emb = pickle.loads(fi.embedding)
                user_embeddings.setdefault(fi.user_id, []).append(emb)

            result = {}
            for uid, embs in user_embeddings.items():
                try:
                    stacked = np.stack(embs, axis=0)
                    result[uid] = stacked.mean(axis=0)
                except Exception as e:
                    app_logger.error(f"فشل في تجميع متجهات المستخدم {uid}: {str(e)}")
            return result
        except Exception as e:
            app_logger.error(f"فشل في الحصول على متجهات الوجوه: {str(e)}")
            return {}

    def delete_face_image(self, face_image_id):
        try:
            fi = self.session.query(FaceImage).filter(FaceImage.id == face_image_id).first()
            if not fi:
                return False, "صورة الوجه غير موجودة"
            self.session.delete(fi)
            self.session.commit()
            app_logger.info(f"تم حذف صورة الوجه: {face_image_id}")
            return True, None
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في حذف صورة الوجه {face_image_id}: {str(e)}")
            return False, str(e)

    # ─── Access Logs ──────────────────────────────────────────

    def log_access_attempt(self, user_id, access_granted, confidence=None,
                           image_path=None, notes=None):
        try:
            log = AccessLog(
                user_id=user_id,
                timestamp=datetime.datetime.utcnow(),
                access_granted=access_granted,
                confidence=confidence,
                image_path=image_path,
                notes=notes
            )
            self.session.add(log)
            self.session.commit()
            app_logger.info(f"سجل وصول: user={user_id}, granted={access_granted}")
            return log
        except Exception as e:
            self.session.rollback()
            app_logger.error(f"فشل في تسجيل محاولة الوصول: {str(e)}")
            return None

    def get_access_logs(self, user_id=None, limit=50):
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
        try:
            start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
            total = self.session.query(func.count(AccessLog.id))\
                .filter(AccessLog.timestamp >= start_date).scalar() or 0
            successful = self.session.query(func.count(AccessLog.id))\
                .filter(AccessLog.timestamp >= start_date)\
                .filter(AccessLog.access_granted == True).scalar() or 0
            failed = total - successful
            rate = (successful / total * 100) if total > 0 else 0
            return {
                'total_attempts': total,
                'successful_attempts': successful,
                'failed_attempts': failed,
                'success_rate': rate,
                'user_stats': {}
            }
        except Exception as e:
            app_logger.error(f"فشل في الحصول على إحصائيات الوصول: {str(e)}")
            return {
                'total_attempts': 0, 'successful_attempts': 0,
                'failed_attempts': 0, 'success_rate': 0, 'user_stats': {}
            }
