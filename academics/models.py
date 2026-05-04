from django.db import models
from core.models import Term

class ClassLevel(models.Model):
    LEVEL_TYPES = (('PRE','Pre-primary'), ('PRIMARY','Primary'))
    name = models.CharField(max_length=20)  # "Pre 1", "Grade 1"
    level_type = models.CharField(max_length=10, choices=LEVEL_TYPES)
    order = models.PositiveSmallIntegerField(unique=True)  # 1..9
    
    class Meta:
        ordering = ['order']
    
    def __str__(self): return self.name

class Subject(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    classes = models.ManyToManyField(ClassLevel, related_name='subjects')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self): return self.name

class Exam(models.Model):
    name = models.CharField(max_length=50)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, null=True, blank=True)
    max_marks = models.PositiveSmallIntegerField(default=100)
    passing_marks = models.PositiveSmallIntegerField(default=40)
    
    class Meta:
        ordering = ['term', 'name']
    
    def __str__(self): return f"{self.name} ({self.term})"

class Result(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    teacher_comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'exam')
        ordering = ['-exam__term', 'subject__name']
    
    def grade(self):
        try:
            percentage = (float(self.marks_obtained) / float(self.exam.max_marks)) * 100
            if percentage >= 80:
                return 'A'
            elif percentage >= 70:
                return 'B'
            elif percentage >= 60:
                return 'C'
            elif percentage >= 50:
                return 'D'
            elif percentage >= 40:
                return 'E'
            else:
                return 'F'
        except (ValueError, ZeroDivisionError):
            return '-'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}: {self.marks_obtained}/{self.exam.max_marks}"

class Attendance(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=1, choices=[('P','Present'),('A','Absent'),('L','Late')])
    
    class Meta: 
        unique_together = ('student','date')
        ordering = ['-date']
    
    def __str__(self): return f"Attendance for {self.student} on {self.date}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    due_date = models.DateField()
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', blank=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self): return self.title

class Timetable(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    academic_year = models.ForeignKey('core.AcademicYear', on_delete=models.CASCADE, default=1)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='timetables')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    period = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('staff.Teacher', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['class_level', 'day_of_week', 'period']
        unique_together = ('class_level', 'day_of_week', 'period', 'academic_year')
    
    def __str__(self): 
        return f"{self.class_level} - {self.get_day_of_week_display()} Period {self.period}: {self.subject.name}"
