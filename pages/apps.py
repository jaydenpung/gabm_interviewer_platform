from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'

    def ready(self):
        # Import here to avoid circular imports
        from django.core.management import call_command
        from django.db import connection
        
        # Check if database is properly migrated before creating admin
        try:
            # Only run if we can access the database and tables exist
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='pages_participant';"
                )
                if cursor.fetchone():
                    # Call the management command to create default admin
                    call_command('create_default_admin')
        except Exception as e:
            # Silently pass if database isn't ready yet (during migrations, etc.)
            pass
