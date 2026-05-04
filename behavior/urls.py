from django.urls import path
from . import views

app_name = 'behavior'

urlpatterns = [
    path('records/', views.BehaviorRecordListView.as_view(), name='behavior_list'),
    path('records/add/', views.BehaviorRecordCreateView.as_view(), name='behavior_create'),
    path('records/<int:pk>/', views.BehaviorRecordDetailView.as_view(), name='behavior_detail'),
    path('records/<int:pk>/edit/', views.BehaviorRecordUpdateView.as_view(), name='behavior_update'),
    path('records/<int:pk>/delete/', views.BehaviorRecordDeleteView.as_view(), name='behavior_delete'),
    path('achievements/', views.AchievementListView.as_view(), name='achievement_list'),
    path('achievements/add/', views.AchievementCreateView.as_view(), name='achievement_create'),
    path('achievements/<int:pk>/', views.AchievementDetailView.as_view(), name='achievement_detail'),
    path('achievements/<int:pk>/edit/', views.AchievementUpdateView.as_view(), name='achievement_update'),
    path('achievements/<int:pk>/delete/', views.AchievementDeleteView.as_view(), name='achievement_delete'),
]