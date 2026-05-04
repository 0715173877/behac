from core.models import AcademicYear

def academic_year_processor(request):
    current_year = AcademicYear.objects.filter(is_current=True).first()
    all_years = AcademicYear.objects.all().order_by('-start_date')
    return {
        'current_year': current_year,
        'all_years': all_years,
    }
