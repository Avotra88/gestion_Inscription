import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Utilisation de variables d'environnement pour des informations sensibles comme la SECRET_KEY
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret-key')  # Remplacez 'default-secret-key' par votre clé par défaut si nécessaire

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Définir STATICFILES_DIRS pour inclure d'autres répertoires statiques
STATICFILES_DIRS = [
     os.path.join(BASE_DIR, "static"),
]

# Dossier où les fichiers statiques seront collectés lors de `collectstatic`
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Quick-start development settings - unsuitable for production
DEBUG = True  # Mettez `False` en production
ALLOWED_HOSTS = []  # Ajouter des hôtes autorisés pour la production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inscriptions',  # Assurez-vous que votre application inscriptions est bien ajoutée ici
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_inscriptions.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_inscriptions.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Utilisez le backend MySQL
        'NAME': os.getenv('DB_NAME', 'gestion_inscription'),  # Utilisez une variable d'environnement pour la base de données
        'USER': os.getenv('DB_USER', 'root'),  # Utilisateur MySQL
        'PASSWORD': os.getenv('DB_PASSWORD', '123456789'),  # Utilisez une variable d'environnement pour le mot de passe
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Si la base de données est sur la même machine
        'PORT': os.getenv('DB_PORT', '3306'),  # Le port MySQL par défaut
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL redirection après login / logout
LOGIN_REDIRECT_URL = '/dashboard/'  # Remplace par l'URL de ton tableau de bord
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Configuration des messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'