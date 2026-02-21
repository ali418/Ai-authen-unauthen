import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# إضافة المجلد الرئيسي إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app
from backend.models import User, FaceImage, AccessLog
from backend.database import add_user, get_user_by_username, add_face_image
from config import Config

class TestBackendAPI(unittest.TestCase):
    """اختبارات لواجهة برمجة التطبيقات في الباك إند"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """تنظيف بيئة الاختبار"""
        self.app_context.pop()
    
    def test_home_page(self):
        """اختبار الصفحة الرئيسية"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """اختبار صفحة تسجيل الدخول"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    @patch('backend.routes.verify_face')
    def test_face_recognition_endpoint(self, mock_verify_face):
        """اختبار نقطة نهاية التعرف على الوجه"""
        # تهيئة المحاكاة
        mock_verify_face.return_value = (True, 'test_user', 0.95)
        
        # إنشاء بيانات اختبار
        test_data = {
            'image': 'base64_encoded_image_data'
        }
        
        # إرسال طلب POST
        response = self.app.post('/api/recognize', 
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        # التحقق من النتائج
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['access_granted'])
        self.assertEqual(data['user'], 'test_user')
        self.assertAlmostEqual(data['confidence'], 0.95)

class TestDatabaseOperations(unittest.TestCase):
    """اختبارات لعمليات قاعدة البيانات"""
    
    @patch('backend.database.session')
    def test_add_user(self, mock_session):
        """اختبار إضافة مستخدم جديد"""
        # تهيئة المحاكاة
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        
        # استدعاء الدالة المراد اختبارها
        result = add_user('test_user', 'test@example.com', 'password123', is_admin=False)
        
        # التحقق من النتائج
        self.assertTrue(result)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('backend.database.session')
    def test_get_user_by_username(self, mock_session):
        """اختبار استرجاع مستخدم بواسطة اسم المستخدم"""
        # إنشاء مستخدم وهمي للاختبار
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = 'test_user'
        mock_user.email = 'test@example.com'
        
        # تهيئة المحاكاة
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_first = mock_filter.first
        mock_first.return_value = mock_user
        
        # استدعاء الدالة المراد اختبارها
        user = get_user_by_username('test_user')
        
        # التحقق من النتائج
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test@example.com')

class TestUserModel(unittest.TestCase):
    """اختبارات لنموذج المستخدم"""
    
    def test_password_hashing(self):
        """اختبار تشفير كلمة المرور"""
        user = User(username='test_user', email='test@example.com')
        user.set_password('password123')
        
        # التحقق من أن كلمة المرور تم تشفيرها
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, 'password123')
        
        # التحقق من صحة التحقق من كلمة المرور
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrong_password'))

if __name__ == '__main__':
    unittest.main()