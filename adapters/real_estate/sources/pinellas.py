# adapters/real_estate/sources/pinellas.py
#
# Real Estate Adapter — Pinellas County Source
#
# Stub. Implement after Hillsborough pipeline is validated.
#
# Source: https://www.pcpao.gov/tools-data/data-downloads/raw-database-files
#
# Target tables:
#   RP_OS_SALES         — sales data (grantee/buyer, grantor/seller, price, date)
#   RP_OS_SITE_ADDRESS  — property address
#   RP_OS_OWNER         — owner data
#   RP_OS_OWNER_MAIL    — owner mailing data
#   RP_OS_PROPERTY_VALUE — property value and use fields


def download_county_files(date, refresh=False):
    raise NotImplementedError("Pinellas source not yet implemented.")
