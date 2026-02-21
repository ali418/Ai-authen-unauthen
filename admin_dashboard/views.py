from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import admin_bp
from .forms import UserForm, FaceImageForm
from backend.database import Database
from backend.models import User, FaceImage, AccessLog
import os
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date, case

db = Database()


class Pagination:
    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        if self.per_page == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def next_num(self):
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                num > self.page - left_current - 1 and num < self.page + right_current
            ) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

# التحقق من صلاحيات المسؤول
def admin_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    decorated_view.__name__ = func.__name__
    return decorated_view

# الصفحة الرئيسية للوحة التحكم
@admin_bp.route('/')
@admin_required
def index():
    # إحصائيات عامة
    total_users = db.session.query(User).count()
    active_users = db.session.query(User).filter_by(is_active=True).count()
    total_access_attempts = db.session.query(AccessLog).count()
    successful_access = db.session.query(AccessLog).filter_by(access_granted=True).count()
    
    # آخر محاولات الوصول
    recent_logs = db.session.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(10).all()
    
    # إحصائيات الوصول خلال الأسبوع الماضي
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.session.query(
        cast(AccessLog.timestamp, Date).label('date'),
        func.count(AccessLog.id).label('total'),
        func.sum(case([(AccessLog.access_granted, 1)], else_=0)).label('granted')
    ).filter(AccessLog.timestamp >= week_ago)\
    .group_by(cast(AccessLog.timestamp, Date))\
    .order_by(cast(AccessLog.timestamp, Date)).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          active_users=active_users,
                          total_access=total_access_attempts,
                          successful_access=successful_access,
                          recent_logs=recent_logs,
                          daily_stats=daily_stats)

# إدارة المستخدمين
@admin_bp.route('/users')
@admin_required
def users():
    users_list = db.get_all_users()
    return render_template('admin/users.html', users=users_list)

# إضافة مستخدم جديد
@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    # تعديل طريقة إنشاء النموذج للعمل مع SimpleForm
    form = UserForm(request.form if request.method == 'POST' else None)
    
    if request.method == 'POST' and form.validate():
        # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
        existing_user = db.get_user_by_email(form.email)
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('admin/user_form.html', form=form, title='إضافة مستخدم جديد')
        
        # إنشاء المستخدم
        user, error = db.add_user(
            username=form.name,
            email=form.email,
            password="password123",  # كلمة مرور افتراضية أو يمكن إضافتها للنموذج
            is_admin=(form.role == 'admin')
        )
        
        if error:
            flash(f'فشل في إضافة المستخدم: {error}', 'error')
            return render_template('admin/user_form.html', form=form, title='إضافة مستخدم جديد')
        
        flash(f'تم إضافة المستخدم {form.name} بنجاح', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='إضافة مستخدم جديد')

# تعديل مستخدم
@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))
    
    # تعديل طريقة إنشاء النموذج للعمل مع SimpleForm
    if request.method == 'POST':
        form = UserForm(request.form)
    else:
        form = UserForm(None, name=user.username, email=user.email, role='admin' if user.is_admin else 'user', is_active=user.is_active)
    
    if request.method == 'POST' and form.validate():
        # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
        existing_user = db.get_user_by_email(form.email)
        if existing_user and existing_user.id != user_id:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_template('admin/user_form.html', form=form, title='تعديل المستخدم')
        
        # تحديث بيانات المستخدم
        success, error = db.update_user(
            user_id,
            username=form.name,
            email=form.email,
            is_admin=(form.role == 'admin')
        )
        
        if not success:
            flash(f'فشل في تحديث بيانات المستخدم: {error}', 'error')
            return render_template('admin/user_form.html', form=form, title='تعديل المستخدم')
            
        flash(f'تم تحديث بيانات المستخدم {form.name} بنجاح', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='تعديل المستخدم')

# حذف مستخدم
@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = db.get_user(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))
    
    db.delete_user(user_id)
    flash(f'تم حذف المستخدم {user.name} بنجاح', 'success')
    return redirect(url_for('admin.users'))

# إدارة صور الوجوه
@admin_bp.route('/users/<int:user_id>/faces')
@admin_required
def user_faces(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_faces.html', user=user)

# إضافة صورة وجه جديدة
@admin_bp.route('/users/<int:user_id>/faces/add', methods=['GET', 'POST'])
@admin_required
def add_face(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('admin.users'))
    
    # تعديل طريقة إنشاء النموذج للعمل مع SimpleForm
    form = FaceImageForm(request.form if request.method == 'POST' else None)
    if request.method == 'POST':
        form.image = request.files.get('image')
        if form.validate() and form.image:
            try:
                # حفظ الصورة في مجلد التحميلات
                import os
                from werkzeug.utils import secure_filename
                from utils.helpers import create_directory_if_not_exists
                import cv2
                import numpy as np
                from face_recognition.detector import FaceDetector
                from face_recognition.embedder import FaceEmbedder
                
                # إنشاء مسار لحفظ الصورة
                upload_dir = os.path.join('uploads', 'faces', str(user_id))
                create_directory_if_not_exists(upload_dir)
                
                # حفظ الصورة المرفوعة
                filename = secure_filename(form.image.filename)
                file_path = os.path.join(upload_dir, filename)
                form.image.save(file_path)
                
                # قراءة الصورة باستخدام OpenCV
                image = cv2.imread(file_path)
                if image is None:
                    flash('فشل في قراءة الصورة المرفوعة', 'error')
                    return redirect(url_for('admin.add_face', user_id=user_id))
                
                # اكتشاف الوجوه في الصورة
                detector = FaceDetector()
                faces = detector.detect_faces(image)
                
                if not faces or len(faces) == 0:
                    flash('لم يتم العثور على وجه في الصورة', 'error')
                    # حذف الصورة إذا لم يتم العثور على وجه
                    os.remove(file_path)
                    return redirect(url_for('admin.add_face', user_id=user_id))
                
                # استخدام أول وجه تم اكتشافه
                face_location = faces[0]
                face_image = detector.extract_face(image, face_location)
                
                # استخراج المتجه المضمن للوجه
                embedder = FaceEmbedder()
                embedding = embedder.get_embedding(face_image)
                
                # إضافة صورة الوجه إلى قاعدة البيانات
                success, error = db.add_face_image(user_id, file_path, embedding)
                
                if success:
                    flash('تم إضافة صورة الوجه بنجاح', 'success')
                    return redirect(url_for('admin.user_faces', user_id=user_id))
                else:
                    flash(f'فشل في إضافة صورة الوجه: {error}', 'error')
                    # حذف الصورة في حالة الفشل
                    os.remove(file_path)
            except Exception as e:
                flash(f'حدث خطأ أثناء معالجة الصورة: {str(e)}', 'error')
        else:
            if not form.image:
                flash('الرجاء اختيار صورة', 'error')
    
    return render_template('admin/face_form.html', form=form, user=user)

# سجلات الوصول
@admin_bp.route('/access-logs')
@admin_required
def access_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    logs_query = db.session.query(AccessLog).order_by(AccessLog.timestamp.desc())
    total = logs_query.count()
    items = (
        logs_query.offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    logs_paginated = Pagination(
        query=logs_query,
        page=page,
        per_page=per_page,
        total=total,
        items=items,
    )
    users_list = db.get_all_users()
    return render_template('admin/access_logs.html', logs=logs_paginated, users=users_list)

# تصدير سجلات الوصول
@admin_bp.route('/access-logs/export')
@admin_required
def export_access_logs():
    # الحصول على معايير التصفية من الطلب
    user_id = request.args.get('user_id', None)
    status = request.args.get('status', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    # إنشاء استعلام قاعدة البيانات
    logs_query = db.session.query(AccessLog).order_by(AccessLog.timestamp.desc())
    
    # تطبيق معايير التصفية
    if user_id and user_id != '':
        logs_query = logs_query.filter(AccessLog.user_id == user_id)
    
    if status:
        if status == 'granted':
            logs_query = logs_query.filter(AccessLog.access_granted == True)
        elif status == 'denied':
            logs_query = logs_query.filter(AccessLog.access_granted == False)
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        logs_query = logs_query.filter(AccessLog.timestamp >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # إضافة يوم واحد للحصول على نهاية اليوم
        end_date = end_date + timedelta(days=1)
        logs_query = logs_query.filter(AccessLog.timestamp < end_date)
    
    # الحصول على جميع السجلات
    logs = logs_query.all()
    
    # إنشاء محتوى CSV
    import csv
    import io
    from flask import make_response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # كتابة رأس الملف
    writer.writerow(['المعرف', 'المستخدم', 'التاريخ والوقت', 'الحالة', 'نسبة الثقة', 'ملاحظات'])
    
    # كتابة البيانات
    for log in logs:
        user_name = log.user.full_name if log.user else 'غير معروف'
        status_text = 'مسموح' if log.access_granted else 'مرفوض'
        writer.writerow([
            log.id,
            user_name,
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            status_text,
            f'{log.confidence:.2f}%' if log.confidence else 'غير متوفر',
            log.notes or ''
        ])
    
    # إنشاء استجابة مع ملف CSV
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=access_logs.csv'
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    
    return response
