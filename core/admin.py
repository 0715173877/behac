from django.contrib import admin
from .models import SchoolInfo, AcademicYear, Term

@admin.register(SchoolInfo)
class SchoolInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'motto', 'tagline', 'primary_dark', 'primary_light', 'primary_bg')
    fieldsets = (
        (None, {
            'fields': ('name', 'motto', 'tagline', 'logo', 'portal_name', 'hero_image')
        }),
        ('Color Scheme', {
            'fields': ('primary_dark', 'primary_light', 'primary_bg'),
            'description': 'Customize the school portal colors. Use hex codes (e.g. #1B5E20).'
        }),

    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_editable = ('is_current',)
    list_filter = ('is_current',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'is_active')
    list_filter = ('academic_year', 'is_active')
