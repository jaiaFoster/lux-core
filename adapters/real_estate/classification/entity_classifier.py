# adapters/real_estate/classification/entity_classifier.py
#
# Real Estate Adapter — Entity Classifier
#
# Determines whether a party record represents a likely real estate buyer
# and classifies the entity type. This logic is adapter-specific and
# should never live in Core.

import re

BUYER_KEYWORDS = [
    "LLC", "INC", "CORP", "CORPORATION", "HOLDINGS", "INVESTMENTS",
    "PROPERTIES", "PROPERTY", "CAPITAL", "HOMES", "REALTY",
    "PARTNERS", "TRUST", "GROUP", "VENTURES"
]

ENTITY_TYPE_MAP = {
    "LLC": "llc",
    "INC": "corporation",
    "CORP": "corporation",
    "CORPORATION": "corporation",
    "TRUST": "trust",
    "HOLDINGS": "llc",
    "INVESTMENTS": "llc",
    "CAPITAL": "llc",
    "PARTNERS": "partnership",
}


def is_likely_buyer(name: str) -> bool:
    """Returns True if the name matches known investor entity patterns."""
    normalized = name.upper()
    return any(kw in normalized for kw in BUYER_KEYWORDS)


def classify_entity_type(name: str) -> str:
    """
    Returns a normalized entity type string.
    Defaults to 'individual' if no business keyword is matched.
    """
    normalized = name.upper()
    for keyword, entity_type in ENTITY_TYPE_MAP.items():
        if keyword in normalized:
            return entity_type
    return "individual"


def get_matched_keyword(name: str) -> str:
    """Returns the first matching keyword, or empty string."""
    normalized = name.upper()
    for kw in BUYER_KEYWORDS:
        if kw in normalized:
            return kw
    return ""


def normalize_name(name: str) -> str:
    """Uppercase, strip extra whitespace, remove punctuation for deduplication."""
    name = name.upper().strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name
