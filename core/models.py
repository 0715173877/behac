from django.db import models

class SchoolInfo(models.Model):
    name = models.CharField(max_length=200, default="Behac International Academy")
    motto = models.CharField(max_length=500, blank=True, default="")
    tagline = models.CharField(max_length=300, blank=True, default="")
    logo = models.ImageField(upload_to='school/', blank=True, null=True)
    portal_name = models.CharField(max_length=200, blank=True, default="", help_text="Name shown on the login portal")
    primary_dark = models.CharField(max_length=7, default="#1B5E20", help_text="Dark primary color (e.g. #1B5E20)")
    primary_light = models.CharField(max_length=7, default="#4CAF50", help_text="Light primary color (e.g. #4CAF50)")
    primary_bg = models.CharField(max_length=7, default="#E8F5E9", help_text="Background tint color (e.g. #E8F5E9)")
    hero_image = models.ImageField(upload_to='hero/', blank=True, null=True, help_text="Default hero background image (used when no Hero Slides are set)")


    class Meta:
        verbose_name = "School Information"
        verbose_name_plural = "School Information"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one SchoolInfo record exists
        if not self.pk and SchoolInfo.objects.exists():
            return  # Don't create a second record
        super().save(*args, **kwargs)

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)  # "2025-2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Term(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)  # Term 1,2,3
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('academic_year', 'name')

    def __str__(self):
        return self.name
