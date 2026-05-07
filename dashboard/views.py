from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from students.models import Student
from academics.models import ClassLevel, Result, Attendance, Assignment, Timetable
from staff.models import Teacher
from finance.models import Payment, FeeStructure
from behavior.models import BehaviorRecord, Achievement
from django.urls import reverse, reverse_lazy
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
import json
from core.models import AcademicYear
from website.models import Application


# ====== HELP / USER GUIDE VIEWS ======
def _is_admin_or_owner(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Owner']).exists()

def _help_context(request, page_title, active_tab):
    """Return common context for help views including user groups."""
    return {
        'page_title': page_title,
        'active_tab': active_tab,
        'user_groups': list(request.user.groups.values_list('name', flat=True)),
    }

@login_required
def help_index(request):
    return render(request, 'help/index.html', _help_context(request, 'User Guide', 'overview'))

@login_required
def help_admin(request):
    if not _is_admin_or_owner(request.user):
        messages.warning(request, "You don't have access to that guide.")
        return redirect('dashboard:help_index')
    return render(request, 'help/admin_guide.html', _help_context(request, 'Admin / Owner Guide', 'admin'))

@login_required
def help_teacher(request):
    if not _is_admin_or_owner(request.user) and not request.user.groups.filter(name='Teacher').exists():
        messages.warning(request, "You don't have access to that guide.")
        return redirect('dashboard:help_index')
    return render(request, 'help/teacher_guide.html', _help_context(request, 'Teacher Guide', 'teacher'))

@login_required
def help_accountant(request):
    if not _is_admin_or_owner(request.user) and not request.user.groups.filter(name='Accountant').exists():
        messages.warning(request, "You don't have access to that guide.")
        return redirect('dashboard:help_index')
    return render(request, 'help/accountant_guide.html', _help_context(request, 'Accountant Guide', 'accountant'))

@login_required
def help_parent(request):
    if not _is_admin_or_owner(request.user) and not request.user.groups.filter(name='Parent').exists():
        messages.warning(request, "You don't have access to that guide.")
        return redirect('dashboard:help_index')
    return render(request, 'help/parent_guide.html', _help_context(request, 'Parent Guide', 'parent'))




class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse('dashboard:home')


class CustomLogoutView(LogoutView):
    """Custom logout view that redirects to login page."""
    next_page = reverse_lazy('login')


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
    elif user.is_superuser or user.groups.filter(name__in=['Admin', 'Owner']).exists():
        return redirect('dashboard:admin_home')
    else:
        return redirect('dashboard:home')


@login_required
def accountant_home(request):
    return redirect('finance:accountant_dashboard')


# ====== ADMIN / OWNER DASHBOARD ======
@login_required
def admin_home(request):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
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

    # Pending applications count
    pending_applications = Application.objects.filter(status='pending').count()
    request.session['pending_applications'] = pending_applications

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
        'pending_applications': pending_applications,
    }
    return render(request, 'dashboard/admin_home.html', context)


# ====== APPLICATION MANAGEMENT (Front-end) ======
@login_required
def application_list(request):
    """List all applications with approve/reject actions"""
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
        return redirect('dashboard:redirect')

    status_filter = request.GET.get('status', '')
    if status_filter in ['pending', 'approved', 'rejected']:
        applications = Application.objects.filter(status=status_filter).order_by('-submitted_at')
    else:
        applications = Application.objects.all().order_by('-submitted_at')

    context = {
        'applications': applications,
        'current_filter': status_filter,
        'pending_count': Application.objects.filter(status='pending').count(),
        'approved_count': Application.objects.filter(status='approved').count(),
        'rejected_count': Application.objects.filter(status='rejected').count(),
        'total_count': Application.objects.count(),
    }
    return render(request, 'dashboard/application_list.html', context)


@login_required
def application_detail(request, pk):
    """View a single application's details"""
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
        return redirect('dashboard:redirect')

    application = get_object_or_404(Application, pk=pk)
    context = {
        'app': application,
    }
    return render(request, 'dashboard/application_detail.html', context)


def _enroll_student_from_application(application):
    """Create Student record and parent User from an approved Application"""
    # 1. Create or get parent user account
    parent_email = application.parent_email.strip().lower()
    parent_username = parent_email

    parent_user = User.objects.filter(username=parent_username).first()
    if not parent_user:
        name_parts = application.parent_full_name.strip().split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        parent_user = User.objects.create_user(
            username=parent_username,
            email=parent_email,
            password='parent123',
            first_name=first_name,
            last_name=last_name,
        )
        parent_group, _ = Group.objects.get_or_create(name='Parent')
        parent_user.groups.add(parent_group)
        parent_user.save()

    # 2. Create Student record
    existing_student = Student.objects.filter(
        birth_cert_number=application.child_birth_certificate
    ).first()

    if existing_student:
        if not existing_student.parent_user:
            existing_student.parent_user = parent_user
            existing_student.parent_name = application.parent_full_name
            existing_student.parent_mobile = application.parent_mobile
            existing_student.parent_occupation = application.parent_occupation
            existing_student.parent_nida = application.parent_nida
            existing_student.save()
        return existing_student, parent_user, True  # True = already existed

    gender = application.child_gender if application.child_gender in ['M', 'F'] else 'M'

    student = Student.objects.create(
        first_name=application.child_first_name,
        middle_name=application.child_middle_name or '',
        last_name=application.child_last_name,
        date_of_birth=application.child_date_of_birth,
        birth_cert_number=application.child_birth_certificate,
        gender=gender,
        current_class=application.grade_applying_for,
        street=application.street,
        parent_name=application.parent_full_name,
        parent_mobile=application.parent_mobile,
        parent_occupation=application.parent_occupation,
        parent_nida=application.parent_nida,
        parent_user=parent_user,
        is_active=True,
    )
    return student, parent_user, False  # False = newly created


@login_required
def application_approve(request, pk):
    """Approve an application and auto-enroll the pupil"""
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
        return redirect('dashboard:redirect')

    application = get_object_or_404(Application, pk=pk)

    if application.status == 'approved':
        messages.warning(request, f'Application for {application.child_first_name} {application.child_last_name} is already approved.')
        return redirect('dashboard:application_list')

    application.status = 'approved'
    application.save()

    # Auto-enroll
    try:
        student, parent_user, existed = _enroll_student_from_application(application)
        if existed:
            messages.success(
                request,
                f'Application approved! Pupil {student.full_name} ({student.registration_number}) already existed and has been linked to parent account. '
                f'Parent login: {parent_user.username} / password: parent123'
            )
        else:
            messages.success(
                request,
                f'Application approved! Pupil {student.full_name} ({student.registration_number}) enrolled successfully! '
                f'Parent login: {parent_user.username} / password: parent123'
            )
    except Exception as e:
        messages.error(request, f'Application approved but enrollment failed: {str(e)}. Please enroll manually.')

    return redirect('dashboard:application_list')


@login_required
def application_reject(request, pk):
    """Reject an application"""
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
        return redirect('dashboard:redirect')

    application = get_object_or_404(Application, pk=pk)

    if application.status == 'approved':
        messages.error(request, 'Cannot reject an already approved application.')
        return redirect('dashboard:application_list')

    application.status = 'rejected'
    application.save()
    messages.success(request, f'Application for {application.child_first_name} {application.child_last_name} has been rejected.')
    return redirect('dashboard:application_list')


@login_required
def application_bulk_approve(request):
    """Bulk approve all pending applications"""
    if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Owner"]).exists()):
        return redirect('dashboard:redirect')

    if request.method == 'POST':
        pending = Application.objects.filter(status='pending')
        count = 0
        errors = 0
        for app in pending:
            try:
                app.status = 'approved'
                app.save()
                _enroll_student_from_application(app)
                count += 1
            except Exception:
                errors += 1

        if count:
            messages.success(request, f'{count} application(s) approved and enrolled successfully.')
        if errors:
            messages.warning(request, f'{errors} application(s) had errors during enrollment.')
        if count == 0 and errors == 0:
            messages.info(request, 'No pending applications to approve.')

    return redirect('dashboard:application_list')


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

    recent_results_count = Result.objects.filter(student__current_class__in=classes).count() if classes else 0

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
