from core.models import AcademicYear
from website.models import Application

def academic_year_processor(request):
    current_year = AcademicYear.objects.filter(is_current=True).first()
    all_years = AcademicYear.objects.all().order_by('-start_date')
    return {
        'current_year': current_year,
        'all_years': all_years,
    }

def pending_applications_processor(request):
    if request.user.is_authenticated and (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=['Admin', 'Owner']).exists()
    ):
        pending_count = Application.objects.filter(status='pending').count()
    else:
        pending_count = 0
    return {
        'pending_applications': pending_count,
    }
