import cv2
import time
from config import Config

class Camera:
    """فئة للتعامل مع الكاميرا والتقاط الصور"""
    
    def __init__(self, camera_source=None, width=None, height=None):
        """تهيئة الكاميرا
        
        Args:
            camera_source (int or str): مصدر الكاميرا (رقم الجهاز أو رابط IP)
            width (int): عرض الإطار
            height (int): ارتفاع الإطار
        """
        self.camera_source = camera_source if camera_source is not None else Config.CAMERA_SOURCE
        self.width = width or Config.CAMERA_WIDTH
        self.height = height or Config.CAMERA_HEIGHT
        self.cap = None
    
    def start(self):
        """بدء تشغيل الكاميرا مع تحسينات للأداء"""
        # إضافة خيارات لتسريع فتح الكاميرا
        self.cap = cv2.VideoCapture(self.camera_source, cv2.CAP_DSHOW)  # استخدام DirectShow لتسريع الاتصال بالكاميرا
        
        if not self.cap.isOpened():
            # محاولة ثانية باستخدام الطريقة الافتراضية
            self.cap = cv2.VideoCapture(self.camera_source)
            if not self.cap.isOpened():
                raise ValueError(f"فشل في فتح الكاميرا: {self.camera_source}")
        
        # ضبط دقة الكاميرا
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # تعيين خيارات إضافية لتحسين الأداء
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # تقليل حجم المخزن المؤقت
        self.cap.set(cv2.CAP_PROP_FPS, 15)  # تحديد معدل الإطارات
        
        # التقاط إطار تجريبي للتأكد من جاهزية الكاميرا
        ret, _ = self.cap.read()
        
        return self.cap.isOpened()
    
    def stop(self):
        """إيقاف تشغيل الكاميرا"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
    
    def capture_frame(self):
        """التقاط إطار من الكاميرا مع تحسينات للأداء
        
        Returns:
            numpy.ndarray: الإطار الملتقط أو None في حالة الفشل
        """
        # التحقق من حالة الكاميرا وإعادة تشغيلها إذا لزم الأمر
        if not self.cap or not self.cap.isOpened():
            try:
                if not self.start():
                    return None
            except Exception as e:
                print(f"خطأ في بدء تشغيل الكاميرا: {e}")
                return None
        
        # محاولة التقاط الإطار مع إعادة المحاولة مرة واحدة في حالة الفشل
        for _ in range(2):  # محاولتان كحد أقصى
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                return frame
            # انتظار قصير قبل المحاولة مرة أخرى
            time.sleep(0.01)
        
        return None
    
    def capture_frames(self, num_frames=5, delay=0.1):
        """التقاط عدة إطارات من الكاميرا
        
        Args:
            num_frames (int): عدد الإطارات المراد التقاطها
            delay (float): التأخير بين الإطارات بالثواني
            
        Returns:
            list: قائمة بالإطارات الملتقطة
        """
        frames = []
        
        for _ in range(num_frames):
            frame = self.capture_frame()
            if frame is not None:
                frames.append(frame)
            time.sleep(delay)
        
        return frames
    
    def show_preview(self, window_name="Camera Preview", wait_key=1):
        """عرض معاينة للكاميرا
        
        Args:
            window_name (str): اسم نافذة العرض
            wait_key (int): وقت الانتظار بالمللي ثانية
            
        Returns:
            int: المفتاح المضغوط أو -1 إذا لم يتم الضغط على أي مفتاح
        """
        frame = self.capture_frame()
        if frame is not None:
            cv2.imshow(window_name, frame)
            return cv2.waitKey(wait_key)
        return -1
        
    def capture(self):
        """التقاط صورة من الكاميرا
        
        Returns:
            tuple: (success, frame) حيث success هو True إذا نجحت العملية و frame هو الإطار الملتقط
        """
        frame = self.capture_frame()
        if frame is not None:
            return True, frame
        return False, None