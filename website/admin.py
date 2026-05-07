from django.contrib import admin
from .models import Application, News, HeroSlide, Feature, AboutInfo, CoreValue, ContactInfo


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'subtitle']
    ordering = ['order', 'created_at']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['child_full_name', 'grade_applying_for', 'parent_full_name', 'parent_mobile', 'status', 'submitted_at']
    list_filter = ['status', 'grade_applying_for', 'submitted_at']
    search_fields = ['child_first_name', 'child_last_name', 'parent_full_name', 'parent_mobile', 'parent_email']
    readonly_fields = ['submitted_at', 'updated_at']
    date_hierarchy = 'submitted_at'

    def child_full_name(self, obj):
        return f"{obj.child_first_name} {obj.child_last_name}"
    child_full_name.short_description = "Child Name"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'published_at']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'content']
    list_editable = ['is_published']
    date_hierarchy = 'published_at'


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order']


@admin.register(AboutInfo)
class AboutInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('About Paragraphs', {
            'fields': ('about_paragraph_1', 'about_paragraph_2', 'about_paragraph_3', 'about_paragraph_4')
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision')
        }),
        ('Statistics', {
            'fields': ('stat_pupils', 'stat_teachers', 'stat_years')
        }),
    )


@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Address & Location', {
            'fields': ('address', 'google_maps_url')
        }),
        ('Phone', {
            'fields': ('phone_1', 'phone_2', 'whatsapp')
        }),
        ('Email', {
            'fields': ('email_1', 'email_2')
        }),
        ('Office Hours', {
            'fields': ('office_hours', 'saturday_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_url')
        }),
    )
