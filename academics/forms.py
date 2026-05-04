from django import forms
from .models import Result, Attendance, Assignment

from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'subject', 'class_level', 'due_date', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        teacher_user = kwargs.pop('teacher_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # If teacher, filter subjects and classes
        if teacher_user and hasattr(teacher_user, 'teacher_profile'):
            teacher = teacher_user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                self.fields['class_level'].queryset = assigned_classes
            assigned_subjects = teacher.subjects.all()
            if assigned_subjects.exists():
                self.fields['subject'].queryset = assigned_subjects

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'exam', 'marks_obtained', 'teacher_comment']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'teacher_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        teacher_user = kwargs.pop('teacher_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Filter exams by current academic year (unless bypass)
        from core.models import AcademicYear, Term
        from .models import Exam
        if teacher_user and hasattr(teacher_user, 'teacher_profile'):
            # Always filter teachers to current year
            current_year = AcademicYear.objects.filter(is_current=True).first()
            if current_year:
                current_terms = Term.objects.filter(academic_year=current_year)
                self.fields['exam'].queryset = Exam.objects.filter(term__in=current_terms)
        else:
            # Admin/owner sees all exams
            pass
        
        # If teacher, filter students by their assigned classes
        if teacher_user and hasattr(teacher_user, 'teacher_profile'):
            teacher = teacher_user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                from students.models import Student
                self.fields['student'].queryset = Student.objects.filter(current_class__in=assigned_classes)
            
            assigned_subjects = teacher.subjects.all()
            if assigned_subjects.exists():
                self.fields['subject'].queryset = assigned_subjects

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }