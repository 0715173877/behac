from django import forms
from .models import BehaviorRecord, Achievement

class BehaviorRecordForm(forms.ModelForm):
    class Meta:
        model = BehaviorRecord
        fields = ['student', 'behavior_type', 'description', 'action_taken', 'resolved']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['student', 'title', 'date_awarded', 'description']
        widgets = {
            'date_awarded': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Filter students to teacher's classes if the user is a teacher
        if user and hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            assigned_classes = teacher.classes.all()
            if assigned_classes.exists():
                self.fields['student'].queryset = Achievement._meta.get_field('student').related_model.objects.filter(
                    current_class__in=assigned_classes, is_active=True
                )