from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("academic-years/", views.AcademicYearListView.as_view(), name="academic_year_list"),
    path("academic-years/add/", views.AcademicYearCreateView.as_view(), name="academic_year_create"),
    path("academic-years/<int:pk>/edit/", views.AcademicYearUpdateView.as_view(), name="academic_year_update"),
    path("academic-years/<int:pk>/delete/", views.AcademicYearDeleteView.as_view(), name="academic_year_delete"),
    path("academic-years/<int:pk>/activate/", views.activate_academic_year, name="activate_academic_year"),

    # Term URLs
    path("terms/", views.TermListView.as_view(), name="term_list"),
    path("terms/add/", views.TermCreateView.as_view(), name="term_create"),
    path("terms/<int:pk>/edit/", views.TermUpdateView.as_view(), name="term_update"),
    path("terms/<int:pk>/delete/", views.TermDeleteView.as_view(), name="term_delete"),
]
