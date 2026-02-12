from pathlib import Path
from decouple import config
from dotenv import load_dotenv 
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env explicito y FORZAR sobreescritura de variables del sistema
# Esto soluciona el problema de que Windows recuerde variables viejas
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path, override=True)

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')

DEBUG = config('DEBUG', default=True, cast=bool)

# API KEYS
VIRUSTOTAL_API_KEY = config('VIRUSTOTAL_API_KEY', default=None)
METADEFENDER_API_KEY = config('METADEFENDER_API_KEY', default=None)
GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)
# Si no hay key especifica para GSB, usamos la de Gemini (Son la misma en Google Cloud)
GSB_API_KEY = config('GOOGLE_SAFE_BROWSING_API_KEY', default=GEMINI_API_KEY)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'incidents',
    'users',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_TZ = True

STATIC_URL = 'static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# LOGGING: Mostrar INFO en consola para debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'incidents': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'services': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PRODUCCIÓN - NO MODIFICAR MANUALMENTE
# Las variables se leen desde variables de entorno en Render
# ═══════════════════════════════════════════════════════════
import os as _os

# Override SECRET_KEY desde entorno si existe
_secret_key = _os.environ.get('SECRET_KEY')
if _secret_key:
    SECRET_KEY = _secret_key

# Modo Debug (False en producción)
_debug_env = _os.environ.get('DEBUG', 'False')
DEBUG = _debug_env == 'True'

    # Permitir todo en producción temporalmente para descartar errores de Host
    ALLOWED_HOSTS = ['*']

    # CORS: dominios del frontend permitidos
    _cors_origins = _os.environ.get('CORS_ALLOWED_ORIGINS', '')
    if _cors_origins:
        CORS_ALLOWED_ORIGINS = [
            origin.strip() for origin in _cors_origins.split(',')
        ]
        # CSRF necesita scheme (https://)
        CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Base de datos: SQLite con ruta absoluta para Render
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# ═══════════════════════════════════════════════════════════
