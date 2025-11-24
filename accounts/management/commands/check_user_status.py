from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class Command(BaseCommand):
    help = 'Check status of users and optionally reset passwords'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Reset password for users with login issues',
        )
        parser.add_argument(
            '--new-password',
            type=str,
            default='newpassword123',
            help='New password to set when resetting',
        )

    def handle(self, *args, **options):
        reset_password = options['reset_password']
        new_password = options['new_password']

        users = User.objects.all()
        self.stdout.write(f"Checking {users.count()} users...")

        for user in users:
            self.stdout.write(f"User: {user.email}")
            self.stdout.write(f"  is_active: {user.is_active}")
            # We cannot check password validity directly, but we can note if password is set
            if not user.password:
                self.stdout.write("  WARNING: No password set!")
            else:
                self.stdout.write("  Password is set.")

            if reset_password:
                user.set_password(new_password)
                user.save()
                self.stdout.write(f"  Password reset to: {new_password}")

        self.stdout.write("User status check complete.")
