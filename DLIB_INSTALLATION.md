# حل مشكلة استيراد مكتبة dlib

هذا الملف يحتوي على تعليمات لحل مشكلة استيراد مكتبة dlib في نظام Windows. المشكلة الشائعة هي الخطأ التالي:

```
from _dlib_pybind11 import * 
ImportError: DLL load failed while importing _dlib_pybind11: The specified module could not be found.
```

هذا الخطأ يحدث عادة بسبب:
1. عدم وجود مكتبات Visual C++ Redistributable المطلوبة
2. عدم تثبيت مكتبة dlib بشكل صحيح للإصدار المناسب من Python
3. عدم قدرة Python على العثور على ملفات DLL المطلوبة

## الحلول المقترحة

### 1. تثبيت Visual C++ Redistributable

مكتبة dlib تعتمد على مكتبات Visual C++ Redistributable. تأكد من تثبيت أحدث إصدار من Visual C++ Redistributable:

- قم بتنزيل وتثبيت [Visual C++ Redistributable for Visual Studio 2022](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### 2. استخراج ملفات DLL من حزمة dlib

قمنا بإنشاء سكربت لاستخراج ملفات DLL من حزمة dlib wheel المناسبة لإصدار Python الخاص بك:

1. قم بتشغيل ملف `extract_dlib_dlls.bat` بالنقر المزدوج عليه
2. سيقوم السكربت بإنشاء مجلد `dll_files` واستخراج ملفات DLL اللازمة إليه
3. بعد الانتهاء، يمكنك تشغيل ملف `test_dlib_import.bat` للتحقق من إمكانية استيراد dlib

### 3. إعادة تثبيت dlib باستخدام ملف .whl المناسب

إذا لم تنجح الطرق السابقة، يمكنك إعادة تثبيت dlib باستخدام ملف .whl المخصص لإصدار Python الخاص بك. تم التأكد من أن المشروع يستخدم Python 3.13.2، لذلك يجب استخدام الملف المناسب:

1. قم بإلغاء تثبيت dlib الحالي (إن وجد):
   ```
   pip uninstall dlib -y
   ```

2. قم بتثبيت dlib باستخدام ملف .whl المناسب لإصدار Python 3.13:
   ```
   pip install "d:\Ai  authen unauthen 0.1\dlib-whl-20.0.0-alpha\dlib-20.0.0-cp313-cp313-win_amd64.whl"
   ```

ملاحظة: إذا كنت تستخدم إصدارًا مختلفًا من Python، فاستخدم ملف .whl المناسب من المجلد `dlib-whl-20.0.0-alpha`.

### 4. إضافة مسار DLL إلى متغيرات البيئة

يمكنك إضافة مسار مجلد `dll_files` إلى متغير البيئة PATH بشكل دائم:

1. افتح PowerShell كمسؤول
2. قم بتنفيذ الأمر التالي (بعد تعديل المسار حسب موقع المشروع لديك):

```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;D:/Ai  authen unauthen 0.1/dll_files", "Machine")
```

### 5. تعديل الكود لإضافة مسار DLL

بدلاً من تعديل متغيرات البيئة، يمكنك إضافة الكود التالي في بداية البرنامج الرئيسي (`run.py`):

```python
import os
import sys

# إضافة مسار ملفات DLL
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dll_files')
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
```

## استكشاف الأخطاء وإصلاحها

إذا استمرت المشكلة، جرب الخطوات التالية:

1. تحقق من إصدار Python المستخدم وتأكد من استخدام ملف .whl المناسب
2. تأكد من تثبيت جميع التبعيات المطلوبة في ملف `requirements.txt`
3. جرب استخدام إصدار أقدم من Python (مثل 3.10 أو 3.11) حيث قد يكون لديها توافق أفضل مع dlib
4. تحقق من وجود ملف `shape_predictor_68_face_landmarks.dat` في المجلد الرئيسي للمشروع

## ملاحظات إضافية

- إذا كنت تستخدم بيئة افتراضية، تأكد من تنشيطها قبل تثبيت أو استخدام dlib
- تأكد من استخدام نسخة 64-bit من Python، حيث أن dlib لا يدعم نسخة 32-bit
- إذا كنت تستخدم CUDA، راجع ملف README.md في مجلد `dlib-whl-20.0.0-alpha` للحصول على تعليمات إضافية