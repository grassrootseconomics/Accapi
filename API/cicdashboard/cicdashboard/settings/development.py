from cicdashboard.settings.common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1$qpv*d%uoex8xe!as6r0#3s@kz1)e&tpb5a@@@)y#dr(5_**t'
#SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASS'],
            'HOST': os.environ['DB_HOST'],
            'PORT': '5432',
    }
}

# Cache time to live in seconds.
CACHE_TTL = 30
CACHE_ENABLED = False

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        #"LOCATION": "redis://127.0.0.1:6379/1",
        "LOCATION": "redis://cic-dev-redis.13yrwl.0001.euc1.cache.amazonaws.com:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "dashboard"
    }
}

# change this to false once testing is complete
IS_TESTING = True
