from django.contrib import admin
from .models import BehaviorRecord, Achievement

@admin.register(BehaviorRecord)
class BehaviorRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'behavior_type', 'date', 'reported_by', 'resolved')
    list_filter = ('behavior_type', 'resolved', 'date')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'date_awarded')
    list_filter = ('date_awarded',)