# ترحيل قاعدة البيانات الأولي
# يقوم هذا الترحيل بإنشاء الهيكل الأساسي لقاعدة البيانات

def upgrade(conn):
    """تطبيق الترحيل
    
    Args:
        conn: اتصال قاعدة البيانات
    """
    cursor = conn.cursor()
    
    # إنشاء جدول المستخدمين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE,
        password_hash VARCHAR(200),
        role VARCHAR(20) DEFAULT 'user',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # إنشاء جدول صور الوجوه
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        image_data BLOB,
        embedding_data BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # إنشاء جدول سجلات الدخول
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        access_granted BOOLEAN DEFAULT 0,
        confidence FLOAT,
        image_data BLOB,
        notes VARCHAR(200),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    )
    ''')
    
    # إنشاء فهارس للتحسين الأداء
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_face_images_user_id ON face_images (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs (timestamp)')
    
    # إنشاء مستخدم مسؤول افتراضي
    cursor.execute('''
    INSERT OR IGNORE INTO users (name, email, role, password_hash, is_active)
    SELECT 'Admin', 'admin@example.com', 'admin', 'pbkdf2:sha256:150000$HASHED_PASSWORD', 1
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com')
    ''')
    
    conn.commit()

def downgrade(conn):
    """التراجع عن الترحيل
    
    Args:
        conn: اتصال قاعدة البيانات
    """
    cursor = conn.cursor()
    
    # حذف الجداول بترتيب عكسي لتجنب مشاكل المفاتيح الأجنبية
    cursor.execute('DROP TABLE IF EXISTS access_logs')
    cursor.execute('DROP TABLE IF EXISTS face_images')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    conn.commit()