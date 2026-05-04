from django import forms
from .models import Payment, FeeCategory, FeeStructure

class PaymentForm(forms.ModelForm):
    student_search = forms.CharField(
        label='Search Student',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type student name, reg number or birth cert...',
            'id': 'studentSearch',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = Payment
        fields = ['student', 'fee_category', 'amount_paid', 'installment_month', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control', 'id': 'studentSelect', 'style': 'display:none'}),
            'fee_category': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'installment_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'student_search':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Make student select hidden by default; we'll use JS
        self.fields['student'].required = True
        self.fields['student'].empty_label = None

class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['class_level', 'academic_year', 'fee_category', 'amount']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'fee_category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaymentBulkUploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel File (.xlsx or .xls)", help_text="Download template first")
