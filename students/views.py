from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Student, OtherRelative, Relationship
from django.contrib.auth.models import User, Group
from .forms import StudentRegistrationForm, OtherRelativeFormSet, StudentBulkUploadForm, TeacherStudentEditForm
from django.core.mail import send_mail
from django.db.models import Sum
from finance.models import Payment
from academics.models import Result
from behavior.models import BehaviorRecord
import pandas as pd
import secrets
import string
from academics.models import ClassLevel
from locations.models import Region, District
from django.views.generic import FormView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name__in=['Admin', 'Owner']).exists()

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        
        # If teacher, filter by their assigned classes
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                qs = qs.filter(current_class__in=assigned_classes)
        
        q = self.request.GET.get('q', '')
        cls = self.request.GET.get('class', '')
        gender = self.request.GET.get('gender', '')
        if q:
            qs = qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(middle_name__icontains=q) | qs.filter(registration_number__icontains=q) | qs.filter(birth_cert_number__icontains=q)
        if cls:
            qs = qs.filter(current_class_id=cls)
        if gender:
            qs = qs.filter(gender=gender)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classlevels'] = ClassLevel.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_class'] = self.request.GET.get('class', '')
        ctx['selected_gender'] = self.request.GET.get('gender', '')
        return ctx

class StudentCreateView(AdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentRegistrationForm   # changed
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['relatives'] = OtherRelativeFormSet(self.request.POST, instance=self.object)
        else:
            data['relatives'] = OtherRelativeFormSet(instance=self.object)
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        relatives = context['relatives']
        self.object = form.save(commit=False)

        # --- Auto-generate password ---
        username = form.cleaned_data['parent_username']
        email = form.cleaned_data['parent_email']
        # Generate a random password: 8 chars letters+digits
        alphabet = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(alphabet) for _ in range(8))
        
        parent_user = User.objects.create_user(
            username=username,
            email=email,
            password=raw_password
        )
        parent_group, _ = Group.objects.get_or_create(name='Parent')
        parent_user.groups.add(parent_group)
        parent_user.first_name = form.cleaned_data['parent_name'].split()[0] if form.cleaned_data['parent_name'] else ''
        parent_user.save()
        try:
            # --- Send email with credentials ---
            send_mail(
                subject='Behac International Academy – Parent Login Credentials',
                message=f"""
    Dear Parent,

    Your account has been created for your child {self.object.first_name} {self.object.last_name}.

    Login details:
    Username: {username}
    Password: {raw_password}

    Please login at http://localhost/login/ and change your password immediately.

    Thank you,
    Behac International Academy
    """,
                from_email='noreply@behac.academy',
                recipient_list=[email],
                fail_silently=False,   # set to True in production to avoid errors if email not configured
            )
        
        except Exception as e:
            # Handle email sending errors
            print(f"Error sending email: {e}")

        
        self.object.parent_user = parent_user
        self.object.save()
        
        if relatives.is_valid():
            relatives.instance = self.object
            relatives.save()
        
        return super().form_valid(form)
   
class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['other_relatives'] = student.other_relatives.all()
        context['payments'] = Payment.objects.filter(student=student).order_by('-payment_date')
        context['total_paid'] = context['payments'].aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        context['results'] = Result.objects.filter(student=student).select_related('exam', 'subject').order_by('-exam__term__academic_year__name')
        context['behavior'] = BehaviorRecord.objects.filter(student=student).order_by('-date')
        context['achievements'] = student.achievements.all().order_by('-date_awarded')
        
        # Group results by academic year and term for progress
        from core.models import AcademicYear
        from itertools import groupby
        results_qs = context['results']
        years_dict = {}
        
        # Group achievements by academic year
        ach_years = {}
        for a in context["achievements"]:
            yr = AcademicYear.objects.filter(start_date__lte=a.date_awarded, end_date__gte=a.date_awarded).first()
            yr_name = yr.name if yr else str(a.date_awarded.year)
            if yr_name not in ach_years:
                ach_years[yr_name] = {"year": yr, "achievements": []}
            ach_years[yr_name]["achievements"].append(a)
        context['achievement_years'] = ach_years
        
        # Group payments by year
        from dateutil.relativedelta import relativedelta
        payments_by_year = {}
        for p in context['payments']:
            yr = AcademicYear.objects.filter(start_date__lte=p.payment_date, end_date__gte=p.payment_date).first()
            yr_name = yr.name if yr else 'Unknown'
            if yr_name not in payments_by_year:
                payments_by_year[yr_name] = {'year': yr, 'payments': [], 'total': 0}
            payments_by_year[yr_name]['payments'].append(p)
            payments_by_year[yr_name]['total'] += p.amount_paid
        context['payments_by_year'] = payments_by_year
        for r in results_qs:
            yr = r.exam.term.academic_year
            yr_name = yr.name
            if yr_name not in years_dict:
                years_dict[yr_name] = {'year': yr, 'terms': {}}
            term_name = r.exam.term.name
            if term_name not in years_dict[yr_name]['terms']:
                years_dict[yr_name]['terms'][term_name] = {'term': r.exam.term, 'results': []}
            years_dict[yr_name]['terms'][term_name]['results'].append(r)
        context['progress_years'] = years_dict
        
        # Behavior grouped by year
        years_beh = {}
        for b in context['behavior']:
            yr = AcademicYear.objects.filter(start_date__lte=b.date, end_date__gte=b.date).first()
            yr_name = yr.name if yr else 'Unknown'
            if yr_name not in years_beh:
                years_beh[yr_name] = []
            years_beh[yr_name].append(b)
        context['behavior_years'] = years_beh
        
        return context

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')
    
    def get_form_class(self):
        # Teachers get limited form, admin gets full form
        if self.request.user.is_superuser or self.request.user.groups.filter(name__in=['Admin', 'Owner']).exists():
            return StudentRegistrationForm
        return TeacherStudentEditForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['relatives'] = OtherRelativeFormSet(self.request.POST, instance=self.object)
        else:
            data['relatives'] = OtherRelativeFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        relatives = context['relatives']
        self.object = form.save()
        if relatives.is_valid():
            relatives.instance = self.object
            relatives.save()
        return super().form_valid(form)

class StudentDeleteView(AdminRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:list')

class StudentBulkUploadView(AdminRequiredMixin, FormView):
    template_name = 'students/bulk_upload.html'
    form_class = StudentBulkUploadForm
    success_url = reverse_lazy('students:list')

    def form_valid(self, form):
        excel_file = self.request.FILES['excel_file']
        try:
            df = pd.read_excel(excel_file)
            required_columns = [
                'first_name', 'last_name', 'date_of_birth', 'gender',
                'birth_cert_number', 'current_class', 'parent_name',
                'parent_mobile', 'parent_username', 'parent_email',
                'region', 'district', 'relationship1_name', 'other_relative1_name',
                'other_relative1_mobile'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise Exception(f"Missing columns: {missing}")

            with transaction.atomic():
                created_count = 0
                skipped_count = 0
                for idx, row in df.iterrows():
                    # Convert row to dict and all values to string
                    row_dict = {}
                    for col, val in row.items():
                        if pd.isna(val):
                            row_dict[col] = ''
                        else:
                            row_dict[col] = str(val).strip()
                    
                    # Skip if no first name or birth cert
                    if not row_dict.get('first_name') or not row_dict.get('birth_cert_number'):
                        skipped_count += 1
                        continue

                    # Check for duplicate student by birth certificate
                    if Student.objects.filter(birth_cert_number=row_dict['birth_cert_number']).exists():
                        print(f"Row {idx+2}: Student with birth_cert {row_dict['birth_cert_number']} already exists. Skipping.")
                        skipped_count += 1
                        continue

                    # ----- 1. ClassLevel -----
                    class_name = row_dict.get('current_class')
                    if not class_name:
                        raise Exception(f"Row {idx+2}: current_class is empty")
                    try:
                        class_level = ClassLevel.objects.get(name=class_name)
                    except ClassLevel.DoesNotExist:
                        raise Exception(f"Row {idx+2}: Class '{class_name}' not found")

                    # ----- 2. Region & District (auto-create) -----
                    region_name = row_dict.get('region')
                    if not region_name:
                        raise Exception(f"Row {idx+2}: region is empty")
                    region, _ = Region.objects.get_or_create(name=region_name)

                    district_name = row_dict.get('district')
                    if not district_name:
                        raise Exception(f"Row {idx+2}: district is empty")
                    district, _ = District.objects.get_or_create(name=district_name, region=region)

                    # ----- 3. Parent User: reuse if exists, else create -----
                    username = row_dict.get('parent_username')
                    email = row_dict.get('parent_email')
                    if not username or not email:
                        raise Exception(f"Row {idx+2}: parent_username or parent_email missing")

                    # Try to find existing user by username or email
                    existing_user = None
                    if User.objects.filter(username=username).exists():
                        existing_user = User.objects.get(username=username)
                    elif User.objects.filter(email=email).exists():
                        existing_user = User.objects.get(email=email)
                    
                    if existing_user:
                        parent_user = existing_user
                        # Ensure the user is in Parent group (just in case)
                        parent_group, _ = Group.objects.get_or_create(name='Parent')
                        if not parent_user.groups.filter(name='Parent').exists():
                            parent_user.groups.add(parent_group)
                        # No password generation or email sending because account already exists
                        send_new_credentials = False
                    else:
                        # Create new user
                        import secrets, string
                        from datetime import datetime
                        raw_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
                        parent_user = User.objects.create_user(username=username, email=email, password=raw_password)
                        parent_group, _ = Group.objects.get_or_create(name='Parent')
                        parent_user.groups.add(parent_group)
                        send_new_credentials = True

                    # ----- 4. Create Student -----
                    from datetime import datetime
                    try:
                        dob = datetime.strptime(row_dict['date_of_birth'], '%Y-%m-%d').date()
                    except:
                        raise Exception(f"Row {idx+2}: invalid date_of_birth (use YYYY-MM-DD)")

                    student = Student.objects.create(
                        first_name=row_dict['first_name'],
                        middle_name=row_dict.get('middle_name', ''),
                        last_name=row_dict['last_name'],
                        date_of_birth=dob,
                        gender=row_dict['gender'],
                        birth_cert_number=row_dict['birth_cert_number'],
                        current_class=class_level,
                        parent_name=row_dict['parent_name'],
                        parent_mobile=row_dict['parent_mobile'],
                        parent_occupation=row_dict.get('parent_occupation', ''),
                        region=region,
                        district=district,
                        street=row_dict.get('street', ''),
                        mobile=row_dict.get('student_mobile', ''),
                        parent_user=parent_user,
                    )

                    # ----- 5. Other Relatives (max 2) -----
                    for rel_num in [1,2]:
                        rel_name = row_dict.get(f'other_relative{rel_num}_name')
                        if not rel_name:
                            continue
                        rel_mobile = row_dict.get(f'other_relative{rel_num}_mobile', '')
                        rel_relationship = row_dict.get(f'relationship{rel_num}_name', '')
                        rel_occupation = row_dict.get(f'other_relative{rel_num}_occupation', '')
                        
                        relationship_obj = None
                        if rel_relationship:
                            relationship_obj, _ = Relationship.objects.get_or_create(name=rel_relationship)
                        OtherRelative.objects.create(
                            student=student,
                            name=rel_name,
                            mobile=rel_mobile[:15] if rel_mobile else '',
                            relationship=relationship_obj,
                            occupation=rel_occupation
                        )

                    # ----- 6. Send email only if new user created -----
                    if send_new_credentials:
                        try:
                            send_mail(
                                subject='Behac International Academy – Your Child Has Been Registered',
                                message=f"""
    Dear Parent,

    Your child {student.first_name} {student.last_name} has been registered successfully.

    Login details:
    Username: {username}
    Password: {raw_password}

    Login at: http://localhost/login/
    Please change your password after login.

    If you have other children, use the same account to access all their information.

    Behac International Academy
    """,
                                from_email='noreply@behac.academy',
                                recipient_list=[email],
                                fail_silently=False,
                            )
                        except Exception as email_err:
                            print(f"Email to {email} failed: {email_err}")
                    else:
                        # Optionally, you could still send a "new child added" notification
                        # but not required.
                        pass

                    created_count += 1

                messages.success(self.request, f"Successfully imported {created_count} students. Skipped {skipped_count} (duplicate birth cert or missing data).")
        except Exception as e:
            messages.error(self.request, f"Import failed: {str(e)}")
            return self.form_invalid(form)
        return super().form_valid(form)


def download_excel_template(request):
    # Create a new workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Students"

    # Define columns (matching the bulk upload expected format)
    columns = [
        "first_name", "last_name", "middle_name", "date_of_birth", "gender",
        "birth_cert_number", "current_class", "parent_name", "parent_mobile",
        "parent_username", "parent_email", "region", "district", "street",
        "student_mobile", "relationship1_name", "other_relative1_name",
        "other_relative1_mobile", "other_relative1_occupation",
        "relationship2_name", "other_relative2_name", "other_relative2_mobile",
        "other_relative2_occupation"
    ]
    sheet.append(columns)

    # Make header row bold
    for col in sheet.iter_cols(max_row=1, max_col=len(columns)):
        col[0].font = Font(bold=True)

    # Add an example row (optional but helpful)
    example_row = [
        "John", "Doe", "", "2017-01-01", "M",
        "BC12345", "Pre 1", "Jane Doe", "0712345678",
        "johndoe_parent", "johndoe@email.com", "Dar es Salaam", "Ilala", "Main Street",
        "0712345679", "Uncle", "Peter Doe", "0712345680", "Driver",
        "Aunt", "Mary Doe", "0712345681", "Teacher"
    ]
    sheet.append(example_row)

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
    workbook.save(response)
    return response







