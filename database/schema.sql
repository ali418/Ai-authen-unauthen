-- مخطط قاعدة البيانات لنظام التعرف على الوجوه
-- يتم إنشاء هذه الجداول تلقائيًا بواسطة SQLAlchemy عند تشغيل التطبيق
-- هذا الملف للتوثيق فقط

-- جدول المستخدمين
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(200),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول صور الوجوه
CREATE TABLE IF NOT EXISTS face_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_data BLOB,
    embedding_data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- جدول سجلات الدخول
CREATE TABLE IF NOT EXISTS access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_granted BOOLEAN DEFAULT 0,
    confidence FLOAT,
    image_data BLOB,
    notes VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- إنشاء مستخدم مسؤول افتراضي
INSERT OR IGNORE INTO users (name, email, role, password_hash, is_active)
VALUES ('Admin', 'admin@example.com', 'admin', 'pbkdf2:sha256:150000$HASHED_PASSWORD', 1);

-- إنشاء فهارس للتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_face_images_user_id ON face_images (user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs (timestamp);