# وحدة قاعدة البيانات

توفر هذه الوحدة أدوات لإدارة قاعدة البيانات في نظام التعرف على الوجوه، بما في ذلك:

- إنشاء وتهيئة قاعدة البيانات
- إدارة ترحيلات قاعدة البيانات
- إنشاء واستعادة النسخ الاحتياطية
- تحسين أداء قاعدة البيانات

## هيكل الوحدة

```
database/
├── __init__.py                  # حزمة قاعدة البيانات
├── db_manager.py                # مدير قاعدة البيانات
├── schema.sql                   # مخطط قاعدة البيانات
├── backups/                     # مجلد النسخ الاحتياطية
└── migrations/                  # مجلد ترحيلات قاعدة البيانات
    ├── __init__.py
    ├── migration_manager.py     # مدير ترحيلات قاعدة البيانات
    └── 20230101000000_initial_schema.py  # ترحيل إنشاء الهيكل الأولي
```

## استخدام مدير قاعدة البيانات

### تهيئة قاعدة البيانات

```python
from database.db_manager import DBManager

manager = DBManager()
manager.initialize_database()
```

### تطبيق الترحيلات

```python
from database.db_manager import DBManager

manager = DBManager()
manager.run_migrations()
```

### إنشاء نسخة احتياطية

```python
from database.db_manager import DBManager

manager = DBManager()
backup_path = manager.create_backup()
print(f"تم إنشاء نسخة احتياطية في: {backup_path}")
```

### استعادة نسخة احتياطية

```python
from database.db_manager import DBManager

manager = DBManager()
manager.restore_backup('/path/to/backup.bak')
```

### الحصول على معلومات قاعدة البيانات

```python
from database.db_manager import DBManager

manager = DBManager()
info = manager.get_database_info()
print(f"حجم قاعدة البيانات: {info['size'] / 1024:.2f} كيلوبايت")
print(f"عدد الجداول: {len(info['tables'])}")
```

### تحسين أداء قاعدة البيانات

```python
from database.db_manager import DBManager

manager = DBManager()
manager.optimize_database()
```

## استخدام مدير الترحيلات

### إنشاء ترحيل جديد

```python
from database.migrations.migration_manager import MigrationManager

manager = MigrationManager()
manager.create_migration('add_new_column')
```

### تطبيق الترحيلات المعلقة

```python
from database.migrations.migration_manager import MigrationManager

manager = MigrationManager()
manager.apply_all_pending_migrations()
```

## استخدام سطر الأوامر

### مدير قاعدة البيانات

```bash
# تهيئة قاعدة البيانات
python database/db_manager.py init

# تطبيق الترحيلات
python database/db_manager.py migrate

# إنشاء نسخة احتياطية
python database/db_manager.py backup

# استعادة نسخة احتياطية
python database/db_manager.py restore /path/to/backup.bak

# عرض معلومات قاعدة البيانات
python database/db_manager.py info

# تحسين أداء قاعدة البيانات
python database/db_manager.py optimize
```

### مدير الترحيلات

```bash
# تطبيق الترحيلات المعلقة
python database/migrations/migration_manager.py run

# إنشاء ترحيل جديد
python database/migrations/migration_manager.py create add_new_column
```