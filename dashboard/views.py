from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from students.models import Student
from academics.models import ClassLevel, Result, Attendance, Assignment, Timetable
from staff.models import Teacher
from finance.models import Payment, FeeStructure
from behavior.models import BehaviorRecord, Achievement
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import json
from core.models import AcademicYear


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse('dashboard:home')

@login_required
def home_page(request):
    return redirect('dashboard:redirect')

@login_required
def home_redirect(request):
    user = request.user
    if user.groups.filter(name='Parent').exists():
        return redirect('dashboard:parent')
    elif user.groups.filter(name='Teacher').exists():
        return redirect('dashboard:teacher')
    elif user.groups.filter(name='Accountant').exists():
        return redirect('finance:accountant_dashboard')
    elif user.is_superuser or user.groups.filter(name__in=['Admin','Owner']).exists():
        return redirect('dashboard:admin_home')
    else:
        return redirect('dashboard:home')

@login_required
def accountant_home(request):
    return redirect('finance:accountant_dashboard')

# ====== ADMIN / OWNER DASHBOARD ======
@login_required
def admin_home(request):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin","Owner"]).exists()):
        return redirect('dashboard:redirect')
    
    today = datetime.now()
    this_month = today.replace(day=1)
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Key Stats
    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_classes = ClassLevel.objects.count()
    total_parents = Student.objects.filter(parent_user__isnull=False).values('parent_user').distinct().count()
    
    # Finance
    total_revenue = Payment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    monthly_revenue = Payment.objects.filter(payment_date__gte=this_month).aggregate(total=Sum('amount_paid'))['total'] or 0
    today_revenue = Payment.objects.filter(payment_date=today.date()).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Monthly income chart data
    monthly_data = []
    month_labels = []
    for m in range(1, today.month + 1):
        month_start = today.replace(day=1, month=m)
        if m == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=m + 1)
        total = Payment.objects.filter(payment_date__gte=month_start, payment_date__lt=month_end).aggregate(total=Sum('amount_paid'))['total'] or 0
        monthly_data.append(float(total))
        month_labels.append(month_start.strftime('%b'))
    
    # Revenue by category
    cat_agg = {}
    for fs in FeeStructure.objects.select_related('fee_category').all():
        name = fs.fee_category.name if fs.fee_category else 'General'
        cat_agg[name] = cat_agg.get(name, 0) + float(fs.amount or 0)
    cat_labels = list(cat_agg.keys())
    cat_data = list(cat_agg.values())
    if not cat_data:
        cat_labels = ['No Data']
        cat_data = [0]
    
    # Class distribution
    class_dist = []
    class_labels = []
    for cls in ClassLevel.objects.all():
        count = Student.objects.filter(current_class=cls, is_active=True).count()
        if count > 0:
            class_labels.append(cls.name)
            class_dist.append(count)
    
    # Recent activity
    recent_payments = Payment.objects.select_related('student', 'fee_category').order_by('-payment_date')[:5]
    recent_results = Result.objects.select_related('student', 'subject', 'exam').order_by('-exam__date')[:5]
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_parents': total_parents,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'today_revenue': today_revenue,
        'monthly_data': json.dumps(monthly_data),
        'month_labels': json.dumps(month_labels),
        'cat_data': json.dumps(cat_data),
        'cat_labels': json.dumps(cat_labels),
        'class_dist': json.dumps(class_dist),
        'class_labels': json.dumps(class_labels),
        'recent_payments': recent_payments,
        'recent_results': recent_results,
        'is_owner': request.user.groups.filter(name='Owner').exists(),
    }
    return render(request, 'dashboard/admin_home.html', context)

# ====== TEACHER DASHBOARD ======
@login_required
def teacher_home(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    classes = teacher.classes.all() if teacher else []
    
    class_count = classes.count()
    student_count = Student.objects.filter(current_class__in=classes, is_active=True).count() if classes else 0
    
    today_weekday = datetime.now().weekday()
    today_timetable = Timetable.objects.filter(teacher=teacher, day_of_week=today_weekday).select_related('class_level', 'subject') if teacher else []
    
    today_results = Result.objects.filter(student__current_class__in=classes).select_related('student', 'subject', 'exam').order_by('-exam__term__academic_year__name')[:15] if classes else []
    
    # My classes stats
    recent_results_count = Result.objects.filter(student__current_class__in=classes).count() if classes else 0
    
    # Upcoming assignments
    upcoming_assignments = Assignment.objects.filter(
        class_level__in=classes,
        due_date__gte=datetime.now()
    ).order_by('due_date')[:5] if classes else []
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'class_count': class_count,
        'student_count': student_count,
        'today_timetable': today_timetable,
        'today_weekday': today_weekday,
        'recent_results': today_results,
        'recent_results_count': recent_results_count,
        'upcoming_assignments': upcoming_assignments,
    }
    return render(request, 'dashboard/teacher.html', context)

# ====== PARENT HELPERS ======
def has_outstanding_balance(student):
    from finance.models import FeeStructure
    from django.db.models import Sum
    total_paid = Payment.objects.filter(student=student).aggregate(total=Sum('amount_paid'))['total'] or 0
    expected = FeeStructure.objects.filter(class_level=student.current_class).aggregate(total=Sum('amount'))['total'] or 0
    balance = max(0, expected - total_paid)
    return balance > 0, balance, expected, total_paid

def check_parent_blocked(request, students, student):
    """Returns (is_blocked, context) if blocked, else (False, None)"""
    is_blocked, balance, expected, paid = has_outstanding_balance(student)
    if is_blocked:
        blocked_students = []
        for s in students:
            b_blocked, b_bal, b_exp, b_paid = has_outstanding_balance(s)
            if b_blocked:
                blocked_students.append({'student': s, 'balance': b_bal, 'expected': b_exp, 'paid': b_paid})
        context = {
            'students': students,
            'student': student,
            'blocked': True,
            'balance': balance,
            'expected': expected,
            'paid': paid,
            'blocked_students': blocked_students,
        }
        return True, context
    return False, None

def get_parent_student(request):
    students = Student.objects.filter(parent_user=request.user)
    if not students.exists():
        return None, None
    student_id = request.GET.get('student_id')
    if student_id:
        try:
            student = students.get(pk=student_id)
        except Student.DoesNotExist:
            student = students.first()
    else:
        student = students.first()
    return students, student

# ====== PARENT DASHBOARD ======
@login_required
def parent_home(request):
    students = Student.objects.filter(parent_user=request.user)
    if not students.exists():
        return render(request, 'dashboard/no_student.html', {
            'message': 'No student linked to your account. Please contact the school.'
        })
    
    # Check outstanding for all
    blocked_students = []
    for s in students:
        total_paid = Payment.objects.filter(student=s).aggregate(total=Sum('amount_paid'))['total'] or 0
        expected = FeeStructure.objects.filter(class_level=s.current_class).aggregate(total=Sum('amount'))['total'] or 0
        balance = max(0, expected - total_paid)
        if balance > 0:
            blocked_students.append({'student': s, 'balance': balance, 'expected': expected, 'paid': total_paid})
    has_outstanding = len(blocked_students) > 0
    
    student_id = request.GET.get('student_id')
    if student_id:
        try:
            student = students.get(pk=student_id)
        except Student.DoesNotExist:
            student = students.first()
    else:
        student = students.first()
    
    this_paid = Payment.objects.filter(student=student).aggregate(total=Sum('amount_paid'))['total'] or 0
    this_expected = FeeStructure.objects.filter(class_level=student.current_class).aggregate(total=Sum('amount'))['total'] or 0
    this_balance = max(0, this_expected - this_paid)
    student_blocked = this_balance > 0
    
    if student_blocked:
        context = {
            'students': students,
            'student': student,
            'blocked': True,
            'balance': this_balance,
            'expected': this_expected,
            'paid': this_paid,
            'has_outstanding': has_outstanding,
            'blocked_students': blocked_students,
        }
        return render(request, 'dashboard/parent_blocked.html', context)
    
    results = Result.objects.filter(student=student).select_related('exam', 'subject')
    payments = Payment.objects.filter(student=student)
    behavior = BehaviorRecord.objects.filter(student=student).order_by('-date')
    attendance_qs = Attendance.objects.filter(student=student)
    attendance = attendance_qs[:14]
    present = attendance_qs.filter(status='P').count()
    absent = attendance_qs.filter(status='A').count()
    late = attendance_qs.filter(status='L').count()
    assignments = Assignment.objects.filter(class_level=student.current_class)[:5]
    achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')[:10]
    
    # Only current year for overview
    current_year = AcademicYear.objects.filter(is_current=True).first()
    current_results = results.filter(exam__term__academic_year=current_year) if current_year else results
    progress_current = {}
    for r in current_results.select_related('exam__term__academic_year'):
        term = r.exam.term.name
        if term not in progress_current:
            progress_current[term] = []
        progress_current[term].append(r)
    
    timetable = Timetable.objects.filter(class_level=student.current_class, academic_year=current_year).select_related('subject', 'teacher').order_by('day_of_week', 'period')[:30] if current_year and student.current_class else []
    assignment_list = Assignment.objects.filter(class_level=student.current_class, due_date__gte=datetime.now())[:10] if student.current_class else []
    total_paid = this_paid
    balance = this_balance
    
    # Chart data
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    payment_by_month = []
    for m in range(1, 13):
        total = Payment.objects.filter(student=student, payment_date__month=m).aggregate(total=Sum('amount_paid'))['total'] or 0
        payment_by_month.append(float(total))
    
    context = {
        'students': students,
        'student': student,
        'results': results,
        'payments': payments,
        'behavior': behavior,
        'attendance': attendance,
        'assignments': assignments,
        'assignment_list': assignment_list,
        'timetable': timetable,
        'achievements': achievements,
        'total_paid': total_paid,
        'expected_fee': this_expected,
        'balance': balance,
        'progress_current': progress_current,
        'payment_receipts': [p.receipt_number for p in payments],
        'payment_by_month': json.dumps(payment_by_month),
        'month_labels': json.dumps(month_labels),
        'present': present,
        'absent': absent,
        'late': late,
    }
    return render(request, 'dashboard/parent.html', context)

# ====== PARENT SUB-VIEWS ======
@login_required
def parent_progress(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    from behavior.models import Achievement
    achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')[:10]
    results = Result.objects.filter(student=student).select_related('exam__term__academic_year', 'subject')
    payments = Payment.objects.filter(student=student)
    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    expected_fee = FeeStructure.objects.filter(class_level=student.current_class).aggregate(total=Sum('amount'))['total'] or 0
    balance = max(0, expected_fee - total_paid)
    progress_current = {}
    for r in results:
        yr = r.exam.term.academic_year.name
        if yr not in progress_current:
            progress_current[yr] = {}
        term = r.exam.term.name
        if term not in progress_current[yr]:
            progress_current[yr][term] = []
        progress_current[yr][term].append(r)
    context = {
        'students': students,
        'student': student,
        'progress_current': progress_current,
        'total_paid': total_paid,
        'expected_fee': expected_fee,
        'balance': balance,
        'achievements': achievements,
    }
    return render(request, 'dashboard/parent_progress.html', context)

@login_required
def parent_payments(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    payments = Payment.objects.filter(student=student).order_by('-payment_date')
    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    expected_fee = FeeStructure.objects.filter(class_level=student.current_class).aggregate(total=Sum('amount'))['total'] or 0
    balance = max(0, expected_fee - total_paid)
    context = {
        'students': students,
        'student': student,
        'payments': payments,
        'total_paid': total_paid,
        'expected_fee': expected_fee,
        'balance': balance,
    }
    return render(request, 'dashboard/parent_payments.html', context)

@login_required
def parent_behavior(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    behavior = BehaviorRecord.objects.filter(student=student).order_by('-date')
    context = {'students': students, 'student': student, 'behavior': behavior}
    return render(request, 'dashboard/parent_behavior.html', context)

@login_required
def parent_attendance(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    attendance = Attendance.objects.filter(student=student).order_by('-date')
    context = {'students': students, 'student': student, 'attendance': attendance}
    return render(request, 'dashboard/parent_attendance.html', context)

@login_required
def parent_timetable(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    current_year = AcademicYear.objects.filter(is_current=True).first()
    from django.db.models import Q
    assignment_list = Assignment.objects.filter(class_level=student.current_class).filter(Q(due_date__gte=datetime.now()) | Q(due_date__isnull=True))[:10]
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    timetable = Timetable.objects.filter(class_level=student.current_class, academic_year=current_year).select_related('subject', 'teacher').order_by('day_of_week', 'period')[:30] if current_year and student.current_class else []
    max_period = max([t.period for t in timetable]) if timetable else 6
    timetable_grid = []
    for p in range(1, max_period + 1):
        row = []
        for d in range(5):
            entries = [t for t in timetable if t.period == p and t.day_of_week == d]
            row.append(entries)
        timetable_grid.append(row)
    context = {
        'students': students,
        'student': student,
        'timetable_grid': timetable_grid,
        'max_period': max_period,
        'weekdays': weekdays[:5],
        'assignments': assignment_list,
    }
    return render(request, 'dashboard/parent_timetable.html', context)

@login_required
def parent_achievements(request):
    students, student = get_parent_student(request)
    if not student:
        return render(request, 'dashboard/no_student.html', {'message': 'No student linked to your account.'})
    is_blocked, block_ctx = check_parent_blocked(request, students, student)
    if is_blocked:
        return render(request, 'dashboard/parent_blocked.html', block_ctx)
    achievements = Achievement.objects.filter(student=student).order_by('-date_awarded')
    context = {'students': students, 'student': student, 'achievements': achievements}
    return render(request, 'dashboard/parent_achievements.html', context)
