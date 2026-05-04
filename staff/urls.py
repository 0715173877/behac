# staff/urls.py
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.TeacherListView.as_view(), name='teacher_list'),
    path('add/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_update'),
    path('<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='teacher_delete'),
    path('<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
        path('<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('<int:teacher_id>/salary/add/', views.add_salary_payment, name='add_salary_payment'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/reset-password/', views.reset_user_password, name='reset_password'),
    path('users/<int:pk>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('users/<int:pk>/groups/', views.change_user_groups, name='change_user_groups'),
    path('users/create/', views.create_user, name='create_user'),
]