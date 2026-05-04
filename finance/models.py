from django.db import models
from students.models import Student
from academics.models import ClassLevel
from core.models import AcademicYear

class FeeCategory(models.Model):
    name = models.CharField(max_length=50)  # "School Fee", "Buns & Transport", "Sweater"
    default_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_recurring = models.BooleanField(default=True)  # monthly vs one-time

    def __str__(self) -> str:
        return self.name

class FeeStructure(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    installment_month = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-12
    notes = models.TextField(blank=True)

class FeeReminder(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    sent_via = models.CharField(max_length=20, choices=[('email','Email'),('sms','SMS')])
    sent_date = models.DateTimeField(auto_now_add=True)