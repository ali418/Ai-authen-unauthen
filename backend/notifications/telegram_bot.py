import requests
import os
from config import Config

class TelegramBot:
    """فئة للتفاعل مع بوت تليجرام لإرسال التنبيهات"""
    
    def __init__(self):
        """تهيئة بوت تليجرام"""
        self.enabled = Config.ENABLE_TELEGRAM_NOTIFICATIONS
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message):
        """إرسال رسالة نصية
        
        Args:
            message (str): نص الرسالة
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        if not self.enabled:
            print("تنبيهات تليجرام غير مفعلة")
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message
            }
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print(f"تم إرسال رسالة تليجرام: {message[:50]}...")
                return True
            else:
                print(f"فشل في إرسال رسالة تليجرام: {response.text}")
                return False
        
        except Exception as e:
            print(f"فشل في إرسال رسالة تليجرام: {e}")
            return False
    
    def send_photo(self, photo_path, caption=None):
        """إرسال صورة
        
        Args:
            photo_path (str): مسار الصورة
            caption (str, optional): نص التعليق
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        if not self.enabled:
            print("تنبيهات تليجرام غير مفعلة")
            return False
        
        if not os.path.exists(photo_path):
            print(f"الصورة غير موجودة: {photo_path}")
            return False
        
        try:
            url = f"{self.api_url}/sendPhoto"
            data = {
                'chat_id': self.chat_id
            }
            
            if caption:
                data['caption'] = caption
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                print(f"تم إرسال صورة تليجرام: {os.path.basename(photo_path)}")
                return True
            else:
                print(f"فشل في إرسال صورة تليجرام: {response.text}")
                return False
        
        except Exception as e:
            print(f"فشل في إرسال صورة تليجرام: {e}")
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
        import datetime
        
        if access_granted:
            message = f"✅ تم منح الوصول للمستخدم {user_name}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message = f"❌ تم رفض الوصول للمستخدم {user_name}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if image_path and os.path.exists(image_path):
            return self.send_photo(image_path, message)
        else:
            return self.send_message(message)
    
    def send_unknown_person_notification(self, image_path=None):
        """إرسال تنبيه شخص غير معروف
        
        Args:
            image_path (str, optional): مسار صورة الوجه
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        import datetime
        
        message = f"⚠️ محاولة وصول من شخص غير معروف\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if image_path and os.path.exists(image_path):
            return self.send_photo(image_path, message)
        else:
            return self.send_message(message)