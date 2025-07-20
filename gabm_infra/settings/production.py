from .base import *

# Production specific settings
# DEBUG setting is inherited from base.py (respects environment variable)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Security settings for production
SECURE_SSL_REDIRECT = False  # Set to True when using HTTPS
SECURE_HSTS_SECONDS = 0      # Enable when using HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = False     # Set to True when using HTTPS