from .base import *

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jlsjc#5zbq6s%bfiihcug&$50#09v*#%ntagd&!v^c&t_wl5a+'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

print("DATABASE FILE:", os.path.abspath(DATABASES['default']['NAME']))