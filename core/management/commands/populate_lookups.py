from django.core.management.base import BaseCommand
from academics.models import ClassLevel, Subject
from locations.models import Region, District
from students.models import Relationship
from finance.models import FeeCategory
from core.models import AcademicYear, Term

class Command(BaseCommand):
    help = 'Populate basic lookup data for Behac International Academy'

    def handle(self, *args, **options):
        self.stdout.write("Populating lookup data...")

        # ---------- Class Levels (Baby, Middle, Pre 1, Standard 1-6) ----------
        class_levels = [
            ('Baby Class', 'PRE', 1),
            ('Middle Class', 'PRE', 2),
            ('Pre 1', 'PRE', 3),
            ('Standard 1', 'PRIMARY', 4),
            ('Standard 2', 'PRIMARY', 5),
            ('Standard 3', 'PRIMARY', 6),
            ('Standard 4', 'PRIMARY', 7),
            ('Standard 5', 'PRIMARY', 8),
            ('Standard 6', 'PRIMARY', 9),
        ]
        for name, level_type, order in class_levels:
            obj, created = ClassLevel.objects.get_or_create(
                name=name,
                defaults={'level_type': level_type, 'order': order}
            )
            if created:
                self.stdout.write(f"  Created ClassLevel: {name}")

        # ---------- Subjects ----------
        subjects = [
            ('MATH', 'Mathematics'),
            ('ENG', 'English'),
            ('KISW', 'Kiswahili'),
            ('SCI', 'Science'),
            ('SST', 'Social Studies'),
            ('RE', 'Religious Education'),
            ('ICT', 'Information Technology'),
            ('ART', 'Art & Crafts'),
            ('PE', 'Physical Education'),
        ]
        for code, name in subjects:
            obj, created = Subject.objects.get_or_create(code=code, defaults={'name': name})
            if created:
                self.stdout.write(f"  Created Subject: {name}")

        # ---------- Regions and Districts (Tanzania example) ----------
        regions_districts = {
            'Dar es Salaam': ['Ilala', 'Kinondoni', 'Temeke', 'Ubungo', 'Kigamboni'],
            'Arusha': ['Arusha City', 'Arusha DC', 'Meru', 'Monduli', 'Ngorongoro'],
            'Mwanza': ['Ilemela', 'Nyamagana', 'Magharibi', 'Kwimba', 'Misungwi'],
            'Mbeya': ['Mbeya City', 'Mbeya DC', 'Rungwe', 'Kyela', 'Mbozi'],
            'Zanzibar Urban': ['Magharibi', 'Mjini', 'West A', 'West B'],
        }
        for region_name, districts in regions_districts.items():
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                self.stdout.write(f"  Created Region: {region_name}")
            for district_name in districts:
                district, created = District.objects.get_or_create(name=district_name, region=region)
                if created:
                    self.stdout.write(f"    Created District: {district_name} ({region_name})")

        # ---------- Relationships ----------
        relationships = [
            'Father', 'Mother', 'Brother', 'Sister', 'Uncle', 'Aunt',
            'Grandfather', 'Grandmother', 'Cousin', 'Guardian', 'Other'
        ]
        for rel in relationships:
            obj, created = Relationship.objects.get_or_create(name=rel)
            if created:
                self.stdout.write(f"  Created Relationship: {rel}")

        # ---------- Fee Categories ----------
        fee_categories = [
            ('School Fee', 50000.00, True),
            ('Buns & Transport', 30000.00, True),
            ('Sweater', 15000.00, False),
            ('T-Shirt', 10000.00, False),
            ('Uniform', 45000.00, False),
            ('Socks', 5000.00, False),
            ('Ream', 8000.00, False),
            ('Farm Dress', 20000.00, False),
            ('Health Care', 25000.00, True),
            ('Graduation', 35000.00, False),
            ('Report Book', 5000.00, False),
        ]
        for name, amount, recurring in fee_categories:
            obj, created = FeeCategory.objects.get_or_create(
                name=name,
                defaults={'default_amount': amount, 'is_recurring': recurring}
            )
            if created:
                self.stdout.write(f"  Created FeeCategory: {name}")

        # ---------- Academic Year & Terms ----------
        current_year, created = AcademicYear.objects.get_or_create(
            name='2025-2026',
            defaults={
                'start_date': '2025-01-15',
                'end_date': '2025-12-15',
                'is_current': True
            }
        )
        if created:
            self.stdout.write("  Created Academic Year: 2025-2026")
            terms = [
                ('Term 1', '2025-01-15', '2025-04-15'),
                ('Term 2', '2025-05-01', '2025-08-30'),
                ('Term 3', '2025-09-15', '2025-12-15'),
            ]
            for name, start, end in terms:
                Term.objects.get_or_create(
                    academic_year=current_year,
                    name=name,
                    defaults={'start_date': start, 'end_date': end, 'is_active': (name == 'Term 1')}
                )
                self.stdout.write(f"    Created Term: {name}")

        self.stdout.write(self.style.SUCCESS("Lookup data population complete."))