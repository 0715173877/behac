from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Result, Attendance, Assignment, Exam, Timetable, Subject, ClassLevel
from .forms import ResultForm, AttendanceForm, AssignmentForm
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.views.generic import FormView
from students.models import Student
import openpyxl
from openpyxl.styles import Font
import pandas as pd

# =========== FORMS FOR NEW MODELS ===========
from django import forms

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'term', 'max_marks', 'passing_marks']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter terms by current academic year
        from core.models import AcademicYear
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            self.fields['term'].queryset = current_year.term_set.all()


class ResultBulkUploadForm(forms.Form):
    excel_file = forms.FileField(label='Upload Excel File (.xlsx)')

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['class_level', 'day_of_week', 'period', 'subject', 'teacher']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        teacher_user = kwargs.pop('teacher_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Auto-set academic year to current
        from core.models import AcademicYear
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            self.fields['academic_year'] = forms.ModelChoiceField(
                queryset=AcademicYear.objects.all(),
                initial=current_year,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label="Academic Year"
            )
            if not self.instance.pk:
                self.initial['academic_year'] = current_year
        
        # If teacher, filter subjects and classes
        if teacher_user and hasattr(teacher_user, 'teacher_profile'):
            teacher = teacher_user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                self.fields['class_level'].queryset = assigned_classes
            assigned_subjects = teacher.subjects.all()
            if assigned_subjects.exists():
                self.fields['subject'].queryset = assigned_subjects

# =========== MIXIN ===========

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Teacher').exists() or self.request.user.is_superuser

from core.models import AcademicYear

def get_academic_year_filter(request):
    show_all = request.GET.get('all', '')
    if show_all == '1' and (request.user.is_superuser or 'Admin' in request.user.groups.all().values_list('name', flat=True)):
        return {}
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if current_year:
        return {'date__gte': current_year.start_date, 'date__lte': current_year.end_date}
    return {}

def get_academic_year_filter_by_field(request, date_field='date'):
    show_all = request.GET.get('all', '')
    if show_all == '1' and (request.user.is_superuser or 'Admin' in request.user.groups.all().values_list('name', flat=True)):
        return {}
    current_year = AcademicYear.objects.filter(is_current=True).first()
    if current_year:
        return {f'{date_field}__gte': current_year.start_date, f'{date_field}__lte': current_year.end_date}
    return {}


# =========== RESULT VIEWS ===========

class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'academics/result_list.html'
    context_object_name = 'results'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('student', 'exam', 'subject')
        
        # If teacher, filter by their assigned subjects & classes
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            assigned_subjects = teacher.subjects.all()
            if assigned_classes.exists():
                qs = qs.filter(student__current_class__in=assigned_classes)
            if assigned_subjects.exists():
                qs = qs.filter(subject__in=assigned_subjects)
        
        # Filter by current academic year (unless ?all=1 is passed for admins)
        from core.models import AcademicYear
        show_all = self.request.GET.get('all', '')
        if not (show_all == '1' and (self.request.user.is_superuser or 'Admin' in self.request.user.groups.all().values_list('name', flat=True))):
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                qs = qs.filter(exam__term__academic_year=current_year)
        
        q = self.request.GET.get('q', '')
        exam_id = self.request.GET.get('exam', '')
        subject_id = self.request.GET.get('subject', '')
        if q:
            qs = qs.filter(student__first_name__icontains=q) | qs.filter(student__last_name__icontains=q) | qs.filter(student__registration_number__icontains=q)
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # If teacher, only show their subjects & all exams
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            ctx['subjects'] = teacher.subjects.all()
            if not ctx['subjects'].exists():
                ctx['subjects'] = Subject.objects.all()
        else:
            ctx['subjects'] = Subject.objects.all()
        ctx['exams'] = Exam.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_exam'] = self.request.GET.get('exam', '')
        ctx['selected_subject'] = self.request.GET.get('subject', '')
        return ctx

class ResultCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = 'academics/result_form.html'
    success_url = reverse_lazy('academics:result_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Enter Exam Results'
        
        # If teacher, only show their assigned classes & subjects
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            context['teacher_subjects'] = teacher.subjects.all()
            context['teacher_classes'] = teacher.classes.all()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher_user'] = self.request.user
        return kwargs

class ResultUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Result
    form_class = ResultForm
    template_name = 'academics/result_form.html'
    success_url = reverse_lazy('academics:result_list')

class ResultDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Result
    template_name = 'academics/result_confirm_delete.html'
    success_url = reverse_lazy('academics:result_list')

# =========== ATTENDANCE VIEWS ===========

class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'academics/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('student')
        
        # Add academic year filter
        year_filter = get_academic_year_filter(self.request)
        if year_filter:
            qs = qs.filter(**year_filter)
        
        # If teacher, only show students in their classes
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                qs = qs.filter(student__current_class__in=assigned_classes)
        
        q = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        if q:
            qs = qs.filter(student__first_name__icontains=q) | qs.filter(student__last_name__icontains=q)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        from core.models import AcademicYear
        ctx['current_year'] = AcademicYear.objects.filter(is_current=True).first()
        return ctx

class AttendanceCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'academics/attendance_form.html'
    success_url = reverse_lazy('academics:attendance_list')

class AttendanceUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'academics/attendance_form.html'
    success_url = reverse_lazy('academics:attendance_list')

# =========== ASSIGNMENT VIEWS ===========

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'academics/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        qs = super().get_queryset()
        year_filter = get_academic_year_filter_by_field(self.request, 'due_date')
        if year_filter:
            qs = qs.filter(**year_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_year'] = AcademicYear.objects.filter(is_current=True).first()
        return ctx

class AssignmentCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'academics/assignment_form.html'
    success_url = reverse_lazy('academics:assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher_user'] = self.request.user
        return kwargs

class AssignmentUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'academics/assignment_form.html'
    success_url = reverse_lazy('academics:assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher_user'] = self.request.user
        return kwargs

class AssignmentDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'academics/assignment_confirm_delete.html'
    success_url = reverse_lazy('academics:assignment_list')

# =========== EXAM VIEWS ===========

class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'academics/exam_list.html'
    context_object_name = 'exams'

class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'academics/exam_form.html'
    success_url = reverse_lazy('academics:exam_list')

class ExamUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'academics/exam_form.html'
    success_url = reverse_lazy('academics:exam_list')

class ExamDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Exam
    template_name = 'academics/exam_confirm_delete.html'
    success_url = reverse_lazy('academics:exam_list')

# =========== TIMETABLE VIEWS ===========

class TimetableListView(LoginRequiredMixin, ListView):
    model = Timetable
    template_name = 'academics/timetable_list.html'
    context_object_name = 'timetables'

    def get_queryset(self):
        qs = super().get_queryset().select_related('class_level', 'subject', 'teacher__user', 'academic_year')
        
        # Filter by academic year
        show_all = self.request.GET.get('all', '')
        if not (show_all == '1' and (self.request.user.is_superuser or 'Admin' in self.request.user.groups.all().values_list('name', flat=True))):
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                qs = qs.filter(academic_year=current_year)
        
        # If teacher, filter by their subjects and classes
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                qs = qs.filter(class_level__in=assigned_classes)
            assigned_subjects = teacher.subjects.all()
            if assigned_subjects.exists():
                qs = qs.filter(subject__in=assigned_subjects)
        
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from datetime import datetime
        ctx['today_weekday'] = datetime.now().weekday()  # 0=Monday, 6=Sunday
        ctx['hasattr_user_teacher'] = hasattr(self.request.user, 'teacher_profile')
        ctx['current_year'] = AcademicYear.objects.filter(is_current=True).first()
        return ctx

class TimetableCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = 'academics/timetable_form.html'
    success_url = reverse_lazy('academics:timetable_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher_user'] = self.request.user
        return kwargs

class TimetableUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = 'academics/timetable_form.html'
    success_url = reverse_lazy('academics:timetable_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher_user'] = self.request.user
        return kwargs

class TimetableDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Timetable
    template_name = 'academics/timetable_confirm_delete.html'
    success_url = reverse_lazy('academics:timetable_list')

# =========== SUBJECT & CLASS LEVEL VIEWS ===========

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            teacher_subjects = teacher.subjects.all()
            if teacher_subjects.exists():
                qs = teacher_subjects
        return qs.distinct()

class ClassLevelListView(LoginRequiredMixin, ListView):
    model = ClassLevel
    template_name = 'academics/classlevel_list.html'
    context_object_name = 'classlevels'

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            teacher_classes = teacher.classes.all()
            if teacher_classes.exists():
                qs = teacher_classes
        return qs.distinct()


# =========== RESULT BULK UPLOAD ===========
def download_excel_template(request):
    from students.models import Student
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Results"
    columns = ['registration_number', 'full_name', 'subject_code', 'exam_name', 'marks_obtained', 'teacher_comment']
    ws.append(columns)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    
    # Get optional filters from query params to pre-fill template
    subject_code = request.GET.get('subject', '')
    class_id = request.GET.get('class', '')
    exam_name = request.GET.get('exam', 'Mid Term 2025')
    
    # If teacher, default to their first assigned subject/class
    if hasattr(request.user, 'teacher_profile'):
        teacher = request.user.teacher_profile
        teacher_subjects = list(teacher.subjects.values_list('code', flat=True))
        teacher_classes = list(teacher.classes.values_list('id', flat=True))
        if not subject_code and teacher_subjects:
            subject_code = teacher_subjects[0]
        if not class_id and teacher_classes:
            class_id = str(teacher_classes[0])
    
    queried_subject = None
    if subject_code:
        try:
            queried_subject = Subject.objects.get(code=subject_code.upper())
        except Subject.DoesNotExist:
            pass
    
    # If class_id provided, pre-fill with students from that class
    students = Student.objects.all()
    queried_class = None
    if class_id:
        students = students.filter(current_class_id=class_id)
        try:
            queried_class = ClassLevel.objects.get(id=class_id)
        except ClassLevel.DoesNotExist:
            pass
    
    # If both selected, add all students with pre-filled subject
    if queried_subject and students.count() > 0:
        for student in students:
            ws.append([
                student.registration_number,
                student.full_name,
                queried_subject.code,
                exam_name,
                '',
                ''
            ])
    else:
        # Generic example rows
        ws.append(['STU001', 'John Doe', subject_code or 'ENG', exam_name, 78, 'Good progress'])
        ws.append(['STU002', 'Jane Smith', subject_code or 'MATH', exam_name, 85, 'Excellent'])
    
    filename = 'result_import_template.xlsx'
    if queried_class:
        filename = f'results_{queried_class.name.replace(" ", "_")}.xlsx'
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

class ResultBulkUploadView(LoginRequiredMixin, TeacherRequiredMixin, FormView):
    template_name = 'academics/result_bulk_upload.html'
    form_class = ResultBulkUploadForm
    success_url = reverse_lazy('academics:result_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Get subjects and classes - filtered for teachers
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            ctx['subjects'] = teacher.subjects.all()
            ctx['classlevels'] = teacher.classes.all()
        if not ctx.get('subjects') or not ctx['subjects'].exists():
            ctx['subjects'] = Subject.objects.all()
        if not ctx.get('classlevels') or not ctx['classlevels'].exists():
            ctx['classlevels'] = ClassLevel.objects.all()
        return ctx

    def get_allowed_subjects(self):
        """Return subject codes the teacher is allowed to use"""
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            return teacher.subjects.values_list('code', flat=True)
        return []
    
    def get_allowed_classes(self):
        """Return class IDs the teacher is allowed to work with"""
        if hasattr(self.request.user, 'teacher_profile'):
            teacher = self.request.user.teacher_profile
            return teacher.classes.values_list('id', flat=True)
        return []

    def form_valid(self, form):
        excel_file = self.request.FILES['excel_file']
        allowed_subjects = self.get_allowed_subjects()
        allowed_classes = self.get_allowed_classes()
        
        try:
            df = pd.read_excel(excel_file)
            required = ['subject_code', 'exam_name', 'marks_obtained']  # registration_number or full_name needed
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise Exception(f"Missing columns: {missing}")

            with transaction.atomic():
                ok = 0
                errors = []
                for idx, row in df.iterrows():
                    rd = {k: (str(v).strip() if pd.notna(v) else '') for k, v in row.items()}
                    bc = rd.get('registration_number')
                    full_name = rd.get('full_name', '')
                    
                    # Try to find student by registration number first
                    student = None
                    if bc:
                        try:
                            student = Student.objects.get(registration_number=bc)
                        except Student.DoesNotExist:
                            pass
                    
                    # Fallback to full_name lookup
                    if not student and full_name:
                        names = full_name.strip().split()
                        if len(names) >= 2:
                            student = Student.objects.filter(
                                first_name__iexact=names[0],
                                last_name__iexact=names[-1]
                            ).first()
                        elif len(names) == 1:
                            student = Student.objects.filter(
                                first_name__iexact=names[0]
                            ).first() or Student.objects.filter(
                                last_name__iexact=names[0]
                            ).first()
                    
                    if not student:
                        errors.append((idx+2, f"Student '{bc or full_name}' not found")); continue
                    
                    # Check if student is in teacher's assigned class
                    if allowed_classes and student.current_class_id not in allowed_classes:
                        errors.append((idx+2, f"Student '{student.registration_number}' not in your assigned class")); continue

                    sc = rd.get('subject_code')
                    if not sc:
                        errors.append((idx+2, 'Missing subject_code')); continue
                    try:
                        subject = Subject.objects.get(code=sc.upper())
                    except Subject.DoesNotExist:
                        errors.append((idx+2, f"Subject '{sc}' not found")); continue
                    
                    # Check if teacher is allowed to record this subject
                    if allowed_subjects and subject.code not in allowed_subjects:
                        errors.append((idx+2, f"Subject '{sc}' not assigned to you")); continue

                    en = rd.get('exam_name')
                    if not en:
                        errors.append((idx+2, 'Missing exam_name')); continue
                    try:
                        exam = Exam.objects.get(name__iexact=en)
                    except Exam.DoesNotExist:
                        errors.append((idx+2, f"Exam '{en}' not found. Create it first.")); continue

                    try:
                        marks = float(rd.get('marks_obtained', 0))
                    except:
                        errors.append((idx+2, 'Invalid marks_obtained')); continue

                    comment = rd.get('teacher_comment', '')
                    existing = Result.objects.filter(student=student, subject=subject, exam=exam).first()
                    if existing:
                        existing.marks_obtained = marks
                        existing.teacher_comment = comment
                        existing.save()
                    else:
                        Result.objects.create(student=student, subject=subject, exam=exam, marks_obtained=marks, teacher_comment=comment)
                    ok += 1

                if errors:
                    self.request.session['result_bulk_errors'] = errors
                    messages.warning(self.request, f"Imported {ok} results with {len(errors)} errors.")
                else:
                    messages.success(self.request, f"Successfully imported {ok} results.")

        except Exception as e:
            messages.error(self.request, f"Import failed: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)
