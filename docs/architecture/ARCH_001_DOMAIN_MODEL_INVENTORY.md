# ARCH-001 Domain Model Inventory

Repository state: `c07e3fc` on branch `codex/arch-001-domain-model` before ARCH-001 changes. This inventory covers all nine SQLAlchemy ORM models in `core/db/models.py` and all four canonical dataclasses in `core/models/entities.py`. Repository evidence only; unproven behavior is marked `Unknown — needs follow-up`.

## ORM Models

### ParticipantModel / `participants`

- Name: `ParticipantModel`; table `participants`
- Exact file: `core/db/models.py`
- Exact lines: `10-22`
- Type: SQLAlchemy ORM table; current persistent actor/party record
- Current fields: `id`, `name`, `normalized_name`, `participant_type`, `source_adapter`, `source_county`, `first_seen`, `last_seen`, `confidence`, JSON `metadata`
- Current relationships: `TransactionModel.buyer_id`/`seller_id`, `ScoreModel.participant_id`, `DealModel.participant_id`/`buyer_id`, and `ContactModel.participant_id` contain string IDs that imply participant relationships; none declares a SQLAlchemy `ForeignKey` (`core/db/models.py:37-49,67-81,84-114`). `SignalModel.subject_id` may contain a participant ID when `subject_type="participant"` (`core/db/models.py:52-64`).
- Current producers: buyer ingestion upserts buyers (`adapters/real_estate/ingestion/pipeline.py:105-147`); foreclosure ingestion upserts sellers (`adapters/real_estate/ingestion/wholesale_pipeline.py:47-109`).
- Current consumers: scoring iterates all participants (`core/scoring/runner.py:21-49`); matching filters organization-like participant types (`core/matching/runner.py:48-86`); diagnostics counts rows (`api/dev/status.py:30-43`).
- Adapter-specific assumptions: `source_county`; current producer fixes `source_adapter="real_estate"`; buyer and distressed-seller roles are encoded through producer context/metadata rather than a role relation (`adapters/real_estate/normalization/to_core.py:16-71`).
- Overlap with another model: canonical `Participant` has the same core fields (`core/models/entities.py:14-30`); `ContactModel` repeats name and normalized name (`core/db/models.py:101-114`).
- Observed inconsistencies: name says contextual role, but docstring defines a persistent real-world entity (`core/models/entities.py:15-20`). IDs are newly generated UUIDs per normalization (`adapters/real_estate/normalization/to_core.py:22-38,49-71`) while ORM upsert identity is normalized name plus adapter (`adapters/real_estate/ingestion/pipeline.py:127-147`; `adapters/real_estate/ingestion/wholesale_pipeline.py:89-109`). Buyer/seller roles are not modeled independently.

### AssetModel / `assets`

- Name: `AssetModel`; table `assets`
- Exact file: `core/db/models.py`
- Exact lines: `25-34`
- Type: SQLAlchemy ORM table; persistent transactable thing
- Current fields: `id`, `asset_type`, `source_adapter`, `address`, JSON `location`, `valuation`, JSON `metadata`
- Current relationships: `TransactionModel.asset_id` and asset-scoped `SignalModel.subject_id` imply links but have no foreign-key constraints (`core/db/models.py:37-64`).
- Current producers: foreclosure and Redfin listing ingestion (`adapters/real_estate/ingestion/wholesale_pipeline.py:47-86,162-204`).
- Current consumers: wholesale upsert lookup (`adapters/real_estate/ingestion/wholesale_pipeline.py:69-86,183-204`) and diagnostics count (`api/dev/status.py:30-43`). No direct API/dashboard consumer is found.
- Adapter-specific assumptions: address/location shape, valuation, property metadata, document number, folio, bedrooms, bathrooms, and listing URL originate in the real-estate adapter (`adapters/real_estate/normalization/to_core.py:74-109`).
- Overlap with another model: canonical `Asset` (`core/models/entities.py:33-46`). `DealModel.asset_address` duplicates an unenforced textual asset reference (`core/db/models.py:84-98`).
- Observed inconsistencies: buyer ingestion writes `TransactionModel.asset_id=doc_num` but emits/persists no Asset (`adapters/real_estate/ingestion/pipeline.py:102-121,150-160`). `valuation` stores a Redfin reported price directly as canonical state, with no source/time provenance (`adapters/real_estate/parsing/listings_parser.py:34-38,73-91`; `adapters/real_estate/normalization/to_core.py:79-108`).

### TransactionModel / `transactions`

- Name: `TransactionModel`; table `transactions`
- Exact file: `core/db/models.py`
- Exact lines: `37-49`
- Type: SQLAlchemy ORM table; first-class recorded transfer/transaction
- Current fields: `id`, `asset_id`, `buyer_id`, `seller_id`, `transaction_type`, `transaction_date`, `price`, `source_adapter`, `source_file`, JSON `metadata`
- Current relationships: string `asset_id`, `buyer_id`, and `seller_id`; no database or ORM foreign keys/relationships.
- Current producers: Hillsborough buyer pipeline only (`adapters/real_estate/ingestion/pipeline.py:150-161`).
- Current consumers: repeat-buyer aggregate by `buyer_id` (`adapters/real_estate/ingestion/pipeline.py:23-58`); diagnostics count (`api/dev/status.py:30-43`). No transaction API/dashboard consumer found.
- Adapter-specific assumptions: fixed buyer/seller role columns; `source_file`; deed type codes; metadata document number; transaction date parsing assumes `%m/%d/%Y` (`adapters/real_estate/ingestion/pipeline.py:150-160`).
- Overlap with another model: canonical `Transaction` (`core/models/entities.py:49-63`), but that dataclass is imported and never constructed (`adapters/real_estate/normalization/to_core.py:9`; repository-wide usage search).
- Observed inconsistencies: ORM row ID reuses the generated Signal ID (`adapters/real_estate/ingestion/pipeline.py:120-121,150-174`); `asset_id` is a document number without a persisted Asset; seller is never populated; no source-record or event linkage.

### SignalModel / `signals`

- Name: `SignalModel`; table `signals`
- Exact file: `core/db/models.py`
- Exact lines: `52-64`
- Type: SQLAlchemy ORM table; derived intelligence indicator
- Current fields: `id`, `subject_id`, `subject_type`, `signal_type`, `value`, `weight`, `source_adapter`, `detected_at`, `explanation`, JSON `metadata`
- Current relationships: polymorphic string `subject_id` plus string discriminator `subject_type`; no foreign key.
- Current producers: repeat-buyer normalization and ingestion (`adapters/real_estate/normalization/to_core.py:138-156`; `adapters/real_estate/ingestion/pipeline.py:120-174`); foreclosure/listing normalization and ingestion (`adapters/real_estate/normalization/to_core.py:112-135`; `adapters/real_estate/ingestion/wholesale_pipeline.py:47-124,162-218`).
- Current consumers: repeat-signal recomputation (`adapters/real_estate/ingestion/pipeline.py:23-58`), scoring (`core/scoring/runner.py:29-49`), matching (`core/matching/runner.py:59-86`), diagnostics (`api/dev/status.py:30-43`).
- Adapter-specific assumptions: signal types `repeat_buyer`, `foreclosure`, `active_listing`, and `price_reduced`; real-estate explanations/metadata (`adapters/real_estate/normalization/to_core.py:112-156`).
- Overlap with another model: canonical `Signal` (`core/models/entities.py:66-81`); `ScoreModel` stores downstream evaluation.
- Observed inconsistencies: sourced conditions (`active_listing`, filing existence) and LUX-derived inferences (`repeat_buyer`, likely motivation) share one structure. Asset-scoped signals are persisted but participant-only scoring cannot consume them (`core/scoring/runner.py:21-49`). No algorithm version or input lineage exists.

### ScoreModel / `scores`

- Name: `ScoreModel`; table `scores`
- Exact file: `core/db/models.py`
- Exact lines: `67-81`
- Type: SQLAlchemy ORM table; persisted derived numeric evaluation
- Current fields: `id`, `participant_id`, copied participant name/type/county/confidence, `score`, `score_confidence`, JSON `explanation`, `scored_at`, `source_adapter`
- Current relationships: `participant_id` implies Participant; no foreign key.
- Current producers: `run_scoring()` upserts one score per participant (`core/scoring/runner.py:12-98`).
- Current consumers: opportunities API (`api/opportunities.py:11-41`), matching (`core/matching/runner.py:38-63`), diagnostics (`api/dev/status.py:45-84`), Opportunities dashboard (`ui/src/App.jsx:237-287,350-355`).
- Adapter-specific assumptions: default `source_adapter="real_estate"`; copied county/type fields; scorer currently iterates participants only (`core/db/models.py:81`; `core/scoring/runner.py:21-27,76-89`).
- Overlap with another model: duplicates Participant display fields; serves as current de facto Opportunity read model though no Opportunity model exists.
- Observed inconsistencies: no algorithm version, input lineage, or subject type; current UI treats categorical confidence as numeric (`ui/src/App.jsx:190-199,275`).

### DealModel / `deals`

- Name: `DealModel`; table `deals`
- Exact file: `core/db/models.py`
- Exact lines: `84-98`
- Type: SQLAlchemy ORM table; workflow/CRM record
- Current fields: `id`, `title`, `status`, `participant_id`, `buyer_id`, `asset_address`, `asking_price`, `offer_price`, `notes`, timestamps, JSON `metadata`
- Current relationships: implied participant/buyer IDs and text asset address; no foreign keys. Outreach can imply a deal through `OutreachModel.deal_id` without a foreign key (`core/db/models.py:117-129`).
- Current producers/consumers: CRUD service (`core/crm/deals.py:10-84`) exposed by `/api/deals` (`api/deals.py:11-47`). No dashboard consumer found.
- Adapter-specific assumptions: buyer terminology, property address, asking/offer prices, and real-estate pipeline statuses.
- Overlap with another model: overlaps future Opportunity/workflow concepts, but current Deal is human workflow state rather than source truth.
- Observed inconsistencies: free-text asset link; participant and buyer are separate columns with undefined semantics; no source Opportunity reference.

### ContactModel / `contacts`

- Name: `ContactModel`; table `contacts`
- Exact file: `core/db/models.py`
- Exact lines: `101-114`
- Type: SQLAlchemy ORM table; mixed actor/contact-method/workflow record
- Current fields: `id`, `participant_id`, duplicated names, phone, email, `contact_type`, notes, timestamps, JSON `metadata`
- Current relationships: implied Participant ID; Outreach may link via `OutreachModel.contact_id`; no foreign keys.
- Current producers/consumers: CRUD service (`core/crm/contacts.py:11-62`) exposed by `/api/contacts` (`api/contacts.py:11-34`). No dashboard consumer found.
- Adapter-specific assumptions: default `contact_type="owner"`; accepted API categories are documented as owner/buyer/agent/attorney/contractor (`AGENTS.md:126-142`). Name normalization imports the real-estate adapter into Core CRM (`core/crm/contacts.py:3-6,23-39`), contradicting the stated boundary that Core never imports adapters (`AGENTS.md:91-98`).
- Overlap with another model: duplicates Participant identity; phone/email are sourced claims suitable for Observation; contact type may be Participation or Relationship.
- Observed inconsistencies: mixes entity identity, contact points, and contextual role; Core depends on adapter-specific normalization.

### OutreachModel / `outreach`

- Name: `OutreachModel`; table `outreach`
- Exact file: `core/db/models.py`
- Exact lines: `117-129`
- Type: SQLAlchemy ORM table; workflow/human-action log
- Current fields: `id`, `deal_id`, `contact_id`, `outreach_type`, `direction`, `status`, `notes`, `occurred_at`, `created_at`, JSON `metadata`
- Current relationships: implied Deal and Contact IDs; no foreign keys.
- Current producers/consumers: create/list service (`core/crm/outreach.py:10-62`) exposed by `/api/outreach` (`api/outreach.py:11-35`). No dashboard consumer found.
- Adapter-specific assumptions: none proven in model fields; current surrounding CRM vocabulary is lead/outreach oriented.
- Overlap with another model: semantically resembles a workflow Event/HumanAction, not canonical market Event.
- Observed inconsistencies: no actor who performed action, no enforced deal/contact relation, no queue/review context.

### SourceFileModel / `source_files`

- Name: `SourceFileModel`; table `source_files`
- Exact file: `core/db/models.py`
- Exact lines: `132-145`
- Type: SQLAlchemy ORM table; partial raw-file processing manifest
- Current fields: `id`, `county`, `filename`, `storage_path`, `file_date`, `file_type`, `status`, `records_extracted` as String, `processed_at`, `created_at`, JSON `metadata`
- Current relationships: none; no pipeline-run, source-record, canonical-record, content-hash, or parser-version relation.
- Current producers: Hillsborough buyer pipeline records only the party file after processing (`adapters/real_estate/ingestion/pipeline.py:75-82,181-193`).
- Current consumers: buyer pipeline skip check (`adapters/real_estate/ingestion/pipeline.py:75-82`) and diagnostics last-file/count (`api/dev/status.py:42-49,74-78`).
- Adapter-specific assumptions: required `county`; P/D file types and Supabase storage paths.
- Overlap with another model: predecessor to raw-evidence metadata, pipeline-run input, and SourceRecord provenance; it is not itself a normalized source row.
- Observed inconsistencies: paired D file is not recorded; wholesale in-memory flows bypass it; no immutability/hash; `records_extracted` is textual; status represents both file and processing concerns.

## Canonical Dataclasses

### Participant

- Name: `Participant`
- Exact file/lines: `core/models/entities.py:14-30`
- Type: canonical dataclass
- Current fields: `id`, `name`, `normalized_name`, `participant_type`, `source_adapter`, `source_county`, first/last seen, confidence, metadata
- Current relationships: none declared; described as an entity capable of being a transaction party (`core/models/entities.py:16-20`).
- Current producers: real-estate normalization for buyer and seller (`adapters/real_estate/normalization/to_core.py:16-71`).
- Current consumers: buyer/wholesale ORM writes (`adapters/real_estate/ingestion/pipeline.py:120-147`; `adapters/real_estate/ingestion/wholesale_pipeline.py:47-109`), signal construction (`adapters/real_estate/normalization/to_core.py:138-156`), and matching candidate construction (`core/matching/runner.py:75-84`).
- Adapter-specific assumptions: county and adapter live on identity; metadata carries party role and real-estate source fields.
- Overlap: `ParticipantModel`; contact identity fields.
- Observed inconsistencies: persistent actor identity and contextual transaction role are collapsed; UUID is regenerated on each normalization before name-based ORM upsert.

### Asset

- Name: `Asset`
- Exact file/lines: `core/models/entities.py:33-46`
- Type: canonical dataclass
- Current fields: `id`, `asset_type`, `source_adapter`, address, location, valuation, metadata
- Current relationships: none declared.
- Current producers: `record_to_asset()` for foreclosure/listing records (`adapters/real_estate/normalization/to_core.py:74-109`).
- Current consumers: wholesale ORM writes and asset Signal construction (`adapters/real_estate/ingestion/wholesale_pipeline.py:47-124,162-218`).
- Adapter-specific assumptions: generic shell, but current mapping embeds real-estate address, folio, listing, bedroom, and sale fields in metadata.
- Overlap: `AssetModel`.
- Observed inconsistencies: current canonical `valuation` is mutable sourced state without observation provenance; no stable external identity or source-record lineage.

### Transaction

- Name: `Transaction`
- Exact file/lines: `core/models/entities.py:49-63`
- Type: canonical dataclass
- Current fields: `id`, `asset_id`, buyer/seller IDs, type/date/price, adapter/source file, metadata
- Current relationships: direct buyer/seller/asset string IDs.
- Current producer(s): no construction found. Imported by `adapters/real_estate/normalization/to_core.py:9` but unused.
- Current consumer(s): no runtime consumer found. `Unknown — needs follow-up` whether external users import it.
- Adapter-specific assumptions: buyer/seller roles and single asset; `source_file` embedded directly.
- Overlap: `TransactionModel`.
- Observed inconsistencies: canonical dataclass is bypassed by buyer ingestion, which constructs ORM rows directly (`adapters/real_estate/ingestion/pipeline.py:150-160`).

### Signal

- Name: `Signal`
- Exact file/lines: `core/models/entities.py:66-81`
- Type: canonical derived-intelligence dataclass
- Current fields: `id`, polymorphic subject, type, value, weight, adapter, detection time, explanation, metadata
- Current relationships: untyped string subject plus discriminator.
- Current producers: adapter normalization (`adapters/real_estate/normalization/to_core.py:112-156`) and ORM-to-dataclass conversion in scoring/matching (`core/scoring/runner.py:29-47`; `core/matching/runner.py:14-25`).
- Current consumers: ORM ingestion, scoring engine, matching engine (`core/scoring/engine.py:13-52`; `core/matching/engine.py:14-95`).
- Adapter-specific assumptions: current signal vocabulary and explanations are real-estate-specific.
- Overlap: `SignalModel`.
- Observed inconsistencies: called canonical source object but semantics are derived; lacks input lineage and algorithm version; sourced facts and inferences are mixed.
