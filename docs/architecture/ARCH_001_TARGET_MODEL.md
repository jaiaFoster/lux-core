# ARCH-001 Target Model

Logical model for DATA-002 planning. All objects remain in PostgreSQL except immutable raw bytes in Supabase Storage. Logical layers do not imply separate services/databases.

## Evidence Layer Context

Raw evidence is immutable, SHA-256-addressed Supabase Storage content. A PipelineRun records execution and its input evidence. These support SourceRecord but are operational/evidence metadata, not replacements for the eight canonical objects below. Repository evidence for both is the incomplete `SourceFileModel` and missing wholesale manifests (`core/db/models.py:132-145`; `adapters/real_estate/ingestion/pipeline.py:75-103,181-193`; `adapters/real_estate/ingestion/wholesale_pipeline.py:29-255`).

## Canonical Layer

### Entity

- Purpose: persistent real-world actor independent of any role or event.
- Identity: canonical UUID; aliases/external identities linked through SourceRecord/Observation/Relationship, not name alone.
- Minimum required fields: `id`, `entity_type`, canonical display name, created/updated timestamps.
- Key relationships: many Participations, Relationships, Observations, SourceRecord lineage.
- Core or Adapter: Core.
- Current predecessor: `Participant` / `ParticipantModel` (`core/models/entities.py:14-30`; `core/db/models.py:10-22`).
- Migration action: staged split with compatibility mapping from participant ID to entity ID.

### Asset

- Purpose: persistent transactable or observable thing.
- Identity: canonical UUID; external/source identities via lineage.
- Minimum required fields: `id`, `asset_type`, created/updated timestamps; canonical display label optional.
- Key relationships: Transactions, Events, Observations, Relationships, SourceRecord lineage.
- Core or Adapter: Core; adapters define mappings/type vocabulary extensions.
- Current predecessor: `Asset` / `AssetModel` (`core/models/entities.py:33-46`; `core/db/models.py:25-34`).
- Migration action: preserve IDs where valid; move volatile reported valuation/location claims to Observations over time; add stable identity/lineage.

### Event

- Purpose: market-agnostic occurrence with time and type: filing, listing publication, auction, status change, transfer occurrence.
- Identity: canonical UUID distinct from upstream record key.
- Minimum required fields: `id`, `event_type`, occurred/effective timestamp or range, created timestamp.
- Key relationships: Participations, Assets, Transaction (optional one-to-one primary event), Observations, SourceRecord lineage.
- Core or Adapter: Core type; adapters map source codes.
- Current predecessor: none; filing/listing facts are currently parser dictionaries or Signals (`adapters/real_estate/parsing/foreclosure_parser.py:62-119`; `adapters/real_estate/parsing/listings_parser.py:62-91`).
- Migration action: add; backfill only where source semantics support an event.

### Transaction

- Purpose: first-class economic/ownership transfer, not a generic event.
- Identity: canonical UUID stable across multiple source reports.
- Minimum required fields: `id`, `event_id`, `transaction_type`, status, created/updated timestamps; consideration may be canonical only when reconciled, otherwise Observation.
- Key relationships: required primary Event; one or more Assets; Entity roles through Participation; SourceRecords/Observations.
- Core or Adapter: Core.
- Current predecessor: `Transaction` / `TransactionModel` (`core/models/entities.py:49-63`; `core/db/models.py:37-49`).
- Migration action: retain valid rows/IDs, create missing Assets/Events, replace fixed buyer/seller semantics with Participation, enforce integrity after backfill.

### Participation

- Purpose: contextual role of an Entity in an Event/Transaction.
- Identity: canonical UUID; uniqueness policy based on event/entity/role/source reconciliation.
- Minimum required fields: `id`, `entity_id`, `event_id`, `role_type`, created timestamp.
- Key relationships: Entity and Event required; optional Transaction convenience link only if justified by constraints.
- Core or Adapter: Core structure; adapter maps roles such as grantee, grantor, lender, homeowner, buyer, seller.
- Current predecessor: `TransactionModel.buyer_id/seller_id`; Participant metadata `party_role` (`core/db/models.py:40-49`; `adapters/real_estate/normalization/to_core.py:32-37,59-70`).
- Migration action: add and backfill known buyer/seller/grantee/grantor roles; retain unknown role evidence in SourceRecord/Observation until resolvable.

### Relationship

- Purpose: durable or time-bounded relation between canonical objects independent of one Event: ownership, affiliation, control, representation, same-as candidate.
- Identity: canonical UUID.
- Minimum required fields: `id`, subject type/ID, object type/ID, relationship type, valid-from/to, status.
- Key relationships: Entities and/or Assets; Observations/SourceRecords support the claim.
- Core or Adapter: Core structure; adapter maps domain relation types.
- Current predecessor: implied Participant/Contact/Deal links and owner concepts; no explicit model (`core/db/models.py:84-129`).
- Migration action: add only for evidenced durable relations; do not duplicate Participation roles.

### Observation

- Purpose: sourced claim, measurement, or reported fact without LUX inference.
- Identity: canonical UUID; idempotency based on SourceRecord, claim type, subject, observed/effective time, and payload hash.
- Minimum required fields: `id`, subject type/ID, observation type, typed value or JSON payload, observed/effective time, `source_record_id`, source confidence, created timestamp.
- Key relationships: one SourceRecord required; canonical subject; optional supersession/retraction relation.
- Core or Adapter: Core contract; adapter supplies source-specific claim mapping.
- Current predecessor: fields embedded in Asset/Participant metadata and raw parser dictionaries (`adapters/real_estate/parsing/hillsborough_parser.py:23-31,54-62`; `adapters/real_estate/parsing/listings_parser.py:34-91`).
- Migration action: add; route new sourced claims here; migrate existing volatile fields only with provenance.

### SourceRecord

- Purpose: normalized but source-faithful representation of one upstream record.
- Identity: UUID plus unique source-system/type/key/schema-version tuple; deterministic record hash fallback.
- Minimum required fields: `id`, source system, record type/key, source schema version, parser/contract version, raw evidence ID/pointer, pipeline run ID, record hash, source timestamps, source-faithful payload.
- Key relationships: required raw evidence and PipelineRun; lineage to canonical objects/Observations.
- Core or Adapter: Core envelope; adapter owns parsing/payload schema.
- Current predecessor: partial `SourceFileModel`, parser dictionaries, and metadata raw records (`core/db/models.py:132-145`; `adapters/real_estate/normalization/to_core.py:32-37`).
- Migration action: add separately from raw-file manifest; make new ingestion record-level and replayable.

## Intelligence Layer

### Signal

- Purpose: explainable LUX inference from canonical evidence.
- Identity: UUID; idempotency/version key by subject, signal type, algorithm version, evaluation window, and input set.
- Minimum required fields: subject, signal type/value, algorithm/rule version, computed time, explanation, input lineage.
- Key relationships: canonical subject and input Observations/Events/Transactions.
- Core or Adapter: Core intelligence contract; domain rules may live adapter-side.
- Current predecessor: `Signal` / `SignalModel` (`core/models/entities.py:66-81`; `core/db/models.py:52-64`).
- Migration action: evolve; keep derived rows, stop placing raw facts here, add version/lineage.
- Why derived: value is a LUX interpretation, e.g. repeat-buyer strength (`adapters/real_estate/normalization/to_core.py:138-156`).

### Score

- Purpose: numeric evaluation of a subject from versioned inputs.
- Identity: UUID per evaluation/run; latest score is a query/projection, not overwritten history by default.
- Minimum required fields: subject, score type/value, scorer version, evaluated time, confidence, input lineage.
- Key relationships: subject, Signals/Observations used, optional Opportunity.
- Core or Adapter: Core intelligence.
- Current predecessor: `ScoreModel` (`core/db/models.py:67-81`).
- Migration action: evolve away from Participant-only/copy fields; add version/lineage and history policy.
- Why derived: computed weighted average (`core/scoring/engine.py:22-45`).

### Prediction

- Purpose: forecast a future outcome over a stated horizon.
- Identity: UUID per model run/subject/horizon.
- Minimum required fields: subject, predicted outcome, horizon, probability/confidence, model version, computed time, input lineage.
- Key relationships: subject, model/run, evidence inputs.
- Core or Adapter: Core intelligence contract.
- Current predecessor: no confirmed current implementation.
- Migration action: no DATA-002 table unless an immediate evidenced consumer exists; reserve contract semantics.
- Why derived: forecast is model output, not source truth.

### Match

- Purpose: versioned compatibility/ranking result between an Opportunity and candidate Entity/Asset.
- Identity: UUID per matcher version/input set; composite idempotency key possible.
- Minimum required fields: opportunity ID, candidate ID/type, score, confidence, matcher version, computed time, explanation, input lineage.
- Key relationships: Opportunity, candidate canonical object, input Signals/Scores.
- Core or Adapter: Core intelligence.
- Current predecessor: in-memory dictionaries from `core/matching/runner.py:88-98`.
- Migration action: define lineage contract; persistence only if product/query history needs it.
- Why derived: computed signal-overlap ranking (`core/matching/engine.py:56-88`).

### Opportunity

- Purpose: actionable derived prospect synthesized from evidence and intelligence, separate from human Deal state.
- Identity: UUID with lifecycle/version policy.
- Minimum required fields: subject, opportunity type/status, created/updated time, current supporting score/signal references.
- Key relationships: canonical subject, Scores/Signals, Matches, optional workflow Deal.
- Core or Adapter: Core intelligence/serving boundary; domain type mappings adapter-side.
- Current predecessor: no model; `/api/opportunities` serializes Score rows (`api/opportunities.py:11-41`).
- Migration action: add only after Score/subject semantics are corrected; avoid equating every Score with active Opportunity.
- Why derived: opportunity is LUX's actionable interpretation, not an upstream fact.

## Workflow Projections

### BuyerProfile

- Inputs: Entity, buyer-role Participations, Transactions, Assets, Observations, Signals/Scores, and source lineage.
- Projection logic: adapter-owned real-estate read model summarizing acquisition history/preferences/evidence; no buyer subtype on Entity.
- Persistence recommendation: materialized projection/table only when query needs justify it; always rebuildable from canonical/versioned inputs.
- Invalidation/refresh: refresh on relevant Participation/Transaction/Asset/Observation changes or contract-version change; record projection version and source watermark.

### SellerCandidate

- Inputs: Entity, seller/owner Participations/Relationships, Assets, foreclosure/listing Events, Observations, and derived Signals/Scores.
- Projection logic: adapter-owned real-estate candidate view; motivation remains derived and explainable.
- Persistence recommendation: materialized projection only for serving performance; never source truth.
- Invalidation/refresh: refresh when ownership/filing/listing evidence or derivation version changes; expire stale candidates explicitly.
