import os
from pathlib import Path
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações diretas (sem decouple)
SECRET_KEY = 'django-insecure-!@#$%^&*()1234567890abcdefghijklmnopqrstuvwxyz'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'main',
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

ROOT_URLCONF = 'esaving.urls'

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

WSGI_APPLICATION = 'esaving.wsgi.application'

try:
    from pymongo import MongoClient
    MONGODB_URI = 'mongodb://localhost:27017/'
    MONGODB_DB_NAME = 'e_saving_db'
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Testar a conexão
    mongo_client.server_info()
    MONGO_DB = mongo_client[MONGODB_DB_NAME]
    print(f"Conectado ao MongoDB: {MONGODB_DB_NAME}")
    
    # Criar coleções se não existirem
    if 'users' not in MONGO_DB.list_collection_names():
        MONGO_DB.create_collection('users')
        # Criar índices
        MONGO_DB.users.create_index('username', unique=True)
        MONGO_DB.users.create_index('email', unique=True)
        MONGO_DB.users.create_index('cpf_cnpj', unique=True)
    
    if 'coletas' not in MONGO_DB.list_collection_names():
        MONGO_DB.create_collection('coletas')
        
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    MONGO_DB = None 

# Database SQLite para auth do Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/area_parceiro/'
LOGOUT_REDIRECT_URL = '/'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "main/static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'