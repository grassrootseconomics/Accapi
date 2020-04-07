from cicdashboard.settings.common import *
# import boto3
# import json

# secrets_client = boto3.client('secretsmanager')
# secret_arn = 'arn:aws:secretsmanager:eu-central-1:847108109661:secret:/prod/dbcredentials-OEPfTY'
# auth_token = secrets_client.get_secret_value(SecretId=secret_arn).get('SecretString')
# d = json.loads(auth_token)
# print(d['password'])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

# SECURITY WARNING: update this when you have the production host

# ALLOWED_HOSTS = [
# #'0.0.0.0', 
# #'localhost', 
# 'https://dashboard.sarafu.network', 
# 'dashboard.sarafu.network',
# 'http://cic-dashboard-frontend-webpage-prod.s3-website.eu-central-1.amazonaws.com',
# 'cic-dashboard-frontend-webpage-prod.s3-website.eu-central-1.amazonaws.com',
# 'https://iqr3ivy96j.execute-api.eu-central-1.amazonaws.com/prod/graphql/'
# ]

ALLOWED_HOSTS =['*']
CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = [
# #'http://0.0.0.0:8080', 
# #'http://localhost:8080',
# 'https://dashboard.sarafu.network',
# 'http://cic-dashboard-frontend-webpage-prod.s3-website.eu-central-1.amazonaws.com',
# 'https://iqr3ivy96j.execute-api.eu-central-1.amazonaws.com/prod/graphql/'
# ]

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'cic_dashboard',
#         'USER': d['username'],
#         'PASSWORD': d['password'],
#         'HOST': d['host'],
#         'PORT': d['port'],
#     }
# }

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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        #"LOCATION": "redis://127.0.0.1:6379/1",
        "LOCATION": 'redis://cic-prod-redis.13yrwl.ng.0001.euc1.cache.amazonaws.com:6379/1',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "dashboard"
    }
}

# change this to false once testing is complete
IS_TESTING = False
