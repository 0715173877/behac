from django.contrib import admin
from .models import Teacher, OtherStaff, SalaryPayment
from django.contrib.contenttypes.admin import GenericTabularInline

class SalaryPaymentInline(GenericTabularInline):
    model = SalaryPayment
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'phone', 'base_salary', 'is_active')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')
    list_filter = ('is_active',)
    filter_horizontal = ('subjects', 'classes')
    inlines = [SalaryPaymentInline]

@admin.register(OtherStaff)
class OtherStaffAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'role', 'base_salary', 'is_active')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')
    list_filter = ('department', 'is_active')
    inlines = [SalaryPaymentInline]

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('staff_member', 'amount', 'month', 'paid_date')
    list_filter = ('month',)
    search_fields = ('object_id',)