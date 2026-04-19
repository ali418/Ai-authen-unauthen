#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ملف تشغيل تطبيق التعرف على الوجوه
Run script for Face Recognition Application
"""

import sys
import os
import io

# Fix Unicode encoding for Arabic text on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# إضافة المجلد الرئيسي إلى مسار البحث
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# طباعة مسار البحث للتشخيص
print("Python search path:")
for path in sys.path:
    print(f"  - {path}")

# استيراد وتشغيل التطبيق
from backend.app import app

if __name__ == "__main__":
    # طباعة عنوان الخادم
    host = '0.0.0.0'  # استمع على جميع الواجهات
    port = 5000
    print(f"\nStarting server at http://localhost:{port}")
    print(f"You can also access it at http://{host}:{port} from other devices on the same network")
    
    # تشغيل التطبيق
    app.run(host=host, port=port, debug=True)