from django.db import models
from students.models import Student
from staff.models import Teacher

class BehaviorRecord(models.Model):
    BEHAVIOR_TYPES = (('POS','Positive'), ('NEG','Negative'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    behavior_type = models.CharField(max_length=3, choices=BEHAVIOR_TYPES)
    description = models.TextField()
    action_taken = models.CharField(max_length=200, blank=True)
    resolved = models.BooleanField(default=False)

class Achievement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    date_awarded = models.DateField()
    description = models.TextField(blank=True)