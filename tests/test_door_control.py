import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# إضافة المجلد الرئيسي إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from door_control.relay import DoorRelay
from door_control.gpio_handler import GPIOHandler

class TestDoorRelay(unittest.TestCase):
    """اختبارات لوحدة التحكم في المرحل (DoorRelay)"""
    
    @patch('door_control.relay.GPIOHandler')
    def setUp(self, mock_gpio_handler):
        """إعداد بيئة الاختبار"""
        # تهيئة المحاكاة
        self.mock_gpio = mock_gpio_handler.return_value
        self.mock_gpio.setup_pin.return_value = None
        self.mock_gpio.set_pin.return_value = None
        
        # إنشاء كائن المرحل للاختبار
        self.relay = DoorRelay(pin=18, open_duration=5)
    
    def test_relay_initialization(self):
        """اختبار تهيئة المرحل"""
        self.assertIsNotNone(self.relay)
        self.assertEqual(self.relay.pin, 18)
        self.assertEqual(self.relay.open_duration, 5)
        self.mock_gpio.setup_pin.assert_called_once_with(18, 'out')
    
    def test_relay_activate(self):
        """اختبار تنشيط المرحل (فتح الباب)"""
        with patch('threading.Timer') as mock_timer:
            mock_timer_instance = mock_timer.return_value
            result = self.relay.activate()
            self.mock_gpio.set_pin.assert_called_once_with(18, 1)
            self.assertTrue(result)
            self.assertTrue(self.relay.is_active())
            mock_timer.assert_called_once()
    
    def test_relay_deactivate(self):
        """اختبار إلغاء تنشيط المرحل (إغلاق الباب)"""
        # تهيئة المرحل كنشط أولاً
        self.relay._active = True
        self.relay._timer = MagicMock()
        
        result = self.relay.deactivate()
        self.mock_gpio.set_pin.assert_called_once_with(18, 0)
        self.assertTrue(result)
        self.assertFalse(self.relay.is_active())
        self.relay._timer.cancel.assert_called_once()
    
    def test_is_active(self):
        """اختبار التحقق من حالة المرحل"""
        # اختبار عندما يكون المرحل غير نشط
        self.relay._active = False
        self.assertFalse(self.relay.is_active())
        
        # اختبار عندما يكون المرحل نشط
        self.relay._active = True
        self.assertTrue(self.relay.is_active())

class TestGPIOHandler(unittest.TestCase):
    """اختبارات لمعالج GPIO"""
    
    @patch('door_control.gpio_handler.GPIO')
    def setUp(self, mock_gpio):
        """إعداد بيئة الاختبار"""
        # تهيئة المحاكاة
        self.mock_gpio = mock_gpio
        self.mock_gpio.setmode.return_value = None
        self.mock_gpio.setup.return_value = None
        self.mock_gpio.output.return_value = None
        self.mock_gpio.HIGH = 1
        self.mock_gpio.LOW = 0
        self.mock_gpio.OUT = 'OUT'
        self.mock_gpio.IN = 'IN'
        self.mock_gpio.BCM = 'BCM'
        
        # إنشاء كائن معالج GPIO للاختبار
        self.gpio_handler = GPIOHandler()
    
    def test_gpio_initialization(self):
        """اختبار تهيئة معالج GPIO"""
        self.assertIsNotNone(self.gpio_handler)
        self.mock_gpio.setmode.assert_called_once_with(self.mock_gpio.BCM)
    
    def test_setup_pin(self):
        """اختبار إعداد دبوس GPIO"""
        self.gpio_handler.setup_pin(18, 'OUT')
        self.mock_gpio.setup.assert_called_once_with(18, self.mock_gpio.OUT)
    
    def test_set_pin(self):
        """اختبار تعيين قيمة لمنفذ GPIO"""
        # اختبار تعيين المنفذ إلى المستوى المرتفع
        self.gpio_handler.set_pin(18, 1)
        self.mock_gpio.output.assert_called_with(18, 1)
        
        # اختبار تعيين المنفذ إلى المستوى المنخفض
        self.gpio_handler.set_pin(18, 0)
        self.mock_gpio.output.assert_called_with(18, 0)
    
    def test_cleanup(self):
        """اختبار تنظيف موارد GPIO"""
        self.gpio_handler.cleanup()
        self.mock_gpio.cleanup.assert_called_once()

    def test_get_pin(self):
        """اختبار قراءة قيمة منفذ GPIO"""
        # تهيئة المحاكاة لإرجاع قيمة محددة
        self.mock_gpio.input.return_value = 1
        
        # اختبار قراءة قيمة المنفذ
        value = self.gpio_handler.get_pin(18)
        self.assertEqual(value, 1)
        self.mock_gpio.input.assert_called_once_with(18)

if __name__ == '__main__':
    unittest.main()