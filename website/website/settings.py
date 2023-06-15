from pathlib import Path
from decouple import Csv, config
from dotenv import load_dotenv
from django.urls import reverse_lazy

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-a!d^4-stv3t6xbpblz235z7gs@k+!iu95tf1bc&ky^a8l__51o'
)

DEBUG = config('DEBUG', cast=bool, default=True)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=Csv(),
    default='127.0.0.1'
)

SITE_ID = 1

MODE = config('MODE', cast=str, default='dev')

INSTALLED_APPS = [
    'account.apps.AccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',

    'blog.apps.BlogConfig', 
    'core.apps.CoreConfig',
    'vookmarks.apps.VookmarksConfig',
    'actions.apps.ActionsConfig', 
    'shop.apps.ShopConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    
    'sorl.thumbnail', #IMAGE
    'taggit', #TAGS # https://github.com/jazzband/django-taggit
    'social_django', #OAUTH2
    'django_extensions', #SSL #https://django-extensions.readthedocs.io/en/latest/
    'debug_toolbar', #TOOLBAR #https://django-debug-toolbar.readthedocs.io/en/latest/
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES_DIR = BASE_DIR / 'templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

#Setting Database (SQLite3 or PostgreSQL)
if MODE == 'dev':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE'),
            'NAME': config('DB_NAME'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
        },
        'blog': {
            'ENGINE': config('DB_ENGINE'),
            'NAME': config('DB_NAME'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
        }
    }

#Setting AUTHENTICATION for Users
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'account.authentication.EmailAuthBackend',
    'social_core.backends.yandex.YandexOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.github.GithubOAuth2',
]

AUTH_USER_MODEL = 'account.User'

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

# Setting language code
LANGUAGE_CODE = 'ru-RU'
USE_I18N = True

# Setting time-zone
TIME_ZONE = 'Europe/Samara'
USE_TZ = True

# Setting auto-generated primary key for Django model
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Setting static and media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Setting cache images
THUMBNAIL_CACHE_BACKEND = 'django.core.cache.backends.filebased.FileBasedCache'
THUMBNAIL_CACHE_LOCATION = BASE_DIR / 'thumb_cache'
CLEANUP_AUTO = True
CLEANUP_KEEP_EXTENSIONS = ['jpg', 'jpeg', 'png']

# Default email-server
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

# Setting Yandex email-server
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', cast=str, default='your-email@yandex.ru')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', cast=str, default='your-password')

DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', cast=str, default='your-email@yandex.ru')
SERVER_EMAIL = config('EMAIL_HOST_USER', cast=str, default='your-email@yandex.ru')

# Action Users LOGIN and LOGOUT
LOGIN_REDIRECT_URL = reverse_lazy("blog:post_list")
LOGIN_URL = reverse_lazy("login")
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'blog:post_list'

# Setting password hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# Setting CSRF-token:
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Social Auth 
SOCIAL_AUTH_JSONFIELD_ENABLED = True #When using PosgreSQL:
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
]

# Auth via Yandex
SOCIAL_AUTH_YANDEX_OAUTH2_KEY = config('YANDEX_KEY')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = config('YANDEX_SECRET')
SOCIAL_AUTH_YANDEX_OAUTH2_SCOPE = []

# Auth via Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('GOOGLE_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('GOOGLE_SECRET')

# Auth via VK.ru
SOCIAL_AUTH_VK_OAUTH2_KEY = config('VK_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = config('VK_SECRET')
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['username']

# Auth via GitHub
SOCIAL_AUTH_GITHUB_KEY = config('GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = config('GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = ['username']

if DEBUG:
    import mimetypes
    mimetypes.add_type('application/javascript', '.js', True)
    mimetypes.add_type('text/css', '.css', True)

ABSOLUTE_URL_OVERRIDES = {
    'account.User': lambda u: reverse_lazy('profile', args=[u.username])
}

# Setting Debug-toolbar:
INTERNAL_IPS = [
    '127.0.0.1',
]

# Setting Redis:
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Setting Cart:
CART_SESSION_ID = 'cart'