# core/models/entities.py
#
# LUX Core Entity Schemas
#
# These are the canonical data structures that Core operates on.
# Adapters are responsible for transforming their source data into these schemas.
# Core never reads raw adapter data directly.

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Participant:
    """
    Any entity that can be a party to a transaction.
    In real estate: a buyer, seller, investor, LLC, individual owner.
    In other markets: a vendor, acquirer, counterparty, etc.
    """
    id: str
    name: str
    normalized_name: str
    participant_type: str           # e.g. "individual", "llc", "corporation", "trust"
    source_adapter: str             # e.g. "real_estate"
    source_county: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    confidence: str = "LOW"         # LOW / MEDIUM / HIGH
    metadata: dict = field(default_factory=dict)


@dataclass
class Asset:
    """
    Any asset that can be transacted.
    In real estate: a property.
    In other markets: a business, vehicle, equipment, etc.
    """
    id: str
    asset_type: str                 # e.g. "residential_property", "commercial_property"
    source_adapter: str
    address: Optional[str] = None
    location: Optional[dict] = None # { city, state, zip, county }
    valuation: Optional[float] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Transaction:
    """
    A recorded or inferred transaction between participants involving an asset.
    """
    id: str
    asset_id: str
    buyer_id: Optional[str] = None
    seller_id: Optional[str] = None
    transaction_type: str = ""      # e.g. "deed_transfer", "sale"
    transaction_date: Optional[datetime] = None
    price: Optional[float] = None
    source_adapter: str = ""
    source_file: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Signal:
    """
    A scored indicator that a participant or asset is likely to transact.
    Signals are produced by adapters and consumed by Core scoring.
    """
    id: str
    subject_id: str                 # participant_id or asset_id
    subject_type: str               # "participant" or "asset"
    signal_type: str                # e.g. "repeat_buyer", "seller_motivation", "distress"
    value: float                    # normalized 0.0 - 1.0
    weight: float = 1.0             # configured per signal type
    source_adapter: str = ""
    detected_at: Optional[datetime] = None
    explanation: str = ""           # human-readable reason
    metadata: dict = field(default_factory=dict)
