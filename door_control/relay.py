# التحكم في المرحل (Relay)
# هذا الملف يوفر واجهة للتحكم في المرحل المتصل بالباب

import time
import threading
from .gpio_handler import GPIOHandler
from config import Config

class DoorRelay:
    """فئة للتحكم في المرحل المتصل بالباب
    
    تستخدم هذه الفئة GPIOHandler للتحكم في المرحل المتصل بالباب
    وتوفر وظائف لفتح وإغلاق الباب
    """
    
    def __init__(self, pin=None, open_duration=None):
        """تهيئة المرحل
        
        Args:
            pin (int, optional): رقم منفذ GPIO المتصل بالمرحل. إذا لم يتم تحديده، سيتم استخدام القيمة من ملف الإعدادات.
            open_duration (float, optional): مدة فتح الباب بالثواني. إذا لم يتم تحديدها، سيتم استخدام القيمة من ملف الإعدادات.
        """
        self.pin = pin if pin is not None else Config.DOOR_RELAY_PIN
        self.open_duration = open_duration if open_duration is not None else Config.DOOR_OPEN_DURATION
        self.gpio = GPIOHandler()
        self.gpio.setup_pin(self.pin, 'out')
        self.gpio.set_pin(self.pin, 0)  # تأكد من أن الباب مغلق عند البدء
        self._active = False
        self._timer = None
        print(f"تم تهيئة مرحل الباب على المنفذ {self.pin} بمدة فتح {self.open_duration} ثانية")
    
    def activate(self):
        """تنشيط المرحل (فتح الباب)
        
        Returns:
            bool: True إذا تم تنشيط المرحل بنجاح
        """
        # إلغاء المؤقت السابق إذا كان موجودًا
        if self._timer:
            self._timer.cancel()
        
        # تنشيط المرحل
        self.gpio.set_pin(self.pin, 1)
        self._active = True
        print(f"تم فتح الباب على المنفذ {self.pin}")
        
        # إعداد مؤقت لإغلاق الباب تلقائيًا بعد المدة المحددة
        self._timer = threading.Timer(self.open_duration, self.deactivate)
        self._timer.daemon = True
        self._timer.start()
        
        return True
    
    def deactivate(self):
        """إلغاء تنشيط المرحل (إغلاق الباب)
        
        Returns:
            bool: True إذا تم إلغاء تنشيط المرحل بنجاح
        """
        # إلغاء المؤقت إذا كان موجودًا
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
        # إلغاء تنشيط المرحل
        self.gpio.set_pin(self.pin, 0)
        self._active = False
        print(f"تم إغلاق الباب على المنفذ {self.pin}")
        
        return True
    
    def is_active(self):
        """التحقق مما إذا كان المرحل نشطًا (الباب مفتوح)
        
        Returns:
            bool: True إذا كان المرحل نشطًا (الباب مفتوح)
        """
        return self._active
    
    def __del__(self):
        """تنظيف عند حذف الكائن"""
        if self._timer:
            self._timer.cancel()
        self.deactivate()