# Expansion Readiness Review — Scaling LUX from One Jurisdiction to Many

**Work Package 4 — Geographic Expansion Research Sprint**
**Scope:** Architecture-only review. No code changes made. Evaluates readiness to scale
from Hillsborough County, FL (the only implemented jurisdiction) to additional Florida
counties, Phoenix/Maricopa County AZ, Troy/Rensselaer County NY, and whatever else the
market-research work package recommends.

**Method:** Read `AGENTS.md` in full, `docs/architecture/ARCH_001_TARGET_MODEL.md` and
`ARCH_001_MODEL_DECISIONS.md`, `core/models/entities.py`, `core/db/models.py`, the full
`adapters/real_estate/` tree, `docs/sources/HILLSBOROUGH_PUBLIC_SOURCE_INVENTORY.md` and
`hillsborough_public_sources.json`, all `.github/workflows/*.yml`, and `docs/ARCHITECTURE.md`.

**Constraint discipline:** Every recommendation below preserves Core as market-agnostic,
preserves the RawEvidence → SourceRecord → Observation/Event provenance chain, never
proposes county-specific logic in `core/`, and prefers "unresolved over false resolution."
Any recommendation that would touch `core/` or a canonical entity is marked
**REQUIRES CTO SIGN-OFF** per AGENTS.md: *"If expansion work starts touching `core/`,
that is itself the signal to stop."* Those are proposals to raise, not approved changes.

---

## 1. Adapter Boundaries

**Current state:** `adapters/real_estate/` is organized into `sources/`, `parsing/`,
`classification/`, `enrichment/`, `normalization/`, `ingestion/`, `linking/`, and
`resolution/`. Structurally this does generalize — `adapters/real_estate/sources/pinellas.py`
already exists as an unimplemented stub for the next Florida county, proving the directory
shape scales to a second source. However, two adapter-wide (not per-jurisdiction) modules
hardcode Hillsborough's identifier vocabulary rather than exposing a jurisdiction-pluggable
contract:

- `adapters/real_estate/resolution/assets.py` — the function is literally named
  `resolve_hillsborough_asset()` and hand-builds identity keys as
  `f"US-FL:HILLSBOROUGH:folio:{folio}"`. A second jurisdiction requires either a parallel
  `resolve_maricopa_asset()` (fine, expected) or — the risk — a temptation to special-case
  the existing function, since nothing enforces a shared resolution interface.
- `adapters/real_estate/linking/asset_linker.py` — `_extract_fields()`'s `field_map` hardcodes
  the canonical identifier vocabulary as `folio`, `pin`, `strap`, `legal_description`,
  `address`. This module is shared across all sources within the real-estate adapter, not
  scoped per county, so it is not purely "adapter-side" in the per-jurisdiction sense the
  Expansion Principles assume — it is *shared adapter machinery* already coupled to
  Hillsborough/Florida field names (folio/PIN/STRAP are Florida property-appraiser
  conventions; Maricopa AZ identifies parcels by APN with no PIN/STRAP equivalent;
  Rensselaer NY uses tax map/SBL numbers and liber/page references, not folio/STRAP at all).

**Recommendation 1.1 — Define a jurisdiction-identifier protocol for the linker**
- *current_state:* `asset_linker.py`'s field vocabulary and `resolution/assets.py`'s key
  format are hardcoded to Hillsborough/Florida conventions inside shared adapter code.
- *proposed_change:* Introduce a small adapter-side (not Core) protocol/interface —
  e.g. `JurisdictionIdentitySchema` — that each jurisdiction's resolution module implements
  to declare its own identifier fields (folio/PIN/STRAP for FL; APN for AZ; SBL/tax-map for
  NY) and canonical key format. `asset_linker.py`'s `_extract_fields`/`_build_asset_index`
  consume that schema instead of a hardcoded field map.
- *expected_benefit:* New jurisdictions extend the linker by declaring a schema rather than
  editing shared code; keeps the "no fuzzy matching, exact-or-unresolved" discipline uniform
  across jurisdictions instead of re-implemented ad hoc each time.
- *migration_cost:* Moderate — one refactor of `asset_linker.py` plus retrofitting
  Hillsborough's existing field map into the new schema shape. No schema/DB change.
- *implementation_risk:* Low-to-moderate. Adapter-only change; existing Hillsborough tests
  (`tests/test_asset_linker.py`) provide a regression harness. Risk is scope creep into
  over-engineering an abstraction before a second real jurisdiction proves the shape right —
  recommend building it *while* implementing Maricopa or the next FL county, not speculatively.

**Recommendation 1.2 — Formalize the adapter contract Hillsborough already demonstrates**
- *current_state:* The adapter boundary (Core imports nothing from adapters; adapters output
  only Core schemas) holds today, verified by inspection of `core/` — no `core/` module
  imports from `adapters/`. This is a real, working strength, not just a stated rule.
- *proposed_change:* Document the concrete file-level checklist implied by Hillsborough's
  layout (`sources/<jurisdiction>.py`, `parsing/<jurisdiction>_*.py`,
  `resolution/resolve_<jurisdiction>_asset()`, `tests/fixtures/<jurisdiction>/`) as the
  literal template new jurisdictions copy, referencing FL-ADAPTER-001.
- *expected_benefit:* Makes the already-good boundary discipline explicit and checkable in
  review, rather than relying on each engineer inferring it from Hillsborough's code.
- *migration_cost:* Low — documentation only, extends existing Expansion Principles.
- *implementation_risk:* Low.

---

## 2. Canonical Entities

**Current state:** `core/models/entities.py` defines `Participant`, `Asset`, `Transaction`,
`Signal` as dataclasses; `core/db/models.py` has the corresponding ORM plus `Event`,
`SourceRecord`, `Observation`, `Match` (per the ARCH-001 target model, `Entity`/
`Participation`/`Relationship`/`Opportunity`/`Prediction` are still planned, not yet built —
`Participant` remains the pre-migration predecessor to `Entity`). The Hillsborough and
Pinellas-stub adapters map cleanly onto this set; nothing about Maricopa or Rensselaer's
data shape (parcels, deeds, liens) obviously needs a *new* top-level canonical concept —
Asset/Transaction/Event/Observation/SourceRecord as currently scoped should hold.

One concrete crack: `source_county` is a literal field on `Participant`
(`core/models/entities.py:26`), `ParticipantModel` (`core/db/models.py:19`), and
`ScoreModel` (`core/db/models.py:91`) — i.e. **Core's canonical schema already encodes an
assumption that "county" is the jurisdiction unit.** This happens to work for every
currently-named expansion target (Hillsborough, Pinellas, Maricopa, Rensselaer are all
counties), but it is jurisdiction-*shaped* rather than jurisdiction-*generic*, and it lives
in Core, not an adapter.

**Recommendation 2.1 — Generalize `source_county` to a jurisdiction identifier — REQUIRES CTO SIGN-OFF**
- *current_state:* `source_county` (free-text string, e.g. `"Hillsborough"`) is a Core field
  on `Participant`/`ParticipantModel`/`ScoreModel`, and `AssetModel.location` JSON is queried
  by a hardcoded `"county"` key in `core/api/data_queries.py:316`.
- *proposed_change:* Rename/generalize to a structured `jurisdiction_code` (e.g.
  `US-FL-HILLSBOROUGH`, `US-AZ-MARICOPA`, `US-NY-RENSSELAER`) with a compatibility read path
  for existing `source_county` values during migration.
- *expected_benefit:* Removes an implicit "market = US county" assumption from Core before
  ADAPTER-002 (a non-real-estate second market) or a non-county jurisdiction makes the
  mismatch actively wrong instead of just imprecise; gives every jurisdiction a single
  canonical, sortable/filterable identity instead of free-text county names.
- *migration_cost:* Moderate — Alembic migration, backfill of existing production rows
  (223 transactions / ~3,856 assets as of the last snapshot), touches
  `core/scoring/runner.py`, `core/api/data_queries.py`, adapter normalization
  (`adapters/real_estate/normalization/to_core.py`), and API response shape.
- *implementation_risk:* Moderate. This is a canonical-schema change in `core/` — per
  AGENTS.md this is explicitly the kind of work that must stop and get CTO sign-off before
  proceeding, not be treated as routine adapter expansion. Flagging as a proposal only; not
  recommended to start without that sign-off, and not urgent at 1-2 jurisdictions.

**Recommendation 2.2 — No new canonical entity needed for AZ/NY at current scope**
- *current_state:* Asset/Transaction/Event/Observation/SourceRecord/Signal/Score/Match cover
  Hillsborough's deed-transfer/parcel domain.
- *proposed_change:* None — explicitly confirm, as a documented decision, that Maricopa and
  Rensselaer's known public-record shapes (recorder deed index, assessor parcel roll,
  liens/judgments) map onto existing entities before any adapter work starts, per Expansion
  Principle 3 ("if a jurisdiction seems to need a new canonical concept, that's a signal to
  stop and raise it explicitly").
- *expected_benefit:* Avoids speculative schema work; keeps the "stop and raise it" discipline
  active rather than assumed.
- *migration_cost:* None (a verification step, done once per new jurisdiction during its
  research phase).
- *implementation_risk:* Low — the risk is process (skipping the verification step under
  time pressure), not technical.

---

## 3. Provenance (RawEvidence → SourceRecord → Observation/Event)

**Current state:** The pipeline is immutable and content-addressed
(`RawEvidenceModel.content_hash`, `storage_uri`), every ingestion is a `PipelineRunModel`,
and `SourceRecordModel` carries `source_name`/`parser_version`/`payload_json` lineage. This
is a real strength and the part of the architecture best proven to generalize — Storage
already uses a jurisdiction-prefixed path convention
(`lux-raw-files/hillsborough/[filename]`), which extends cleanly to
`lux-raw-files/maricopa_az/[filename]`, `lux-raw-files/rensselaer_ny/[filename]`, etc.,
with no collision risk since hashing is content-based.

The gap: jurisdiction is not a first-class, indexed column anywhere in the provenance chain
— it's implicit in free-text `source_name` values (e.g. `"hillsborough_clerk_to_parcels"`).
At one jurisdiction this is invisible. At many, operational questions ("show me all raw
evidence for Maricopa ingested this week," "which jurisdiction's pipeline runs are failing")
require string-parsing `source_name` rather than filtering a column.

**Recommendation 3.1 — Add an indexed jurisdiction column to provenance tables — REQUIRES CTO SIGN-OFF**
- *current_state:* `PipelineRunModel`, `RawEvidenceModel`, `SourceRecordModel` have no
  `jurisdiction_code` column; jurisdiction is only recoverable by parsing `source_name`.
- *proposed_change:* Add a nullable, indexed `jurisdiction_code` column to those three tables
  (additive migration, backfilled from existing `source_name` values via a one-time script).
- *expected_benefit:* Direct filterable/indexable jurisdiction scoping for ops dashboards
  (`/api/ops/sources`, `/api/ops/runs`), audits, and future per-jurisdiction rate/cost
  tracking, without touching the provenance chain's semantics.
- *migration_cost:* Low — additive nullable column, no backfill correctness risk (existing
  rows keep working with `NULL`, backfill script derives values from `source_name` mapping).
- *implementation_risk:* Low, but this is still a `core/db/models.py` schema change and thus
  falls under the "touching core/ is the signal to stop" rule even though it is additive and
  low-risk. Distinguish for sign-off purposes from Recommendation 2.1: this is a new
  *observability* column, not a change to canonical entity semantics — worth flagging that
  distinction explicitly when raising it, since the two carry different risk profiles despite
  both being `core/db/` changes.

**Recommendation 3.2 — Keep the Storage path-prefix convention, make it explicit policy**
- *current_state:* `lux-raw-files/hillsborough/[filename]` is a working, undocumented
  convention (implicit in `adapters/real_estate/ingestion/downloader.py` usage), not a
  written rule.
- *proposed_change:* Document the `lux-raw-files/<jurisdiction_slug>/[filename]` prefix
  convention explicitly in the Repo Structure / Approved Architecture Scaffold section of
  AGENTS.md so every new jurisdiction adapter follows it without reinventing the layout.
- *expected_benefit:* Prevents accidental convention drift (e.g. a future adapter using
  `az_maricopa/` vs `maricopa_az/` vs `maricopa/`) that would complicate later
  cross-jurisdiction tooling.
- *migration_cost:* Negligible — documentation only.
- *implementation_risk:* Low.

---

## 4. Normalization (Legal Description / Address)

**Current state:** `adapters/real_estate/normalization/legal_description.py` is explicitly
scoped to Florida conventions — its own docstring calls it a "Hillsborough / Florida
real-estate legal-description normalizer." It parses LOT/BLOCK/PHASE/UNIT/PARCEL/TRACT
tokens into an order-invariant `LegalComponents` structure and only treats a match as
deterministic when both sides are "strong" (lot+block+subdivision, or lot+subdivision).
This was built the hard way — DATA-006I2 diagnosed that an earlier order-sensitive
normalizer silently produced different canonical strings for the same parcel depending on
whether Clerk or HCPA data put the subdivision name first, and DATA-006I3 fixed it with the
current structured-component model.

**That lesson generalizes; the code does not.** Florida's lot/block/subdivision platting
system is not universal:

- Maricopa County, AZ parcels are identified primarily by APN; legal descriptions for
  unplatted or western-grid land commonly use Section-Township-Range or metes-and-bounds,
  not lot/block/subdivision.
- Rensselaer County, NY uses tax map/SBL (Section-Block-Lot) numbers and deed liber/page
  references — a different identifier and legal-description grammar entirely.

So every new non-Florida jurisdiction needs a **new normalizer written from scratch**, not a
parameterization of the existing one. The reusable part is the *discipline* — order-invariant
structured parsing, explicit strength classification, `matches()` requiring both sides strong
— not the regex/abbreviation table itself.

**Recommendation 4.1 — Extract the normalization *pattern* as a shared contract, keep grammar per-jurisdiction**
- *current_state:* `NormalizedLegalDescription`, `LegalComponents`, and the
  strength-classification constants are hardwired to the FL grammar inside one module with
  no separation between "the discipline" and "the Florida-specific parsing."
- *proposed_change:* Extract a small adapter-level base contract (dataclass shape +
  `is_strong`/`matches()` semantics + the "exact-canonical-match-or-unresolved" rule) that
  each jurisdiction's normalizer must satisfy, while leaving the actual token grammar
  (LOT/BLOCK vs. APN/Section-Township-Range vs. SBL) fully jurisdiction-specific.
- *expected_benefit:* Guarantees the DATA-006I2/I3 lesson (order-sensitivity, no fuzzy
  matching, strength gating) is structurally enforced for every future jurisdiction's
  normalizer, instead of relying on each engineer rediscovering it independently.
- *migration_cost:* Moderate — one refactor pass on the existing FL normalizer to conform to
  the extracted contract, done once, ideally alongside building the first non-FL normalizer
  (Maricopa) so the contract is validated against a genuinely different grammar rather than
  guessed at.
- *implementation_risk:* Moderate. Real risk is under-specifying the contract before a second
  grammar exists to test it against — recommend deferring extraction until Maricopa or Troy
  normalization work actually starts, not doing it speculatively now.

**Recommendation 4.2 — Treat non-FL normalization as its own investigation ticket per jurisdiction**
- *current_state:* No ticket in the registry yet scopes "build the Maricopa legal-description
  /APN normalizer" or "build the Rensselaer SBL normalizer" as work.
- *proposed_change:* When Phoenix/Maricopa or Troy/Rensselaer work is scheduled, open a
  dedicated investigation ticket (per "Investigation always precedes implementation")
  specifically for that jurisdiction's identifier/legal-description grammar, modeled on how
  DATA-006I2 investigated Florida's before DATA-006I3 implemented the fix — do not assume the
  Florida normalizer's structure ports with minor edits.
- *expected_benefit:* Prevents a rushed adapter from silently reusing FL lot/block logic
  against APN or SBL data and producing plausible-looking but wrong canonical keys — exactly
  the "unresolved is better than false resolution" failure mode this project has already been
  burned by once.
- *migration_cost:* None beyond normal ticket scoping.
- *implementation_risk:* Low if followed; the risk being managed is process discipline, not
  code.

---

## 5. Jurisdiction Registry

**Current state:** There is no formal jurisdiction registry. Jurisdiction identity is
scattered across inconsistent representations:

- `docs/sources/hillsborough_public_sources.json` top-level field:
  `"jurisdiction": "Hillsborough County, Florida"` (free text).
- The same file's per-source entries use a different format:
  `"jurisdiction": "FL:HILLSBOROUGH"` (code-like, but inconsistent with the top-level string
  and not documented as a formal code scheme).
- `adapters/real_estate/resolution/assets.py` hardcodes yet a third format inside identity
  keys: `"US-FL:HILLSBOROUGH:folio:..."`.
- AGENTS.md's Expansion Strategy refers to jurisdictions only in prose ("Phoenix, Arizona
  (Maricopa County)").

No single place lists active/planned jurisdictions, their status, or points to their
per-source registry file.

**Recommendation 5.1 — Add a jurisdiction registry doc + stable code scheme**
- *current_state:* No canonical list of jurisdictions; three incompatible ad hoc string
  formats already in use for the one jurisdiction that exists today.
- *proposed_change:* Add `docs/jurisdictions/jurisdiction_registry.json` (mirroring the
  `docs/sources/` pattern) listing each jurisdiction with a single stable code
  (`US-FL-HILLSBOROUGH`, `US-FL-PINELLAS`, `US-AZ-MARICOPA`, `US-NY-RENSSELAER`), status
  (`active` / `validating` / `planned`), state/FIPS metadata, and a pointer to its
  `docs/sources/<jurisdiction>_public_sources.json` file. Adopt that code scheme everywhere
  jurisdiction currently appears as free text (source registries, resolution-key prefixes,
  future `jurisdiction_code` column from Recommendation 3.1).
- *expected_benefit:* One canonical answer to "what jurisdictions exist and what state are
  they in," and a consistent code format that stops proliferating incompatible ad hoc
  strings as jurisdiction count grows past 1.
- *migration_cost:* Low — new doc/JSON file, plus updating the existing Hillsborough registry
  and resolution-key prefix to match the adopted code scheme (a small, mechanical,
  adapter-side + docs-side change — not a `core/` change).
- *implementation_risk:* Low. Best done before Phoenix/Troy work starts, so the second and
  third jurisdictions don't each invent their own ad hoc jurisdiction-string format the way
  Hillsborough's three inconsistent formats already did.

**Recommendation 5.2 — Do not promote to a Core `Jurisdiction` table yet**
- *current_state:* No `JurisdictionModel` exists; jurisdiction is metadata, not a queried
  relational entity.
- *proposed_change:* Keep jurisdiction as a docs/config-level registry (5.1), not a Core
  database table, until query needs prove otherwise — consistent with Approved Scaffold rule
  10 ("PostgreSQL remains sufficient until relationship-query evidence proves otherwise")
  and the general "materialize only when justified" philosophy already applied to
  BuyerProfile/SellerCandidate.
- *expected_benefit:* Avoids a premature `core/` schema change; a docs-level registry is
  sufficient for 2-5 jurisdictions and is trivially promotable to a real table later if
  cross-jurisdiction relational queries (e.g. "all jurisdictions an Entity has bought in")
  become a real product need.
- *migration_cost:* None (explicitly the cost being avoided).
- *implementation_risk:* Low. If a future work package does propose a Core `Jurisdiction`
  table, that is a canonical-entity change and would itself need CTO sign-off — noting this
  now so it isn't proposed casually later.

---

## 6. Source Registry (`docs/sources/`)

**Current state:** `hillsborough_public_sources.json` + `HILLSBOROUGH_PUBLIC_SOURCE_INVENTORY.md`
is a solid, working pattern: per-source `probe_supported`/`ingest_supported`/
`database_write_allowed` flags gate production writes (Pre-Ingestion Source Rule), and
`scripts/probe_public_sources.py` + `.github/workflows/probe-public-sources.yml` operate
against it non-destructively. This generalizes structurally — a new jurisdiction gets its own
`docs/sources/<jurisdiction>_public_sources.json` + companion prose doc, following the exact
same shape.

Two gaps become visible at N jurisdictions × M source types rather than 1×N:

- No top-level index of *which* per-jurisdiction registry files exist (addressed by
  Recommendation 5.1's jurisdiction registry, which can double as this index).
- No formal JSON Schema for the registry file shape — it's implicitly defined by
  `SourceDescriptor.from_mapping()` in `adapters/real_estate/sources/connectors.py`, so a
  malformed new-jurisdiction registry file would only fail at runtime probe/ingest time, not
  at authoring time.

**Recommendation 6.1 — Formalize the source registry JSON Schema**
- *current_state:* Registry file shape is defined implicitly by
  `SourceDescriptor.from_mapping()`'s field access, with no standalone schema to validate
  against.
- *proposed_change:* Extract a JSON Schema (or lightweight Python validation) from
  `SourceDescriptor`'s fields, and have `scripts/probe_public_sources.py` validate a new
  jurisdiction's registry file against it before probing, failing fast with a clear error
  instead of a runtime `KeyError`/silently-wrong default.
- *expected_benefit:* Faster, clearer failure for whoever authors the third, fourth, fifth
  jurisdiction's registry file — catches typos/missing-required-field mistakes before they
  reach a probe workflow run.
- *migration_cost:* Low — one schema file + a validation call added to the existing probe
  script; no change to `SourceDescriptor` itself required.
- *implementation_risk:* Low.

**Recommendation 6.2 — Cross-link the source registry into the jurisdiction registry**
- *current_state:* Per-jurisdiction source registries exist in isolation; nothing lists them
  together.
- *proposed_change:* Covered by Recommendation 5.1 — the jurisdiction registry's per-entry
  pointer to its source registry file *is* the fix; called out here so this section's gap is
  traceable to that recommendation rather than treated as a separate piece of work.
- *expected_benefit:* Avoids building two overlapping registries.
- *migration_cost:* None additional.
- *implementation_risk:* Low.

---

## 7. Scheduling (GitHub Actions)

**Current state:** Contrary to what "scheduled crons" in AGENTS.md's prose might suggest,
inspection of all 19 files in `.github/workflows/` shows only **two** use an actual
`schedule:`/`cron:` trigger (`code-enforcement-scrape.yml`, weekly;
`scheduled-rescrub-stale-phones.yml`, weekly). Every ingestion/linking/scoring workflow
(`manual-ingestion.yml`, `manual-parcel-ingestion.yml`, `manual-asset-linker.yml`,
`targeted-parcel-lookup.yml`, `commit-deterministic-asset-links.yml`, `seller-pressure.yml`,
`buyer-intelligence.yml`, `match-snapshot.yml`, `property-graph-audit.yml`, etc.) is
`workflow_dispatch`-only, with bounded numeric/date inputs, driven either manually or by
`scripts/run_lux_workflow_pipeline.py` (the OPS-AUTO-001 orchestrator CLI) chaining dispatch
→ wait → validate → checkpoint across steps.

This is actually a reasonable foundation for multi-jurisdiction scale: it is not naive
per-source cron, and workflows already take bounded parameters (`max_transactions`,
date ranges, page/subdivision offsets) rather than being hardcoded to fixed batch sizes.
**However, none of the current workflow files take a jurisdiction/adapter-module input** —
they are wired to Hillsborough-specific ingestion service calls under the hood. Left
unaddressed, the natural failure mode when Pinellas/Maricopa/Rensselaer are added is
duplicating each workflow file per jurisdiction (`manual-ingestion-maricopa.yml`,
`manual-ingestion-rensselaer.yml`, ...), which *does* explode linearly with jurisdiction
count even though the current single-jurisdiction setup doesn't look like it will.

**Recommendation 7.1 — Parameterize ingestion/linking workflows by jurisdiction instead of duplicating files**
- *current_state:* Ingestion-family workflow YAML files call Hillsborough-specific scripts/
  services directly, with no jurisdiction selector input.
- *proposed_change:* Add a `jurisdiction` (or `adapter_module`) `workflow_dispatch` input to
  the ingestion, parcel-ingestion, and linker workflows, and have the underlying Python entry
  points resolve the correct adapter module/source config from that input (using the
  jurisdiction registry from Recommendation 5.1) rather than hardcoding Hillsborough.
- *expected_benefit:* Keeps workflow-file count roughly constant as jurisdiction count grows,
  instead of growing linearly; keeps the orchestrator CLI's chaining logic reusable across
  jurisdictions with a single extra parameter.
- *migration_cost:* Moderate — touches each ingestion-family workflow file's inputs and the
  Python scripts they invoke; must preserve today's Hillsborough-only behavior as the default
  during transition (bounded, reviewable change, adapter/ops-level only).
- *implementation_risk:* Moderate. Best sequenced to happen *before* the second real
  jurisdiction (Pinellas or Maricopa) goes into production ingestion, not after — retrofitting
  parameterization once two hardcoded workflow copies already exist in production is more
  work and more risk than doing it once, first.

**Recommendation 7.2 — Keep the manual-approval gates; don't add jurisdiction-based auto-write**
- *current_state:* Write-mode operations (linker commits, scoring writes, outreach) require
  Jaia's explicit approval per the Approved Operational Policy, regardless of source.
- *proposed_change:* None — explicitly preserve this as jurisdiction count grows; do not let
  "more jurisdictions to manage" become pressure to auto-approve write-mode operations for
  new jurisdictions to save review time.
- *expected_benefit:* Keeps the "unresolved is better than false resolution" discipline from
  eroding under the operational load of managing more jurisdictions at once.
- *migration_cost:* None (a policy to hold the line on, not a change).
- *implementation_risk:* Low technically; the real risk is organizational/process drift, which
  is why it's stated explicitly here.

---

## 8. Storage (Supabase Postgres + Storage)

**Current state:** Supabase Storage's content-addressed, jurisdiction-prefixed bucket layout
(Section 3) scales cleanly with jurisdiction count. Postgres is the deeper concern: several
query patterns already load full tables into memory rather than scoping by jurisdiction or
paginating, and this is a problem *before* multi-jurisdiction scale even enters the picture:

- `adapters/real_estate/linking/asset_linker.py`'s `_build_asset_index()` runs
  `session.query(AssetModel).all()` — an unbounded full-table load — on every linker
  invocation, to build an in-memory index by folio/PIN/STRAP/legal/address.
- Graph queries in `core/services/graph/property_graph.py`
  (`get_linked_asset_summary`, `audit_property_graph`) run without jurisdiction scoping,
  by design (GRAPH-001 is intentionally jurisdiction-agnostic today since there's only one).

At Hillsborough's current scale (~3,856 assets per the last production snapshot; the
county's public parcel layer alone estimates ~527,882 total parcels per
`HILLSBOROUGH_PUBLIC_SOURCE_INVENTORY.md`) this is already a real cost, not a hypothetical
one. Maricopa County, AZ has on the order of 1.5M+ parcels. Multiplying this pattern across
several jurisdictions' full parcel universes will make `_build_asset_index()`'s
load-everything-into-memory approach the first thing to break, independent of any
jurisdiction-specific logic.

**Recommendation 8.1 — Scope and index linker/graph queries instead of full-table loads**
- *current_state:* `_build_asset_index()` and related linker queries load and index the
  entire `assets` table in memory on every run, with no jurisdiction or bounded-batch scoping
  beyond the transaction side (`max_transactions`).
- *proposed_change:* Add database-level indexes on the identifier fields currently indexed
  only in Python memory (folio/PIN/STRAP live inside `AssetModel.metadata_` JSON today, so
  this likely means promoting the highest-value identifiers to indexed columns or expression
  indexes), and scope `_build_asset_index()` to the jurisdiction(s) relevant to the current
  batch of transactions being linked rather than the whole table.
- *expected_benefit:* Keeps linker runtime roughly constant per batch instead of growing with
  total cross-jurisdiction Asset count; this is Recommendation 3.1's `jurisdiction_code`
  column's second use case (query scoping, not just observability).
- *migration_cost:* Moderate — requires the Recommendation 3.1 schema change (or an
  equivalent JSON-path index) plus a refactor of `_build_asset_index()`'s query. Should be
  sequenced together with 3.1 rather than as a separate migration.
- *implementation_risk:* Moderate, and this is a `core/db/` schema change (new indexes,
  possibly promoted columns) — flag alongside Recommendation 3.1 for the same sign-off
  conversation. The index-only portion (no semantic change) is lower-risk than the
  jurisdiction-column portion and could be split out and done first if useful.

**Recommendation 8.2 — No sharding/read-replica work yet; revisit with real multi-jurisdiction volume data**
- *current_state:* Single Postgres instance, no partitioning.
- *proposed_change:* None now — explicitly defer sharding/partitioning/read-replica
  discussion until 8.1's indexing fix is in place and real query-latency data exists from at
  least one non-Hillsborough jurisdiction in production, per Approved Scaffold rule 10.
- *expected_benefit:* Avoids speculative infrastructure investment ahead of evidence, matching
  the project's stated bias ("No Kafka, Spark, Flink, Airflow, or microservice split at
  current scale").
- *migration_cost:* None (the cost being deferred, not avoided forever).
- *implementation_risk:* Low now; the risk being managed is doing this work too early.

---

## 9. Graph Integration (GRAPH-001)

**Current state:** GRAPH-001 is explicitly scoped as read-only computed queries over
canonical tables — no separate graph database, no duplicated truth store — and this is
locked in as an Approved Provisional Decision ("No graph database or heavy streaming stack
without demonstrated need"). At today's coverage (12/406 linked transactions, 2.96%) this
is clearly sufficient. The queries in `property_graph.py` are not jurisdiction-scoped, which
is currently correct (there's only one jurisdiction to scope against) but will need revisiting
for two independent reasons as jurisdiction count grows:

- **Query cost**, for the same reason as Section 8 — multi-hop joins
  (Transaction → Event → SourceRecord → Observations, Asset → Transactions) against
  ever-larger, currently under-indexed tables.
- **Product need** — a genuinely cross-jurisdiction graph question ("does this LLC buy in
  both Hillsborough and Maricopa?") requires Entity/Relationship resolution *across*
  jurisdictions, which is exactly the planned-but-not-yet-built ENTITY-001/REL-001 work per
  the ARCH-001 target model, not something GRAPH-001's current per-Asset/per-Transaction
  queries are shaped to answer today.

**Recommendation 9.1 — Keep the computed-graph approach; don't introduce a graph database preemptively**
- *current_state:* Read-only computed queries, no graph DB, per Approved Scaffold rule 10/11.
- *proposed_change:* None — explicitly reaffirm this decision as correct for the current and
  near-term (2-5 jurisdiction) scale. Revisit only when both (a) Recommendation 8.1's indexing
  is in place and still insufficient, and (b) ENTITY-001/REL-001 create genuine
  cross-jurisdiction relationship-query demand that computed joins can't serve.
- *expected_benefit:* Prevents a graph-database introduction that AGENTS.md's own scaffold
  rules already anticipate and reject absent demonstrated need.
- *migration_cost:* None (the point is not doing this yet).
- *implementation_risk:* Low now. If this is revisited later, note explicitly: introducing a
  graph database or a second system of truth would be a `core/` architecture decision and
  would need the same CTO sign-off as any other Approved Scaffold rule reversal — flagging
  this now so a future work package doesn't propose it as routine scaling work.

**Recommendation 9.2 — Add jurisdiction filters to graph API endpoints when the second jurisdiction lands**
- *current_state:* `/api/graph/summary`, `/api/graph/linked-assets`, etc. have no
  jurisdiction query parameter.
- *proposed_change:* Once a second jurisdiction has production data, add an optional
  jurisdiction filter to the graph read endpoints (using Recommendation 3.1/5.1's
  jurisdiction code), so dashboard/ops consumers can scope views without the API always
  returning a cross-jurisdiction blend.
- *expected_benefit:* Keeps the dashboard's graph views legible as data volume grows across
  jurisdictions with very different coverage/maturity levels (e.g. Hillsborough at
  meaningful coverage vs. a newly-launched Maricopa adapter at near-zero).
- *migration_cost:* Low — additive query parameter on existing read-only endpoints, no schema
  change beyond what 3.1 already proposes.
- *implementation_risk:* Low.

---

## 10. Testing Strategy

**Current state:** `tests/` follows a consistent per-feature pattern
(`test_asset_linker.py`, `test_legal_description_normalization.py`,
`test_hcpa_parcel_ingestion.py`, `test_hcpa_crosswalk.py`, `test_hillsborough_clerk_detail_parser.py`,
etc.) backed by `tests/fixtures/hillsborough/` fixture files (sample clerk-detail JSON,
document-type-lookup text) — no live network calls in CI, matching Expansion Principle 7.
This is a well-proven, low-risk pattern that generalizes directly: a new jurisdiction adds
`tests/fixtures/<jurisdiction>/` plus its own `test_<jurisdiction>_*.py` files mirroring the
Hillsborough set.

The one gap is that this pattern is currently *implicit* (inferred from how Hillsborough's
tests happen to be organized) rather than a written requirement, and nothing in the existing
tests specifically regression-tests the "unresolved is better than false resolution"
discipline in a way a new jurisdiction's tests are required to replicate — that discipline is
enforced today by the DATA-006I linker's design plus code review, not by an explicit,
reusable test contract.

**Recommendation 10.1 — Make the fixture/test structure an explicit per-jurisdiction requirement**
- *current_state:* Expansion Principle 7 says "new adapters need their own parser/resolution
  tests, following the existing pattern in `tests/`" — correct in spirit, but doesn't name the
  concrete structure (`tests/fixtures/<jurisdiction>/`, one test file per adapter module).
- *proposed_change:* Add the concrete structure to the Expansion Principles checklist:
  `tests/fixtures/<jurisdiction_slug>/` directory; `test_<jurisdiction>_parser.py`,
  `test_<jurisdiction>_asset_linker.py` (or equivalent) test files; explicit test fixtures
  captured from real (but non-sensitive) sample records, matching how
  `tests/fixtures/hillsborough/clerk_detail/instrument_with_legal.json` was captured.
- *expected_benefit:* Removes ambiguity for whoever builds the Maricopa/Rensselaer adapter
  about what "following the existing pattern" concretely means; makes review consistent.
- *migration_cost:* Low — documentation-only addition to an already-existing principle.
- *implementation_risk:* Low.

**Recommendation 10.2 — Require an explicit "unresolved over false resolution" regression test per jurisdiction**
- *current_state:* The deterministic-only, no-fuzzy-matching discipline is proven for
  Hillsborough by `tests/test_asset_linker.py` and `tests/test_legal_description_normalization.py`,
  but there's no named, reusable pattern requiring every future jurisdiction's linker/normalizer
  to ship an equivalent test asserting it *refuses* to resolve on weak/ambiguous evidence.
- *proposed_change:* Add a checklist item (alongside 10.1) requiring each new jurisdiction's
  test suite to include at least one test that feeds the linker/normalizer intentionally
  ambiguous or weak evidence and asserts it returns unresolved rather than a guessed link —
  mirroring what `test_asset_linker.py` already does for Hillsborough, made an explicit
  requirement rather than an emergent property of copying Hillsborough's tests.
- *expected_benefit:* Directly protects the project's oldest and most load-bearing rule at
  exactly the point (a new, unfamiliar jurisdiction's data, built under expansion-speed
  pressure) where it's most likely to quietly erode.
- *migration_cost:* Low — one test-writing convention, applied per new jurisdiction going
  forward; no retrofit of Hillsborough needed since its tests already effectively do this.
- *implementation_risk:* Low.

---

## Overall Summary — Readiness and Biggest Scaling Risks

**Overall assessment:** The architecture is in genuinely good shape to expand. The
Core/adapter boundary is real and currently unviolated (verified by inspection, not just
by policy), the provenance chain is immutable and content-addressed in a way that already
generalizes across jurisdictions via the Storage path convention, and the canonical entity
set (Asset/Transaction/Event/Observation/SourceRecord/Signal/Score/Match) doesn't obviously
need a new concept for Maricopa or Rensselaer's known data shapes. The "unresolved is better
than false resolution" discipline is well-proven under real pressure (DATA-006I2/I3's
order-sensitivity bug and fix is direct evidence the project catches and corrects exactly
this class of mistake). None of the ten areas reviewed surfaced a blocking architectural
flaw — the gaps found are extension points that don't yet exist, not violations of the
existing design.

**Biggest scaling risk:** The **legal-description/identifier normalization layer** is the
single area where "reuse the existing adapter contract" will be hardest to honor in practice.
`adapters/real_estate/normalization/legal_description.py` and the field vocabulary hardcoded
into `adapters/real_estate/linking/asset_linker.py` are built specifically around Florida's
lot/block/subdivision platting system and folio/PIN/STRAP identifiers. Maricopa County, AZ
(APN-based, Section-Township-Range/metes-and-bounds legal descriptions) and Rensselaer
County, NY (tax map/SBL numbers, liber/page deed references) both require genuinely new
normalizer and linker-field work, not configuration of the existing FL-shaped code. Because
`asset_linker.py`'s field-mapping logic is shared adapter machinery rather than
per-jurisdiction, the realistic failure mode is not a clean new adapter directory — it's
quiet special-casing inside the shared linker/resolution modules as each new jurisdiction is
added under deadline pressure, which would erode the adapter-boundary discipline over time
without ever technically touching `core/`. This is squarely a "prove it a second time"
problem, which is exactly what AGENTS.md's Phoenix/Troy validation strategy already
anticipates — the review's main recommendation (4.1/4.2) is to treat that extraction as work
to do *during* the first non-Florida jurisdiction, not before it and not after it.

**Second-order risk:** Full-table-load query patterns (`_build_asset_index()` in the linker,
unscoped graph queries) are already a latent cost at Hillsborough's single-jurisdiction scale
and will become a real operational problem — independent of any jurisdiction-specific logic —
once Maricopa's much larger parcel universe (roughly 3x Hillsborough's) is added to the same
tables without jurisdiction-scoped indexing.

**Core/ touch points requiring explicit sign-off:** Two recommendations in this review would
touch `core/` and must not proceed without the CTO sign-off AGENTS.md requires:

1. **Recommendation 2.1** — generalizing `source_county` to a structured `jurisdiction_code`
   on `Participant`/`ParticipantModel`/`ScoreModel`. This changes a canonical entity's field
   semantics, not just adds an index — the higher-risk of the two core/ touch points.
2. **Recommendation 3.1 / 8.1** — adding an indexed `jurisdiction_code` column to
   `PipelineRunModel`/`RawEvidenceModel`/`SourceRecordModel`, and adding indexes to
   support scoped (non-full-table-scan) linker/graph queries. This is additive and lower-risk
   than 2.1 (no existing semantics change, nullable, backfillable), but is still a
   `core/db/models.py` schema change and therefore falls under the same "stop and get
   sign-off" rule.

Every other recommendation in this review (adapter-side linker/resolution schema
abstraction, per-jurisdiction normalizer work, the jurisdiction and source registries,
workflow parameterization, testing checklist items) is adapter-, docs-, config-, or
CI-level and does not require touching `core/` or a canonical entity.
