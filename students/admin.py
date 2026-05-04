from django.contrib import admin
from .models import Relationship, Student, OtherRelative

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'gender', 'current_class')
    list_filter = ('gender', 'current_class')
    search_fields = ('first_name', 'last_name')

@admin.register(OtherRelative)
class OtherRelativeAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'relationship', 'mobile')
    list_filter = ('relationship',)
    
@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')