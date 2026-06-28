# core/

LUX Core — Market Intelligence Engine

This package contains all market-agnostic logic. It operates exclusively
on LUX Core entity schemas and has no knowledge of any specific market.

## Modules

| Module | Responsibility |
|---|---|
| `models/` | Canonical entity schemas: Participant, Asset, Transaction, Signal |
| `scoring/` | Weighted opportunity scoring from Signals |
| `matching/` | Counterparty matching and ranking |
| `crm/` | Deal and contact management |
| `api/` | REST API surface (Flask) |
| `db/` | Database connection and migrations |

## Boundary Rule

Core imports nothing from `adapters/`.
Adapters import Core schemas. Never the reverse.
