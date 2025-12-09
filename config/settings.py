
#? config/settings.py
import os
from pathlib import Path
from decouple import config

#* Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

#* SECURITY WARNING: Dejar la llave de producción en el .env!
SECRET_KEY = config('SECRET_KEY')

#* SECURITY WARNING: No correr con debug en producción!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

#* Definición de aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Para formateo de números (intcomma)

    #? Apps propias
    'apps.core',
    'apps.services',
    'apps.products',
    'apps.contact',
    'apps.accounts',
    'apps.payments',

    #? Third party apps
    'rest_framework',
]

#* Custom User Model
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #? Context processor personalizado para el carrito
                'apps.products.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

#* Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

#* Contraseñas de validación
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

#* Configuración Colombia
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

#* Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

#* Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

#* Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#* Email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

#* Celery Configuration (para sincronización API)
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

#* API Mayorista
WHOLESALER_API_URL = config('WHOLESALER_API_URL', default='')
WHOLESALER_API_KEY = config('WHOLESALER_API_KEY', default='')

#* Configuración de Autenticación
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

#* Configuración de Sesión
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True en producción

#* Configuración de Seguridad para Producción
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

#* Configuración Pillow para imágenes
# Pillow ya está instalado como dependencia de Django para ImageField

#* Wompi Payment Gateway Configuration
# Llaves de prueba oficiales de Wompi (Sandbox)
# IMPORTANTE: Cambiar estas llaves en producción usando variables de entorno
config('EMAIL_HOST')
WOMPI_PUBLIC_KEY = config('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY = config('WOMPI_PRIVATE_KEY')
WOMPI_INTEGRITY_KEY = config('WOMPI_INTEGRITY_KEY')
WOMPI_ENVIRONMENT = config('WOMPI_ENVIRONMENT')  # sandbox or production
WOMPI_API_BASE_URL = 'https://sandbox.wompi.co/v1' if WOMPI_ENVIRONMENT == 'sandbox' else 'https://production.wompi.co/v1'
WOMPI_EVENTS_SECRET = config('WOMPI_EVENTS_SECRET')