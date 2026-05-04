from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Teacher, SalaryPayment

class TeacherForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="First name")
    middle_name = forms.CharField(max_length=50, required=False, label="Middle name")
    last_name = forms.CharField(max_length=30, required=True, label="Last name")
    # password field removed – auto‑generated

    class Meta:
        model = Teacher
        fields = [
            'employee_id', 'phone', 'address', 'hire_date',
            'qualification', 'cv', 'certificates',
            'subjects', 'classes', 'base_salary', 'is_active'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'classes': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'qualification': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['middle_name'].initial = self.instance.middle_name
            self.fields['last_name'].initial = user.last_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance.pk and self.instance.user:
            if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
                raise forms.ValidationError("Username already taken.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.pk and self.instance.user:
            if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
                raise forms.ValidationError("Email already used by another user.")
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already used.")
        return email

    def save(self, commit=True):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        middle_name = self.cleaned_data['middle_name']
        last_name = self.cleaned_data['last_name']

        # Get or create user
        if self.instance.pk and self.instance.user:
            user = self.instance.user
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            password_sent = False
        else:
            # Generate random password
            import secrets, string
            raw_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            user = User.objects.create_user(
                username=username, email=email, password=raw_password,
                first_name=first_name, last_name=last_name
            )
            # Send email with credentials
            try:
                send_mail(
                    subject='Behac International Academy – Teacher Account Created',
                    message=f"""
Dear Teacher,

Your account has been created.

Login details:
Username: {username}
Password: {raw_password}

Please login at http://localhost/login/ and change your password.

Behac International Academy
""",
                    from_email='noreply@behac.academy',
                    recipient_list=[email],
                    fail_silently=False,
                )
                password_sent = True
            except Exception:
                password_sent = False

        self.instance.user = user

        # Save the teacher instance with middle_name
        teacher = super().save(commit=False)
        teacher.middle_name = middle_name
        if commit:
            teacher.save()
            self.save_m2m()
        return teacher

class SalaryPaymentForm(forms.ModelForm):
    update_base_salary = forms.BooleanField(
        required=False,
        label="Update base salary to this amount",
        help_text="Check if this payment represents a new permanent salary"
    )

    class Meta:
        model = SalaryPayment
        fields = ['amount', 'month', 'notes', 'update_base_salary']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def clean_month(self):
        month_data = self.cleaned_data['month']
        if isinstance(month_data, str):
            from datetime import datetime
            try:
                return datetime.strptime(month_data, '%Y-%m').date()
            except ValueError:
                raise forms.ValidationError("Enter a valid month in YYYY-MM format.")
        return month_data