from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from academics.models import Subject, ClassLevel

class StaffBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    middle_name = models.CharField(max_length=50, blank=True, null=True)   # <-- added
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    hire_date = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qualification = models.TextField(blank=True)
    cv = models.FileField(upload_to='staff/cv/', blank=True, null=True)
    certificates = models.FileField(upload_to='staff/certificates/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def full_name(self):
        return f"{self.user.first_name} {self.middle_name or ''} {self.user.last_name}".strip()

    def __str__(self):
        return f"{self.full_name()} ({self.employee_id})"

class Teacher(StaffBase):
    subjects = models.ManyToManyField(Subject, blank=True, related_name='teachers')
    classes = models.ManyToManyField(ClassLevel, blank=True, related_name='teachers')

class OtherStaff(StaffBase):
    DEPARTMENT_CHOICES = [("HR", "Human Resources"), ("IT", "Information Technology"), ("Finance", "Finance"), ("Admin", "Administration"), ("Support", "Support Services")]
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    role = models.CharField(max_length=100)

class SalaryPayment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    staff_member = GenericForeignKey('content_type', 'object_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(help_text="First day of the month (e.g., 2025-01-01)")
    paid_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-month']
        unique_together = ('content_type', 'object_id', 'month')

    def __str__(self):
        return f"{self.staff_member} - {self.month.strftime('%B %Y')} - {self.amount}"