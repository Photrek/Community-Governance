import os
import shutil
from datetime import datetime, timedelta
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Deletes expired sessions and temporary directories based on settings.SESSION_COOKIE_AGE.'

    def handle(self, *args, **options):
        # Call Django's built-in clearsessions command to delete database entries
        call_command('clearsessions')
        self.stdout.write(self.style.SUCCESS(f'Called "python manage.py clearsessions"'))

        # Delete temporary folders
        default_expiry = 2 * 60 * 60
        current_time = datetime.now()

        temp_directory_path = settings.SWAE_TEMP_DIR
        try:
            expiry_seconds = settings.SESSION_COOKIE_AGE
        except Exception:
            expiry_seconds = default_expiry

        for root, dirs, files in os.walk(temp_directory_path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                dir_creation_time = datetime.fromtimestamp(os.path.getctime(dir_path))
                dt = current_time - dir_creation_time
                if dt > timedelta(seconds=expiry_seconds):
                    shutil.rmtree(dir_path)
                    self.stdout.write(self.style.SUCCESS(f'Deleted temporary directory: {dir_path}'))