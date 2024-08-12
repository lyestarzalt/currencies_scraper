import boto3
from botocore.exceptions import ClientError
from decouple import Config, RepositoryEnv, Csv
import json
import os
from utils.logger import get_logger

logger = get_logger('ConfigLogger')

def get_firebase_secrets() -> dict:
    """Fetch Firebase secrets for staging and production environments from AWS Secrets Manager."""
    region_name = "ap-southeast-1"
    secret_name = 'FIREBASE_CREDENTIALS'
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        logger.info("Successfully fetched secret")
    except ClientError as e:
        logger.error(f"Error fetching secret {secret_name}: {str(e)}")
        raise e
    secrets_dict = json.loads(get_secret_value_response['SecretString'])
    firebase_secrets = {
        'staging': json.loads(secrets_dict.get('FIREBASE_CREDENTIALS_STAGING', '{}')),
        'production': json.loads(secrets_dict.get('FIREBASE_CREDENTIALS_PRODUCTION', '{}'))
    }
    return firebase_secrets

    
if os.path.exists('.env'):
    config = Config(RepositoryEnv('.env'))
else:
    config = Config(os.environ)

API_BASE_URL = config('API_BASE_URL')
SCRAPER_LAMBDAS = config('SCRAPER_LAMBDAS', cast=Csv())
EXCLUDED_CURRENCIES = config('EXCLUDED_CURRENCIES', cast=Csv())
ENV = config('ENV')

logger.info(f"Running in {ENV} environment")
firebase_secrets = get_firebase_secrets()

if ENV == 'staging':
    FIREBASE_CREDENTIALS = firebase_secrets['staging']
    logger.info("Loaded staging Firebase credentials")
elif ENV == 'production':
    FIREBASE_CREDENTIALS = firebase_secrets['production']
    logger.info("Loaded production Firebase credentials")
else:
    logger.error("Invalid environment specified")
    raise ValueError("Invalid environment specified")

def get_collection_name(base_name: str) -> str:
    """Return collection name based on the environment."""
    suffix = '_test' if ENV == 'staging' else ''
    return f"{base_name}{suffix}"
