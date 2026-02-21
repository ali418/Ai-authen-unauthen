# حزمة قاعدة البيانات
# توفر هذه الحزمة واجهة برمجة للتعامل مع قاعدة البيانات

from backend.database import Database
from backend.models import init_db

__all__ = ['Database', 'init_db']