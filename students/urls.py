from django.urls import path
from . import views

app_name = 'students'
urlpatterns = [
    path('', views.StudentListView.as_view(), name='list'),
    path('add/', views.StudentCreateView.as_view(), name='create'),
     path('bulk-upload/', views.StudentBulkUploadView.as_view(), name='bulk_upload'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='delete'),
    path('download-template/', views.download_excel_template, name='download_template'),
]