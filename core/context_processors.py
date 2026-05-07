from .models import SchoolInfo

def school_info_processor(request):
    school_info = SchoolInfo.objects.first()
    return {
        'school_info': school_info,
    }
