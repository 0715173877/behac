from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('redirect/', views.home_redirect, name='redirect'),
    path('parent/', views.parent_home, name='parent'),
    path('parent/progress/', views.parent_progress, name='parent_progress'),
    path('parent/payments/', views.parent_payments, name='parent_payments'),
    path('parent/behavior/', views.parent_behavior, name='parent_behavior'),
    path('parent/attendance/', views.parent_attendance, name='parent_attendance'),
    path('parent/achievements/', views.parent_achievements, name='parent_achievements'),
    path('parent/timetable/', views.parent_timetable, name='parent_timetable'),
    path('teacher/', views.teacher_home, name='teacher'),
    path('accountant/', views.accountant_home, name='accountant'),
    path('internal/', views.admin_home, name='admin_home'),   # new
]