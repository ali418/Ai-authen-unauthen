import cv2
import numpy as np
from config import Config
import os

class FaceDetector:
    """فئة لاكتشاف الوجوه في الصور"""
    
    def __init__(self, detection_model=None):
        """تهيئة كاشف الوجوه
        
        Args:
            detection_model (str): نموذج الكشف عن الوجوه ('mtcnn', 'opencv', 'dlib', 'simple')
        """
        self.detection_model = detection_model or Config.FACE_DETECTION_MODEL
        
        if self.detection_model == 'simple':
            # استخدام كاشف الوجوه المدمج في OpenCV
            model_path = 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + model_path)
            print(f"تم تحميل كاشف الوجوه البسيط باستخدام OpenCV Haar Cascade")
        elif self.detection_model == 'opencv':
            # استخدام كاشف الوجوه المدمج في OpenCV
            model_path = 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + model_path)
        elif self.detection_model == 'dlib':
            # سيتم تنفيذه لاحقًا - استخدام dlib للكشف عن الوجوه
            try:
                import dlib
                self.detector = dlib.get_frontal_face_detector()
            except ImportError as e:
                print(f"خطأ في تحميل dlib: {e}")
                print("سيتم استخدام كاشف الوجوه البسيط بدلاً من ذلك")
                self.detection_model = 'simple'
                model_path = 'haarcascade_frontalface_default.xml'
                self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + model_path)
        elif self.detection_model == 'mtcnn':
            # سيتم تنفيذه لاحقًا - استخدام MTCNN للكشف عن الوجوه
            try:
                from mtcnn import MTCNN
                self.detector = MTCNN()
            except ImportError as e:
                print(f"خطأ في تحميل MTCNN: {e}")
                print("سيتم استخدام كاشف الوجوه البسيط بدلاً من ذلك")
                self.detection_model = 'simple'
                model_path = 'haarcascade_frontalface_default.xml'
                self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + model_path)
        else:
            raise ValueError(f"نموذج الكشف غير مدعوم: {self.detection_model}")
    
    def detect_faces(self, image):
        """اكتشاف الوجوه في الصورة
        
        Args:
            image (numpy.ndarray): صورة بتنسيق OpenCV (BGR)
            
        Returns:
            list: قائمة بمستطيلات الوجوه المكتشفة [(x, y, w, h), ...]
        """
        if self.detection_model == 'simple' or self.detection_model == 'opencv':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # تحسين معلمات الكشف: تقليل معامل القياس وتقليل الحد الأدنى للجيران لزيادة الحساسية
            faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            return faces
        
        elif self.detection_model == 'dlib':
            # تحويل الصورة إلى تنسيق RGB لـ dlib
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = self.detector(rgb_image)
            # تحويل نتائج dlib إلى تنسيق (x, y, w, h)
            return [(face.left(), face.top(), face.width(), face.height()) for face in faces]
        
        elif self.detection_model == 'mtcnn':
            # MTCNN يتوقع صورة RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = self.detector.detect_faces(rgb_image)
            # استخراج مستطيلات الوجوه من نتائج MTCNN
            return [(face['box'][0], face['box'][1], face['box'][2], face['box'][3]) for face in faces]
    
    def extract_face(self, image, face_location, target_size=(160, 160)):
        """استخراج صورة الوجه من الصورة الكاملة
        
        Args:
            image (numpy.ndarray): صورة بتنسيق OpenCV (BGR)
            face_location (tuple): موقع الوجه (x, y, w, h)
            target_size (tuple): حجم الصورة المستهدف
            
        Returns:
            numpy.ndarray: صورة الوجه المستخرجة والمعدلة الحجم
        """
        x, y, w, h = face_location
        face_image = image[y:y+h, x:x+w]
        return cv2.resize(face_image, target_size)