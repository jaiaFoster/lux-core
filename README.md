# LUX — Linked Unified Exchange

A market intelligence platform that discovers, evaluates, and facilitates high-probability transactions across fragmented markets.

Adapter #1: Residential real estate, Tampa Bay.

---

## Structure

```
lux/
├── core/           # Market-agnostic intelligence engine
├── adapters/       # Market-specific data and classification logic
├── ui/             # Internal dashboard and CRM interface
└── data/           # Raw and processed data (gitignored)
```

## Core Question

Before adding any feature, ask:

> Does this belong in `core/` or in `adapters/real_estate/`?

If it's reusable across markets → `core/`
If it's specific to real estate → `adapters/real_estate/`

---

## Adapters

| Adapter | Status |
|---|---|
| Real Estate (Tampa Bay) | 🟡 In Progress |

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Architecture

See `/docs` for the full Technical Architecture Approval Document.
