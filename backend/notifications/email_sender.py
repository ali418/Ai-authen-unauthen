import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from config import Config

class EmailSender:
    """فئة لإرسال التنبيهات عبر البريد الإلكتروني"""
    
    def __init__(self):
        """تهيئة مرسل البريد الإلكتروني"""
        self.enabled = Config.ENABLE_EMAIL_NOTIFICATIONS
        self.sender = Config.EMAIL_SENDER
        self.password = Config.EMAIL_PASSWORD
        self.recipient = Config.EMAIL_RECIPIENT
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
    
    def send_notification(self, subject, message, image_path=None):
        """إرسال تنبيه عبر البريد الإلكتروني
        
        Args:
            subject (str): عنوان البريد الإلكتروني
            message (str): نص الرسالة
            image_path (str, optional): مسار الصورة المرفقة
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        if not self.enabled:
            print("تنبيهات البريد الإلكتروني غير مفعلة")
            return False
        
        try:
            # إنشاء رسالة البريد الإلكتروني
            email = MIMEMultipart()
            email['From'] = self.sender
            email['To'] = self.recipient
            email['Subject'] = subject
            
            # إضافة نص الرسالة
            email.attach(MIMEText(message, 'plain'))
            
            # إضافة الصورة إذا تم توفيرها
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    email.attach(image)
            
            # الاتصال بخادم SMTP وإرسال البريد الإلكتروني
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(email)
            
            print(f"تم إرسال تنبيه البريد الإلكتروني: {subject}")
            return True
        
        except Exception as e:
            print(f"فشل في إرسال تنبيه البريد الإلكتروني: {e}")
            return False
    
    def send_access_notification(self, user_name, access_granted, image_path=None):
        """إرسال تنبيه وصول
        
        Args:
            user_name (str): اسم المستخدم
            access_granted (bool): هل تم منح الوصول أم لا
            image_path (str, optional): مسار صورة الوجه
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        if access_granted:
            subject = f"تم منح الوصول لـ {user_name}"
            message = f"تم منح الوصول للمستخدم {user_name} في {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            subject = f"تم رفض الوصول لـ {user_name}"
            message = f"تم رفض الوصول للمستخدم {user_name} في {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_notification(subject, message, image_path)
    
    def send_unknown_person_notification(self, image_path=None):
        """إرسال تنبيه شخص غير معروف
        
        Args:
            image_path (str, optional): مسار صورة الوجه
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        subject = "محاولة وصول من شخص غير معروف"
        message = f"تم اكتشاف محاولة وصول من شخص غير معروف في {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_notification(subject, message, image_path)