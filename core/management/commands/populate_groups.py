from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create user groups and assign permissions for Behac International Academy'

    def handle(self, *args, **options):
        self.stdout.write("Creating groups...")

        # Define groups and their permissions (codename only)
        groups_permissions = {
            'Parent': [
                # View own children (custom permission – we'll create it)
                'view_own_student',
                # Can view results, payments, behavior (read‑only)
                'view_result', 'view_payment', 'view_behaviorrecord',
            ],
            'Teacher': [
                # Can add, change, view results, behavior, attendance
                'add_result', 'change_result', 'view_result',
                'add_behaviorrecord', 'change_behaviorrecord', 'view_behaviorrecord',
                'add_attendance', 'change_attendance', 'view_attendance',
                'view_student',  # can see student list (read‑only)
            ],
            'Accountant': [
                # Fee management
                'add_feecategory', 'change_feecategory', 'view_feecategory',
                'add_feestructure', 'change_feestructure', 'view_feestructure',
                'add_payment', 'change_payment', 'view_payment',
                'view_student',  # to link payments to students
            ],
            'Admin': [
                # All permissions for students, staff, academics, finance, behavior
                # We'll assign all permissions dynamically later, or use is_superuser
            ],
            'Owner': [],  # Owner is superuser, has all permissions
        }

        # Get or create groups
        for group_name in groups_permissions.keys():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"  Created group: {group_name}")
            else:
                self.stdout.write(f"  Group already exists: {group_name}")

        # Assign permissions (except Admin & Owner – they get full access via superuser flag)
        # For simplicity, we assign common permissions. Admin can be superuser.
        # Owner will be superuser manually.

        # Get all available permissions from all apps
        all_perms = Permission.objects.all()
        perm_dict = {f"{p.content_type.app_label}.{p.codename}": p for p in all_perms}

        # Helper to assign permissions to a group
        def assign_perms(group_name, codenames):
            group = Group.objects.get(name=group_name)
            for codename in codenames:
                # Try to find the permission
                perm = None
                for full, p in perm_dict.items():
                    if p.codename == codename:
                        perm = p
                        break
                if perm:
                    group.permissions.add(perm)
                    self.stdout.write(f"    Assigned {codename} to {group_name}")
                else:
                    self.stdout.write(f"    Warning: Permission {codename} not found")

        # Assign permissions for Parent, Teacher, Accountant
        assign_perms('Parent', groups_permissions['Parent'])
        assign_perms('Teacher', groups_permissions['Teacher'])
        assign_perms('Accountant', groups_permissions['Accountant'])

        # For Admin: assign all permissions (or make superuser)
        admin_group = Group.objects.get(name='Admin')
        admin_group.permissions.set(all_perms)  # give everything
        self.stdout.write("  Assigned all permissions to Admin group")

        # For Owner: typically a superuser, no group permissions needed
        self.stdout.write(self.style.SUCCESS("Groups and permissions populated."))
        self.stdout.write("Note: Owner and Admin users should be created as superusers (is_superuser=True) for full access.")
        