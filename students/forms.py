from django import forms
from django.contrib.auth.models import User

from locations.models import District, Region
from .models import Student, OtherRelative
from academics.models import ClassLevel
from django.forms import inlineformset_factory

class StudentRegistrationForm(forms.ModelForm):
    # Parent user fields
    parent_username = forms.CharField(max_length=150, label="Parent Username")
    parent_email = forms.EmailField(label="Parent Email")
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=True, empty_label="Select Region")
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=True, empty_label="Select District")

    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender',
            'religion', 'nida', 'birth_cert_number', 'current_class',
            'region', 'district', 'street', 'mobile',
            'parent_name', 'parent_mobile', 'parent_occupation', 'parent_nida'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'current_class': forms.Select(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'nida': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_cert_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_nida': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
        
        # When editing, pre-fill parent fields from instance
        if self.instance.pk:
            self.fields['parent_occupation'].initial = self.instance.parent_occupation
            self.fields['parent_name'].initial = self.instance.parent_name
            self.fields['parent_mobile'].initial = self.instance.parent_mobile
            self.fields['parent_nida'].initial = self.instance.parent_nida
            
            if self.instance.parent_user:
                self.fields['parent_username'].initial = self.instance.parent_user.username
                self.fields['parent_email'].initial = self.instance.parent_user.email
                self.fields['parent_username'].widget.attrs['readonly'] = True
                self.fields['parent_username'].widget.attrs['class'] = 'form-control bg-light'

    def clean_parent_username(self):
        username = self.cleaned_data.get('parent_username')
        # On edit, if empty, return existing
        if not username and self.instance.pk and self.instance.parent_user:
            return self.instance.parent_user.username
        return username
    
    def clean_parent_email(self):
        email = self.cleaned_data.get('parent_email')
        if not email and self.instance.pk and self.instance.parent_user:
            return self.instance.parent_user.email
        return email
    
    def clean_parent_occupation(self):
        val = self.cleaned_data.get('parent_occupation')
        if not val and self.instance.pk:
            return self.instance.parent_occupation
        return val
    
    def clean_parent_name(self):
        val = self.cleaned_data.get('parent_name')
        if not val and self.instance.pk:
            return self.instance.parent_name
        return val
    
    def clean_parent_mobile(self):
        val = self.cleaned_data.get('parent_mobile')
        if not val and self.instance.pk:
            return self.instance.parent_mobile
        return val

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('parent_username')
        email = cleaned_data.get('parent_email')
        
        if username:
            existing = User.objects.filter(username=username)
            if self.instance.pk and self.instance.parent_user:
                existing = existing.exclude(pk=self.instance.parent_user.pk)
            if existing.exists():
                raise forms.ValidationError("Username already taken.")
        
        if email:
            existing = User.objects.filter(email=email)
            if self.instance.pk and self.instance.parent_user:
                existing = existing.exclude(pk=self.instance.parent_user.pk)
            if existing.exists():
                raise forms.ValidationError("Email already used.")
        return cleaned_data

OtherRelativeFormSet = inlineformset_factory(
    Student,
    OtherRelative,
    fields=('name', 'mobile', 'relationship', 'occupation'),
    extra=2,
    max_num=2,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'mobile': forms.TextInput(attrs={'class': 'form-control'}),
        'relationship': forms.Select(attrs={'class': 'form-select'}),
        'occupation': forms.TextInput(attrs={'class': 'form-control'}),
    }
)

class StudentBulkUploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel File (.xlsx or .xls)", help_text="Download template first")


class TeacherStudentEditForm(forms.ModelForm):
    """Limited form for teachers - only personal info"""
    class Meta:
        model = Student
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender',
            'religion', 'nida', 'birth_cert_number',
            'street', 'mobile',
            'parent_name', 'parent_mobile', 'parent_occupation', 'parent_nida'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'nida': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_cert_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_nida': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
