# مدير قاعدة البيانات
# يوفر هذا الملف واجهة برمجة سهلة للتعامل مع قاعدة البيانات وإدارتها

import os
import sqlite3
import shutil
from datetime import datetime
from config import Config
from backend.models import init_db
from .migrations.migration_manager import MigrationManager

class DBManager:
    """فئة لإدارة قاعدة البيانات"""
    
    def __init__(self, db_path=None):
        """تهيئة مدير قاعدة البيانات
        
        Args:
            db_path (str, optional): مسار قاعدة البيانات. إذا لم يتم تحديده، سيتم استخدامه من الإعدادات.
        """
        # استخراج مسار قاعدة البيانات من URI
        if db_path is None:
            db_uri = Config.DATABASE_URI
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri[10:]
            else:
                raise ValueError(f"نوع قاعدة البيانات غير مدعوم: {db_uri}")
        
        self.db_path = db_path
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'backups')
        
        # التأكد من وجود مجلد النسخ الاحتياطية
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def initialize_database(self):
        """تهيئة قاعدة البيانات
        
        Returns:
            bool: True إذا تم تهيئة قاعدة البيانات بنجاح
        """
        try:
            # تهيئة قاعدة البيانات باستخدام SQLAlchemy
            init_db()
            print("تم تهيئة قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            print(f"خطأ أثناء تهيئة قاعدة البيانات: {str(e)}")
            return False
    
    def run_migrations(self):
        """تشغيل ترحيلات قاعدة البيانات
        
        Returns:
            int: عدد الترحيلات التي تم تطبيقها
        """
        try:
            manager = MigrationManager(self.db_path)
            count = manager.apply_all_pending_migrations()
            print(f"تم تطبيق {count} ترحيلات")
            return count
        except Exception as e:
            print(f"خطأ أثناء تطبيق الترحيلات: {str(e)}")
            return 0
    
    def create_backup(self):
        """إنشاء نسخة احتياطية من قاعدة البيانات
        
        Returns:
            str: مسار ملف النسخة الاحتياطية
        """
        # التأكد من وجود قاعدة البيانات
        if not os.path.exists(self.db_path):
            print(f"خطأ: قاعدة البيانات {self.db_path} غير موجودة")
            return None
        
        # إنشاء اسم ملف النسخة الاحتياطية
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        db_name = os.path.basename(self.db_path)
        backup_filename = f"{db_name}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # نسخ ملف قاعدة البيانات
            shutil.copy2(self.db_path, backup_path)
            print(f"تم إنشاء نسخة احتياطية: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}")
            return None
    
    def restore_backup(self, backup_path):
        """استعادة نسخة احتياطية
        
        Args:
            backup_path (str): مسار ملف النسخة الاحتياطية
            
        Returns:
            bool: True إذا تمت الاستعادة بنجاح
        """
        # التأكد من وجود ملف النسخة الاحتياطية
        if not os.path.exists(backup_path):
            print(f"خطأ: ملف النسخة الاحتياطية {backup_path} غير موجود")
            return False
        
        try:
            # إنشاء نسخة احتياطية من قاعدة البيانات الحالية قبل الاستعادة
            current_backup = self.create_backup()
            
            # استعادة النسخة الاحتياطية
            shutil.copy2(backup_path, self.db_path)
            print(f"تم استعادة النسخة الاحتياطية: {backup_path}")
            print(f"تم إنشاء نسخة احتياطية من قاعدة البيانات السابقة: {current_backup}")
            return True
        except Exception as e:
            print(f"خطأ أثناء استعادة النسخة الاحتياطية: {str(e)}")
            return False
    
    def get_backup_list(self):
        """الحصول على قائمة النسخ الاحتياطية
        
        Returns:
            list: قائمة بمسارات ملفات النسخ الاحتياطية
        """
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.bak'):
                backups.append(os.path.join(self.backup_dir, filename))
        
        return sorted(backups, reverse=True)
    
    def get_database_info(self):
        """الحصول على معلومات قاعدة البيانات
        
        Returns:
            dict: معلومات قاعدة البيانات
        """
        info = {
            'path': self.db_path,
            'size': 0,
            'tables': [],
            'rows': {}
        }
        
        # التأكد من وجود قاعدة البيانات
        if not os.path.exists(self.db_path):
            return info
        
        # حجم قاعدة البيانات
        info['size'] = os.path.getsize(self.db_path)
        
        try:
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # الحصول على قائمة الجداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            info['tables'] = tables
            
            # الحصول على عدد الصفوف في كل جدول
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                info['rows'][table] = count
            
            conn.close()
        except Exception as e:
            print(f"خطأ أثناء الحصول على معلومات قاعدة البيانات: {str(e)}")
        
        return info
    
    def optimize_database(self):
        """تحسين أداء قاعدة البيانات
        
        Returns:
            bool: True إذا تم التحسين بنجاح
        """
        try:
            # إنشاء نسخة احتياطية قبل التحسين
            self.create_backup()
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # تشغيل VACUUM لتحسين الأداء وتقليل حجم الملف
            cursor.execute("VACUUM")
            
            # تحليل قاعدة البيانات
            cursor.execute("ANALYZE")
            
            conn.commit()
            conn.close()
            
            print("تم تحسين أداء قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            print(f"خطأ أثناء تحسين أداء قاعدة البيانات: {str(e)}")
            return False

# استخدام الفئة
def initialize_and_migrate():
    """تهيئة قاعدة البيانات وتطبيق الترحيلات"""
    manager = DBManager()
    manager.initialize_database()
    manager.run_migrations()

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    manager = DBManager()
    return manager.create_backup()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        manager = DBManager()
        
        if command == 'init':
            manager.initialize_database()
        elif command == 'migrate':
            manager.run_migrations()
        elif command == 'backup':
            manager.create_backup()
        elif command == 'restore' and len(sys.argv) > 2:
            manager.restore_backup(sys.argv[2])
        elif command == 'info':
            info = manager.get_database_info()
            print(f"مسار قاعدة البيانات: {info['path']}")
            print(f"حجم قاعدة البيانات: {info['size'] / 1024:.2f} كيلوبايت")
            print(f"عدد الجداول: {len(info['tables'])}")
            print("الجداول:")
            for table in info['tables']:
                print(f"  {table}: {info['rows'].get(table, 0)} صف")
        elif command == 'optimize':
            manager.optimize_database()
        else:
            print("الاستخدام:")
            print("  python db_manager.py init - تهيئة قاعدة البيانات")
            print("  python db_manager.py migrate - تطبيق الترحيلات")
            print("  python db_manager.py backup - إنشاء نسخة احتياطية")
            print("  python db_manager.py restore PATH - استعادة نسخة احتياطية")
            print("  python db_manager.py info - عرض معلومات قاعدة البيانات")
            print("  python db_manager.py optimize - تحسين أداء قاعدة البيانات")
    else:
        print("الاستخدام:")
        print("  python db_manager.py init - تهيئة قاعدة البيانات")
        print("  python db_manager.py migrate - تطبيق الترحيلات")
        print("  python db_manager.py backup - إنشاء نسخة احتياطية")
        print("  python db_manager.py restore PATH - استعادة نسخة احتياطية")
        print("  python db_manager.py info - عرض معلومات قاعدة البيانات")
        print("  python db_manager.py optimize - تحسين أداء قاعدة البيانات")