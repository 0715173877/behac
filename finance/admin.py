from django.contrib import admin
from .models import FeeCategory, FeeStructure, Payment

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'is_recurring')
    list_editable = ('default_amount', 'is_recurring')

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'academic_year', 'fee_category', 'amount')
    list_filter = ('class_level', 'academic_year', 'fee_category')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_category', 'amount_paid', 'payment_date', 'receipt_number')
    list_filter = ('payment_date', 'fee_category')
    search_fields = ('student__first_name', 'student__last_name', 'receipt_number')
    date_hierarchy = 'payment_date'