# ARCH-001 Migration Plan

## Recommendation

**DATA-002 should be split into three coherent schema patches.** No further architecture investigation is required before beginning Patch 1, but production row counts, collision queries, and raw-object accessibility must be captured as pre-migration verification. Three patches keep rollback boundaries understandable while avoiding prolonged preservation of weak schema.

## Patch 1 — Evidence and Lineage Foundation

- Purpose: make ingestion replayable before canonical identity is rewritten.
- Models affected: evolve `source_files` toward immutable raw-evidence metadata; add PipelineRun, SourceRecord, canonical-lineage mapping, and Observation foundations.
- Migration required: yes; additive tables/columns/indexes/constraints. Backfill content hashes and run/source metadata where evidence exists; mark unavailable provenance explicitly.
- Data loss risk: low if additive. Main risk is falsely claiming provenance for legacy rows.
- Rollback: drop new unused tables/columns before writers depend on them; retain existing `source_files` data and ingestion paths during compatibility window.
- Dependencies: Supabase object-read access; source-system naming; parser/contract version convention; decision on dry-run logging.
- Verification target: one Hillsborough D/P pair and one Redfin response are hash-addressed, attached to PipelineRuns, parsed into idempotent SourceRecords/Observations, and replay to identical record hashes without changing business tables.

## Patch 2 — Canonical Identity, Events, and Transactions

- Purpose: implement Entity/Participation/Event/Relationship and repair Asset/Transaction integrity without big-bang API replacement.
- Models affected: split Participant into Entity + Participation; evolve Asset and Transaction; add Event and Relationship; add participant-to-entity compatibility mapping.
- Migration required: yes; new tables, backfills, temporary compatibility columns/views, then foreign keys after orphan/collision remediation.
- Data loss risk: medium/high. Name-based participant deduplication may have merged distinct actors; fresh UUID normalization may have created aliases; orphan transaction assets need reconciliation.
- Rollback: retain original participant and transaction columns/tables until backfill validation and dual-read cutover complete; reverse writers to compatibility path.
- Dependencies: Patch 1 lineage; identity resolution rules; document-number source scope; production collision/orphan reports.
- Verification target: every migrated transaction has an existing Asset, primary Event, source lineage, and role Participations; participant compatibility IDs resolve deterministically; no unaccounted row loss.

## Patch 3 — Intelligence and Workflow Alignment

- Purpose: separate sourced facts from derivation and align APIs/workflow with new canonical IDs.
- Models affected: evolve Signal and Score with typed subjects, algorithm versions, and input lineage; define Opportunity; align Deal/Contact/Outreach links; add BuyerProfile/SellerCandidate projections only if serving tickets require persistence.
- Migration required: yes for intelligence/workflow constraints and lineage. Prediction/Match persistence is deferred unless an evidenced consumer requires history.
- Data loss risk: medium. Existing Signal rows mix facts/inferences; Score rows duplicate Participant fields; CRM IDs are unenforced.
- Rollback: maintain legacy API read models and old ID columns until parity checks pass; derived data can be recomputed from versioned inputs after cutover.
- Dependencies: Patches 1–2; scorer/matcher version contracts; API compatibility plan; classification of existing Signal rows from production data.
- Verification target: sourced Redfin/county claims remain Observations/Events; versioned Signals and Scores cite inputs; asset and entity subjects both work; Opportunity is distinct from Score; CRM links resolve; old API responses remain compatible until DATA-005/006 cutover.

## Top Migration Risks

1. **Identity collision/split risk:** normalized name + adapter is not reliable Entity identity (`adapters/real_estate/ingestion/pipeline.py:127-147`).
2. **Orphan Asset risk:** buyer transactions currently use document numbers without Asset rows (`adapters/real_estate/ingestion/pipeline.py:150-160`).
3. **False provenance risk:** legacy rows may not map to durable raw objects because wholesale flows bypass storage/manifests (`adapters/real_estate/sources/foreclosure.py:38-90`; `adapters/real_estate/sources/listings.py:60-71`).
4. **Semantic reclassification risk:** current Signals mix sourced conditions and inference (`adapters/real_estate/parsing/listings_parser.py:62-91`; `adapters/real_estate/parsing/foreclosure_parser.py:89-119`).
5. **Compatibility risk:** Participant IDs/names are copied or referenced across Score, Deal, Contact, APIs, and matching without foreign keys (`core/db/models.py:67-114`; `api/opportunities.py:23-41`; `core/matching/runner.py:38-98`).

## Required Pre-Migration Evidence

- Production counts and null/distinct/collision profiles for all nine tables.
- Orphan reports for transaction asset/buyer/seller IDs and CRM implied IDs.
- Supabase object inventory and hashability for manifest paths.
- Existing Signal type/value distribution and representative metadata.
- Confirmation of external API/consumer dependencies outside repository: `Unknown — needs follow-up` until owners respond.

These are implementation-patch prerequisites, not a reason for another architecture ticket.
