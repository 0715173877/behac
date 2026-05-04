from django.urls import path
from . import views

app_name = 'finance'
urlpatterns = [
    # Accountant Dashboard
    path('dashboard/', views.AccountantDashboardView.as_view(), name='accountant_dashboard'),
    path('select-student/', views.select_student_for_payment, name='select_student'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
    path('payments/<int:pk>/receipt/', views.ReceiptView.as_view(), name='receipt'),
    path('payments/<int:pk>/receipt/pdf/', views.payment_receipt_pdf, name='receipt_pdf'),
    path('payments/bulk-upload/', views.PaymentBulkUploadView.as_view(), name='payment_bulk_upload'),
    path('payments/download-template/', views.download_payment_template, name='download_payment_template'),     
    
    # Reports
    path('reports/', views.payment_report, name='payment_report'),
    path('reports/export/', views.export_payments_excel, name='export_payments'),
    path('reports/outstanding/', views.outstanding_report, name='outstanding_report'),
    path('reports/outstanding/export/', views.export_outstanding_excel, name='export_outstanding'),

    # Fee Categories
    path('categories/', views.FeeCategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.FeeCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.FeeCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.FeeCategoryDeleteView.as_view(), name='category_delete'),
    
    # Fee Structures
    path('structures/', views.FeeStructureListView.as_view(), name='feestructure_list'),
    path('structures/add/', views.FeeStructureCreateView.as_view(), name='feestructure_create'),
    path('structures/<int:pk>/edit/', views.FeeStructureUpdateView.as_view(), name='feestructure_update'),
    path('structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='feestructure_delete'),
]