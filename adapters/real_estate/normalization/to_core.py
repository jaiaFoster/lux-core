# adapters/real_estate/normalization/to_core.py
#
# Real Estate Adapter — Normalization
#
# Transforms real-estate-specific parsed records into LUX Core entity schemas.
# This is the adapter boundary. Core never sees raw county record data.

from datetime import datetime
from core.models.entities import Participant, Asset, Transaction, Signal
from adapters.real_estate.classification.entity_classifier import (
    classify_entity_type, normalize_name, get_matched_keyword
)
import uuid


def record_to_participant(record: dict) -> Participant:
    """
    Transform a parsed county party record into a Core Participant.
    """
    name = record.get("buyer_name", "")
    normalized = normalize_name(name)
    keyword = get_matched_keyword(name)

    return Participant(
        id=str(uuid.uuid4()),
        name=name,
        normalized_name=normalized,
        participant_type=classify_entity_type(name),
        source_adapter="real_estate",
        source_county=record.get("source_county"),
        first_seen=record.get("source_date"),
        last_seen=record.get("source_date"),
        confidence=record.get("confidence", "LOW"),
        metadata={
            "matched_keyword": keyword,
            "source_file": record.get("source_file"),
            "raw_record": record.get("raw_record"),
            "party_role": record.get("party_role"),
        }
    )


def participant_to_signal(participant: Participant, repeat_count: int = 1) -> Signal:
    """
    Generate a repeat_buyer Signal from a Participant's activity.
    Signal strength scales with repeat transaction count.
    """
    value = min(repeat_count / 10.0, 1.0)  # normalize: 10+ appearances = 1.0

    return Signal(
        id=str(uuid.uuid4()),
        subject_id=participant.id,
        subject_type="participant",
        signal_type="repeat_buyer",
        value=value,
        weight=1.0,
        source_adapter="real_estate",
        detected_at=datetime.utcnow(),
        explanation=f"Appeared {repeat_count} time(s) as buyer in public records.",
        metadata={"repeat_count": repeat_count}
    )
