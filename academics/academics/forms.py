from django import forms
from .models import Result

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'exam', 'marks_obtained', 'teacher_comment']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={'step': '0.01'}),
        }