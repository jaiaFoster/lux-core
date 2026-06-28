# adapters/real_estate/ingestion/downloader.py
#
# Real Estate Adapter — Downloader
#
# Handles downloading and caching of public record files from county sources.
# Migrated and refactored from AIR (hillsborough_buyer_scraper_mvp.py).
# County-specific logic lives in adapters/real_estate/sources/.

import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from core.logger import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = Path("data/raw")


def get_cache_path(county: str, filename: str) -> Path:
    path = RAW_DATA_DIR / county
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


def download_file(url: str, dest_path: Path, refresh: bool = False) -> bool:
    """
    Download a file to dest_path. Skip if cached unless refresh=True.
    Returns True on success, False on failure.
    """
    if dest_path.exists() and not refresh:
        return True

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        dest_path.write_bytes(response.content)
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False


def date_range(start: datetime, end: datetime):
    """Yield dates from start to end inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
