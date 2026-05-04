from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),
    path('finance/', include('finance.urls')),
    path('teachers/', include('staff.urls')),
    path('behavior/', include('behavior.urls')),
    path('core/', include('core.urls')),
    path('', dashboard_views.home_page, name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
]

# For serving static/media in development only
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)