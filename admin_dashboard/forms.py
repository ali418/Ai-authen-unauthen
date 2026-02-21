# استبدال flask_wtf بنموذج بسيط
# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired, FileAllowed
# from wtforms import StringField, EmailField, SelectField, BooleanField, PasswordField, TextAreaField
# from wtforms.validators import DataRequired, Email, Length, Optional

class SimpleForm:
    """نموذج بسيط بديل عن FlaskForm"""
    def __init__(self, formdata=None, **kwargs):
        self.formdata = formdata or {}
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.errors = {}
        
    def validate(self):
        """التحقق من صحة النموذج"""
        return len(self.errors) == 0
        
    def validate_on_submit(self):
        """التحقق من صحة النموذج عند الإرسال"""
        return self.validate()

class UserForm(SimpleForm):
    """نموذج إدارة المستخدمين"""
    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        self.name = formdata.get('name', '') if formdata else kwargs.get('name', '')
        self.email = formdata.get('email', '') if formdata else kwargs.get('email', '')
        self.role = formdata.get('role', '') if formdata else kwargs.get('role', '')
        self.password = formdata.get('password', '') if formdata else kwargs.get('password', '')
        self.is_active = formdata.get('is_active', True) if formdata else kwargs.get('is_active', True)
        
    def validate(self):
        if not self.name or len(self.name) < 2:
            self.errors['name'] = 'الاسم مطلوب ويجب أن يكون أكثر من حرفين'
        if not self.email or '@' not in self.email:
            self.errors['email'] = 'البريد الإلكتروني غير صالح'
        if not self.role or self.role not in ['user', 'admin', 'security']:
            self.errors['role'] = 'الرجاء اختيار دور صالح'
        if self.password and len(self.password) < 6:
            self.errors['password'] = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'
        return super().validate()

class FaceImageForm(SimpleForm):
    """نموذج إضافة صورة وجه"""
    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        self.image = formdata.get('image', None) if formdata else kwargs.get('image', None)
        self.notes = formdata.get('notes', '') if formdata else kwargs.get('notes', '')
        
    def validate(self):
        if not self.image:
            self.errors['image'] = 'الصورة مطلوبة'
        elif hasattr(self.image, 'filename'):
            ext = self.image.filename.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                self.errors['image'] = 'يجب أن تكون الصورة بتنسيق JPG أو PNG فقط'
        if self.notes and len(self.notes) > 200:
            self.errors['notes'] = 'الملاحظات يجب أن تكون أقل من 200 حرف'
        return super().validate()

class AccessLogFilterForm(SimpleForm):
    """نموذج تصفية سجلات الوصول"""
    def __init__(self, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        self.user = formdata.get('user', '') if formdata else kwargs.get('user', '')
        self.access_granted = formdata.get('access_granted', '') if formdata else kwargs.get('access_granted', '')
        self.date_from = formdata.get('date_from', '') if formdata else kwargs.get('date_from', '')
        self.date_to = formdata.get('date_to', '') if formdata else kwargs.get('date_to', '')