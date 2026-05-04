from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Results
    path('results/', views.ResultListView.as_view(), name='result_list'),
    path('results/add/', views.ResultCreateView.as_view(), name='result_create'),
    path('results/bulk-upload/', views.ResultBulkUploadView.as_view(), name='result_bulk_upload'),
    path('results/download-template/', views.download_excel_template, name='result_download_template'),
    path('results/<int:pk>/edit/', views.ResultUpdateView.as_view(), name='result_update'),
    path('results/<int:pk>/delete/', views.ResultDeleteView.as_view(), name='result_delete'),
    
    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/add/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    
    # Assignments
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/add/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_update'),
    path('assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    
    # Exams
    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('exams/add/', views.ExamCreateView.as_view(), name='exam_create'),
    path('exams/<int:pk>/edit/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('exams/<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),
    
    # Timetables
    path('timetables/', views.TimetableListView.as_view(), name='timetable_list'),
    path('timetables/add/', views.TimetableCreateView.as_view(), name='timetable_create'),
    path('timetables/<int:pk>/edit/', views.TimetableUpdateView.as_view(), name='timetable_update'),
    path('timetables/<int:pk>/delete/', views.TimetableDeleteView.as_view(), name='timetable_delete'),
    
    # Subjects & ClassLevels (read-only lists)
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('classes/', views.ClassLevelListView.as_view(), name='classlevel_list'),
]