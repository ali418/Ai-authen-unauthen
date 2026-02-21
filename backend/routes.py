from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_from_directory, Response
from flask_login import login_user, logout_user, login_required, current_user
import cv2
import time
import numpy as np
import os
import time
import pickle
import datetime
from werkzeug.utils import secure_filename

# استيراد المسجلات والدوال المساعدة
from utils.logger import app_logger, security_logger, access_logger
from utils.helpers import format_datetime, is_valid_image_file, create_directory_if_not_exists, generate_unique_id

# استيراد الإعدادات
from config import Config

# استيراد قاعدة البيانات والنماذج
from backend.database import Database
from backend.models import User, FaceImage, AccessLog

# استيراد وحدات التعرف على الوجوه
# تغيير طريقة الاستيراد لتجنب التعارض مع حزمة face_recognition
import sys
import os
# التأكد من إضافة المجلد الرئيسي إلى مسار البحث
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# استيراد الوحدات باستخدام المسار المطلق
from face_recognition.detector import FaceDetector
from face_recognition.aligner import FaceAligner
from face_recognition.embedder import FaceEmbedder
from face_recognition.matcher import FaceMatcher
from face_recognition.camera import Camera

# إنشاء كائنات التعرف على الوجوه
face_detector = FaceDetector()
face_aligner = FaceAligner()
face_embedder = FaceEmbedder()
face_matcher = FaceMatcher(threshold=Config.FACE_SIMILARITY_THRESHOLD)

# إنشاء كائن الكاميرا
camera = Camera()

# إنشاء كائن قاعدة البيانات
db = Database()

# إنشاء مخططات
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# تكوين مجلد التحميل
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
create_directory_if_not_exists(UPLOAD_FOLDER)

# مجلد صور الوجوه
FACE_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'faces')
create_directory_if_not_exists(FACE_IMAGES_FOLDER)

# مجلد صور محاولات الوصول
ACCESS_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'access_attempts')
create_directory_if_not_exists(ACCESS_IMAGES_FOLDER)

@main_bp.route('/')
def index():
    """الصفحة الرئيسية"""
    app_logger.info("تم الوصول إلى الصفحة الرئيسية")
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    app_logger.info(f"تم الوصول إلى لوحة التحكم بواسطة المستخدم: {current_user.username}")
    return render_template('dashboard.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_user_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            security_logger.info(f"تم تسجيل دخول المستخدم: {username}")
            return redirect(url_for('main.dashboard'))
        else:
            security_logger.warning(f"محاولة تسجيل دخول فاشلة لاسم المستخدم: {username}")
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    username = current_user.username
    logout_user()
    security_logger.info(f"تم تسجيل خروج المستخدم: {username}")
    return redirect(url_for('main.index'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user, error = db.add_user(username, email, password)
        
        if user:
            security_logger.info(f"تم تسجيل مستخدم جديد: {username}")
            flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('main.login'))
        else:
            security_logger.warning(f"فشل في تسجيل مستخدم جديد: {username}, السبب: {error}")
            flash(f'فشل في إنشاء الحساب: {error}', 'danger')
    
    return render_template('register.html')

@main_bp.route('/profile')
@login_required
def profile():
    """صفحة الملف الشخصي"""
    app_logger.info(f"تم الوصول إلى صفحة الملف الشخصي بواسطة المستخدم: {current_user.username}")
    face_images = db.get_face_images(current_user.id)
    return render_template('profile.html', user=current_user, face_images=face_images)

@main_bp.route('/add_face', methods=['GET', 'POST'])
@login_required
def add_face():
    """إضافة صورة وجه جديدة"""
    if request.method == 'POST':
        if 'face_image' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['face_image']
        
        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)
        
        if file and is_valid_image_file(file.filename):
            # إنشاء اسم ملف فريد
            filename = secure_filename(file.filename)
            unique_filename = f"{generate_unique_id()}_{filename}"
            file_path = os.path.join(FACE_IMAGES_FOLDER, unique_filename)
            
            # حفظ الملف
            file.save(file_path)
            
            try:
                # قراءة الصورة
                image = cv2.imread(file_path)
                if image is None:
                    os.remove(file_path)
                    flash('فشل في قراءة الصورة', 'danger')
                    return redirect(request.url)
                
                # اكتشاف الوجه
                faces = face_detector.detect_faces(image)
                if len(faces) == 0:
                    os.remove(file_path)
                    flash('لم يتم العثور على وجه في الصورة', 'danger')
                    return redirect(request.url)
                
                if len(faces) > 1:
                    os.remove(file_path)
                    flash('تم العثور على أكثر من وجه في الصورة، يرجى تقديم صورة بوجه واحد فقط', 'danger')
                    return redirect(request.url)
                
                # محاذاة الوجه
                face_aligned = face_aligner.align_face(image)
                
                # استخراج المتجه المضمن
                embedding = face_embedder.get_embedding(face_aligned)
                
                # حفظ في قاعدة البيانات
                success, error = db.add_face_image(current_user.id, file_path, embedding)
                
                if success:
                    app_logger.info(f"تم إضافة صورة وجه جديدة للمستخدم: {current_user.username}")
                    flash('تم إضافة صورة الوجه بنجاح', 'success')
                else:
                    os.remove(file_path)
                    flash(f'فشل في إضافة صورة الوجه: {error}', 'danger')
            except Exception as e:
                app_logger.error(f"خطأ أثناء معالجة صورة الوجه: {str(e)}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(f'حدث خطأ أثناء معالجة الصورة: {str(e)}', 'danger')
        else:
            flash('نوع الملف غير مدعوم، يرجى استخدام صور بتنسيق JPG أو PNG', 'danger')
        
        return redirect(url_for('main.profile'))
    
    return render_template('add_face.html')

@main_bp.route('/delete_face/<int:face_id>', methods=['POST'])
@login_required
def delete_face(face_id):
    """حذف صورة وجه"""
    # التحقق من أن صورة الوجه تنتمي للمستخدم الحالي
    face_image = db.session.query(FaceImage).filter(FaceImage.id == face_id, FaceImage.user_id == current_user.id).first()
    
    if not face_image:
        app_logger.warning(f"محاولة حذف صورة وجه غير موجودة أو غير مملوكة بواسطة المستخدم: {current_user.username}")
        flash('صورة الوجه غير موجودة أو غير مصرح لك بحذفها', 'danger')
        return redirect(url_for('main.profile'))
    
    # حذف الملف الفعلي
    if os.path.exists(face_image.image_path):
        try:
            os.remove(face_image.image_path)
        except Exception as e:
            app_logger.error(f"فشل في حذف ملف صورة الوجه: {str(e)}")
    
    # حذف من قاعدة البيانات
    success, error = db.delete_face_image(face_id)
    
    if success:
        app_logger.info(f"تم حذف صورة وجه للمستخدم: {current_user.username}")
        flash('تم حذف صورة الوجه بنجاح', 'success')
    else:
        app_logger.error(f"فشل في حذف صورة وجه من قاعدة البيانات: {error}")
        flash(f'فشل في حذف صورة الوجه: {error}', 'danger')
    
    return redirect(url_for('main.profile'))

@main_bp.route('/access_logs')
@login_required
def access_logs():
    """عرض سجلات الوصول"""
    # المسؤولون يمكنهم رؤية جميع السجلات، المستخدمون العاديون يرون سجلاتهم فقط
    if current_user.is_admin:
        logs = db.get_access_logs(limit=100)
        app_logger.info(f"تم عرض جميع سجلات الوصول بواسطة المسؤول: {current_user.username}")
    else:
        logs = db.get_access_logs(user_id=current_user.id, limit=100)
        app_logger.info(f"تم عرض سجلات الوصول الخاصة بالمستخدم: {current_user.username}")
    
    return render_template('access_logs.html', logs=logs, format_datetime=format_datetime)

@main_bp.route('/admin/users')
@login_required
def admin_users():
    """إدارة المستخدمين (للمسؤولين فقط)"""
    if not current_user.is_admin:
        security_logger.warning(f"محاولة وصول غير مصرح به إلى صفحة إدارة المستخدمين من قبل: {current_user.username}")
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.dashboard'))
    
    users = db.get_all_users()
    app_logger.info(f"تم عرض قائمة المستخدمين بواسطة المسؤول: {current_user.username}")
    
    return render_template('admin/users.html', users=users)

@main_bp.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """إضافة مستخدم جديد (للمسؤولين فقط)"""
    if not current_user.is_admin:
        security_logger.warning(f"محاولة وصول غير مصرح به إلى صفحة إضافة مستخدم من قبل: {current_user.username}")
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        user, error = db.add_user(username, email, password, is_admin)
        
        if user:
            security_logger.info(f"تم إضافة مستخدم جديد بواسطة المسؤول {current_user.username}: {username}, المسؤول: {is_admin}")
            flash('تم إضافة المستخدم بنجاح', 'success')
            return redirect(url_for('main.admin_users'))
        else:
            security_logger.warning(f"فشل في إضافة مستخدم جديد بواسطة المسؤول {current_user.username}: {error}")
            flash(f'فشل في إضافة المستخدم: {error}', 'danger')
    
    return render_template('admin/add_user.html')

@main_bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """تعديل مستخدم (للمسؤولين فقط)"""
    if not current_user.is_admin:
        security_logger.warning(f"محاولة وصول غير مصرح به إلى صفحة تعديل مستخدم من قبل: {current_user.username}")
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('main.admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        # إذا كان حقل كلمة المرور فارغًا، لا تقم بتحديثها
        if not password:
            password = None
        
        success, error = db.update_user(user_id, username, email, password, is_admin)
        
        if success:
            security_logger.info(f"تم تحديث معلومات المستخدم {username} بواسطة المسؤول: {current_user.username}")
            flash('تم تحديث معلومات المستخدم بنجاح', 'success')
            return redirect(url_for('main.admin_users'))
        else:
            security_logger.warning(f"فشل في تحديث معلومات المستخدم بواسطة المسؤول {current_user.username}: {error}")
            flash(f'فشل في تحديث معلومات المستخدم: {error}', 'danger')
    
    return render_template('admin/edit_user.html', user=user)

@main_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """حذف مستخدم (للمسؤولين فقط)"""
    if not current_user.is_admin:
        security_logger.warning(f"محاولة وصول غير مصرح به إلى وظيفة حذف مستخدم من قبل: {current_user.username}")
        flash('غير مصرح لك بالوصول إلى هذه الوظيفة', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # لا يمكن للمسؤول حذف نفسه
    if user_id == current_user.id:
        security_logger.warning(f"محاولة حذف ذاتي من قبل المسؤول: {current_user.username}")
        flash('لا يمكنك حذف حسابك الخاص', 'danger')
        return redirect(url_for('main.admin_users'))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('main.admin_users'))
    
    # حذف صور الوجوه الفعلية
    face_images = db.get_face_images(user_id)
    for face_image in face_images:
        if os.path.exists(face_image.image_path):
            try:
                os.remove(face_image.image_path)
            except Exception as e:
                app_logger.error(f"فشل في حذف ملف صورة الوجه: {str(e)}")
    
    # حذف المستخدم من قاعدة البيانات
    success, error = db.delete_user(user_id)
    
    if success:
        security_logger.info(f"تم حذف المستخدم {user.username} بواسطة المسؤول: {current_user.username}")
        flash('تم حذف المستخدم بنجاح', 'success')
    else:
        security_logger.warning(f"فشل في حذف المستخدم بواسطة المسؤول {current_user.username}: {error}")
        flash(f'فشل في حذف المستخدم: {error}', 'danger')
    
    return redirect(url_for('main.admin_users'))

@main_bp.route('/admin/stats')
@login_required
def admin_stats():
    """إحصائيات النظام (للمسؤولين فقط)"""
    if not current_user.is_admin:
        security_logger.warning(f"محاولة وصول غير مصرح به إلى صفحة الإحصائيات من قبل: {current_user.username}")
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # إحصائيات المستخدمين
    users_count = len(db.get_all_users())
    
    # إحصائيات صور الوجوه
    face_images = db.get_face_images()
    face_images_count = len(face_images)
    
    # إحصائيات الوصول
    access_stats = db.get_access_stats(days=30)
    
    app_logger.info(f"تم عرض إحصائيات النظام بواسطة المسؤول: {current_user.username}")
    
    return render_template(
        'admin/stats.html',
        users_count=users_count,
        face_images_count=face_images_count,
        access_stats=access_stats
    )

# واجهة برمجة التطبيقات (API) للتعرف على الوجوه

@api_bp.route('/recognize', methods=['POST'])
def recognize():
    """التعرف على الوجه من خلال الكاميرا"""
    try:
        # التقاط صورة من الكاميرا
        success, frame = camera.capture()
        if not success:
            app_logger.error("فشل في التقاط صورة من الكاميرا")
            return jsonify({'success': False, 'error': 'فشل في التقاط صورة من الكاميرا'})
        
        # اكتشاف الوجوه في الصورة
        faces = face_detector.detect_faces(frame)
        if len(faces) == 0:
            access_logger.warning("محاولة وصول: لم يتم اكتشاف أي وجه")
            return jsonify({'success': False, 'error': 'لم يتم اكتشاف أي وجه'})
        
        if len(faces) > 1:
            access_logger.warning("محاولة وصول: تم اكتشاف أكثر من وجه")
            return jsonify({'success': False, 'error': 'تم اكتشاف أكثر من وجه، يرجى التأكد من وجود شخص واحد فقط أمام الكاميرا'})
        
        # محاذاة الوجه
        face_aligned = face_aligner.align_face(frame, faces[0])
        
        # استخراج المتجه المضمن
        embedding = face_embedder.get_embedding(face_aligned)
        
        # الحصول على جميع متجهات الوجوه المضمنة من قاعدة البيانات
        embeddings_dict = db.get_face_embeddings()
        
        if not embeddings_dict:
            access_logger.warning("محاولة وصول: لا توجد وجوه مسجلة في النظام")
            return jsonify({'success': False, 'error': 'لا توجد وجوه مسجلة في النظام'})
        
        # مطابقة الوجه مع الوجوه المخزنة باستخدام الطريقة الهجينة
        user_id, confidence = face_matcher.match(embedding, embeddings_dict, method=Config.FACE_SIMILARITY_METHOD)
        
        # حفظ صورة محاولة الوصول
        timestamp = int(time.time())
        image_filename = f"access_{timestamp}.jpg"
        image_path = os.path.join(ACCESS_IMAGES_FOLDER, image_filename)
        cv2.imwrite(image_path, frame)
        
        if user_id is not None:
            # تم العثور على تطابق
            user = db.get_user_by_id(user_id)
            
            if user:
                # تسجيل محاولة الوصول الناجحة
                db.log_access_attempt(
                    user_id=user_id,
                    access_granted=True,
                    confidence=int(confidence * 100),
                    image_path=image_path,
                    notes=f"تم التعرف على المستخدم {user.username} بنسبة ثقة {int(confidence * 100)}%"
                )
                
                access_logger.info(f"تم منح الوصول للمستخدم: {user.username}, نسبة الثقة: {int(confidence * 100)}%")
                
                return jsonify({
                    'success': True,
                    'access_granted': True,
                    'user_id': user_id,
                    'username': user.username,
                    'confidence': int(confidence * 100),
                    'message': f"مرحبًا {user.username}! تم التعرف عليك بنجاح."
                })
            else:
                # المستخدم غير موجود (حالة نادرة)
                db.log_access_attempt(
                    user_id=None,
                    access_granted=False,
                    confidence=int(confidence * 100),
                    image_path=image_path,
                    notes=f"تم العثور على تطابق لمستخدم غير موجود (معرف: {user_id})"
                )
                
                access_logger.warning(f"تم العثور على تطابق لمستخدم غير موجود (معرف: {user_id})")
                
                return jsonify({
                    'success': True,
                    'access_granted': False,
                    'message': "لم يتم التعرف عليك. الوصول مرفوض."
                })
        else:
            # لم يتم العثور على تطابق
            db.log_access_attempt(
                user_id=None,
                access_granted=False,
                confidence=0,
                image_path=image_path,
                notes="لم يتم العثور على تطابق"
            )
            
            access_logger.warning("محاولة وصول: لم يتم العثور على تطابق")
            
            return jsonify({
                'success': True,
                'access_granted': False,
                'message': "لم يتم التعرف عليك. الوصول مرفوض."
            })
    
    except Exception as e:
        app_logger.error(f"خطأ أثناء عملية التعرف على الوجه: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/door/open', methods=['POST'])
def open_door():
    """محاكاة فتح الباب"""
    try:
        # رسالة بسيطة بدلاً من التحكم بالباب
        access_logger.info("تمت محاكاة فتح الباب")
        return jsonify({'success': True, 'message': 'تمت محاكاة فتح الباب بنجاح - الباب غير متصل حالياً'})
    except Exception as e:
        app_logger.error(f"فشل في محاكاة فتح الباب: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/door/status', methods=['GET'])
def door_status():
    """الحصول على حالة الباب"""
    try:
        # حالة وهمية للتوضيح - تم تبسيطها
        status = {
            'is_open': False,
            'message': 'نظام التحكم بالباب غير متصل حالياً'
        }
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        app_logger.error(f"فشل في الحصول على حالة الباب: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/live_view')
@login_required
def live_view():
    """عرض الكاميرا المباشر"""
    app_logger.info(f"تم الوصول إلى صفحة عرض الكاميرا المباشر بواسطة المستخدم: {current_user.username}")
    return render_template('live_view.html')

@main_bp.route('/video_feed')
@login_required
def video_feed():
    """توفير بث الفيديو المباشر من الكاميرا"""
    def generate_frames():
        last_frame_time = time.time()
        frame_interval = 1.0 / 3.0
        last_valid_frame = None
        embeddings_dict = db.get_face_embeddings()
        
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - last_frame_time
                
                # التحقق مما إذا كان الوقت قد حان لإطار جديد
                if elapsed >= frame_interval:
                    frame = camera.capture_frame()
                    if frame is not None:
                        last_valid_frame = frame.copy()
                        faces = face_detector.detect_faces(frame)
                        if embeddings_dict is None or len(embeddings_dict) == 0:
                            for (x, y, w, h) in faces:
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                                cv2.putText(frame, "NO ENROLLED FACES", (x, max(y - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        else:
                            for (x, y, w, h) in faces:
                                face_image = face_detector.extract_face(frame, (x, y, w, h))
                                embedding = face_embedder.get_embedding(face_image)
                                user_id, confidence = face_matcher.match(embedding, embeddings_dict, method=Config.FACE_SIMILARITY_METHOD)
                                if user_id is not None:
                                    user = db.get_user_by_id(user_id)
                                    label = user.username if user else "AUTHORIZED"
                                    color = (0, 255, 0)
                                else:
                                    label = "UNAUTHORIZED"
                                    color = (0, 0, 255)
                                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                                cv2.putText(frame, label, (x, max(y - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        frame = cv2.resize(frame, (640, 480))
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                        ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                        frame_bytes = buffer.tobytes()
                    elif last_valid_frame is not None:
                        frame = cv2.resize(last_valid_frame, (640, 480))
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                        ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                        frame_bytes = buffer.tobytes()
                    else:
                        img = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(img, "Camera not connected", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                        ret, buffer = cv2.imencode('.jpg', img)
                        frame_bytes = buffer.tobytes()
                    last_frame_time = current_time
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    time.sleep(0.01)
                
        except Exception as e:
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            error_message = str(e)
            y_pos = 100
            for i in range(0, len(error_message), 40):
                cv2.putText(img, error_message[i:i+40], (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                y_pos += 40
            
            ret, buffer = cv2.imencode('.jpg', img)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    # إرجاع استجابة متعددة الأجزاء
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')














     
        
        
