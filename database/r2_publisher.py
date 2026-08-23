import json
from datetime import datetime, timedelta
from typing import Dict, List

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from models.currency import Currency
from utils.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET,
    R2_ENDPOINT_URL,
    R2_SECRET_ACCESS_KEY,
    get_r2_key_prefix,
)
from utils.logger import get_logger

logger = get_logger("R2Publisher")

# Cache the "latest" files at the edge for a day, allow client caching for an
# hour, and let the edge serve stale-while-revalidating if origin is briefly down.
_LATEST_CACHE_CONTROL = (
    "public, max-age=3600, s-maxage=86400, stale-while-revalidate=86400"
)
_HISTORY_CACHE_CONTROL = _LATEST_CACHE_CONTROL

_CORE_CURRENCY_CODES = {
    "AED",
    "CAD",
    "CHF",
    "CNY",
    "EUR",
    "GBP",
    "MAD",
    "SAR",
    "TND",
    "TRY",
    "USD",
}


class R2Publisher:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name="auto",
            config=BotoConfig(signature_version="s3v4", retries={"max_attempts": 3}),
        )
        self._bucket = R2_BUCKET
        self._prefix = get_r2_key_prefix()

    def upload_exchange_rates(
        self, currencies: List[Currency], market: str
    ) -> None:
        """Write the latest rates for a market ('parallel' or 'official') to R2."""
        if market not in {"parallel", "official"}:
            raise ValueError(f"market must be 'parallel' or 'official', got {market!r}")

        rates: Dict[str, Dict[str, object]] = {
            c.currencyCode: {
                "currencyCode": c.currencyCode,
                "name": c.name,
                "symbol": c.symbol,
                "flag": c.flag,
                "buy": c.buy,
                "sell": c.sell,
                "date": c.update_date,
                "is_core": c.is_core,
            }
            for c in currencies
        }

        payload = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "rates": rates,
        }
        key = f"{self._prefix}/{market}/latest.json"
        self._put_json(key, payload, _LATEST_CACHE_CONTROL)
        logger.info(
            "Uploaded %s rates to R2 (%d entries) at key=%s",
            market,
            len(rates),
            key,
        )

    def update_currency_trends(self, core_currencies: List[Currency]) -> None:
        """Read-modify-write today's buy rate into each core currency's history file.

        Mirrors FirestoreManager.update_currency_trends: 730-day rolling window,
        keyed by ISO date. Non-core currencies are ignored.
        """
        current_date = datetime.now().date().strftime("%Y-%m-%d")
        cutoff_date = (
            datetime.now().date() - timedelta(days=730)
        ).strftime("%Y-%m-%d")

        for currency in core_currencies:
            if currency.currencyCode not in _CORE_CURRENCY_CODES:
                continue

            key = f"{self._prefix}/history/{currency.currencyCode}.json"
            existing = self._get_json(key) or {}
            existing[current_date] = currency.buy

            filtered = {
                date_str: rate
                for date_str, rate in existing.items()
                if date_str >= cutoff_date
            }
            self._put_json(key, filtered, _HISTORY_CACHE_CONTROL)

        logger.info(
            "Updated currency trends on R2 for %d core currencies.",
            len(_CORE_CURRENCY_CODES),
        )

    def _put_json(
        self, key: str, payload: object, cache_control: str
    ) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=body,
                ContentType="application/json",
                CacheControl=cache_control,
            )
        except ClientError as e:
            logger.error("R2 put_object failed for key=%s: %s", key, e, exc_info=True)
            raise

    def _get_json(self, key: str) -> Dict[str, object] | None:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in {"NoSuchKey", "404"}:
                return None
            logger.error("R2 get_object failed for key=%s: %s", key, e, exc_info=True)
            raise
        return json.loads(response["Body"].read())
