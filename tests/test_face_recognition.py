import unittest
import sys
import os
import numpy as np

# إضافة المجلد الرئيسي إلى مسار البحث
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from face_recognition.detector import FaceDetector
from face_recognition.aligner import FaceAligner
from face_recognition.embedder import FaceEmbedder
from face_recognition.matcher import FaceMatcher
from config import Config

class TestFaceDetector(unittest.TestCase):
    """اختبارات لوحدة كشف الوجوه"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.detector = FaceDetector()
    
    def test_detector_initialization(self):
        """اختبار تهيئة كاشف الوجوه"""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.detector)
    
    def test_detect_faces_with_no_face(self):
        """اختبار كشف الوجوه في صورة بدون وجوه"""
        # إنشاء صورة فارغة للاختبار
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        faces = self.detector.detect(empty_image)
        self.assertEqual(len(faces), 0)

class TestFaceAligner(unittest.TestCase):
    """اختبارات لوحدة محاذاة الوجوه"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.aligner = FaceAligner()
    
    def test_aligner_initialization(self):
        """اختبار تهيئة محاذي الوجوه"""
        self.assertIsNotNone(self.aligner)
        self.assertIsNotNone(self.aligner.predictor)

class TestFaceEmbedder(unittest.TestCase):
    """اختبارات لوحدة استخراج متجهات الوجوه"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.embedder = FaceEmbedder()
    
    def test_embedder_initialization(self):
        """اختبار تهيئة مستخرج متجهات الوجوه"""
        self.assertIsNotNone(self.embedder)
        self.assertIsNotNone(self.embedder.model)
    
    def test_embedding_dimensions(self):
        """اختبار أبعاد متجه الوجه المستخرج"""
        # إنشاء صورة وجه وهمية للاختبار
        face_image = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
        embedding = self.embedder.get_embedding(face_image)
        self.assertEqual(embedding.shape[0], self.embedder.EMBEDDING_SIZE)

class TestFaceMatcher(unittest.TestCase):
    """اختبارات لوحدة مطابقة الوجوه"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.matcher = FaceMatcher(threshold=Config.FACE_SIMILARITY_THRESHOLD)
    
    def test_matcher_initialization(self):
        """اختبار تهيئة مطابق الوجوه"""
        self.assertIsNotNone(self.matcher)
        self.assertEqual(self.matcher.threshold, Config.FACE_SIMILARITY_THRESHOLD)
    
    def test_compute_similarity(self):
        """اختبار حساب التشابه بين متجهين"""
        # إنشاء متجهين متطابقين
        embedding1 = np.ones(128)
        embedding2 = np.ones(128)
        similarity = self.matcher.compute_similarity(embedding1, embedding2)
        self.assertEqual(similarity, 1.0)
        
        # إنشاء متجهين مختلفين
        embedding3 = np.ones(128)
        embedding4 = np.zeros(128)
        similarity = self.matcher.compute_similarity(embedding3, embedding4)
        self.assertLess(similarity, 1.0)

if __name__ == '__main__':
    unittest.main()