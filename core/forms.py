from django import forms
from .models import AcademicYear, Term

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 2025-2026"}),
        }

class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["academic_year", "name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Term 1"}),
            "academic_year": forms.Select(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["academic_year"].queryset = AcademicYear.objects.all().order_by("-start_date")
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            self.initial["academic_year"] = current_year
