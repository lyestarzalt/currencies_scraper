import boto3
from botocore.exceptions import ClientError
from decouple import Config, RepositoryEnv, Csv
import json
import os
from typing import Dict, Any, List, Set
from utils.logger import get_logger

logger = get_logger("ConfigLogger")

# Load configuration
if os.path.exists(".env"):
    config = Config(RepositoryEnv(".env"))
else:
    config = Config(os.environ)

# Typed environment variables
API_BASE_URL: str = config("API_BASE_URL", default="") # type: ignore

SCRAPER_LAMBDAS: List[str] = config("SCRAPER_LAMBDAS", cast=Csv()) # type: ignore
EXCLUDED_CURRENCIES: Set[str] = config("EXCLUDED_CURRENCIES", cast=Csv()) # type: ignore
ENV: str = config("ENV") # type: ignore

logger.info(f"Running in {ENV} environment")


def get_firebase_secrets() -> Dict[str, Dict[str, Any]]:
    """
    Fetch Firebase secrets for staging and production environments from AWS Secrets Manager.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing Firebase secrets for staging and production environments.
    """
    region_name: str = "ap-southeast-1"
    secret_name: str = "FIREBASE_CREDENTIALS"
    session = boto3.session.Session() # type: ignore
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        logger.info("Successfully fetched secret")
    except ClientError as e:
        logger.error(f"Error fetching secret {secret_name}: {str(e)}")
        raise e

    secrets_dict: Dict[str, str] = json.loads(get_secret_value_response["SecretString"])
    firebase_secrets: Dict[str, Dict[str, Any]] = {
        "staging": json.loads(secrets_dict.get("FIREBASE_CREDENTIALS_STAGING", "{}")),
        "production": json.loads(
            secrets_dict.get("FIREBASE_CREDENTIALS_PRODUCTION", "{}")
        ),
    }
    return firebase_secrets


firebase_secrets: Dict[str, Dict[str, Any]] = get_firebase_secrets()
FIREBASE_CREDENTIALS: Dict[str, Any]

if ENV == "staging":
    FIREBASE_CREDENTIALS = firebase_secrets["staging"]
    logger.info("Loaded staging Firebase credentials")
elif ENV == "production":
    FIREBASE_CREDENTIALS = firebase_secrets["production"]
    logger.info("Loaded production Firebase credentials")
else:
    logger.error("Invalid environment specified")
    raise ValueError("Invalid environment specified")


def get_collection_name(base_name: str) -> str:
    """Return collection name based on the environment."""
    suffix: str = "_test" if ENV == "staging" else ""
    return f"{base_name}{suffix}"
