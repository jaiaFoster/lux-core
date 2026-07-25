# ARCH-001 Model Decisions

These are architecture decisions for DATA-002 planning. No model or data has been changed.

## Existing Model Disposition Matrix

Each model has exactly one primary disposition.

| Current Model | Disposition | Target Concept | Evidence | Migration Impact | Open Question |
|---|---|---|---|---|---|
| ORM `ParticipantModel` | SPLIT | `Entity` + `Participation`; temporary compatibility mapping | It stores persistent actor identity but buyer/seller context is producer metadata or fixed transaction columns (`core/db/models.py:10-22,37-49`; `adapters/real_estate/normalization/to_core.py:16-71`) | Backfill Entity; create role records; preserve participant IDs/compatibility views during cutover | Are normalized name + adapter collisions present in production? |
| ORM `AssetModel` | EVOLVE | `Asset` + sourced `Observation` values | Generic asset shell exists, but valuation/location metadata lack per-claim provenance (`core/db/models.py:25-34`; `adapters/real_estate/normalization/to_core.py:74-109`) | Preserve Asset IDs; move volatile/source claims incrementally; add lineage | What stable source/canonical identity resolves address changes? |
| ORM `TransactionModel` | EVOLVE | first-class `Transaction` linked to `Event`, Asset, Participation, SourceRecord | Current direct buyer/seller strings and orphan asset reference lack enforced integrity (`core/db/models.py:37-49`; `adapters/real_estate/ingestion/pipeline.py:150-160`) | Add Event/role/lineage links; backfill; retain transaction identity | Is document number unique per source/county or only within a file/system? |
| ORM `SignalModel` | EVOLVE | derived `Signal` with typed subject, version, and input lineage | Current facts and inferences share polymorphic strings; asset signals miss scoring (`core/db/models.py:52-64`; `core/scoring/runner.py:21-49`) | Preserve explainable signals; reclassify future sourced facts as Observation/Event; add lineage/version | Which existing rows are facts versus inferences? Production audit needed. |
| ORM `ScoreModel` | EVOLVE | derived `Score` and separate `Opportunity` projection/object | It persists derived evaluation and copied Participant fields, and APIs treat scores as opportunities (`core/db/models.py:67-81`; `api/opportunities.py:11-41`) | Generic subject/lineage; stop duplicating identity fields; staged API compatibility | Must historical scores be immutable runs or latest-only? |
| ORM `DealModel` | EVOLVE | workflow `Deal` linked to Opportunity, Entity, Asset | Current model is human workflow state with weak participant/buyer/free-text asset references (`core/db/models.py:84-98`) | Add enforced/generic links without making Deal canonical market truth | Which statuses/workflows remain active product scope? |
| ORM `ContactModel` | SPLIT | `Entity` + contact-method `Observation`/Relationship + workflow projection | Duplicates identity and mixes phone/email/role; Core imports real-estate normalizer (`core/db/models.py:101-114`; `core/crm/contacts.py:3-6,23-39`) | Backfill actor/contact claims; preserve contact API compatibility temporarily | Are contacts always real-world entities, or sometimes unverified strings? |
| ORM `OutreachModel` | EVOLVE | workflow `OutreachActivity`/human action linked to Deal/Entity | Existing action log has implied, unenforced deal/contact links (`core/db/models.py:117-129`; `core/crm/outreach.py:24-43`) | Add enforced links/actor and preserve history | Retention and audit requirements are Unknown — needs follow-up. |
| ORM `SourceFileModel` | EVOLVE | raw-evidence metadata plus PipelineRun input; SourceRecord is separate | Current file manifest lacks hash/run/parser/lineage and covers only P file (`core/db/models.py:132-145`; `adapters/real_estate/ingestion/pipeline.py:75-82,181-193`) | Backfill hashes where raw objects exist; add run/input relations; do not pretend file equals record | Can all existing Supabase objects be read and hashed? |
| Dataclass `Participant` | SPLIT | `Entity` + `Participation` contract | Docstring defines entity while name/fields conflate role and source (`core/models/entities.py:14-30`) | Version adapter contract; keep compatibility type during staged migration | Which external imports exist outside repository? |
| Dataclass `Asset` | EVOLVE | canonical `Asset` contract with Observation lineage | Current type is generic, but embeds mutable valuation and adapter source (`core/models/entities.py:33-46`) | Version contract; distinguish identity from observations | Minimum cross-market identity fields need adapter samples beyond real estate. |
| Dataclass `Transaction` | EVOLVE | first-class `Transaction` linked to Event/Participation/SourceRecord | It has correct first-class intent but is unused and fixed to buyer/seller roles (`core/models/entities.py:49-63`; only import at `adapters/real_estate/normalization/to_core.py:9`) | Activate through versioned contract after schema supports it | One-to-one versus one-to-many Transaction/Event cardinality for complex markets needs validation. |
| Dataclass `Signal` | EVOLVE | derived `Signal` contract with version/input lineage | Explicitly described as scored indicator; current adapter emits both facts and inference (`core/models/entities.py:66-81`; `adapters/real_estate/normalization/to_core.py:112-156`) | Version contract; move sourced claims to Observation/Event going forward | Existing-row reclassification requires data inspection. |

No current model is classified `KEEP CANONICAL`, `ADAPTER-SPECIFIC`, or `DEPRECATE` as its primary disposition. Existing structures contain reusable data, but every one needs semantic, relationship, provenance, or layer correction. Real-estate-specific parser dictionaries remain adapter-side; they are not current ORM/dataclass models in this matrix.

## Decision: Participant to Entity

### Recommendation

Choose **C: compatibility migration**, with **B (`Entity` + `Participation`) as the target model**.

- `Entity` is the persistent real-world actor.
- `Participation` records an Entity's contextual role in an Event or Transaction: buyer, seller, grantee, grantor, lender, homeowner, counterparty, or adapter-defined role code.
- Existing `Participant` IDs remain temporarily addressable through a mapping/compatibility layer while producers, scoring, matching, CRM, and APIs migrate.
- Do not preserve `Participant` as the long-term canonical actor name.

### Evidence and conflict analysis

- Current fields: identity fields plus adapter/county/provenance-like fields (`core/models/entities.py:21-30`; `core/db/models.py:13-22`). Entity identity should not change because it appears in a different transaction role.
- Identity semantics: normalization creates a fresh UUID but persistence deduplicates by normalized name + adapter (`adapters/real_estate/normalization/to_core.py:16-38`; `adapters/real_estate/ingestion/pipeline.py:127-147`). Current identity rules are weak and adapter-scoped.
- Transaction roles: fixed `buyer_id`/`seller_id` columns (`core/db/models.py:40-49`) cannot represent lender, grantor, grantee, agent, government body, or future-market roles.
- Buyer/seller semantics: both normalize into the same Participant structure; seller role lives in metadata (`adapters/real_estate/normalization/to_core.py:16-71`). This directly supports separating actor from role.
- Foreign keys: no current relationship is enforced, lowering physical migration coupling but increasing integrity risk (`core/db/models.py:37-145`).
- API dependencies: opportunities serialize copied participant fields from Score; CRM accepts participant/buyer IDs (`api/opportunities.py:23-41`; `api/deals.py:21-39`; `api/contacts.py:21-28`). Compatibility is needed to avoid simultaneous API replacement.
- Dashboard dependencies: dashboard consumes IDs/names but does not directly query Participant (`ui/src/App.jsx:237-335`). API compatibility can shield it.
- Adapter dependencies: normalizers return Participant and pipelines persist ParticipantModel (`adapters/real_estate/normalization/to_core.py:16-71`; `adapters/real_estate/ingestion/pipeline.py:120-147`; `adapters/real_estate/ingestion/wholesale_pipeline.py:47-109`). Contract versioning is required.

Repository evidence supports the provisional direction. Conflict is migration breadth, not semantics: Participant touches ingestion, scoring, matching, CRM, APIs, and derived rows. Therefore a one-step rename is unsafe even with limited data.

## Decision: Transaction and Event

### Recommendation

Choose **Option C: Transaction references Event but remains separate**.

- `Event` captures an occurrence and chronology: filing recorded, listing published, auction scheduled, ownership transfer observed.
- `Transaction` captures the domain transfer/economic act: asset(s), consideration, transaction type/status, and a required primary `event_id` once migrated.
- `Participation` attaches Entities and roles to Event; Transaction uses those roles rather than fixed buyer/seller columns long-term.
- A Transaction may cite multiple SourceRecords/Observations. Its primary Event is one-to-one for the initial implementation; later supporting events may relate through Relationship if evidence requires it.

### Required semantics

- Transaction identity: canonical UUID, stable across multiple source reports; source keys belong to SourceRecord, not canonical Transaction ID.
- Transaction type: market-agnostic controlled type plus adapter mapping; current deed codes stay adapter/source data (`adapters/real_estate/ingestion/pipeline.py:20,117-160`).
- Asset linkage: enforced Transaction-to-Asset relation; current orphan document-number link is invalid target behavior.
- Entity roles: Participation rows, not fixed buyer/seller-only fields.
- Source provenance: Transaction lineage to SourceRecord(s); reported price/date can also be Observations when source claims conflict.
- Future adapters: Event provides generic chronology; Transaction remains optimized for transfers and does not become a universal event bag.

Why not Option A: it duplicates chronology/roles and leaves filings/listings disconnected from transactions. Why not Option B: single-table inheritance or generic Event payload would weaken Transaction's first-class constraints. Option C preserves both requirements.

## Decision: Observation Boundary

### Strict definitions

- **Observation:** sourced claim, measurement, or reported fact. Must retain source, observed/effective time, payload/value, provenance, and optional source confidence. It is not a LUX conclusion.
- **Signal:** LUX-derived inference from Observations, Events, Transactions, or other canonical facts. Must retain algorithm/rule version and input lineage.
- **Score:** numeric evaluation over versioned inputs/signals. Must retain scorer version, subject, evaluated time, and lineage.
- **Prediction:** forecast about a future outcome, with model version, horizon, confidence/probability, and input lineage.

### Current examples

- Observation-like: Redfin `PRICE`, days on market, address, and listing status are sourced CSV claims (`adapters/real_estate/parsing/listings_parser.py:34-91`). Current code collapses price into `Asset.valuation` and listing/staleness into Signal (`adapters/real_estate/normalization/to_core.py:79-108`; `adapters/real_estate/parsing/listings_parser.py:62-71`). Target: preserve claims as Observations; derive motivation/staleness Signal separately.
- Observation/Event-like: Hillsborough document type/date/price and party name/role are source facts (`adapters/real_estate/parsing/hillsborough_parser.py:23-31,54-62`). Target: SourceRecord + Observations/Participation/Event, not inference.
- Signal: `repeat_buyer` strength is calculated from count (`adapters/real_estate/normalization/to_core.py:138-156`; `adapters/real_estate/ingestion/pipeline.py:23-58`). This is confirmed derived inference.
- Signal with mixed semantics: `foreclosure` uses a real filing plus hardcoded urgency value (`adapters/real_estate/parsing/foreclosure_parser.py:16-24,89-119`). Filing is Event/Observation; urgency is Signal.
- Score: weighted average from Signals persisted in `scores` (`core/scoring/engine.py:22-45`; `core/scoring/runner.py:64-92`).
- Prediction: **No confirmed current implementation.**
- Match: signal-overlap ranking is derived (`core/matching/engine.py:56-88`).
- Opportunity: no explicit model; `/api/opportunities` exposes Score rows as opportunities (`api/opportunities.py:11-41`).

Confidence on an Observation describes source/claim quality. Confidence on Signal/Score/Prediction describes derivation/model confidence. These must not share an ambiguous field without type semantics.

## Decision: SourceRecord Boundary

### Required chain

```text
Immutable Raw Evidence
        ↓
SourceRecord (source-faithful normalized record)
        ↓ lineage
Entity / Asset / Event / Transaction / Participation / Relationship / Observation
        ↓ derivation lineage
Signal / Score / Prediction / Match / Opportunity
```

### Recommendation

- Identity: canonical UUID plus uniqueness on `(source_system, source_record_type, source_record_key, source_schema_version)`; if upstream has no stable key, use a deterministic record hash scoped to raw object.
- Source system: stable market-agnostic code, e.g. `hillsborough_clerk`, `redfin`; adapter is recorded separately.
- Source record key: upstream document/listing/row identifier, never overloaded as Asset/Transaction ID.
- Raw object pointer: immutable Supabase Storage object reference.
- Content hash: raw evidence metadata stores SHA-256 and byte length; SourceRecord points to raw evidence and may store a record-level hash.
- Pipeline run: required run ID records adapter, contract/parser version, start/end/status, dry-run, counts, and errors.
- Parser version: required version of adapter-to-canonical/source-record contract.
- Canonical lineage: explicit mapping rows from SourceRecord to canonical object type/ID and transformation version; avoid opaque JSON-only provenance.
- Replay: a run reads immutable hash-addressed evidence, regenerates SourceRecords under a parser version, then idempotently reconciles canonical objects. Replay never mutates raw evidence.

### Comparison with current state

- Current `SourceFileModel` records county/name/path/status but no content hash, parser version, run, or canonical lineage (`core/db/models.py:132-145`).
- Buyer ingestion checks/writes only the P file even though P and D are inputs (`adapters/real_estate/ingestion/pipeline.py:75-103,181-193`).
- Foreclosure and Redfin flows use memory/temp files and never create SourceFile rows (`adapters/real_estate/sources/foreclosure.py:38-90`; `adapters/real_estate/sources/listings.py:60-71`; `adapters/real_estate/ingestion/wholesale_pipeline.py:29-255`).
- Parser records currently place temporary local paths into `source_file` (`adapters/real_estate/parsing/hillsborough_parser.py:23-31,54-62`), which is not durable provenance.

SourceFile should evolve into raw-evidence metadata/run-input tracking. SourceRecord must be separate because one raw file contains many upstream records and one canonical object may derive from several records.

## Scaffold Conflicts Found

No approved scaffold decision is disproved by repository evidence. Current code conflicts with several desired properties:

1. Raw evidence is not consistently immutable/archived or content-hashed.
2. Not every ingestion has a pipeline run.
3. Canonical records do not retain explicit SourceRecord lineage.
4. Adapter-specific fields leak into canonical models/CRM, including `source_county` and Core importing adapter name normalization (`core/crm/contacts.py:3-6`).
5. Derived outputs lack algorithm/model version and input lineage.
6. Current health semantics mix UI liveness messaging with no DB readiness check (`api/health.py:5-13`; `ui/src/App.jsx:343-388`).

These are implementation gaps supporting the scaffold, not evidence for graph/streaming/microservice infrastructure.
