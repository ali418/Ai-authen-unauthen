# مدير ترحيلات قاعدة البيانات
# يستخدم هذا الملف لإدارة ترحيلات قاعدة البيانات

import os
import sqlite3
import datetime
import importlib.util
from config import Config

class MigrationManager:
    """فئة لإدارة ترحيلات قاعدة البيانات"""
    
    def __init__(self, db_path=None):
        """تهيئة مدير الترحيلات
        
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
        self.migrations_dir = os.path.dirname(os.path.abspath(__file__))
        self.migrations_table = 'migrations'
        
        # التأكد من وجود جدول الترحيلات
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """التأكد من وجود جدول الترحيلات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_applied_migrations(self):
        """الحصول على قائمة الترحيلات المطبقة
        
        Returns:
            list: قائمة بأسماء الترحيلات المطبقة
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT migration_name FROM {self.migrations_table} ORDER BY id")
        migrations = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return migrations
    
    def get_available_migrations(self):
        """الحصول على قائمة الترحيلات المتاحة
        
        Returns:
            list: قائمة بأسماء الترحيلات المتاحة
        """
        migrations = []
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != os.path.basename(__file__):
                migrations.append(filename[:-3])  # إزالة .py
        
        return sorted(migrations)
    
    def get_pending_migrations(self):
        """الحصول على قائمة الترحيلات المعلقة
        
        Returns:
            list: قائمة بأسماء الترحيلات المعلقة
        """
        applied = set(self.get_applied_migrations())
        available = self.get_available_migrations()
        
        return [m for m in available if m not in applied]
    
    def apply_migration(self, migration_name):
        """تطبيق ترحيل معين
        
        Args:
            migration_name (str): اسم الترحيل
            
        Returns:
            bool: True إذا تم تطبيق الترحيل بنجاح
        """
        # التحقق من وجود ملف الترحيل
        migration_path = os.path.join(self.migrations_dir, f"{migration_name}.py")
        if not os.path.exists(migration_path):
            print(f"خطأ: ملف الترحيل {migration_path} غير موجود")
            return False
        
        # تحميل وتنفيذ الترحيل
        try:
            # تحميل الوحدة ديناميكيًا
            spec = importlib.util.spec_from_file_location(migration_name, migration_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # تنفيذ دالة الترحيل
            if hasattr(module, 'upgrade'):
                conn = sqlite3.connect(self.db_path)
                module.upgrade(conn)
                
                # تسجيل الترحيل كمطبق
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO {self.migrations_table} (migration_name) VALUES (?)", (migration_name,))
                
                conn.commit()
                conn.close()
                print(f"تم تطبيق الترحيل: {migration_name}")
                return True
            else:
                print(f"خطأ: الترحيل {migration_name} لا يحتوي على دالة upgrade()")
                return False
        except Exception as e:
            print(f"خطأ أثناء تطبيق الترحيل {migration_name}: {str(e)}")
            return False
    
    def apply_all_pending_migrations(self):
        """تطبيق جميع الترحيلات المعلقة
        
        Returns:
            int: عدد الترحيلات التي تم تطبيقها
        """
        pending = self.get_pending_migrations()
        applied_count = 0
        
        for migration in pending:
            if self.apply_migration(migration):
                applied_count += 1
        
        return applied_count
    
    def create_migration(self, name):
        """إنشاء ملف ترحيل جديد
        
        Args:
            name (str): اسم الترحيل
            
        Returns:
            str: مسار ملف الترحيل الذي تم إنشاؤه
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # إنشاء قالب ملف الترحيل
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('''
# ترحيل قاعدة البيانات

def upgrade(conn):
    """تطبيق الترحيل
    
    Args:
        conn: اتصال قاعدة البيانات
    """
    cursor = conn.cursor()
    
    # كتابة عمليات الترحيل هنا
    # مثال:
    # cursor.execute("""ALTER TABLE users ADD COLUMN new_column TEXT""")
    
    conn.commit()

def downgrade(conn):
    """التراجع عن الترحيل
    
    Args:
        conn: اتصال قاعدة البيانات
    """
    cursor = conn.cursor()
    
    # كتابة عمليات التراجع هنا
    # مثال:
    # cursor.execute("""ALTER TABLE users DROP COLUMN new_column""")
    
    conn.commit()
''')
        
        print(f"تم إنشاء ملف الترحيل: {filepath}")
        return filepath

# استخدام الفئة
def run_migrations():
    """تشغيل جميع الترحيلات المعلقة"""
    manager = MigrationManager()
    count = manager.apply_all_pending_migrations()
    print(f"تم تطبيق {count} ترحيلات")

def create_new_migration(name):
    """إنشاء ملف ترحيل جديد
    
    Args:
        name (str): اسم الترحيل
    """
    manager = MigrationManager()
    manager.create_migration(name)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'run':
            run_migrations()
        elif command == 'create' and len(sys.argv) > 2:
            create_new_migration(sys.argv[2])
        else:
            print("الاستخدام:")
            print("  python migration_manager.py run - تطبيق جميع الترحيلات المعلقة")
            print("  python migration_manager.py create NAME - إنشاء ملف ترحيل جديد")
    else:
        print("الاستخدام:")
        print("  python migration_manager.py run - تطبيق جميع الترحيلات المعلقة")
        print("  python migration_manager.py create NAME - إنشاء ملف ترحيل جديد")