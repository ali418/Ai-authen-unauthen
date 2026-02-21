# التعامل مع منافذ GPIO
# هذا الملف يوفر واجهة للتعامل مع منافذ GPIO

import os
import time
import platform

class GPIOHandler:
    """فئة للتعامل مع منافذ GPIO
    
    توفر هذه الفئة واجهة مجردة للتعامل مع منافذ GPIO
    مع دعم للتشغيل على أنظمة مختلفة (Raspberry Pi وأنظمة أخرى للاختبار)
    """
    
    def __init__(self):
        self.is_raspberry_pi = self._is_running_on_raspberry_pi()
        self.pins_state = {}  # لتتبع حالة المنافذ في وضع المحاكاة
        
        if self.is_raspberry_pi:
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.GPIO.setmode(GPIO.BCM)  # استخدام ترقيم BCM
                self.GPIO.setwarnings(False)
                print("تم تهيئة GPIO على Raspberry Pi")
            except ImportError:
                print("تحذير: لم يتم العثور على وحدة RPi.GPIO. سيتم استخدام وضع المحاكاة.")
                self.is_raspberry_pi = False
        else:
            print("تشغيل في وضع المحاكاة: سيتم محاكاة GPIO")
    
    def _is_running_on_raspberry_pi(self):
        """التحقق مما إذا كان الكود يعمل على Raspberry Pi"""
        return platform.system() == "Linux" and os.path.exists("/proc/device-tree/model") and "Raspberry Pi" in open("/proc/device-tree/model").read()
    
    def setup_pin(self, pin, mode):
        """إعداد منفذ GPIO
        
        Args:
            pin (int): رقم المنفذ
            mode (str): 'in' للدخل أو 'out' للخرج
        """
        if self.is_raspberry_pi:
            if mode == 'in':
                self.GPIO.setup(pin, self.GPIO.IN)
            else:  # 'out'
                self.GPIO.setup(pin, self.GPIO.OUT)
        else:
            # تتبع حالة المنفذ في وضع المحاكاة
            self.pins_state[pin] = 0
            print(f"محاكاة: تم إعداد المنفذ {pin} كـ {mode}")
    
    def set_pin(self, pin, value):
        """تعيين قيمة لمنفذ GPIO
        
        Args:
            pin (int): رقم المنفذ
            value (int): 0 للمستوى المنخفض أو 1 للمستوى المرتفع
        """
        if self.is_raspberry_pi:
            self.GPIO.output(pin, value)
        else:
            # تحديث حالة المنفذ في وضع المحاكاة
            self.pins_state[pin] = value
            print(f"محاكاة: تم تعيين المنفذ {pin} إلى {value}")
    
    def get_pin(self, pin):
        """قراءة قيمة منفذ GPIO
        
        Args:
            pin (int): رقم المنفذ
            
        Returns:
            int: 0 للمستوى المنخفض أو 1 للمستوى المرتفع
        """
        if self.is_raspberry_pi:
            return self.GPIO.input(pin)
        else:
            # قراءة حالة المنفذ من وضع المحاكاة
            return self.pins_state.get(pin, 0)
    
    def cleanup(self):
        """تنظيف وإعادة تعيين منافذ GPIO"""
        if self.is_raspberry_pi:
            self.GPIO.cleanup()
        else:
            self.pins_state = {}
            print("محاكاة: تم تنظيف جميع منافذ GPIO")