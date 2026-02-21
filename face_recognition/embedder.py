import numpy as np
import cv2
from config import Config
import os

class FaceEmbedder:
    """فئة لاستخراج المتجهات المضمنة للوجوه"""
    
    def __init__(self, model_name=None):
        """تهيئة مستخرج المتجهات المضمنة
        
        Args:
            model_name (str): اسم النموذج المستخدم ('facenet', 'arcface', 'simple')
        """
        self.model_name = model_name or Config.FACE_RECOGNITION_MODEL
        
        # إضافة خيار 'simple' كبديل لا يتطلب tensorflow
        if self.model_name == 'simple':
            print("استخدام نموذج بسيط لاستخراج المتجهات المضمنة")
            self.model = None
        elif self.model_name == 'facenet':
            # استخدام نموذج FaceNet المدرب مسبقًا
            # هذا مثال فقط، ستحتاج إلى تنزيل النموذج المناسب
            model_path = 'facenet_keras.h5'
            try:
                from tensorflow.keras.models import load_model
                self.model = load_model(model_path)
            except Exception as e:
                print(f"خطأ في تحميل نموذج FaceNet: {e}")
                print("سيتم استخدام نموذج بسيط بديل للتجربة")
                self.model = None
                self.model_name = 'simple'  # التبديل إلى النموذج البسيط
        
        elif self.model_name == 'arcface':
            # استخدام نموذج ArcFace
            # هذا مثال فقط، ستحتاج إلى تثبيت مكتبة insightface
            try:
                import insightface
                from insightface.app import FaceAnalysis
                self.model = FaceAnalysis()
                self.model.prepare(ctx_id=0)
            except Exception as e:
                print(f"خطأ في تحميل نموذج ArcFace: {e}")
                print("سيتم استخدام نموذج بسيط بديل للتجربة")
                self.model = None
                self.model_name = 'simple'  # التبديل إلى النموذج البسيط
        else:
            raise ValueError(f"نموذج التعرف غير مدعوم: {self.model_name}")
    
    def preprocess_face(self, face_image):
        """معالجة صورة الوجه قبل استخراج المتجه المضمن
        
        Args:
            face_image (numpy.ndarray): صورة الوجه
            
        Returns:
            numpy.ndarray: صورة الوجه المعالجة
        """
        if self.model_name == 'facenet':
            # تغيير حجم الصورة إلى 160x160 وتحويلها إلى RGB
            face_image = cv2.resize(face_image, (160, 160))
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            # تطبيع القيم بين -1 و 1
            face_image = (face_image - 127.5) / 128.0
            return np.expand_dims(face_image, axis=0)
        
        elif self.model_name == 'arcface':
            # ArcFace يتوقع صورة RGB
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            return face_image
    
    def get_embedding(self, face_image):
        """استخراج المتجه المضمن من صورة الوجه
        
        Args:
            face_image (numpy.ndarray): صورة الوجه
            
        Returns:
            numpy.ndarray: المتجه المضمن للوجه
        """
        # إذا كان النموذج البسيط
        if self.model_name == 'simple':
            # استخراج ميزات بسيطة من الصورة
            # تغيير حجم الصورة إلى 128x128 لزيادة الدقة
            resized = cv2.resize(face_image, (128, 128))
            # تحويل إلى صورة رمادية
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            # تطبيق تحسين التباين لتحسين الميزات
            gray = cv2.equalizeHist(gray)
            # استخراج ميزات بسيطة (متوسط وانحراف معياري لكل منطقة)
            features = []
            # تقسيم الصورة إلى 25 منطقة (5×5) لزيادة الدقة
            h, w = gray.shape
            block_h, block_w = h // 5, w // 5
            for i in range(5):
                for j in range(5):
                    block = gray[i*block_h:(i+1)*block_h, j*block_w:(j+1)*block_w]
                    # إضافة المتوسط والانحراف المعياري والوسيط كميزات
                    features.append(np.mean(block))
                    features.append(np.std(block))
                    features.append(np.median(block))
            # تحسين استخراج ميزات الحواف باستخدام عدة عتبات
            edges1 = cv2.Canny(gray, 50, 150)
            edges2 = cv2.Canny(gray, 100, 200)
            
            # استخراج ميزات الحواف من كل منطقة
            for i in range(3):
                for j in range(3):
                    h_block = h // 3
                    w_block = w // 3
                    block_edges1 = edges1[i*h_block:(i+1)*h_block, j*w_block:(j+1)*w_block]
                    block_edges2 = edges2[i*h_block:(i+1)*h_block, j*w_block:(j+1)*w_block]
                    
                    features.append(np.mean(block_edges1))
                    features.append(np.mean(block_edges2))
            # تحويل إلى مصفوفة numpy وتطبيعها
            embedding = np.array(features, dtype=np.float32)
            # تطبيع المتجه
            if np.linalg.norm(embedding) > 0:
                embedding = embedding / np.linalg.norm(embedding)
            return embedding
        
        # للتجربة فقط - إذا لم يتم تحميل النموذج بنجاح
        if self.model is None:
            # إنشاء متجه عشوائي للتجربة
            return np.random.rand(128)
        
        if self.model_name == 'facenet':
            # معالجة الصورة
            processed_image = self.preprocess_face(face_image)
            # استخراج المتجه المضمن
            embedding = self.model.predict(processed_image)[0]
            return embedding / np.linalg.norm(embedding)  # تطبيع المتجه
        
        elif self.model_name == 'arcface':
            # ArcFace يقوم بالكشف واستخراج المتجه المضمن معًا
            faces = self.model.get(face_image)
            if len(faces) > 0:
                return faces[0].embedding
            return None