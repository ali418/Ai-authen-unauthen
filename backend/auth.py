from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2

# Change relative imports to absolute imports
from backend.database import Database
from backend.models import User, FaceImage
from backend.routes import UPLOAD_FOLDER, face_detector, face_aligner, face_embedder, camera

# إنشاء Blueprint
auth_bp = Blueprint('auth', __name__)

# إنشاء مثيل من قاعدة البيانات
db = Database()

# وظيفة تحميل المستخدم لـ Flask-Login
def load_user(user_id):
    return db.get_user_by_id(int(user_id))

# صفحة تسجيل الدخول
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.get_user_by_email(email)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        flash('البريد الإلكتروني أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

# تسجيل الخروج
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# إضافة مستخدم جديد
@auth_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية إضافة مستخدمين')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role', 'user')
        password = request.form.get('password')
        
        # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل')
            return render_template('add_user.html')
        
        # إنشاء المستخدم
        user, error = db.add_user(username=name, email=email, password=password, is_admin=(role == 'admin'))
        if error:
            flash(f'فشل في إنشاء المستخدم: {error}')
            return render_template('add_user.html')
        
        flash(f'تم إضافة المستخدم {name} بنجاح')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_user.html')

# تعديل مستخدم
@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية تعديل المستخدمين')
        return redirect(url_for('main.index'))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        is_active = 'is_active' in request.form
        
        # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
        existing_user = db.get_user_by_email(email)
        if existing_user and existing_user.id != user_id:
            flash('البريد الإلكتروني مستخدم بالفعل')
            return render_template('edit_user.html', user=user)
        
        # تحديث بيانات المستخدم
        success, error = db.update_user(user_id, username=name, email=email, is_admin=(role == 'admin'))
        if not success:
            flash(f'فشل في تحديث بيانات المستخدم: {error}')
            return render_template('edit_user.html', user=user)
        
        # تحديث كلمة المرور إذا تم توفيرها
        password = request.form.get('password')
        if password and password.strip():
            success, error = db.update_user(user_id, password=password)
            if not success:
                flash(f'فشل في تحديث كلمة المرور: {error}')
                return render_template('edit_user.html', user=user)
        
        flash(f'تم تحديث بيانات المستخدم {name} بنجاح')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_user.html', user=user)

# حذف مستخدم
@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية حذف المستخدمين')
        return redirect(url_for('main.index'))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود')
        return redirect(url_for('main.dashboard'))
    
    # حذف المستخدم
    success, error = db.delete_user(user_id)
    if not success:
        flash(f'فشل في حذف المستخدم: {error}')
        return redirect(url_for('main.dashboard'))
    
    flash(f'تم حذف المستخدم {user.username} بنجاح')
    return redirect(url_for('main.dashboard'))

# إضافة صورة وجه لمستخدم
@auth_bp.route('/users/<int:user_id>/add_face', methods=['GET', 'POST'])
@login_required
def add_face(user_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية إضافة صور الوجه')
        return redirect(url_for('main.index'))
    
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # التقاط صورة من الكاميرا أو تحميل صورة
        if 'capture' in request.form:
            # التقاط صورة من الكاميرا
            camera.start()
            frame = camera.capture_frame()
            camera.stop()
            
            if frame is None:
                flash('فشل في التقاط الصورة من الكاميرا')
                return render_template('add_face.html', user=user)
            
            # معالجة الصورة وإضافتها لقاعدة البيانات
            process_face_image(frame, user)
            
            flash('تم إضافة صورة الوجه بنجاح')
            return redirect(url_for('main.dashboard'))
        
        elif 'file' in request.files:
            # تحميل صورة من الملف
            file = request.files['file']
            
            if file.filename == '':
                flash('لم يتم اختيار ملف')
                return render_template('add_face.html', user=user)
            
            if file:
                # حفظ الملف مؤقتًا
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # قراءة الصورة
                frame = cv2.imread(filepath)
                if frame is None:
                    flash('فشل في قراءة الصورة')
                    os.remove(filepath)  # حذف الملف المؤقت
                    return render_template('add_face.html', user=user)
                
                # معالجة الصورة وإضافتها لقاعدة البيانات
                process_face_image(frame, user)
                
                # حذف الملف المؤقت
                os.remove(filepath)
                
                flash('تم إضافة صورة الوجه بنجاح')
                return redirect(url_for('main.dashboard'))
    
    return render_template('add_face.html', user=user)

# وظيفة مساعدة لمعالجة صورة الوجه وإضافتها لقاعدة البيانات
def process_face_image(frame, user):
    # اكتشاف الوجه في الصورة
    faces = face_detector.detect_faces(frame)
    if len(faces) == 0:
        flash('لم يتم اكتشاف أي وجه في الصورة')
        return False
    
    # استخدام الوجه الأول المكتشف
    face_location = faces[0]
    
    # محاذاة الوجه
    aligned_face = face_aligner.align_face(frame, face_location)
    if aligned_face is None:
        flash('فشل في محاذاة الوجه')
        return False
    
    # استخراج المتجه المضمن
    embedding = face_embedder.extract_embedding(aligned_face)
    if embedding is None:
        flash('فشل في استخراج المتجه المضمن للوجه')
        return False
    
    # حفظ الصورة والمتجه المضمن في قاعدة البيانات
    import pickle
    import io
    from PIL import Image
    
    # تحويل الصورة إلى بيانات ثنائية
    img_pil = Image.fromarray(cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB))
    img_io = io.BytesIO()
    img_pil.save(img_io, 'JPEG')
    img_data = img_io.getvalue()
    
    # تحويل المتجه المضمن إلى بيانات ثنائية
    embedding_data = pickle.dumps(embedding)
    
    # إنشاء سجل صورة الوجه
    face_image = FaceImage(user_id=user.id, image_data=img_data, embedding_data=embedding_data)
    db.session.add(face_image)
    db.session.commit()
    
    return True