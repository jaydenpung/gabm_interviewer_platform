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
            # Use Django's database-agnostic approach to check if table exists
            with connection.cursor() as cursor:
                table_names = connection.introspection.table_names(cursor)
                if 'pages_participant' in table_names:
                    # Call the management command to create default admin
                    call_command('create_default_admin')
        except Exception as e:
            # Silently pass if database isn't ready yet (during migrations, etc.)
            pass
