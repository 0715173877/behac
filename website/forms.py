from django import forms
from .models import Application
from academics.models import ClassLevel


class ApplicationForm(forms.ModelForm):
    grade_applying_for = forms.ModelChoiceField(
        queryset=ClassLevel.objects.all(),
        empty_label="Select grade/class...",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
    )

    class Meta:
        model = Application
        fields = [
            'child_first_name', 'child_middle_name', 'child_last_name',
            'child_date_of_birth', 'child_gender', 'child_birth_certificate',
            'child_previous_school', 'grade_applying_for',
            'parent_full_name', 'parent_relationship', 'parent_mobile',
            'parent_email', 'parent_occupation', 'parent_nida',
            'region', 'district', 'street',
            'additional_info',
        ]
        widgets = {
            'child_date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'child_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'child_middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter middle name (optional)'}),
            'child_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'child_gender': forms.Select(attrs={'class': 'form-select'}),
            'child_birth_certificate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter birth certificate number'}),
            'child_previous_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Previous school name (if any)'}),
            'parent_full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'parent_relationship': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select relationship...'),
                ('Father', 'Father'),
                ('Mother', 'Mother'),
                ('Guardian', 'Guardian'),
                ('Grandparent', 'Grandparent'),
                ('Sibling', 'Sibling'),
                ('Other', 'Other'),
            ]),
            'parent_mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0712 345 678'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter occupation'}),
            'parent_nida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIDA number (optional)'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter region'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter district'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter street/village name'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any additional information (optional)'}),
        }
