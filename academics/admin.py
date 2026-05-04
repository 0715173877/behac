from django.contrib import admin
from .models import ClassLevel, Subject, Exam, Result, Attendance, Assignment

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_type', 'order')
    list_editable = ('order',)
    list_filter = ('level_type',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    filter_horizontal = ('classes',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'max_marks', 'passing_marks')
    list_filter = ('term',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam', 'subject')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_level', 'due_date')
    list_filter = ('class_level', 'subject', 'due_date')