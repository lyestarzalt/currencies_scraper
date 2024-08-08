import boto3
from botocore.exceptions import ClientError
from decouple import Config, RepositoryEnv, Csv
import json
import os
from utils.logger import get_logger

logger = get_logger('ConfigLogger')

def get_secret(secret_name: str, region_name: str = "ap-southeast-1") -> str:
    """Fetch secret value from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        logger.info(f"Successfully fetched secret for {secret_name}")
    except ClientError as e:
        logger.error(f"Error fetching secret {secret_name}")
        raise e

    return get_secret_value_response['SecretString']

if os.path.exists('.env'):
    config = Config(RepositoryEnv('.env'))
else:
    config = Config(os.environ)

API_BASE_URL = config('API_BASE_URL')
SCRAPER_LAMBDAS = config('SCRAPER_LAMBDAS', cast=Csv())
EXCLUDED_CURRENCIES = config('EXCLUDED_CURRENCIES', cast=Csv())
ENV = config('ENV')

logger.info(f"Running in {ENV} environment")

if ENV == 'staging':
    try:
        FIREBASE_CREDENTIALS = json.loads(get_secret('FIREBASE_CREDENTIALS_STAGING'))
        logger.info("Loaded staging Firebase credentials")
    except Exception as e:
        logger.error(f"Error loading staging Firebase credentials")
        raise
elif ENV == 'production':
    try:
        FIREBASE_CREDENTIALS = json.loads(get_secret('FIREBASE_CREDENTIALS_PRODUCTION'))
        logger.info("Loaded production Firebase credentials")
    except Exception as e:
        logger.error(f"Error loading production Firebase credentials")
        raise
else:
    logger.error("Invalid environment specified")
    raise ValueError("Invalid environment specified")
