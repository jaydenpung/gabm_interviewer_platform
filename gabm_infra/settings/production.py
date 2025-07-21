from .base import *

# Production specific settings
# DEBUG setting is inherited from base.py (respects environment variable)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Security settings for production
SECURE_SSL_REDIRECT = True  # Set to True when using HTTPS
SECURE_HSTS_SECONDS = 1      # Enable when using HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = True     # Set to True when using HTTPS