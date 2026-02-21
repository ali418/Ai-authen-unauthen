# وحدة التحكم في الأبواب
# تستخدم هذه الوحدة للتحكم في فتح وإغلاق الأبواب باستخدام GPIO

from .relay import DoorRelay

# إنشاء كائن للتحكم في الباب يمكن استخدامه من الخارج
door_relay = DoorRelay()

def open_door():
    """فتح الباب لمدة محددة في الإعدادات"""
    return door_relay.activate()

def close_door():
    """إغلاق الباب"""
    return door_relay.deactivate()

def is_door_open():
    """التحقق مما إذا كان الباب مفتوحًا"""
    return door_relay.is_active()