from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='website_home'),
    path('about/', views.about, name='website_about'),
    path('apply/', views.apply, name='website_apply'),
    path('apply/success/', views.apply_success, name='website_apply_success'),
    path('news/', views.news_list, name='website_news'),
    path('news/<int:pk>/', views.news_detail, name='website_news_detail'),
    path('contact/', views.contact, name='website_contact'),
]
