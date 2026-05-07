from django.db import models
from django.utils import timezone
from academics.models import ClassLevel


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    # Child's information
    child_first_name = models.CharField(max_length=100, verbose_name="Child's First Name")
    child_middle_name = models.CharField(max_length=100, blank=True, verbose_name="Child's Middle Name")
    child_last_name = models.CharField(max_length=100, verbose_name="Child's Last Name")
    child_date_of_birth = models.DateField(verbose_name="Child's Date of Birth")
    child_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Child's Gender")
    child_birth_certificate = models.CharField(max_length=100, verbose_name="Birth Certificate Number")
    child_previous_school = models.CharField(max_length=200, blank=True, verbose_name="Previous School (if any)")
    grade_applying_for = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, verbose_name="Grade/Class Applying For")

    # Parent/Guardian information
    parent_full_name = models.CharField(max_length=200, verbose_name="Parent/Guardian Full Name")
    parent_relationship = models.CharField(max_length=50, verbose_name="Relationship to Child")
    parent_mobile = models.CharField(max_length=15, verbose_name="Mobile Number")
    parent_email = models.EmailField(verbose_name="Email Address")
    parent_occupation = models.CharField(max_length=100, verbose_name="Occupation")
    parent_nida = models.CharField(max_length=20, blank=True, verbose_name="NIDA Number (if any)")

    # Address
    region = models.CharField(max_length=100, verbose_name="Region")
    district = models.CharField(max_length=100, verbose_name="District")
    street = models.CharField(max_length=200, verbose_name="Street/Village")

    # Extra
    additional_info = models.TextField(blank=True, verbose_name="Additional Information")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return f"{self.child_first_name} {self.child_last_name} - {self.grade_applying_for}"


class HeroSlide(models.Model):
    image = models.ImageField(upload_to='hero_slides/', verbose_name="Slide Image")
    title = models.CharField(max_length=200, blank=True, help_text="Optional: Overrides the default hero title for this slide")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Optional: Overrides the default hero subtitle for this slide")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which slides appear")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self):
        return f"Slide {self.order}: {self.title or 'Untitled'}"


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return self.title


class Feature(models.Model):
    """Dynamic features/cards shown on the home page 'Why Choose Us?' section"""
    icon = models.CharField(max_length=50, default="bi-star", help_text="Bootstrap icon class (e.g. bi-book, bi-people)")
    title = models.CharField(max_length=200, help_text="Feature title")
    description = models.TextField(help_text="Feature description")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"

    def __str__(self):
        return self.title


class AboutInfo(models.Model):
    """About page content - mission, vision, stats, and paragraphs"""
    about_paragraph_1 = models.TextField(blank=True, default="", help_text="First about paragraph")
    about_paragraph_2 = models.TextField(blank=True, default="", help_text="Second about paragraph")
    about_paragraph_3 = models.TextField(blank=True, default="", help_text="Third about paragraph")
    about_paragraph_4 = models.TextField(blank=True, default="", help_text="Fourth about paragraph")
    mission = models.TextField(blank=True, default="", help_text="School mission statement")
    vision = models.TextField(blank=True, default="", help_text="School vision statement")
    stat_pupils = models.CharField(max_length=20, default="500+", help_text="Pupils count display (e.g. 500+)")
    stat_teachers = models.CharField(max_length=20, default="30+", help_text="Teachers count display (e.g. 30+)")
    stat_years = models.CharField(max_length=20, default="10+", help_text="Years established display (e.g. 10+)")

    class Meta:
        verbose_name = "About Page Content"
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return "About Page Settings"

    def save(self, *args, **kwargs):
        if not self.pk and AboutInfo.objects.exists():
            return
        super().save(*args, **kwargs)


class CoreValue(models.Model):
    """Core values shown on the about page"""
    icon = models.CharField(max_length=50, default="bi-star", help_text="Bootstrap icon class")
    title = models.CharField(max_length=200, help_text="Value title")
    description = models.TextField(help_text="Value description")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Core Value"
        verbose_name_plural = "Core Values"

    def __str__(self):
        return self.title


class ContactInfo(models.Model):
    """Contact information displayed on the contact page and footer"""
    address = models.CharField(max_length=300, default="Dar es Salaam, Tanzania")
    phone_1 = models.CharField(max_length=30, default="+255 712 345 678")
    phone_2 = models.CharField(max_length=30, blank=True, default="+255 712 345 679")
    email_1 = models.EmailField(default="info@behac.ac.tz")
    email_2 = models.EmailField(blank=True, default="admissions@behac.ac.tz")
    office_hours = models.CharField(max_length=200, default="Monday - Friday: 7:30 AM - 4:00 PM")
    saturday_hours = models.CharField(max_length=200, blank=True, default="Saturday: 8:00 AM - 12:00 PM")
    whatsapp = models.CharField(max_length=30, blank=True, default="+255 712 345 678")
    google_maps_url = models.URLField(blank=True, default="https://maps.google.com/?q=Dar+es+Salaam+Tanzania")
    facebook_url = models.URLField(blank=True, default="")
    instagram_url = models.URLField(blank=True, default="")
    twitter_url = models.URLField(blank=True, default="")
    whatsapp_url = models.URLField(blank=True, default="")

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return "Contact Settings"

    def save(self, *args, **kwargs):
        if not self.pk and ContactInfo.objects.exists():
            return
        super().save(*args, **kwargs)
