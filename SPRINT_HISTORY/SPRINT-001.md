# SPRINT-001 — Geographic Expansion Research & Expansion Framework

**Completed:** 2026-07-24 · **Type:** research/documentation only, no code/schema/ingestion changes · **PR:** #49

## Summary

Ranked 5 expansion markets against 13 criteria, cataloged 108 public
datasets across Maricopa AZ, Rensselaer NY, and four Florida counties,
documented 31 opportunity signals with priority against the live ticket
registry, reviewed expansion architecture for multi-jurisdiction
scalability, and ran an open-ended scan for additional intelligence
sources.

## Key findings

- **Markets**: top 5 = Pinellas, Maricopa, Orange, Pasco, Duval counties.
  Maricopa and Rensselaer (both already AGENTS.md-committed targets)
  confirmed; Rensselaer flagged with a population-decline and weak-data-
  access risk note. Austin, TX and Salt Lake County, UT deprioritized
  (non-disclosure states break LUX's evidence model).
- **Datasets**: 108 cataloged. Pasco County's confirmed bulk parcel-download
  endpoint and Florida's Sunbiz SFTP bulk feed are the two best-documented
  bulk-access sources found.
- **Signals**: 31 documented. Top near-term priorities: HUD USPS vacancy
  data (free, unimplemented), heir/inherited property (best-evidenced new
  signal), cash buyers (validates the already-scoped INTEL-003), LLC/entity
  purchases (complements DATA-006G, DATA-011).
- **Architecture**: biggest scaling risk is the legal-description/identifier
  normalizer, which is Florida-specific in current code. Two `core/` changes
  flagged as needing explicit sign-off before Maricopa/Rensselaer adapter
  work: generalizing `source_county` to `jurisdiction_code`, and adding
  jurisdiction scoping to provenance tables. Neither has been implemented.

## Full detail

Full review packet and all five work-package deliverables live in the
canonical repository (`fsassaman-commits/lux-core`) under `docs/research/`
and `docs/architecture/` — this file is a summary for the state mirror, not
a replacement for those documents.
