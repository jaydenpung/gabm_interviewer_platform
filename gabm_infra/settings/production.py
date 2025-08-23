from .base import *

# Production specific settings
# DEBUG setting is inherited from base.py (respects environment variable)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# CSRF Trusted Origins - required for external domains like ngrok
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8010',
    'http://127.0.0.1:8010',
    'https://96671d6e3739.ngrok-free.app',
    'https://117eea970c63.ngrok-free.app',
    'https://docker-host.java-elevator.ts.net',
]

# Security settings for production
SECURE_SSL_REDIRECT = True  # Set to True when using HTTPS
SECURE_HSTS_SECONDS = 1      # Enable when using HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True  # Set to True when using HTTPS
CSRF_COOKIE_SECURE = True     # Set to True when using HTTPS