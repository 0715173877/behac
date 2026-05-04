from django.db import models
from academics.models import ClassLevel   # will define later
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class Relationship(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Student(models.Model):
    # Registration number (auto-generated)
    registration_number = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    
    # Personal
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True) 
    last_name = models.CharField(max_length=50)
    nida = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()
    birth_cert_number = models.CharField(max_length=50, unique=True)
    religion = models.CharField(max_length=50, blank=True)
    region = models.ForeignKey('locations.Region', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
    current_class = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True)
    registration_date = models.DateField(auto_now_add=True)
    street = models.CharField(max_length=200, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    # Parent/Guardian (primary)
    parent_name = models.CharField(max_length=100)
    parent_mobile = models.CharField(max_length=15)
    parent_occupation = models.CharField(max_length=100)
    parent_nida = models.CharField(max_length=20, blank=True)
    # Link to Django user (parent account)
    parent_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registration_date']

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        if not self.registration_number:
            # Auto-generate: BIA-YYYY-NNNN
            year = timezone.now().strftime('%Y')
            last_student = Student.objects.filter(
                registration_number__startswith=f'BIA-{year}-'
            ).order_by('registration_number').last()
            
            if last_student and last_student.registration_number:
                last_num = int(last_student.registration_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.registration_number = f'BIA-{year}-{new_num:04d}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"

class OtherRelative(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='other_relatives')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    relationship = models.ForeignKey(Relationship, on_delete=models.SET_NULL, null=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"

class StudentClassHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='class_history')
    class_level = models.ForeignKey('academics.ClassLevel', on_delete=models.CASCADE)
    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('core.Term', on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Student class histories"

    def __str__(self):
        return f"{self.student.full_name} → {self.class_level.name} ({self.academic_year.name})"
