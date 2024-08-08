from decouple import Config, RepositoryEnv, Csv
import json
import os

if os.path.exists('.env'):
    config = Config(RepositoryEnv('.env'))
else:
    config = Config(os.environ)
API_BASE_URL = config('API_BASE_URL')
SCRAPER_LAMBDAS = config('SCRAPER_LAMBDAS', cast=Csv())

EXCLUDED_CURRENCIES = config('EXCLUDED_CURRENCIES', cast=Csv())
ENV = config('ENV')

if ENV == 'staging':
    FIREBASE_CREDENTIALS = json.loads(config('FIREBASE_CREDENTIALS_STAGING'))
elif ENV == 'production':
    FIREBASE_CREDENTIALS = json.loads(config('FIREBASE_CREDENTIALS_PRODUCTION'))
else:
    raise ValueError("Invalid environment specified.")
