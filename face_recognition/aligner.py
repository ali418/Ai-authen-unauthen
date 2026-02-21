import cv2
import numpy as np
import os

# Try to import dlib with better error handling
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import dlib: {e}")
    print("Attempting to use alternative methods for face alignment.")
    print("To fix this issue, please refer to the DLIB_INSTALLATION.md file.")
    DLIB_AVAILABLE = False

class FaceAligner:
    """فئة لمحاذاة الوجوه المكتشفة"""
    
    def __init__(self, predictor_path=None):
        """تهيئة محاذي الوجوه
        
        Args:
            predictor_path (str): مسار ملف نموذج التنبؤ بالنقاط المميزة للوجه
        """
        # استخدام dlib للتنبؤ بالنقاط المميزة للوجه
        try:
            predictor_path = predictor_path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shape_predictor_68_face_landmarks.dat')
            
            # التحقق من وجود الملف
            if not os.path.exists(predictor_path):
                print(f"Warning: Predictor file not found at {predictor_path}")
                print("Download the file from: https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2")
                print("Extract it and place it in the project root directory.")
                self.predictor = None
                self.use_dlib = False
            elif not DLIB_AVAILABLE:
                print("dlib is not available. Using OpenCV for face alignment instead.")
                self.predictor = None
                self.use_dlib = False
                # Initialize OpenCV face detector
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            else:
                self.predictor = dlib.shape_predictor(predictor_path)
                self.use_dlib = True
                # Initialize dlib's face detector
                self.detector = dlib.get_frontal_face_detector()
        except Exception as e:
            print(f"Error initializing FaceAligner: {e}")
            print("Using OpenCV for face alignment instead.")
            self.predictor = None
            self.use_dlib = False
            # Initialize OpenCV face detector
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def align_face(self, image, face_width=256, padding=0.25):
        """محاذاة الوجه في الصورة
        
        Args:
            image (numpy.ndarray): صورة تحتوي على وجه
            face_width (int): عرض الوجه المطلوب في الصورة الناتجة
            padding (float): نسبة التوسيع حول الوجه
            
        Returns:
            numpy.ndarray: صورة الوجه بعد المحاذاة
        """
        if self.use_dlib and self.predictor is not None:
            return self._align_face_dlib(image, face_width, padding)
        else:
            return self._align_face_opencv(image, face_width, padding)
    
    def _align_face_dlib(self, image, face_width=256, padding=0.25):
        """محاذاة الوجه باستخدام dlib
        
        Args:
            image (numpy.ndarray): صورة تحتوي على وجه
            face_width (int): عرض الوجه المطلوب في الصورة الناتجة
            padding (float): نسبة التوسيع حول الوجه
            
        Returns:
            numpy.ndarray: صورة الوجه بعد المحاذاة
        """
        # تحويل الصورة إلى RGB إذا كانت بتنسيق BGR
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # اكتشاف الوجوه في الصورة
        faces = self.detector(gray, 1)
        
        # إذا لم يتم اكتشاف أي وجه، إرجاع الصورة الأصلية
        if len(faces) == 0:
            return image
        
        # استخدام أول وجه تم اكتشافه
        face = faces[0]
        
        # التنبؤ بالنقاط المميزة للوجه
        landmarks = self.predictor(gray, face)
        
        # استخراج إحداثيات العينين
        left_eye = (landmarks.part(36).x, landmarks.part(36).y)
        right_eye = (landmarks.part(45).x, landmarks.part(45).y)
        
        # حساب مركز كل عين
        left_eye_center = ((landmarks.part(36).x + landmarks.part(39).x) // 2,
                           (landmarks.part(36).y + landmarks.part(39).y) // 2)
        right_eye_center = ((landmarks.part(42).x + landmarks.part(45).x) // 2,
                            (landmarks.part(42).y + landmarks.part(45).y) // 2)
        
        # حساب الزاوية بين العينين
        dY = right_eye_center[1] - left_eye_center[1]
        dX = right_eye_center[0] - left_eye_center[0]
        angle = np.degrees(np.arctan2(dY, dX))
        
        # حساب المسافة بين العينين
        eye_distance = np.sqrt((dX ** 2) + (dY ** 2))
        
        # حساب معامل التكبير/التصغير
        desired_eye_distance = 0.3 * face_width
        scale = desired_eye_distance / eye_distance
        
        # حساب مركز العينين
        eyes_center = ((left_eye_center[0] + right_eye_center[0]) // 2,
                       (left_eye_center[1] + right_eye_center[1]) // 2)
        
        # إنشاء مصفوفة الدوران
        M = cv2.getRotationMatrix2D(eyes_center, angle, scale)
        
        # تحديث عنصر الإزاحة في المصفوفة
        tX = face_width * 0.5
        tY = face_width * 0.4
        M[0, 2] += (tX - eyes_center[0])
        M[1, 2] += (tY - eyes_center[1])
        
        # تطبيق التحويل الهندسي
        output = cv2.warpAffine(image, M, (face_width, face_width),
                                flags=cv2.INTER_CUBIC)
        
        return output
    
    def _align_face_opencv(self, image, face_width=256, padding=0.25):
        """محاذاة الوجه باستخدام OpenCV
        
        Args:
            image (numpy.ndarray): صورة تحتوي على وجه
            face_width (int): عرض الوجه المطلوب في الصورة الناتجة
            padding (float): نسبة التوسيع حول الوجه
            
        Returns:
            numpy.ndarray: صورة الوجه بعد المحاذاة
        """
        # تحويل الصورة إلى رمادي إذا كانت ملونة
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # اكتشاف الوجوه باستخدام OpenCV
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # إذا لم يتم اكتشاف أي وجه، إرجاع الصورة الأصلية
        if len(faces) == 0:
            return image
        
        # استخدام أول وجه تم اكتشافه
        x, y, w, h = faces[0]
        
        # حساب مركز الوجه
        center_x = x + w // 2
        center_y = y + h // 2
        
        # حساب حجم الوجه مع التوسيع
        face_size = int(max(w, h) * (1 + padding))
        
        # حساب نقطة البداية مع مراعاة التوسيع
        start_x = max(0, center_x - face_size // 2)
        start_y = max(0, center_y - face_size // 2)
        
        # اقتصاص الوجه
        face_img = image[start_y:start_y + face_size, start_x:start_x + face_size]
        
        # إذا كان الاقتصاص خارج حدود الصورة، إرجاع الصورة الأصلية
        if face_img.size == 0:
            return image
        
        # تغيير حجم الصورة إلى الحجم المطلوب
        aligned_face = cv2.resize(face_img, (face_width, face_width), interpolation=cv2.INTER_CUBIC)
        
        return aligned_face