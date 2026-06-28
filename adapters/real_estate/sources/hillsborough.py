# adapters/real_estate/sources/hillsborough.py
#
# Real Estate Adapter — Hillsborough County Source
#
# All Hillsborough-specific URL patterns, file naming conventions,
# and directory listing logic lives here.
# Migrated from AIR hillsborough_buyer_scraper_mvp.py.

from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from adapters.real_estate.ingestion.downloader import download_file, get_cache_path
import requests
from core.logger import get_logger

logger = get_logger(__name__)

BASE_URL = "https://publicrec.hillsclerk.com/OfficialRecords/DailyIndexes/"
COUNTY = "hillsborough"

FILE_PREFIXES = {
    "D": "document",
    "P": "party",
    "M": "mapping"
}


def list_available_files(date: datetime) -> list:
    """
    Fetch the directory listing for a given date and return
    matching D/P/M filenames.
    """
    try:
        response = requests.get(BASE_URL, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        date_str = date.strftime("%Y%m%d")
        files = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if date_str in href:
                for prefix in FILE_PREFIXES:
                    if href.startswith(prefix) or f"/{prefix}" in href:
                        files.append(href)
        return files
    except Exception as e:
        logger.error(f"Failed to list files for {date}: {e}")
        return []


def download_county_files(date: datetime, refresh: bool = False) -> list:
    """
    Download all D/P/M files for a given date.
    Returns list of local file paths that succeeded.
    """
    available = list_available_files(date)
    downloaded = []

    for filename in available:
        url = BASE_URL + filename
        dest = get_cache_path(COUNTY, filename)
        success = download_file(url, dest, refresh=refresh)
        if success:
            downloaded.append(dest)

    return downloaded
