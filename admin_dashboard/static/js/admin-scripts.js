/**
 * ملف JavaScript الرئيسي للوحة تحكم المسؤول
 */

document.addEventListener('DOMContentLoaded', function() {
    // إخفاء رسائل التنبيه تلقائيًا بعد 5 ثوانٍ
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // تفعيل tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تفعيل popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // تأكيد الحذف
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete-form');
    confirmDeleteForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('هل أنت متأكد من حذف هذا العنصر؟ هذا الإجراء لا يمكن التراجع عنه.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
    
    // تفعيل تحديد التاريخ في نماذج التصفية
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // تعيين التاريخ الافتراضي إذا لم يكن محددًا
        if (input.id === 'date_from' && !input.value) {
            const lastMonth = new Date();
            lastMonth.setMonth(lastMonth.getMonth() - 1);
            input.valueAsDate = lastMonth;
        }
        
        if (input.id === 'date_to' && !input.value) {
            input.valueAsDate = new Date();
        }
    });
});