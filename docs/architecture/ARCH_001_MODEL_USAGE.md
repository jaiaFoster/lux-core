# ARCH-001 Model Usage

Current runtime semantics traced from code at starting commit `c07e3fc`. No flows were executed.

## Hillsborough Buyer Flow

- Input: Hillsborough D and P daily index files selected by date (`adapters/real_estate/sources/hillsborough.py:41-82`).
- Adapter/parser: files archived in Supabase Storage, read into temporary files, then parsed by `parse_party_file()` and `parse_document_file()` (`adapters/real_estate/ingestion/downloader.py:55-101`; `adapters/real_estate/ingestion/pipeline.py:84-103`).
- Canonical objects emitted: `Participant` and `Signal`; no `Asset` or canonical `Transaction` is constructed (`adapters/real_estate/ingestion/pipeline.py:105-121`; `adapters/real_estate/normalization/to_core.py:16-38,138-156`).
- ORM tables written: `participants`, `transactions`, `signals`, and one `source_files` party-file row (`adapters/real_estate/ingestion/pipeline.py:127-193`).
- ORM tables read: `source_files`, `participants`, `transactions`, `signals` (`adapters/real_estate/ingestion/pipeline.py:23-58,75-82,127-179`).
- Derived objects created: `repeat_buyer` Signal; its value is later recomputed from transaction count (`adapters/real_estate/normalization/to_core.py:138-156`; `adapters/real_estate/ingestion/pipeline.py:23-58`).
- API consumer: indirect through scoring to `/api/opportunities` and matching to `/api/matches` (`core/scoring/runner.py:21-98`; `api/opportunities.py:11-41`; `api/matches.py:10-18`).
- Dashboard consumer: Opportunities and Matches (`ui/src/App.jsx:237-335,350-362`).
- Missing relationship: transaction-to-existing Asset; explicit seller Participation; D-file manifest; source-record lineage.
- Evidence: `adapters/real_estate/ingestion/pipeline.py:61-212`.

### Confirmed buyer asset-reference breakpoint

1. Asset reference originates from `doc_num = record["document_number"]` at `adapters/real_estate/ingestion/pipeline.py:113-115`.
2. ORM transaction assigns `asset_id=doc_num` at `adapters/real_estate/ingestion/pipeline.py:150-159`.
3. No `Asset` object is emitted: the only normalization calls are `record_to_participant()` and `participant_to_signal()` at `adapters/real_estate/ingestion/pipeline.py:120-121`.
4. No `AssetModel` is imported or persisted in this module (`adapters/real_estate/ingestion/pipeline.py:1-16,127-193`).
5. No FK integrity is enforced: `asset_id` is `Column(String, nullable=False, index=True)` without `ForeignKey` (`core/db/models.py:37-49`); the initial migration also creates plain String ID columns (`core/db/migrations/versions/cb08f30b5b56_initial_schema.py:62-76`).
6. Downstream assumptions: repeat-buyer computation uses only `buyer_id`, so it does not detect missing Assets (`adapters/real_estate/ingestion/pipeline.py:23-58`). No transaction API/dashboard consumer exists. Current observable impact is referential ambiguity rather than a proven runtime exception.

## Foreclosure Flow

- Input: Hillsborough D/P/M bytes downloaded in memory (`adapters/real_estate/sources/foreclosure.py:26-63`).
- Adapter/parser: D/P/M parsers, foreclosure join, then HCPA enrichment (`adapters/real_estate/sources/foreclosure.py:65-93`).
- Canonical objects emitted: `Asset`, seller `Participant`, and asset-scoped `Signal` (`adapters/real_estate/ingestion/wholesale_pipeline.py:47-56`; `adapters/real_estate/normalization/to_core.py:41-135`).
- ORM tables written: `assets`, `participants`, `signals` (`adapters/real_estate/ingestion/wholesale_pipeline.py:69-126`).
- ORM tables read: `assets`, `participants` for upsert lookup.
- Derived objects created: `foreclosure` Signal. Current parser supplies urgency value and explanation from filing type (`adapters/real_estate/parsing/foreclosure_parser.py:19-24,89-119`).
- API consumer: diagnostics count only; no asset/foreclosure API (`api/dev/status.py:30-43`).
- Dashboard consumer: none confirmed.
- Missing relationship: seller-to-Asset/filing Participation; source record; transaction/event; raw archive/run lineage.
- Evidence: `adapters/real_estate/ingestion/wholesale_pipeline.py:29-142`.

## Redfin Flow

- Input: Redfin CSV HTTP response (`adapters/real_estate/sources/listings.py:35-76`).
- Adapter/parser: `parse_redfin_csv()` normalizes listing rows (`adapters/real_estate/parsing/listings_parser.py:25-98`).
- Canonical objects emitted: `Asset` and asset-scoped `Signal`; no Entity/Participant (`adapters/real_estate/ingestion/wholesale_pipeline.py:162-173`).
- ORM tables written: `assets`, `signals` (`adapters/real_estate/ingestion/wholesale_pipeline.py:183-220`).
- ORM tables read: `assets` by address/adapter for upsert.
- Derived objects created: `active_listing` or `price_reduced` Signal based on days on market (`adapters/real_estate/parsing/listings_parser.py:62-71`).
- API consumer: diagnostics count only.
- Dashboard consumer: none confirmed.
- Missing relationship: listing/source record to Asset; seller/listing Participation; reported price/DOM Observations; raw evidence/run lineage.
- Evidence: `adapters/real_estate/ingestion/wholesale_pipeline.py:145-235`.

## Scoring Flow

- Input: all Participant rows and participant-subject Signal rows (`core/scoring/runner.py:21-47`).
- Adapter/parser: none; ORM Signal converted to canonical `Signal` dataclass.
- Canonical objects emitted: transient `Signal` objects only.
- ORM tables written: `scores` unless dry-run (`core/scoring/runner.py:64-92`).
- ORM tables read: `participants`, `signals`, existing `scores`.
- Derived objects created: weighted score, categorical confidence, explanation (`core/scoring/engine.py:22-52`).
- API consumer: `/api/opportunities` (`api/opportunities.py:11-41`).
- Dashboard consumer: Opportunities (`ui/src/App.jsx:237-287,350-355`).
- Missing relationship: generic scored subject; algorithm version; source Observation/Signal lineage; explicit Opportunity.
- Evidence: `core/scoring/runner.py:12-98`.

Asset signals from foreclosure/Redfin do not enter this flow because it iterates Participant rows and queries signals by each participant ID (`core/scoring/runner.py:21-49`).

## Matching Flow

- Input: top `scores`, organization-like `participants`, and their `signals` (`core/matching/runner.py:38-86`).
- Adapter/parser: none; ORM objects converted to canonical Participant/Signal dataclasses.
- Canonical objects emitted: transient `Participant` and `Signal` objects.
- ORM tables written: none.
- ORM tables read: `scores`, `participants`, `signals`.
- Derived objects created: in-memory Match dictionaries using signal-type overlap (`core/matching/engine.py:22-88`; `core/matching/runner.py:86-104`).
- API consumer: `/api/matches` recomputes them on GET (`api/matches.py:10-18`).
- Dashboard consumer: Matches (`ui/src/App.jsx:289-335,357-362`).
- Missing relationship: persisted Match identity, algorithm version, inputs/lineage, explicit Opportunity, candidate role/Participation.
- Evidence: `core/matching/runner.py:28-104`.

## API Flow

- Inputs/reads: `scores` for opportunities; scores/participants/signals for matches; CRM tables for deals/contacts/outreach; all nine tables for diagnostics (`api/opportunities.py:11-41`; `api/matches.py:10-18`; `core/crm/deals.py:10-84`; `core/crm/contacts.py:11-62`; `core/crm/outreach.py:10-62`; `api/dev/status.py:30-84`).
- Writes: deals, contacts, outreach via POST/PATCH; wholesale ingestion trigger can write assets/participants/signals (`api/deals.py:21-41`; `api/contacts.py:21-28`; `api/outreach.py:22-29`; `api/run_wholesale.py:16-44`).
- Derived objects: opportunities are serialized Score rows; matches are computed dictionaries, not persistent models.
- Missing relationship: stable API contracts for Entity/Event/Observation/SourceRecord; data readiness separated from liveness.
- Evidence: health is static (`api/health.py:5-13`); diagnostics are separate/token-gated (`api/dev/status.py:18-93`).

## Dashboard Flow

- Input/API: hardcoded production `/api/health`, `/api/opportunities`, `/api/matches` (`ui/src/App.jsx:3,343-362`).
- Canonical/ORM knowledge: none directly; consumes JSON projections.
- Derived objects displayed: Score rows as Opportunities and in-memory Match rows.
- Missing relationship: no Entity, Asset, Event, Transaction, Observation, SourceRecord, run, freshness, or provenance view.
- Evidence: only Opportunities/Matches tabs render (`ui/src/App.jsx:337-397`). Confidence strings are incorrectly passed to numeric `ScoreBar` (`ui/src/App.jsx:190-199,275,326`).

## Workflow / CRM Flow

- Deals: CRUD on `deals`, with implied participant/buyer and free-text asset address (`core/crm/deals.py:10-84`).
- Contacts: CRUD on `contacts`; Core imports adapter-specific name normalization (`core/crm/contacts.py:3-6,23-39`).
- Outreach: create/list `outreach` with implied deal/contact links (`core/crm/outreach.py:10-62`).
- Dashboard consumer: none confirmed.
- Missing relationships: enforced links, entity/contact-method separation, Opportunity origin, human actor, provenance/audit policy.
