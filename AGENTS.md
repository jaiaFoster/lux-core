# AGENTS.md — LUX Core Orientation File
# Read this first. Every time. Before touching anything.

---

## AGENTS.md Update Policy

This file is the living operational source of truth for LUX agents.

Every PR must update this file if it changes project state, ticket state, architecture, workflow, environment requirements, or known risks.
Every PR must reconcile the full living Ticket Registry, not only the current ticket.

Every review packet must include:

- Tickets closed by the patch
- Tickets newly created by the patch
- Status changes to existing tickets
- Any new blocker discovered
- Blocked/unblocked ticket changes
- Full Ticket Registry reconciliation summary
- Whether the Ticket Registry below was reconciled
- Explicit ask: proceed?

Rules:

- Preserve existing ticket IDs.
- Do not silently delete unfinished work.
- Move completed work to Completed.
- Add newly discovered work to Discovered / Unscoped unless scope is already approved.
- Update the full Ticket Registry, not only Current Priority.
- Jaia merges — Codex never self-merges.

---

## What Is LUX

LUX (Linked Unified Exchange) is a market intelligence platform. It discovers,
scores, and matches participants in fragmented markets: it turns scattered
public records into canonical evidence, scores that evidence into seller and
buyer intelligence, ranks buyer↔seller matches, and routes the best of those
matches into a human-reviewed outreach queue.

Adapter #1 is residential real estate, Tampa Bay FL. **This is not a real
estate app** — real estate is the validation environment for a market-agnostic
Core intelligence engine. See "Project Philosophy" below for the single
question every part of LUX exists to answer, and "Expansion Strategy" for how
the same engine is being proven portable across jurisdictions.

---

## Current Project State

**The infrastructure phase is complete.** LUX has operationally demonstrated,
in production, every piece of the durable data engine the project set out to
build before implementing intelligence:

- **Canonical data model** — Participant/Asset/Transaction/Event/Observation/
  SourceRecord/Signal/Score/Match, PostgreSQL as the system of record
  (ARCH-001, DATA-002).
- **Public record ingestion** — the Hillsborough Clerk daily D/P/M index,
  distress-signal mining, code enforcement, and bulk HCPA parcel ingestion all
  run in production on scheduled crons.
- **Immutable provenance/evidence pipeline** — every ingested file is
  content-hashed and archived to a private Supabase bucket before parsing;
  every canonical record traces back to the raw evidence it came from
  (DATA-006A, OPS-RAW-001, `ARCHIVE_VERIFIED`).
- **Deterministic normalization** — adapters output source-faithful,
  non-fabricated fields; unresolved has always beaten false resolution.
- **Targeted parcel enrichment** — bulk HCPA parcel/legal-description
  ingestion (DATA-006E/J/J1/J2) has written thousands of parcel Assets with
  legal-description evidence.
- **Deterministic Transaction → Asset linking** — a working, replayable,
  reviewed-commit linker (DATA-006I/K/K1) exists and has committed real
  production links. Read that as "the linking machinery is proven," not "the
  graph is fully linked": as of the last production check, 12 of 406
  transactions carry a deterministic Asset link (2.96% coverage). Growing that
  coverage is an open, actively worked problem (DATA-006L, DATA-012, DATA-013,
  INTEL-004, OPS-AUTO-002), not a solved one.
- **GRAPH-001 operational proof** — read-only, computed graph queries over the
  canonical tables (no separate graph database) are live in production,
  verified by a passing production graph audit.
- **Property graph APIs** — `/api/graph/*` (summary, linked-assets, per-asset
  detail, per-asset timeline, per-transaction graph) expose that graph to the
  dashboard and to anything else that wants it.

With that machinery proven, **engineering priority has shifted from building
ingestion infrastructure to improving the derived intelligence built on top of
it, and to closing the loop to a real transaction**:

- INTEL-001 (seller pressure) and INTEL-002 (buyer demand) v1 are live,
  scoring canonical evidence into explainable, versioned projections.
- DATA-009 reconnected `/api/opportunities` and `/api/matches` to those
  projections, replacing an earlier ad hoc scorer/matcher (now deprecated).
- MATCH-001 persists ranked candidate matches with outcome tracking (200
  candidates as of the last snapshot).
- OUTREACH-001 v1 ships human-reviewed, compliance-gated outreach drafts over
  those matches — currently running against the Lead Engine's mock contact
  providers until go-live (LEADGEN-002 through LEADGEN-005).

So: the current priority is not "build the intelligence engine" — it exists
and is live — it's closing the last mile to a real, contacted, transacted
lead. See "Current Project Status" below for exact ticket numbers and the
latest production snapshot, and "Current Strategic Objective" for what all of
this is in service of.

---

## Current Strategic Objective — MVP-001 First Dollar

The company's current strategic objective is a single named milestone:
**MVP-001 — First Dollar.**

**Success is defined as:** generate one successful wholesale transaction
entirely through LUX intelligence, by identifying a motivated seller from
canonical public evidence and a compatible buyer from buyer intelligence, and
closing that match into an actual completed deal.

This is a sharper bar than an earlier, softer definition recorded elsewhere in
this file's ticket history ("first qualified lead + outreach packet"). A
qualified lead and an approved outreach packet are necessary steps on the
path — they are not the milestone itself. A closed transaction is: real money
changing hands because LUX correctly identified the seller, correctly
identified the buyer, and a human closed the loop. This file's Ticket Registry
entry for MVP-001 has been updated to match.

Every ticket, adapter, and intelligence model should be evaluated against one
question: **does this move LUX closer to producing that first real
transaction?** Work that doesn't — another county with no plan to link it,
another signal type with no plan to score it, more UI with no decision it
changes — is lower priority than work that does.

---

## Expansion Strategy

LUX's near-term geographic expansion runs on three tracks in parallel:
continued depth in Florida, and two out-of-state markets chosen specifically
to stress-test architectural portability, not just add data volume.

### Florida — continue expanding

Hillsborough County is proven end to end: ingestion → provenance → canonical
storage → linking → intelligence → matching → outreach. The next Florida
counties should be prioritized using:

- **public data quality** — does the recorder publish a usable, ideally
  machine-readable, daily or bulk index?
- **recorder quality** — stable URLs, no login wall, reasonable rate limits, a
  documented or reverse-engineerable contract.
- **assessor/property-appraiser availability** — a parcel/legal-description or
  folio/PIN source equivalent to HCPA.
- **investor activity** — real wholesale-relevant transaction volume, not just
  raw record counts.
- **transaction volume** — enough deal flow for the county to matter.

Engineers expanding within Florida must reuse the canonical models
(Participant/Asset/Transaction/Event/Observation/SourceRecord/Signal/Score/
Match) and the existing adapter contract under `adapters/real_estate/` without
exception. County-specific business logic belongs in adapter-side parsers and
source clients — never in `core/`. FL-ADAPTER-001 is the formal Florida county
adapter contract this expansion depends on.

### Phoenix, Arizona (Maricopa County) — first out-of-state validation

Purpose: prove the architecture, not just add a market.

- **Validate portability.** Can a new adapter be built against Core's existing
  canonical schemas and ingestion contracts without changing Core itself?
- **Exercise a different recorder ecosystem.** Maricopa's recorder and
  assessor systems are structurally different from Hillsborough/HCPA —
  different formats, different access patterns, parcel numbers instead of
  folio/STRAP. This is deliberately a harder, more different test than another
  Florida county would be.
- **Build buyer history in a western market.** Investor/buyer behavior in a
  fast-growth Sun Belt market outside Florida gives INTEL-002 a genuinely
  independent data point, not more of the same regional pattern.

Success for Phoenix is not transaction volume — it's proof that the adapter
boundary held: Core needed zero changes, and everything county-specific lived
in a new `adapters/real_estate/` source/parser pair.

### Troy, New York (Rensselaer County) — second multi-state validation

Purpose: confirm portability is a pattern, not a one-off.

- **Validate portability a second time**, in a market about as different from
  both Hillsborough and Phoenix as reasonably available — a small Northeast
  county with its own recorder implementation.
- **Exercise another recorder implementation**, widening the set of
  real-world access patterns the adapter contract has proven itself against.
- **Confirm canonical entities remain unchanged.** If Troy also requires zero
  Core schema changes, that's strong evidence the canonical model is actually
  market-agnostic, not just Florida-shaped.

Phoenix and Troy are explicitly architecture-validation milestones, not
revenue bets. Neither is expected to independently justify its own cost the
way continued Florida expansion or MVP-001 delivery is — their value is
proving LUX's adapter model generalizes before further scaling investment
goes into it.

---

## Expansion Principles

Every new jurisdiction — a new Florida county, Phoenix, Troy, or anything
after them — should follow the same workflow:

1. **Research available public sources.** Identify the recorder/clerk daily
   index or bulk file, the assessor/property-appraiser parcel source, and any
   distress/code-enforcement/permit feeds, before writing any code. Document
   access method, format, terms, and rate limits — the same non-mutating
   source-probe discipline already required by the Pre-Ingestion Source Rule.
2. **Build or adapt source adapters.** New `adapters/real_estate/sources/` and
   `adapters/real_estate/parsing/` modules per source. Reuse the existing
   Hillsborough/HCPA adapters as a template wherever the source shape allows.
3. **Map data into canonical entities.** Adapter output must conform to
   Core's existing schemas (`core/models/entities.py`, `core/db/models.py`)
   unchanged. If a jurisdiction seems to need a new canonical concept, that's
   a signal to stop and raise it explicitly — not to quietly bolt it onto the
   adapter.
4. **Preserve provenance.** Every new source's raw files go through the same
   immutable, content-addressed RawEvidence → SourceRecord → Observation/Event
   pipeline. No shortcuts.
5. **Validate deterministic linking.** Reuse the DATA-006I discipline: only
   exact parcel/folio/PIN/STRAP or exact deterministic legal-description/
   address evidence may link a Transaction to an Asset, in any jurisdiction,
   ever. No fuzzy matching, no owner-name matching, no document-number-as-
   identity.
6. **Verify graph integrity.** Confirm the read-only graph queries (GRAPH-001)
   return correct results for the new jurisdiction's data before calling it
   done — linked transactions, unique linked assets, coverage percentage,
   zero invalid foreign keys.
7. **Add regression coverage.** New adapters need their own parser/resolution
   tests, following the existing pattern in `tests/` — fixtures and mocks, no
   live network calls in CI.
8. **Document assumptions.** A short audit doc under `docs/audits/` per new
   source, in the style of the existing DATA-006 series: what was confirmed,
   what wasn't, what the next ticket is.

**New jurisdictions should primarily introduce new adapters — not redesign
the core model.** If expansion work starts touching `core/`, that is itself
the signal to stop and get explicit architectural sign-off before continuing,
not a normal part of expansion.

---

## Intelligence Phase

Seller intelligence (INTEL-001) and buyer intelligence (INTEL-002) v1 are live
in production, scoring canonical evidence into versioned, explainable
projections, reconnected to the read APIs (DATA-009), and persisted into
ranked, outcome-tracked matches (MATCH-001). The first build of the
intelligence phase is done.

What's still open is quality, not existence:

- **Coverage** — match quality is bottlenecked by how many transactions have
  a deterministically linked Asset (2.96% as of the last production check).
  DATA-006L, DATA-012, DATA-013, INTEL-004, and OPS-AUTO-002 all exist
  specifically to grow linked coverage toward pressure-weighted, actionable
  properties rather than raw volume.
- **Confidence estimation** — INTEL-003 (cash-buyer detection) and further
  signal work exist to sharpen what a score actually means, not just how many
  subjects have one.
- **Price context** — VAL-001 remains blocked specifically because reliable
  Asset price context requires deeper linker coverage, not because valuation
  logic itself is unbuilt.

**Operating rule:** additional raw record counts — more ingested transactions,
more scraped distress filings — are valuable only to the extent they improve
match quality, i.e. they either grow deterministic linkage coverage or
sharpen a score's confidence. Ingestion work that doesn't do one of those two
things needs some other explicit justification, not an assumption of default
value. This is the same "unresolved is better than false resolution"
discipline the project has always applied to Asset linking, extended to
intelligence and coverage-growth work generally.

---

## Buyer Validation Strategy — Path to First Dollar

The intended path from where LUX stands today to MVP-001 (First Dollar):

1. **Expand geographic coverage** — continued Florida counties plus
   Phoenix/Troy validation (see Expansion Strategy). *In progress.*
2. **Build richer buyer histories** — INTEL-002, deepened by DATA-010
   (historical deed backfill) and additional markets. *In progress.*
3. **Build seller intelligence** — INTEL-001 seller pressure. **Live.**
4. **Build buyer intelligence** — INTEL-002 buyer demand. **Live.**
5. **Generate buyer ↔ seller matches** — DATA-009 + MATCH-001 persisted,
   outcome-tracked matches. **Live** (200 candidates as of the last snapshot).
6. **Human review** — OUTREACH-001's approval queue: every draft is reviewed
   before it can send; nothing auto-sends. **Live** (v1 shipped 2026-07-22).
7. **Skip trace only the highest-confidence matches** — OUTREACH-003, gated
   on LEADGEN-002 through LEADGEN-005 (production migration, lawful-use
   attestation, provider keys, first live bounded batch). **Not yet live** —
   currently running on mock contact providers.
8. **Contact both parties** — the actual outreach send, once step 7 produces
   real, compliant, callable contacts.
9. **Complete the first wholesale transaction** — MVP-001 itself.

Skip tracing is explicitly a **targeted enrichment step on the
highest-confidence matches only** (step 7), not a bulk ingestion or
blanket-enrichment strategy. It runs after matching, not instead of it, and
only against leads a human has already judged worth contacting. That keeps
cost and compliance exposure bounded, and keeps the system honest about which
contacts are worth having — the same "unresolved is better than false
resolution" philosophy applied to people instead of parcels.

---

## Project Philosophy

LUX exists to answer one question, repeatedly, for every property and every
moment in time:

**Given this seller today, who is the best buyer to contact, and why?**

Every feature, ticket, adapter, and intelligence model should be evaluated
against whether it improves the quality of that recommendation — the accuracy
of "this seller," the precision of "today," the correctness of "best buyer,"
or the honesty of "why." A feature that doesn't sharpen at least one of those
four things is not obviously worth building yet, no matter how interesting it
is on its own.

This is also why the project's oldest rule — unresolved is better than false
resolution — is not just an Asset-linking rule. It's the same discipline
applied everywhere: a wrong "best buyer" recommendation is worse than no
recommendation, because it spends a human's limited outreach attention on the
wrong person and erodes trust in every recommendation after it.

---

## Current Project Status

Current Phase:
Derived Intelligence Live — Outreach Next

Current Milestone:
Both market sides scored from canonical evidence (INTEL-001 seller pressure, INTEL-002 buyer demand), reconnected APIs (DATA-009), and 200 persisted candidate matches with outcome tracking (MATCH-001). Next: human-reviewed outreach packets (OUTREACH-001) toward MVP-001 First Dollar.

Product Milestone:
MVP-001 — First Dollar. Close the first wholesale transaction entirely
sourced and matched through LUX: canonical public evidence → linked
Transaction → Asset → property timeline → seller-side Participant/Entity
evidence → buyer-side evidence → opportunity qualification → human-reviewed
outreach → contacted, closed deal. A qualified lead and an approved outreach
packet are steps on this path, not the milestone itself — see "Current
Strategic Objective" above.

Completed:
- DATA-001 — Repository & Data Flow Audit
- ARCH-001 — Canonical Domain Model Consolidation
- DATA-002 — Schema Migration Foundation + Production Migration
- DATA-003 — First Production Hillsborough Ingestion
- DATA-004A — Production Migration Hotfix for Transaction Asset Nullability
- DATA-004 — Production Migration + Bounded Ingestion Integrity Verification
- DATA-005 — Hillsborough Asset Resolution Classification + Raw Archive Closeout Patch
- DATA-006 — Hillsborough deed-field correction (property/parcel phase remains open)
- DATA-007 — Hillsborough Distress Signal Mining
- DATA-008 — Hillsborough Code Enforcement Integration
- MATCH-002 — Asset Scoring + Price-Fit Matching
- DATA-006A — Supabase Raw Archive Upload Diagnostics + Fix
- OPS-RAW-001 — Production Raw Archive Verification
- INGEST-CORE-002 — Bounded Ingestion Workflow Reliability
- OBS-001 — Ingestion Integrity Counters and Diagnostics
- API-READINESS-001 — Data Readiness + Query API
- API-READY-002 — Readiness Contract Hardening
- DATA-006B — Clerk Instrument Detail Investigation + Evidence Enrichment Infrastructure
- DATA-006C — HCPA Parcel Crosswalk (implemented, not yet wired to live evidence)
- UI-DATA-001 — Dashboard Data Visibility
- DATA-006D — Clerk/HCPA Source Verification + Asset Resolution Unblocker
- OPS-NET-001 — Agent Network Egress Source Verification
- API-METRIC-001 — Fix Misleading Asset Resolution Metric
- DATA-006D — Public Source Inventory + Connector Scaffold
- DATA-006D1 — Source Probe Reliability + Registry Cleanup
- DATA-006E — Hillsborough Public Parcel/HCPA Ingestion
- UI-002 / OPS-002 — Operations & Market Graph Dashboard Rebuild (2026-07-18 closeout)
- INGEST-LINK-001 — Daily re-ingestion no longer wipes committed asset links (2026-07-18)
- LINK-RESTORE-001 — 2 wiped deterministic links restored; graph back to 8 links (2026-07-18)
- INTEL-001 — Seller Pressure / Transaction Readiness Engine v1 (2026-07-18)
- INGEST-DISTRESS-001 — Bounded ingestion distress mining fixed; daily cron mines full day (2026-07-18)
- INTEL-002 — Buyer Intelligence Engine v1 (2026-07-18)
- DATA-009 — Scoring/Matching Reconnection v1 (2026-07-18)
- MATCH-001 — Matching hardening: buy boxes, persisted matches, outcome tracking (2026-07-18)

Current Priority:
- OUTREACH-001 — Human-reviewed outreach drafts and approval queue. First target set exists: 200 persisted candidate matches with lineage. No blind auto-send, no contact enrichment without SKIP-001/ENRICH-001 compliance decisions.

Next:
- OUTREACH-002 — Response capture after OUTREACH-001.
- SKIP-001 / ENRICH-001 — compliance-approved contact source decision (hard dependency for outreach delivery).
- VAL-001 — Valuation once Asset price context deepens via parcel/linker coverage.

Production status snapshot (2026-07-18, post-MATCH-001):
- transactions 223, transactions_with_asset 8, coverage 3.59%, invalid FK 0
- scores: 1,397 seller pressure (1 CRITICAL / 13 HIGH / 201 ELEVATED), 226 buyer demand (13 ACTIVE)
- matches: 200 persisted candidates (run match-snapshot-24b03e4e)
- daily cron now mines distress signals continuously (INGEST-DISTRESS-001)
- schema head: a1c4e9d27b31 (matches table)

First successful Hillsborough production ingestion:
- run_id: `9df53f8a-e733-44b6-97a2-9d44c9cb897d`
- raw_rows: 8426
- source_records: 8349
- events: 2245
- observations: 18915
- errors: 0

Latest bounded ingestion / integrity status:
- Production schema head verified: `9b81c2d4e6f0`
- M-file classification: `DOCUMENT_TYPE_LOOKUP`
- Asset classification: `PARCEL_EVIDENCE_NO_MATCH` for current linker evidence: Clerk legal descriptions exist, but current parcel coverage has no deterministic match.
- Assets resolved/created: `0/0`
- Transactions safely unresolved: `20`
- Invalid Asset FK: `0`
- Dry-run runtime: `4.05s`
- Errors: none
- Raw archive production run `ae735048-5217-42ed-872f-2b53fedf5f5d`: 3/3 uploads verified, 0 fallbacks, 0 failures
- Parcel ingestion production run `d9021414-a9b5-4d70-9e86-b3801764bd37`: 50 Assets, 50 SourceRecords, 300 Observations, raw archive `ARCHIVE_VERIFIED`, transaction linking intentionally 0
- Canceled 2,500-record parcel write uploaded 25 raw pages but did not improve DB coverage: `asset_legal_descriptions_seen` stayed 168, parcel-side PIN/STRAP stayed 500, `candidate_links` stayed 0, `transactions_linked` stayed 0, errors empty. Treat as timeout before DB commit; do not rerun same job.

Confirmed open ingestion-integrity gaps:
- Current Hillsborough D/P/M index files lack property evidence.
- Clerk instrument property data plus HCPA parcel/property data is required for real asset resolution.
- Raw archive is production-verified as `ARCHIVE_VERIFIED`; private bucket preflight and all three content-addressed uploads passed.
- Current runtime directly verified Clerk detail, HCPA exact-folio, and Clerk daily-index access. Clerk detail JSON supplies legal description but no parcel/folio/strap/site address. DATA-006E must inspect HCPA bulk parcel/legal data before deterministic Asset linkage.
- API/dashboard must distinguish total canonical Assets from transaction-linked
  Asset resolution. `assets_resolved` is a compatibility alias for
  transaction-linked transactions, not `assets_total`.
- New public sources must pass the non-mutating source-probe workflow and
  checklist before any production ingestion workflow is clicked.
- Exact parcel source confirmed for DATA-006E:
  `https://maps.hillsboroughcounty.org/arcgis/rest/services/InfoLayers/HC_ParcelsPublic/FeatureServer/0`
  (`dbo.PARCEL_PUBLIC`). Parcel ingestion creates canonical Assets and
  Observations only; Clerk transaction linking remains DATA-006I.
- DATA-006I is the first replayable transaction-to-Asset linker. It may link
  only exact folio/PIN/STRAP, unique deterministic legal description, or exact
  property-address evidence. Document number, owner name, party name, price,
  date, fuzzy legal/address, and guesses are forbidden.
- DATA-006I3 operational verification on main produced targeted candidates
  (`projected_exact_candidates=6`) and proved targeted lookup can fetch 1,163
  parcel records from 25 queries. The follow-up 25-subdivision write timed out
  at the workflow boundary and lost the final result artifact. Do not rerun the
  same 25-subdivision write. DATA-006I4 must process 3-5 subdivisions per run,
  commit per subdivision, persist progress after each subdivision, and resume
  from checkpoint.
- DATA-006I4 operational execution completed targeted parcel writes in chunks:
  0-4, 5-9, 10-14, 15-19, and 20-24. Final linker dry-run with 50 transactions
  produced 8 deterministic candidates, `normalized_legal_ambiguous=0`,
  `transactions_linked=0`, `invalid_asset_fk=0`, and candidate-set hash
  `7eba7828161b7bc77b2fe03ffd7faef4f432f9e270be6b97b0a0db9e036d306d`.
  DATA-006K must commit only bounded reviewed candidates, default 2 links per
  run, with review packet, graph delta, progress checkpoint, rollback metadata,
  and no fuzzy/name/price/date matching.
- DATA-006K operational execution committed all 8 reviewed deterministic links
  in bounded pairs. Final production state: `transactions_with_asset=8`,
  `transactions_without_asset=135`, linkage coverage `5.59%`,
  `invalid_asset_fk=0`, readiness `GRAPH_PARTIALLY_LINKED`. Future writes must
  use immutable reviewed candidate artifacts; shrinking offset semantics are
  deprecated and blocked in production write mode unless explicitly overridden.
- GRAPH-001 must use computed read-only graph queries from canonical tables for
  v1. Do not introduce Neo4j or duplicate canonical data into a second truth
  store.
- Parcel ingestion must run in chunked page ranges after DATA-006J1. Pages 0-4
  already exist; next preferred ranges are pages 5-9, 10-14, 15-19, and 20-24.

North Star:
Build a durable, reusable data engine before implementing intelligence.

Development Philosophy:
1. Understand
2. Normalize
3. Store
4. Query
5. Visualize
6. Score
7. Match
8. Automate
9. Learn

Investigation always precedes implementation. No implementation ticket should begin until the relevant investigation ticket is complete.

---

## Approved Provisional Decisions

- Participant evolves toward Entity.
- Transaction remains first-class.
- Transaction references Event.
- Observation is first-class and represents sourced claims/facts.
- SourceRecord is first-class and represents source-faithful upstream records.
- Incremental migration is preferred; coherent larger patches are allowed because current data volume is limited.
- PostgreSQL remains the system of record.
- Supabase Storage remains the intended raw evidence store.
- Ingestion remains batch-first and replayable.
- BuyerProfile and SellerCandidate are projections, not canonical truth.
- No graph database or heavy streaming stack without demonstrated need.
- Unresolved is preferable to false resolution.
- County document numbers are not canonical Asset identity.
- Hillsborough M files must not be treated as property mappings unless actual evidence proves that variant.

Approved Architecture Scaffold:
1. PostgreSQL is the system of record.
2. Supabase Storage holds raw evidence.
3. Raw evidence is immutable and content-addressable by hash.
4. Every ingestion belongs to a PipelineRun.
5. Every canonical record retains source-evidence provenance.
6. Adapters parse source-specific data; canonical truth remains in Core.
7. Preferred canonical concepts are Entity, Asset, Event, Transaction, Participation, Relationship, Observation, and SourceRecord.
8. Signal, Score, Prediction, Match, and Opportunity are derived intelligence.
9. BuyerProfile and SellerCandidate are projections.
10. PostgreSQL remains sufficient until relationship-query evidence proves otherwise.
11. No Kafka, Spark, Flink, Airflow, or microservice split at current scale.
12. Ingestion is batch-first with replayable boundaries.
13. Adapter-to-canonical contracts are versioned.
14. Derived outputs retain algorithm/model version and input lineage.
15. Liveness, readiness, pipeline health, and data freshness are separate.

Runtime Separation Rule:
- Frontend displays data.
- API exposes endpoints and may trigger jobs.
- Workers and CLI perform ingestion, scraping, parsing, scoring, matching, and heavy analysis.
- Core ingestion services must not depend on Vercel, React, or dashboard code.
- Any scheduled runtime must call the same ingestion service used by CLI.

Pre-Ingestion Source Rule:
- Every new public source must exist in the machine-readable source registry.
- Every new public source must have a prose inventory entry.
- Probe workflows are non-mutating and must not require `DATABASE_URL` or
  Supabase secrets.
- Production ingestion requires source probe artifact review, raw archive plan,
  canonical projection plan, bounded limits, idempotency plan, and Jaia approval.
- Registry flags `database_write_allowed` and `ingest_supported` must both be
  true before a workflow may write a new source to production.

---

## Ticket Registry — Source of Truth

### Current

| Ticket | Owner | Status | Goal | Blocked By | Unlocks |
|---|---|---|---|---|---|
| OUTREACH-001 | Jaia/Codex | IN PROGRESS / v1 SHIPPED 2026-07-22 | Human-reviewed outreach drafts + approval queue over persisted matches | v1 built: match->lead bridge, templated multi-channel drafts (SMS/email/mail), approval lifecycle, compliance-gated to leadgen callable contacts, OutreachModel logging. Contact source now LEADGEN-001 (Option A). Real contacts need leadgen go-live (migration run + attestation + provider keys) | MVP-001 |

### Open — Committed

| Ticket | Owner | Status | Goal | Dependencies / Notes |
|---|---|---|---|---|
| OPS-SYNC-001 | Jaia/Claude | SOURCE-SIDE READY, DESTINATION RESET PENDING JAIA CONFIRMATION | Automated AI-readable project-state mirror: publish AGENTS.md/PROJECT_STATE.yaml/ROADMAP.yaml/OPEN_DECISIONS.yaml/CEO_BRIEF.md/SPRINT_HISTORY to jaiaFoster/lux-core after every push to main | `.github/workflows/publish-ai-state.yml` + `scripts/publish_ai_state.py` (12 unit tests passing) + all 5 required artifacts created this patch. `LUX_STATE_REPO_TOKEN` secret already provisioned by Jaia. Destination repo confirmed to be an abandoned June-2026 project scaffold (2 commits, 61 files, not a fork) — its reset (removing obsolete scaffold content via a normal, non-force commit) requires Jaia's explicit go-ahead before the first sync runs, per this repo's own "confirm before destructive actions on unfamiliar state" discipline. See `docs/runbooks/OPS_SYNC_001_AI_STATE_MIRROR.md` |
|---|---|---|---|---|
| UI-001 | Fox | IN PROGRESS | React app init + dashboard | Continue but do not hardcode data that should come from API |
| INGEST-002 | Kyle | IN PROGRESS | Pinellas County pipeline | Must follow same Evidence → SourceRecord → Observation/Event pattern |
| CRM-002 | Jaia/Claude | BACKLOG | Unified communications dashboard | After dashboard/data readiness work |
| INGEST-CORE-001 | Codex/Kyle | OPEN | Consolidate shared ingestion evidence/archive behavior behind one tested service | DATA-006A fixes current helper; unlock when all adapters use common durable archive contract |
| DATA-010 | Codex/Kyle | OPEN | Historical deed backfill: bulk-ingest clerk index archive (years back) to deepen buyer purchase histories, price bands, and repeat-buyer detection | Use OPS-AUTO-001 orchestrator in bounded chunks; date-range ingestion inputs added 2026-07-18 |
| DATA-011 | Codex/Kyle | OPEN | Seller-side capture: persist FRM/GRANTOR parties and populate transactions.seller_id (currently always null; grantors discarded) | Enables liquidity-event signals + ownership chains; ingestion service change |
| INTEL-003 | Codex/Kyle | OPEN | Cash-buyer detection: deed recorded without concurrent mortgage => cash purchase signal (investor marker) | Derivable from existing D-file doc types; strengthens INTEL-002 demand classification |
| OPS-CI-001 | Codex | OPEN | Add migration/schema smoke to CI and make manual operational workflows easier to verify | Non-blocking |
| OPS-NODE-001 | Fox/Codex | OPEN | Track GitHub Actions Node 20 deprecation warnings from checkout/setup-python/upload-artifact actions | Maintenance only; not a data blocker |
| SEC-NPM-001 | Fox | OPEN | Review pre-existing npm moderate/high audit findings from UI dependency install | Not introduced by data patches; reconfirmed present after `npm install` for this patch's dashboard build |
| DATA-006 | Codex/Kyle | OPEN | Full Hillsborough Property/Parcel Source Integration: resolve transaction-linked Assets using parcel/legal evidence | Depends on API-METRIC-001, DATA-006D/D1, DATA-006E, DATA-006J1, and DATA-006I |
| DATA-006I | Codex/Kyle | OPEN / READY FOR CLOSEOUT | Production Deterministic Linker: write `transactions.asset_id` only for reviewed deterministic candidates with candidate hashes, provenance, idempotency, no silent overwrite | DATA-006K wrote 8 links; SCORE-LIVE-001 push 2026-07-22 committed 4 more (8 -> 12); DATA-006K1 hardens future writes |
| DATA-006F | Codex/Kyle | OPEN | Clerk Civil bulk + daily filing ingestion | Requires source-probe artifact, parser contract, archive/idempotency design |
| DATA-006P | Codex/Kyle | OPEN | Probate daily filing ingestion | Requires compliance review; no auto-outreach based on probate alone |
| DATA-006G | Codex/Kyle | OPEN | Sunbiz entity data baseline + deltas | Separate statewide connector; supports entity/relationship resolution |
| DATA-006H | Codex/Kyle | OPEN | PermitsPlus permit/CO ingestion | Requires parcel linkage and source-probe artifact |
| DATA-006Z | Codex/Kyle | OPEN | GIS zoning/flood/building-footprint enrichment | Requires canonical Asset identity first |
| TAX-001 | Codex/Kyle | OPEN | Hillsborough tax collector / delinquent tax / tax certificate source investigation | Source and terms unknown |
| AUCTION-001 | Codex/Kyle | OPEN | RealAuction foreclosure/tax deed source investigation | Do not scrape behind login without explicit approval |
| SKIP-001 | Jaia/Claude/Codex | OPEN | Compliance-safe free/public contact enrichment strategy | No skip-tracing implementation approved yet |
| FL-ADAPTER-001 | CTO/Codex | OPEN | Florida county adapter contract | Needed before expanding beyond Hillsborough safely |
| DATA-006L | Codex/Claude | IN PROGRESS (campaign started 2026-07-25) | Subdivision-driven targeted parcel coverage campaign: run targeted-parcel-lookup.yml over subdivisions in unlinked transactions in bounded chunks, each followed by linker dry-run -> DATA-006K reviewed commit | 207 distinct missing subdivisions / 260 unresolved tx catalogued (docs/audits/DATA_006L_CAMPAIGN_RUNBOOK.md, target list data006L_targets.json). First chunk (max_subdivisions=5, offset=0) dispatched. Ordering is yield-based (INTEL-004 pressure-weighting blocked on DATA-011). Continue offsets 5,10,15,… ; track absolute linked count + per-chunk yield |
| DATA-013 | Codex/Kyle | OPEN | Clerk instrument-detail legal-desc enrichment at scale: canonicalize more of the 587 raw document.legal_description events into mapping.legal_desc (only 99 enriched) to grow matchable transaction-side evidence | Uses hillsborough_clerk_instrument_detail write path (DATA-ROBUST-001); multiplies with DATA-006L |
| SILD-001 | Codex/Kyle | OPEN (found 2026-07-25) | Clerk legal-description parse defect: the literal string `SILD` is stored as the legal_description on 23 unresolved transactions — a corrupted/placeholder value (likely a mangled 'SUBD'). These 23 can never link until the parser is fixed | Found during DATA-012 triage; ingestion-parse fix in the Hillsborough clerk parser; low effort, unblocks 23 tx |
| DATA-012 | Codex/Claude | TRIAGE DONE / NORMALIZER FIX LANDED 2026-07-25 | Legal-description mismatch triage over the 259 strong no-match descriptions (434 unresolved tx). Result: **88% (229) are missing-parcel coverage, not a normalizer bug** — the DATA-006I3 order-invariant rewrite already cleared the ordering class. Only ~13 have the parcel present; of those 1 already matches (Carriage Park) and ~1 recovered by this fix (Bay Port Colony). Fix: single-letter B/L expansion no longer produces spurious BLOCKBLOCK/BLOCKLOT on doubled/hyphenated identifiers (II-B, B B). 4 regression tests, 401 suite green. See docs/audits/DATA_012_LEGAL_DESC_TRIAGE.md | Conclusion: coverage is the lever -> proceed to DATA-006L (pressure-weighted per INTEL-004). Remaining un-actioned: SILD placeholder legal on 23 tx (new ingest-parse ticket); roman-numeral phase + #N-unit deliberately NOT forced (overlap partial-lot cases that must stay unresolved) |
| INTEL-004 | Codex/Kyle | OPEN / BLOCKED-BY DATA-011 (assessed 2026-07-25) | Pressure-weighted parcel coverage targeting: order parcel ingestion toward subdivisions/ZIPs where INTEL-001 seller-pressure concentrates | **Not yet actionable:** 0 of 434 unresolved tx have an ELEVATED+ pressure participant (only 3 have any pressure score), transactions.seller_id is 100% null (DATA-011), and pressure signals sit on participant subjects (owner names) not parcels. Pressure-weighting today would be fabricated. Unblock: DATA-011 seller capture + ownership→asset links. Interim DATA-006L ordering is yield-based (unresolved tx per subdivision). Evidence: docs/audits/DATA_006L_CAMPAIGN_RUNBOOK.md |
| OPS-AUTO-002 | Codex/Claude | v1 SHIPPED + FULL-AUTO 2026-07-25 | Automated parcel->linker->commit coverage loop, fully unattended | `.github/workflows/ops-auto-002-coverage-loop.yml`: weekly (Mon 07:00 UTC) self-contained loop diagnostics -> parcel dry-run -> parcel WRITE -> linker dry-run -> bounded reviewed DATA-006K link commit -> graph audit -> **Phase 6 safety abort** on any invalid FK/conflict. **Schedule runs mode=commit fully unattended (owner-authorized, see Approved Operational Policy exception); no variable or click needed.** Repo var `OPS_AUTO_002_SCHEDULE_MODE` is an optional kill-switch (report/ingest). Modes resolved by `scripts/ops_auto_002_mode.py` (10 unit tests). Deterministic-only, bounded (candidate_limit 2/pair, commit_max_pairs cap), rollback-logged. Manual dispatch still defaults to safe report |
| LEADGEN-002 | Fox/Kyle | OPEN | Run the leadgen + outreach production migration (Alembic head d7f3a9b1c2e4: lead_*/trace + outreach_drafts) via the manual migration Action; verify production schema head | FIRST go-live step; unblocks every contact/outreach action. Tables are additive; existing tables untouched |
| LEADGEN-003 | Jaia | OPEN | Record the lawful-use attestation (ComplianceSettingsModel via /api/compliance/attest) confirming lawful, non-FCRA use | Skip-trace is hard-blocked until attested (trace jobs cannot enqueue). Requires LEADGEN-002 |
| LEADGEN-004 | Kyle | OPEN | Provision BatchData (skip-trace) + DNC.com (scrub) accounts; add BATCHDATA_API_KEY, DNC_API_KEY, and the DNC SAN number to Vercel env | Providers fall back to safe mocks until keys present; the DNC.com adapter refuses to instantiate without DNC_API_KEY (fail-safe). Legal/vendor terms reviewed here |
| LEADGEN-005 | Kyle/Codex | OPEN | Activate live providers + run the first bounded live skip-trace batch; verify DNC scrub, callable gating, append-only audit, and that no forbidden fields (SSN/DOB/financial) are ever persisted | Requires LEADGEN-002/003/004. Proves real contacts land compliantly before scale |
| OUTREACH-003 | Codex/Jaia | OPEN | Opportunity->lead skip-trace loop: bounded workflow to run the match->lead bridge over top persisted matches and enqueue trace jobs, feeding real callable contacts into the OUTREACH-001 approval queue | Requires LEADGEN-005. Closes the loop from persisted match to a contactable, human-reviewed draft; first real path to MVP-001 |

### Planned — Product / Intelligence

| Ticket | Owner | Status | Goal | Dependencies / Notes |
|---|---|---|---|---|
| ENTITY-001 | CTO/Codex | PLANNED | Evolve Participant toward Entity | After data foundation stabilizes |
| ENTITY-002 | CTO/Codex | PLANNED | Add Participation model for Entity roles in Events/Transactions | After ENTITY-001 |
| REL-001 | CTO/Codex | PLANNED | Relationship model: ownership/control/shared-address/entity graph | After Entity/Participation |
| VAL-001 | Kyle/Codex | PLANNED | Valuation engine: fair value, investor price, likely spread, confidence | Requires reliable Asset profiles |
| OPP-001 | Codex | PLANNED | Opportunity ranking: combine Asset + Entity + pressure + valuation + buyer intelligence | Depends on INTEL/VAL/MATCH |
| ENRICH-001 | Jaia/Claude | PLANNED | Contact enrichment strategy: public/free, paid providers, waterfall, internal skip tracing | Major commercial bottleneck |
| ENRICH-002 | Jaia/Claude | PLANNED | Internal skip-tracing pipeline research/prototype | After ENRICH-001 decision matrix |
| OUTREACH-001 | Jaia/Codex | PLANNED | Human-reviewed outreach drafts and approval queue | No blind auto-send |
| OUTREACH-002 | Jaia/Codex | PLANNED | Response capture + channel preference tracking | After OUTREACH-001 |
| LEARN-001 | CTO/Codex | PLANNED | Outcome learning loop: responses, offers, closes, rejects feed model improvement | After outreach + CRM |
| SOURCE-001 | Kyle | PLANNED | Foreclosure feed integration | Real-estate adapter source |
| SOURCE-002 | Kyle | PLANNED | Probate feed integration | Real-estate adapter source |
| SOURCE-003 | Kyle | PLANNED | Tax delinquency feed integration | Real-estate adapter source |
| SOURCE-005 | Kyle | PLANNED | Permit feed integration | Real-estate adapter source |
| ADAPTER-002 | CTO/Jaia | FUTURE | Select second market adapter after real-estate engine proves reusable | Candidates: land, businesses, equipment, vehicles, surplus inventory |
| MVP-001 | Jaia/Codex | PLANNED | First Dollar milestone: close one real wholesale transaction entirely sourced and matched through LUX — a qualified lead and a reviewed outreach packet are necessary steps, not the milestone itself (sharpened from an earlier "first qualified lead" definition; see "Current Strategic Objective") | DATA-006I, GRAPH-001, INTEL-001, DATA-009, MATCH-001, and OUTREACH-001 are complete/live; remaining path runs through LEADGEN-002…005 (real contact providers) and OUTREACH-003 (skip-trace loop into the approval queue) |
| LAND-001 | Jaia/Codex | PLANNED | Vacant Land Intelligence | After MVP-001 proves real-estate graph/intelligence loop |
| UNCLAIMED-001 | Jaia/Codex | PLANNED | Unclaimed Funds Recovery Vertical Discovery | Future public-record vertical; compliance review before outreach |

### Planned — Business / Growth

| Ticket | Owner | Status | Goal | Notes |
|---|---|---|---|---|
| ROADMAP-001 | — | MONTH 3+ | Social media → idea pipeline | Future growth path |
| ROADMAP-002 | — | MONTH 3+ | Contractor/inspector finder | Potential marketplace add-on |
| ROADMAP-003 | — | MONTH 3+ | Community paid tier | Potential monetization |
| ROADMAP-004 | — | MONTH 3+ | LUX as ad platform | Future monetization |

### Blocked

| Ticket | Status | Reason | Unblock Condition |
|---|---|---|---|
| DATA-006 | PARTIALLY UNBLOCKED | 12 deterministic transaction-to-Asset links exist (8 -> 12 on 2026-07-22); coverage still low at 2.96% (12/406) | Continue deterministic source expansion after GRAPH-001 proof |
| DATA-006I | READY FOR CLOSEOUT | Production linker write proof exists; future batches require DATA-006K1 artifact semantics | Closeout documentation / next deterministic source expansion |
| VAL-001 | BLOCKED | Valuation requires reliable Asset profiles and price context | Deterministic linker coverage growth (DATA-006 open phase) |

### Completed

| Ticket | Status | Evidence |
|---|---|---|
| SPRINT-001 — Geographic Expansion Research & Expansion Framework | COMPLETE 2026-07-24, research/documentation only, no code/schema/ingestion changes | Five work packages: market ranking (`docs/research/market-ranking.md`, top 5 = Pinellas/Maricopa/Orange/Pasco/Duval, Rensselaer kept with a population-decline risk note, Austin/Salt Lake deprioritized as non-disclosure states), public dataset inventory (`docs/research/data-source-inventory.md`, 108 datasets), opportunity-signal research (`docs/research/opportunity-signals.md`, 31 signals), expansion architecture review (`docs/architecture/expansion-review.md`, flags the legal-description normalizer as the top scaling risk and two `core/` touch points needing explicit sign-off before use), open-ended opportunity scan (`docs/research/future-opportunities.md`). Full synthesis in `docs/research/SPRINT-001-SUMMARY.md`. Validates and adds execution detail to the existing Expansion Strategy; does not reverse it. Proposed as new Discovered/Unscoped items below: VACANCY-001, HEIR-001 |
| LEADGEN-001 — Skip Tracing & Lead Management | LANDED ON MAIN 2026-07-22 (forward-merged from feat/leadgen-phase1 / PR #47 work by Kyle); RUNS ON MOCKS until go-live | Self-contained `core/leadgen` module: property import, licensed skip-trace adapters (BatchData + mock), DNC/litigator/suppression compliance gate, lead pipeline, compliant exports. 11 `lead_*`/trace tables via migration `c4a71d02e8b9` (re-parented onto `a1c4e9d27b31`). Leads/Compliance/Reports dashboard tabs. 104 module tests. Go-live steps still pending: run migration, record attestation, add BatchData/DNC.com keys |
| DATA-ROBUST-001 — Signal Robustness Batch 1 | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | (1) Manual ingestion workflow gains date-range + budget inputs for the 7/5-7/17 missed-distress backfill; (2) `hillsborough_clerk_instrument_detail` registry flag `database_write_allowed` enabled with Tim's approval to scale legal-desc enrichment toward SCORE-LIVE-001 thresholds; (3) `/api/ops/summary` now reports per-signal-type freshness (the two-week distress outage would have been visible in a day); (4) absentee-owner signal derivation (`scripts/derive_absentee_signals.py` + workflow, 810 candidates from parcel site-vs-mailing mismatch, INTEL-001 weight 0.15 as readiness multiplier). 4 new tests (280 total) |
| MATCH-001 — Ranked Counterparty Matching Hardening | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | Merged `a244a97`. Migration `a1c4e9d27b31` applied via manual migration workflow (schema head verified in production). First snapshot write approved by Tim: 200 candidate matches persisted (run `match-snapshot-24b03e4e`), progressed-row protection unit-tested. `/api/matches?source=snapshot` live; PATCH outcome round-trip verified in production (candidate -> reviewed -> candidate). Buy-box config ships empty by design; owner-name price-context heuristic investigated and rejected (1/1,397 match rate) |
| DATA-009 — Scoring/Matching Reconnection v1 | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | `/api/opportunities` now serves only the versioned INTEL-001 projection (legacy unversioned scores and buyer scores excluded — previously ALL score rows ranked together, and intel buyer rows would have surfaced as "opportunities"). `/api/matches` replaced legacy signal-overlap matcher (which ranked buyers identically for every opportunity) with `core/intel/market_matching.py` (DATA-009-v1): deterministic read-only pairing of INTEL-001 x INTEL-002, match = 0.45 pressure + 0.35 demand + 0.20 price-fit (buyer band +/-30%, neutral 0.5 unknown), full lineage to both score rows. Legacy core/scoring + core/matching retained but deprecated. 9 new tests |
| INTEL-002 — Buyer Intelligence Engine v1 | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | Merged `e762f3b`. Production write approved by Tim after dry-run review: 226 buyers scored (13 ACTIVE / 213 SINGLE_RECENT), PipelineRun `intel-buyer-intelligence-4ccf036b`. `/api/intel/buyers` live — top: WERNER TRUST (5 purchases), OPENDOOR PROPERTY TRUST I (3, \$170k-\$260k band), PINELLAS EQUITIES/SKYWAY PLUS/BREEZY HOLDINGS LLCs. Full transaction lineage on every score |
| INGEST-DISTRESS-001 — Bounded Ingestion Starved Distress Mining | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | Root cause `_apply_limits` buyer-first sort + truncation cut all distress doc types from bounded runs (0 distress signals mined since 2026-07-04). Fix merged `e4f1ffd`: ParsedGroup carries pre-limit document/party views for distress mining; counts now expose `signals_created`/`distress_signals_created`. Verified: manual ingestion run `898f7677` (group 2026071301) created 593 distress signals; INTEL-001 scoring refresh run `intel-seller-pressure-04779c51` rescored 1,397 subjects (1 CRITICAL / 13 HIGH / 201 ELEVATED / 1,182 LOW) |
| INTEL-001 — Seller Pressure / Transaction Readiness Engine v1 | COMPLETE WITH FOLLOW-UP (v1 shipped 2026-07-18) | `core/intel/seller_pressure.py` (versioned INTEL-001-v1: recency decay 90d half-life, type-weighted distress, distinct-type stacking, equity-as-context, full signal lineage); `scripts/run_seller_pressure.py` (dry-run default, replay mode, --write gated); `api/intel/pressure.py` read-only endpoint; `.github/workflows/seller-pressure.yml`; 10 unit tests. Dry-run on production evidence: 854 subjects, 8 HIGH / 95 ELEVATED / 751 LOW. Initial production score write approved by Tim and executed with `intel_seller_pressure` PipelineRun audit. Follow-ups: distress mining is stale since 2026-07-04 (refresh cadence needed); asset-level pressure aggregation once graph coverage grows; dashboard surfacing |
| LINK-RESTORE-001 — Restore Wiped Deterministic Links | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | Tim explicitly approved. Fix deployed first (`62928f6` READY), then guarded SQL restore of the 2 links from DATA-006K rollback-log evidence, with `asset_link_restore` pipeline_run audit record. Live `/api/ops/summary` confirms 8 linked transactions, 7 unique linked Assets, 3.59% coverage, invalid_asset_fk=0 |
| UI-002 — LUX Dashboard Rebuild | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | PR #46 merged (`265b693`); production deployment READY and commit-matched; dashboard renders live truthful data (GRAPH_PARTIAL_LINK_COVERAGE, 3,856 assets, 223 transactions); `scripts/check_dashboard_ui.mjs` ok; 4/4 ops dashboard tests pass |
| OPS-002 — Operations and Source Freshness Dashboard | COMPLETE / OPERATIONALLY VERIFIED 2026-07-18 | `/api/ops/summary`, `/api/ops/sources` (11 sources), `/api/ops/runs`, `/api/roadmap` all live and correct; daily ingestion crons green through 2026-07-17 |
| INGEST-LINK-001 — Daily Re-Ingestion Wiped Committed Asset Links | COMPLETE (fix authored this patch) | Root cause `ingestion/service.py` existing-transaction branch unconditionally assigned `transaction.asset_id = asset_id` (always None for D/P/M); 2026-07-13 cron re-ingested 2026-06-30 files and nulled 2 of 8 DATA-006K links. Fix: `_apply_transaction_asset_link()` preserves committed links, counts `asset_links_preserved`/`asset_link_conflicts`, never silently overwrites; 6 regression tests in `tests/test_ingestion_link_preservation.py` |
| DATA-001 — Repository & Data Flow Audit | COMPLETE | Audit docs created; no implementation scope creep |
| ARCH-001 — Canonical Domain Model Consolidation | COMPLETE | Entity direction, Transaction/Event, Observation, SourceRecord approved |
| DATA-002 — Schema Migration Foundation + Production Migration | COMPLETE | Production DB migrated to `586b5fe58f0d` and schema verified |
| DATA-003 — First Production Hillsborough Ingestion | COMPLETE | Successful run `9df53f8a-e733-44b6-97a2-9d44c9cb897d` |
| DATA-004A — Transaction Asset Nullability Hotfix | COMPLETE | Production migration to `9b81c2d4e6f0` succeeded |
| DATA-004 — Bounded Production Ingestion Integrity Verification | COMPLETE | Bounded ingestion successful, invalid FK = 0, unresolved transactions preserved; operational archive follow-up closed by DATA-006A/OPS-RAW-001 |
| DATA-005 — Hillsborough Asset Resolution + Raw Archive + DATA-004 Closeout | COMPLETE | M classified as `DOCUMENT_TYPE_LOOKUP`; archive production-verified by DATA-006A; remaining parcel linkage is DATA-006/DATA-006B/DATA-006C |
| DATA-006 — Hillsborough Deed Field Correction | COMPLETE WITH OPEN PHASE | Correct deed parsing merged; property/parcel source integration remains open under the same preserved ID |
| DATA-007 — Hillsborough Distress Signal Mining | COMPLETE | Distress signal mining and resolution merged; old planned Query API scope preserved as API-READINESS-001 |
| DATA-008 — Hillsborough Code Enforcement Integration | COMPLETE | Code enforcement adapter integration merged; old planned dashboard scope preserved as UI-DATA-001 |
| MATCH-002 — Asset Scoring + Price-Fit Matching | COMPLETE | Asset scoring and price-fit matching changes merged; DATA-009 remains broader reconnection work |
| SOURCE-004 — Code Enforcement Feed Integration | COMPLETE | Delivered through DATA-008 |
| OPS-MIGRATE-001 — Manual Alembic Migration GitHub Action | COMPLETE | Workflow applies migrations from GitHub Actions using `DATABASE_URL` secret |
| DATA-006A — Supabase Raw Archive Upload Diagnostics + Fix | COMPLETE | Merged SHA `0d043fa`; production run `ae735048-5217-42ed-872f-2b53fedf5f5d` verified bucket preflight, 3 successes, 0 fallbacks/failures, `ARCHIVE_VERIFIED` |
| OPS-RAW-001 — Production Raw Archive Verification | COMPLETE | Private `lux-raw-files` bucket accepted all three content-addressed D/P/M uploads with HTTP 200 |
| INGEST-CORE-002 — Bounded Ingestion Workflow Reliability | COMPLETE | Merged workflow enforces archive and integrity gates and preserves result artifact |
| OBS-001 — Ingestion Integrity Counters and Diagnostics | COMPLETE | Production artifact verified archive, FK, and duplicate counters; sanitized failure diagnostics remain available |
| DATA-006 — Hillsborough Property/Parcel Source Integration | COMPLETE WITH FOLLOW-UP | PR #24 confirmed HCPA exact folio/PIN/address source and preserved safe unresolved state; DATA-006B/DATA-006C ran this patch, deterministic linkage now requires DATA-006D |
| API-READINESS-001 — Data Readiness + Query API | COMPLETE | PR #24 added five read-only data endpoints; Vercel deployment and preview API smoke passed; PR #25 normalizes legacy unresolved labels only |
| API-READY-002 — Readiness Contract Hardening | COMPLETE | `data_ready_for_scoring` now requires clean integrity, a scoring-safe classification, and linked-count/coverage thresholds instead of one linked transaction; `/api/data/assets?resolved=false` returns HTTP 400 pointing to `/api/data/unresolved`; see `docs/audits/API_READY_002_READINESS_CONTRACT.md` |
| DATA-006B — Clerk Instrument Detail Enrichment + Infrastructure | COMPLETE | Probe + enrichment scripts, GH workflow, source registry entry, 26 tests; write mode confirmed in DATA-006B1. 10 mapping.legal_desc Observations written to production DB. |
| DATA-006B1 — Clerk Enrichment PipelineRun FK Hotfix | COMPLETE | `_create_pipeline_run()` now runs before the document loop; write mode confirmed: 10 RawEvidence, 10 SourceRecord, 10 Observation rows written. |
| DATA-006C — HCPA Parcel Crosswalk | COMPLETE | `adapters/real_estate/resolution/hcpa_crosswalk.py` validates candidate folio/address against HCPA before any Asset resolves; unit-tested against mocked responses; not yet wired into the live pipeline because DATA-006B produced no real candidate to crosswalk — see `docs/audits/DATA_006C_HCPA_PARCEL_CROSSWALK.md` |
| UI-DATA-001 — Dashboard Data Visibility | COMPLETE | Added a read-only "Data" tab to `ui/src/App.jsx` showing readiness, ingestion health, asset resolution, raw archive, and the unresolved queue; `ui/dist` rebuilt and committed — see `docs/audits/UI_DATA_001_DASHBOARD_VISIBILITY.md` |
| DATA-006D — Clerk/HCPA Source Verification + Asset Resolution Unblocker | COMPLETE WITH FOLLOW-UP | Direct Clerk/HCPA/daily-index access verified; observed Clerk JSON parser and bounded five-page fetcher added; legal-only evidence confirmed; exact HCPA crosswalk hardened; DATA-006E required for bulk legal/parcel linkage |
| OPS-NET-001 — Agent Network Egress Source Verification | COMPLETE FOR CURRENT SOURCES | DNS, TLS, and HTTP 200 verified for Clerk detail, HCPA exact folio, and Clerk daily contract; repeatable probe and manual fallback workflow added |
| API-METRIC-001 — Fix Misleading Asset Resolution Metric | COMPLETE | Originally scoped as DATA-006B in handoff; renamed to avoid conflict with DATA-006B Clerk Instrument Detail Investigation. `assets_resolved` now means transaction-linked Assets, not total Assets. |
| DATA-006D — Public Source Inventory + Connector Scaffold | COMPLETE | Public-source inventory, machine-readable registry, connector scaffold, source-probe script/workflow, and pre-ingestion checklist merged in PR #28. |
| DATA-006D1 — Source Probe Reliability + Registry Cleanup | COMPLETE | PR #29 fixed top-level probe status semantics and verified `HC_ParcelsPublic/FeatureServer/0`; unsupported sources no longer hide supported-source failures. |
| DATA-006E — Hillsborough Public Parcel/HCPA Ingestion | COMPLETE | Production run `d9021414-a9b5-4d70-9e86-b3801764bd37` succeeded: 1 raw page, 100 raw rows, 50 Assets, 50 SourceRecords, 300 Observations, `ARCHIVE_VERIFIED`, 0 transaction links by design. |
| DATA-006J1 — Resumable Chunked Parcel Ingestion | COMPLETE | `start_page`/`result_offset` added to connector, ingestion function, standalone script, workflow; per-page commit/checkpoint; PR #38 fixed duplicate `start_page` input; 4-chunk backfill (chunks 5–9/10–14/15–19/20–24) succeeded via OPS-AUTO-001 orchestrator: 2,000 Assets + 2,000 legal observations, 0 errors. |
| OPS-AUTO-001 — GitHub Actions Orchestration CLI | COMPLETE | `scripts/run_lux_workflow_pipeline.py` dispatches, waits, validates, checkpoints; 19 tests passing; orchestration ID `73306e5b` ran DATA-006J2 4-chunk backfill successfully. |
| DATA-006J2 — Resumable Parcel Coverage Backfill | COMPLETE | All 4 chunks (pages 5–9, 10–14, 15–19, 20–24) succeeded: 2,000 Assets, 2,000 legal observations, 0 errors. Linker dry-run showed 0 candidates — diagnosed as order-invariant mismatch (Clerk puts lot/block first; HCPA puts subdivision first). Addressed by DATA-006I3. |
| DATA-006I2 — Legal Description Match Diagnostics | COMPLETE | Read-only diagnostic script + workflow (PR #39) merged and run. Results: 32 no-match rows, 19 abbreviation_token_mismatch, 12 no_plausible_parcel_in_current_coverage, 1 partial. Confirmed root cause: order-sensitive normalizer produced different canonicals for same parcel depending on field ordering. DATA-006I3 addresses this. |
| DATA-006I3 — Targeted Parcel Retrieval + Order-Invariant Normalizer | COMPLETE | Merged to main. Operational dry-run proved targeted LEGAL1 lookup and order-invariant canonicalization; write timeout led to DATA-006I4 chunked recovery. |
| DATA-006I4 — Chunked Targeted Parcel Write + Progress Recovery | COMPLETE | PR #42 merged at `5a281fd`. Post-merge chunks wrote targeted parcel coverage: 1,040 targeted records, 537 created / 503 existing Assets, SourceRecords, and legal Observations, RawEvidence 13 created / 7 existing. Linker dry-run `29206968447` found 8 deterministic candidates, 0 ambiguous, 0 invalid FK, 0 writes. |
| DATA-006K — Deterministic Link Commit Safety Framework | COMPLETE / OPERATIONALLY VERIFIED | PR #43 merged. Bounded dry-run/write pairs committed all 8 deterministic legal-description links. Final check found 0 remaining candidates, 0 invalid FK, 0 conflicts, readiness `GRAPH_PARTIALLY_LINKED`, graph summary shows 8 `transaction_asset` edges. |
| DATA-006K1 — Stable Reviewed-Candidate Commits | COMPLETE / OPERATIONALLY VERIFIED | PR #44 merged and PR #45 route hotfix merged. Future writes consume immutable reviewed candidate artifacts, revalidate exact decision hashes, resume by candidate identity/hash, and reject offset-only production writes unless explicitly overridden. |
| GRAPH-001 — Property Graph v1 | COMPLETE / OPERATIONALLY VERIFIED | Production graph audit run `29210909454` passed after route hotfix: 8 linked transactions, 7 unique linked Assets, 5.59% coverage, 0 invalid Asset refs, dynamic asset/timeline/transaction graph endpoints 200. |
| DATA-006J — Larger Parcel Ingestion + Multi-Page Lineage Fix | COMPLETE WITH FOLLOW-UP | Multi-page raw provenance fixed, combined `parcel.legal_description` observation added, parcel script/workflow added. Larger canceled write exposed need for DATA-006J1 resumable chunks. |
| DATA-006B — Clerk Instrument Detail Enrichment + Infrastructure | COMPLETE | Probe + enrichment scripts, GH workflow, source registry entry, 26 tests; write mode confirmed in DATA-006B1. |
| DATA-006B1 — Clerk Enrichment PipelineRun FK Hotfix | COMPLETE | `_create_pipeline_run()` now runs before the document loop; write mode confirmed: 10 RawEvidence, 10 SourceRecord, 10 Observation rows written. |

Historical ticket-note:
- Earlier DATA-006B/D labels were used for Clerk-detail investigation and
  Clerk/HCPA source verification. The metric fix was later scoped as DATA-006B
  in a handoff, then renamed here to API-METRIC-001 to preserve DATA-006B for
  Clerk Instrument Detail Investigation. DATA-006D remains complete as source
  inventory/scaffold; DATA-006D1 is the probe-reliability follow-up.

### Discovered / Unscoped

| Item | Evidence | Needs Decision |
|---|---|---|
| VACANCY-001 (proposed) | SPRINT-001/WP3+WP5 independently identified HUD's Aggregated USPS Administrative Data on Address Vacancies (free, quarterly, tract-level, no source-probe friction) as the highest-value not-yet-implemented signal researched, extending the live absentee-owner pattern | Scope as a new ticket, prioritize behind existing OPEN work per your call |
| HEIR-001 (proposed) | SPRINT-001/WP3 found heir/inherited property to be the best-evidenced *new* signal researched (Fannie Mae/HAC national study, Urban Institute, NAR-backed UPHPA partition-action mechanism); shares surname-matching/probate-status infrastructure with the already-OPEN DATA-006P | Scope alongside DATA-006P rather than as a fully separate ticket, per your call |
| jurisdiction_code core/ schema change (proposed) | SPRINT-001/WP4 flags two specific core/ changes (generalizing `source_county` to `jurisdiction_code`; adding jurisdiction scoping to PipelineRun/RawEvidence/SourceRecord) as required before Maricopa/Rensselaer adapters can cleanly extend the shared linker without special-casing it | Needs a formal ADR and your explicit sign-off before any Maricopa/Rensselaer implementation work starts, per "if expansion work starts touching core/, that is itself the signal to stop" |
| UI data contract | Dashboard exists but useful data readiness is not yet surfaced | API-READINESS-001 defines read contract; UI-DATA-001 now consumes it (complete this patch) |
| Notion roadmap sync | Workflow exists | Decide whether AGENTS ticket registry should sync to Notion or remain manual |
| Future paid data providers | Contact enrichment is a major bottleneck | ENRICH-001 decision matrix |
| Clerk transaction link evidence | Parcel Assets now exist, but Clerk transaction rows may still lack folio/PIN/STRAP/legal/address evidence | DATA-006I audit decides whether DATA-006B Clerk instrument detail is required |
| Parcel legal description coverage | Canceled 2,500-record write left DB around prior 500-parcel state: `asset_legal_descriptions_seen` 168, parcel-side PIN/STRAP 500, `candidate_links` 0, all 32 strong transaction descriptions `no_match` | DATA-006J1 chunked ranges, then DATA-006I dry-run |

Registry reconciliation for DATA-006A:
- Preserved DATA-006 and recorded its completed deed-parser work plus open property/parcel phase.
- Recorded merged DATA-007 distress and DATA-008 code-enforcement work as complete.
- Preserved displaced planned Query API and dashboard scopes as API-READINESS-001 and UI-DATA-001.
- Added INGEST-CORE-001, INGEST-CORE-002, and OBS-001; retained OPS-RAW-001 as the post-merge operational proof ticket.

Registry reconciliation for DATA-006 + API-READINESS-001:
- Closed DATA-006A, OPS-RAW-001, INGEST-CORE-002, and OBS-001 from merged production proof.
- Removed the stale raw-archive discovery row after moving its verified completion evidence into those completed tickets.
- Set DATA-006 and API-READINESS-001 to current / ready for review.
- Kept UI-DATA-001 and intelligence tickets blocked from scope expansion.
- Added DATA-006B and DATA-006C as discovered follow-ups because current Clerk indexes cannot deterministically query HCPA.
- OPS-NODE-001 remains open and non-blocking.

Registry reconciliation after PR #24 merge / PR #25 compatibility closeout:
- Moved API-READINESS-001 to completed after Vercel deployment and endpoint smoke.
- Moved DATA-006 property-source confirmation to complete with explicit DATA-006B/DATA-006C follow-ups.
- Promoted DATA-006B to current and DATA-006C to open/next; UI-DATA-001 remains open and unchanged.
- No other tickets were renumbered, removed, blocked, or unblocked.

Registry reconciliation after API-READY-002 + DATA-006B + DATA-006C + UI-DATA-001 patch:
- Closed API-READY-002, DATA-006B (investigation phase, open blocker preserved), DATA-006C, and UI-DATA-001; moved all four to Completed.
- Updated DATA-006's follow-up note to point at DATA-006D instead of DATA-006B/DATA-006C, since those two ran this patch.
- Created DATA-006D (Current) — Clerk instrument-detail field extraction, blocked on real page access.
- Created OPS-NET-001 (Open) and added it to Discovered/Unscoped — this coding-agent sandbox's network egress policy denies both `hillsclerk.com` and `gis.hcpafl.org`, discovered while attempting DATA-006B/DATA-006C investigation; production Vercel is unaffected.
- Updated INTEL-001/VAL-001/MATCH-001's Blocked-By column to include DATA-006D, since DATA-006/DATA-006B/DATA-006C alone did not produce live Asset resolution.
- The patch's own instructions referred to dashboard work as "DATA-007"; that ID is permanently assigned to the completed Distress Signal Mining ticket in this registry, so the existing UI-DATA-001 ID was used instead and no duplicate/renumbered ticket was created — see `docs/audits/UI_DATA_001_DASHBOARD_VISIBILITY.md`.
- No ticket was silently deleted, renumbered, or had its history overwritten.

Registry reconciliation after DATA-006D + OPS-NET-001:
- Closed OPS-NET-001 for current Clerk/HCPA sources after direct DNS/TLS/HTTP verification; manual fallback retained.
- Closed DATA-006D with follow-up: observed JSON parser/fetcher complete, but legal-only evidence cannot resolve Assets through BasicSearch.
- Created/promoted DATA-006E as Current for official HCPA bulk parcel/legal crosswalk work.
- DATA-006 remains complete with open phase; INTEL-001, VAL-001, and MATCH-001 remain blocked because linked coverage is still zero.
- OPS-NODE-001 remains open/non-blocking. No ticket deleted or renumbered.

Registry reconciliation after DATA-006I1 patch (merged PR #33):
- Closed DATA-006B and DATA-006B1 (both confirmed complete; write mode producing 10 rows each).
- Closed DATA-006I1 (merged to main as PR #33) — evidence normalization framework v1 with 25 tests passing.
- Linker now gates legal descriptions on strength + canonical match; new audit counters expose normalization diagnostics per sample transaction.

Registry reconciliation after DATA-006J patch:
- DATA-006J promoted to Current (multi-page lineage fix + legal_desc observation + standalone script).
- DATA-006I demoted to Next — blocked on DATA-006J merging first (DATA-006I1 already merged).
- Operational note: DATA-006I1 dry-run showed asset_legal_descriptions_normalized = 4 from 50 parcels. DATA-006J scales to 500+ parcels and adds parcel.legal_description observations so the linker's transaction-side evidence collector can also pick them up directly.
- Discovered/Unscoped updated: "Larger parcel ingestion lineage" resolved by DATA-006J.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after OPS-AUTO-001 + DATA-006J2 patch:
- Added OPS-AUTO-001 as Current — GitHub Actions orchestration CLI (`scripts/run_lux_workflow_pipeline.py`), 19 tests passing.
- Added DATA-006J2 as Current — resumable parcel coverage backfill using orchestrator, chunks 5–9/10–14/15–19/20–24.
- DATA-006J updated: added `start_page` support (connector, ingestion function, standalone script, workflow); fixed `raw_by_page` from list to dict so chunked runs starting at page N map features to correct raw evidence rows.
- DATA-006I remains NEXT — orchestrator will trigger linker dry-run automatically after all parcel chunks pass.
- Added approved operational policy: Codex may use authenticated GitHub CLI to trigger approved bounded ingestion dry-runs, matching write chunks, audits, and linker dry-runs. Linker write mode, destructive operations, scoring writes, enrichment outreach, and production contact actions require Jaia's explicit approval.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-006I patch:
- Closed DATA-006D1 and DATA-006E using PR #29 and production parcel run
  `d9021414-a9b5-4d70-9e86-b3801764bd37`.
- Promoted DATA-006I to Current.
- Added DATA-006J for larger parcel ingestion + multi-page lineage hardening.
- Preserved DATA-006B as Clerk Instrument Detail Investigation if the DATA-006I
  audit proves DailyIndexes insufficient.
- INTEL-001, VAL-001, and MATCH-001 remain blocked until transaction-to-Asset
  coverage is proven.

Registry reconciliation after DATA-006J1 patch:
- Marked DATA-006J complete with follow-up.
- Promoted DATA-006J1 to Current because the 2,500-record write timed out before
  DB coverage improved.
- Kept DATA-006I blocked from write mode while `candidate_links = 0`.
- Updated current blocker from missing instrument detail to parcel coverage
  mismatch: `PARCEL_EVIDENCE_NO_MATCH`.

Registry reconciliation after DATA-006I2 + DATA-006I3 patch:
- Closed DATA-006J1, OPS-AUTO-001, DATA-006J2: all confirmed complete — 4-chunk backfill ran successfully via orchestrator (2,000 Assets, 2,000 legal observations, 0 errors).
- Closed DATA-006I2: diagnostics PR #39 merged and run; 32 no-match rows; root cause confirmed as order-sensitive normalizer.
- Added DATA-006I3 as Current: structured LegalComponents model, order-invariant canonical, targeted ArcGIS LEGAL1 lookup, 3-phase workflow; 63 tests passing; PR open for Jaia review.
- DATA-006I remains BLOCKED pending DATA-006I3 merge + write execution; linker dry-run expected to show candidate_links > 0 afterward.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-006I3 operational verification + DATA-006I/GRAPH-001 branch:
- Moved DATA-006I3 from Current to Completed with operational follow-up evidence.
- Promoted DATA-006I to Current for safe production deterministic link writes.
- Added GRAPH-001 as Current and explicitly blocked completion on production linked-Asset proof.
- Added MVP-001 — First Dollar planned milestone.
- Updated Next path to INTEL-001 then DATA-009/MATCH/OUTREACH after graph proof.
- No ticket deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-006I4 patch:
- Promoted DATA-006I4 to Current after DATA-006I3 operational verification showed the targeted write path must be chunked and resumable.
- Moved DATA-006I from Current to Open/Blocked until targeted subdivision chunks are durably written and linker dry-run candidates are reviewed.
- Moved GRAPH-001 from Current to Open/Blocked until at least one deterministic transaction-to-Asset link exists in production.
- Preserved MVP-001 and intelligence roadmap order.

Registry reconciliation after DATA-006K patch:
- Marked DATA-006I4 complete with post-merge operational evidence: 1,040 targeted records processed and 8 deterministic dry-run candidates found, with 0 ambiguous candidates and 0 invalid FK.
- Promoted DATA-006K to Current as the safety framework required before production `transaction.asset_id` writes.
- Kept DATA-006I blocked until DATA-006K dry-run artifacts are reviewed and bounded write mode commits approved candidates safely.
- Kept GRAPH-001 blocked for completion until at least one DATA-006K production link exists and graph audit can prove a property timeline.
- Preserved MVP-001 / INTEL-001 / DATA-009 / MATCH-001 / OUTREACH-001 order: graph proof before intelligence and first-dollar work.
- No ticket deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-006K1 + GRAPH-001 patch:
- Marked DATA-006K complete / operationally verified with 8 production deterministic links and zero invalid FK.
- Promoted DATA-006K1 to Current to replace shrinking offset writes with immutable reviewed artifacts and decision-hash resume.
- Promoted GRAPH-001 to Current because production linked transactions now exist and graph proof is in scope.
- Moved DATA-006I to ready-for-closeout; future linker batches are governed by DATA-006K1 safety semantics.
- Kept INTEL-001 blocked pending GRAPH-001 audit/timeline proof; OPS-NODE-001 remains open/non-blocking.

Registry reconciliation after GRAPH-001 route smoke:
- Production graph audit passed on main, but direct dynamic Vercel routes for asset/transaction graph detail returned 404.
- Current hotfix adds explicit Vercel rewrites for graph detail endpoints before the generic `/api/(.*)` catch-all and extends graph audit smoke to test dynamic sample paths.
- GRAPH-001 remains Current until the post-merge graph audit proves summary, linked-assets, asset graph, asset timeline, and transaction graph endpoints live.

Registry reconciliation after UI-002 + OPS-002 start:
- Marked DATA-006K1 and GRAPH-001 complete / operationally verified using production graph audit run `29210909454`.
- Promoted UI-002 and OPS-002 to Current to rebuild dashboard and operations/source-freshness visibility from live APIs.
- Moved INTEL-001/INTEL-002/DATA-009 to Next after operators can see graph health, low coverage, and source freshness clearly.
- Added machine-readable roadmap source for UI use; AGENTS.md remains living registry source of truth.
- Kept intelligence/scoring/outreach blocked; no production scoring or outreach work is authorized in UI-002/OPS-002.

Registry reconciliation after UI-002 + OPS-002 closeout (2026-07-18):
- Marked UI-002 and OPS-002 complete / operationally verified: production deployment matches main HEAD `265b693`, all four new ops/roadmap endpoints live, dashboard truthful against live DB state.
- Discovered INGEST-LINK-001 during closeout verification: daily D/P/M re-ingestion silently nulled committed `transactions.asset_id` links (8 → 6 between 2026-07-12 and 2026-07-17; production now shows 6 linked / 223 total / 2.69% coverage). Fix authored in this patch with regression tests; no DB writes performed.
- Created LINK-RESTORE-001 to restore the 2 wiped links from DATA-006K rollback-log evidence; Tim explicitly approved and the restore was executed and verified the same day (8 links, 0 invalid FK, audit record `asset_link_restore`).
- Promoted INTEL-001 from Blocked to Current per the documented Next path.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after INTEL-001 v1 (2026-07-18):
- Shipped INTEL-001 v1: deterministic, versioned, explainable seller pressure projection derived from canonical signals; scores persist to `scores` with `source_adapter=intel_seller_pressure` (no schema migration; projection not canonical truth).
- Scoring write executed only after Tim's explicit approval and dry-run review, honoring the operational policy that scoring writes are never automatic.
- Promoted INTEL-002 to Current; DATA-009 and MATCH-001 remain next per roadmap.
- Discovered: distress signal mining has not run since 2026-07-04 — root-caused and fixed same day as INGEST-DISTRESS-001 (see Completed). Daily cron ingestion now mines the full parsed day for distress signals; no separate cadence needed.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after INTEL-002 v1 implementation:
- Shipped INTEL-002 v1 (engine `core/intel/buyer_intelligence.py`, runner, read-only `/api/intel/buyers`, workflow, 10 tests). BuyerProfile remains a projection; entity form is context, not score; nominal <$1k considerations excluded from price bands.
- Scoring write executed same day with Tim's explicit approval after dry-run review (run `intel-buyer-intelligence-4ccf036b`); DATA-009 promoted to Current.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-009 v1:
- Reconnected derived intelligence end-to-end: canonical evidence -> INTEL-001/INTEL-002 projections -> versioned opportunities and matches APIs. Legacy core/scoring + core/matching are deprecated (superseded), not deleted; legacy scores rows remain in the table but are excluded from APIs.
- /api/matches is a read-only view over persisted projections (no writes on GET) — runtime separation preserved.
- Known v1 limits recorded under MATCH-001: participant-level opportunities have no price context until graph links resolve them to Assets (price_fit neutral); no buy-box config; matches are not persisted.
- Promoted MATCH-001 to Current. MVP-001 path: MATCH-001 -> OUTREACH-001 -> first-dollar packet.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after MATCH-001 implementation:
- Buy boxes are STATED buyer criteria in config/buy_boxes.json (repo-versioned, PR-audited, empty at launch — no fabricated criteria); they take precedence over INTEL-002 observed bands with exact bounds (no +/-30% tolerance).
- Investigated participant-to-parcel price context via order-invariant owner-name matching: only 1 of 1,397 pressured participants matched current parcel coverage (3,663 of ~500k parcels), so the heuristic was NOT shipped — unresolved is better than false resolution. Price context grows via parcel ingestion + deterministic linker.
- matches table migration a1c4e9d27b31 authored via Alembic (head after 6fe982b4090f); production apply via manual migration workflow pending.
- Snapshot semantics: candidate rows refresh on re-snapshot; progressed rows (reviewed/contacted/...) are never overwritten.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after MATCH-001 closeout:
- Migration a1c4e9d27b31 applied through the standard manual workflow; production alembic head verified.
- First match snapshot persisted with Tim's approval: 200 candidate rows, full component lineage to INTEL score rows, PipelineRun audit.
- Outcome tracking verified live via PATCH round-trip.
- Promoted OUTREACH-001 to Current. Its hard dependency is contact information: contacts table is empty and no skip-tracing/enrichment path is approved (SKIP-001 / ENRICH-001) — outreach drafting can proceed against matches, but delivery needs a compliance-approved contact source.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-ROBUST-001 (signal robustness batch 1):
- Shipped: backfill-capable ingestion workflow, instrument-detail write enablement, per-signal-type freshness in ops summary, absentee-owner derivation.
- Registered as new open tickets rather than scope-creeping this patch: DATA-010 (historical deed backfill), DATA-011 (seller-side grantor capture), INTEL-003 (cash-buyer detection). Sunbiz remains DATA-006G; entity resolution remains ENTITY-001.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after DATA-ROBUST-001 production runs (all verified):
- Distress backfill COMPLETE: all 8 missed day-groups mined via date-range ingestion runs — 062501 (878), 062601 (761), 063001 (1,338), 070101 (1,040), 070201 (863), 070601 (733), 070801 (875), 070901 (798) = 7,286 recovered distress signals. Signals table: 1,230 -> 9,197+.
- Clerk instrument-detail enrichment write mode at scale: mapping.legal_desc observations 10 -> 99 (run ffe38b37, archive_raw on). Next step for SCORE-LIVE-001: linker dry-run over the new evidence, then reviewed DATA-006K1 commits.
- Absentee-owner derivation: 810 signals written (run absentee-signals-94b94c24), exactly matching the pre-run SQL estimate.
- INTEL-001 rescored on the enriched evidence: 7,208 subjects — 16 CRITICAL / 131 HIGH / 2,097 ELEVATED / 4,964 LOW (was 1,397 subjects, 1 CRITICAL / 13 HIGH). Top-of-funnel grew ~10x.
- Operational note: date-range bounded ingestion processes ONE group per run (budget limiter breaks after the first group). Single-day dispatches with default budgets are the correct backfill pattern; distress mining always sees the full day regardless of budgets.
- No tickets deleted, renumbered, or silently overwritten.

Operational note 2026-07-18 (post-DATA-ROBUST-001 verification runs):
- Linker dry-run #10 over 250 transactions with the new evidence: classification LINK_EVIDENCE_AVAILABLE; transaction-side legal descriptions now 312; 1 new deterministic exact candidate (0 ambiguous), 240 no-match rows — parcel coverage remains the binding constraint. Next: DATA-006K1 reviewed commit for the 1 candidate (links 8 -> 9, requires explicit approval), and targeted parcel lookup (DATA-006I4 workflow) over the 240 no-match legal descriptions to widen the match pool.
- Match snapshot refreshed post-rescore: 200 computed, 170 created, 30 updated, 0 progressed rows touched (run match-snapshot-f19da47b). The 16 CRITICAL sellers now head the persisted outreach queue.

Approved runbook 2026-07-18 (Tim: "i approve all of it") — SCORE-LIVE-001 coverage push:
1. Targeted parcel lookup (DATA-006I4 workflow), max_transactions=250, dry_run=false, write_enabled=true, in subdivision chunks: offset 0 COMPLETE (run 85a67219, 968 rows), offset 5 dispatched with run_linker_dry_run=true (run dc8d403f), then offsets 10, 15, 20... until targeted keys exhausted. Phase-1 dry-run for the same key set validated in workflow run #14.
2. After parcel chunks: fresh linker dry-run (manual-asset-linker workflow, max_transactions=250, defaults).
3. Commit ALL resulting deterministic candidates via DATA-006K workflow in bounded pairs (dry_run first to produce the reviewed candidate artifact, then dry_run=false + write_enabled=true + reviewed_run=<dry-run's run id>), repeating candidate_offset in steps of 2 per DATA-006K1 semantics. Approval for these linker writes is on record in this note.
4. Then: match snapshot refresh + graph audit.
Each step is clickable from the Actions UI; no further per-step approval needed per this record.

Registry reconciliation after SCORE-LIVE-001 autoresume coverage push (2026-07-22, GitHub Actions recovered from the 2026-07-19 platform outage):
- Gate cleared: githubstatus.com Actions component Operational before any dispatch (only Copilot AI Model Providers was degraded).
- Fresh linker dry-run (manual-asset-linker run 29881411057, max_transactions=250, defaults): candidate_links=4, all DETERMINISTIC_NORMALIZED_LEGAL_DESCRIPTION at MEDIUM_HIGH confidence, classification LINKED_WITH_DETERMINISTIC_EVIDENCE, 0 ambiguous, 0 invalid FK.
- Committed all 4 candidates via DATA-006K in two bounded reviewed pairs per DATA-006K1 semantics: offset 0 (reviewed_run 29881694737 -> write 29881765862, +2), offset 2 (reviewed_run 29881962597 -> write 29882069854, +2); offset 4 dry-run 29882199752 confirmed 0 remaining.
- transactions.asset_id links 8 -> 12; invalid_asset_fk = 0 (verified in Supabase: two asset_link_commit pipeline_runs each inserted_rows=2).
- Match snapshot refreshed with write=true (run 29882436430) and property-graph-audit (run 29882511046) both succeeded.
- /api/ops/summary: transactions_with_asset 12, asset_coverage_percent 2.96%, graph classification GRAPH_PARTIAL_LINK_COVERAGE, unique_linked_assets 10 (2 assets with multiple transactions). Coverage rose from the pre-push 8-link state.
- Parcel coverage remains the binding constraint: widening the match pool still requires more targeted parcel chunks (targeted-parcel-lookup.yml, subdivision_offset 10,15,20..., dry_run=false, write_enabled=true).
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after coverage-strategy ticket intake (2026-07-22, Tim approved adding these to the roadmap):
- Added five OPEN tickets to attack the parcel-coverage constraint surfaced by the SCORE-LIVE-001 push: DATA-006L (subdivision-driven targeted parcel coverage campaign), DATA-013 (Clerk instrument-detail legal-desc enrichment at scale), DATA-012 (legal-description mismatch triage), INTEL-004 (pressure-weighted parcel coverage targeting), OPS-AUTO-002 (automated parcel->linker->commit loop).
- Evidence from live DB probe: 587 events carry document.legal_description but only 99 are canonicalized to mapping.legal_desc; 4,169 assets carry parcel legal descriptions; 12 transactions linked. Overlap between the two sides, not raw evidence volume, is the binding constraint.
- Recommended sequencing: DATA-012 (cheap format audit) -> DATA-013 + DATA-006L (grow matchable evidence + parcels) -> INTEL-004 (aim it at value) -> OPS-AUTO-002 (automate the loop).
- Also reflected in docs/roadmap/lux_roadmap.json (dashboard roadmap) under a new Coverage Expansion section.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after LEADGEN-001 landing + OUTREACH-001 v1 (2026-07-22, Tim approved: land the Lead Engine on main and build OUTREACH-001 on it, Option A):
- Forward-merged the stale feat/leadgen-phase1 (PR #47, Kyle) onto main: resolved core/db/models.py (import union), ui/src/App.jsx (main ops dashboard shell + Leads/Compliance/Reports/Outreach tabs), and ui/dist (rebuilt bundle). Linearized Alembic: re-parented leadgen migration c4a71d02e8b9 onto main's matches migration a1c4e9d27b31; single head is now d7f3a9b1c2e4.
- OUTREACH-001 v1 (Option A: leadgen leads are the single source of truth for contact + compliance):
  * Bridge core/crm/outreach_bridge.py: resolves a persisted match's opportunity Asset -> address+owner -> leadgen LeadProperty+Lead (resolved_asset_id backlink), honoring the global suppression list.
  * Templated multi-channel drafts core/crm/outreach_templates.py (SMS/email/mail), no LLM, no auto-send language.
  * core/crm/outreach_drafts.py: generation gated on currently-callable phones / non-suppressed emails; approval lifecycle (pending->approved->sent / rejected) with the compliance gate re-checked at approve AND send; approved/sent drafts logged to the CRM OutreachModel activity log. Nothing dials/texts/emails.
  * New table outreach_drafts (migration d7f3a9b1c2e4). API: /api/outreach_drafts (GET queue, POST generate) + /api/outreach_drafts/[draft_id] (PATCH review). Outreach dashboard tab with inline target contact.
  * vercel.json: added explicit dynamic routes for outreach_drafts and the leadgen [param] endpoints (leads, trace_jobs, phones/suppress) ahead of the /api/(.*) catch-all. No top-level functions key.
- Tests: 13 new (tests/test_outreach_drafts.py) covering bridge resolve/idempotency/suppression/no-address, compliance-gated generation, idempotent generation, mail-only fallback, approve/reject/edit/mark_sent lifecycle, approval blocked when a contact goes non-callable, and OutreachModel logging. Full suite green: 397 passed (+ code_enforcement standalone). UI builds (vite, 34 modules).
- OUTREACH-001 moved to IN PROGRESS / v1 SHIPPED; its former hard blocker (no contact source) is resolved by LEADGEN-001. Real contacts still require leadgen go-live (run migration on production, record lawful-use attestation, add BatchData + DNC.com provider keys) — none of which were performed here.
- No tickets deleted, renumbered, or silently overwritten.

Registry reconciliation after Lead Engine go-live ticket intake (2026-07-22, Tim: create tickets for what's needed to start getting contacts):
- Added the go-live path as OPEN tickets: LEADGEN-002 (run production migration), LEADGEN-003 (lawful-use attestation), LEADGEN-004 (BatchData + DNC.com accounts/keys + DNC SAN), LEADGEN-005 (activate live providers + first bounded live skip-trace batch), OUTREACH-003 (opportunity->lead skip-trace loop feeding the outreach queue).
- Dependency order: LEADGEN-002 -> LEADGEN-003 + LEADGEN-004 -> LEADGEN-005 -> OUTREACH-003. Until this path is complete the system runs on mock providers, so no real phones/emails are produced.
- Ownership per the Lead Engine brief: migration Fox/Kyle, attestation Jaia, provider keys Kyle. Financial/legal actions (vendor sign-up, key entry) stay with the team, not automated.
- Governance: PR #47's leadgen work is already on main via the 2026-07-22 forward-merge; the PR itself should be closed as landed-via-integration (Jaia/Kyle).
- Also reflected in docs/roadmap/lux_roadmap.json under a new Lead Engine Go-Live section.
- No tickets deleted, renumbered, or silently overwritten.

Documentation reorganization (2026-07-22, AGENTS.md strategic refresh — no code, behavior, or database changes; no ticket status changes):
- Moved "What This Is" up to immediately follow the Update Policy, and inserted new onboarding-oriented sections ahead of the existing "Current Project Status" detail: Current Project State, Current Strategic Objective (MVP-001 First Dollar), Expansion Strategy (Florida county criteria, Phoenix/Maricopa, Troy/Rensselaer), Expansion Principles (8-step new-jurisdiction workflow), Intelligence Phase, Buyer Validation Strategy, and Project Philosophy.
- Sharpened MVP-001's success definition from "first qualified lead + outreach packet" to "one closed wholesale transaction," per explicit direction from Jaia; updated both the Product Milestone line and the MVP-001 Ticket Registry row (Planned — Product / Intelligence) to match, including a refreshed dependency list (GRAPH-001/INTEL-001/DATA-009/MATCH-001/OUTREACH-001 are now complete; the live remaining path is LEADGEN-002…005 and OUTREACH-003).
- Added Phoenix (Maricopa County, AZ) and Troy (Rensselaer County, NY) as approved forward expansion targets. Neither has any ingestion, adapter, or ticket work started yet — they are documented as planned architecture-validation milestones, not claimed as in-progress or complete.
- Supplemented the Live API Endpoints and Database tables with the Graph/Intel/Ops/Lead-Engine/Outreach/Compliance surface that had been built in production but was undocumented here (endpoints in `api/graph/`, `api/intel/`, `api/ops/`, `api/leads*`, `api/trace_jobs*`, `api/compliance/`, `api/outreach_drafts*`, plus the `matches` and Lead Engine tables in `core/db/models.py`). Flagged that full request/response contracts for that surface are not yet documented to the same depth as the original five endpoints — an open gap, not claimed as complete.
- Added the three pending Lead Engine provider environment variables (BATCHDATA_API_KEY, DNC_API_KEY, DNC_SAN) to Environment Variables, marked pending per LEADGEN-004.
- Did not alter any ticket's status, owner, or evidence in the Ticket Registry itself (other than the MVP-001 row above); did not delete or renumber any ticket; the full Ticket Registry, all historical reconciliation notes, and all governance sections (Critical Rules, Adapter Boundary, Approved Operational Policy, Handoff Standard) are preserved verbatim.

Registry reconciliation after SPRINT-001 (2026-07-24, Geographic Expansion Research & Expansion Framework):
- Closed SPRINT-001 as a research/documentation-only ticket — no code, schema, or ingestion changes; see full evidence in the Completed table above and the full review packet at `docs/research/SPRINT-001-SUMMARY.md`.
- Added VACANCY-001, HEIR-001, and a proposed `jurisdiction_code` core/ schema change to Discovered/Unscoped, all requiring your decision before any implementation work begins; none are scoped or approved by this patch.
- Validated, not changed, the existing Expansion Strategy: continued Florida expansion, Maricopa/Phoenix, and Rensselaer/Troy are all confirmed as still the right priorities, with added execution detail (an evidence-ranked Florida county order — Pinellas, Orange, Pasco, Duval — and a risk note on Rensselaer's population decline and weak permit/probate access, both already framed correctly in the existing Buyer Validation Strategy language as a non-revenue architecture-validation bet).
- `FL-ADAPTER-001` and `DATA-006P` remain OPEN, unchanged in status, but SPRINT-001's research adds concrete rationale for sequencing them (FL-ADAPTER-001 before further FL county work; DATA-006P alongside the new HEIR-001 proposal).
- No ticket deleted, renumbered, or silently overwritten. No production system, data, or scoring behavior was touched by this patch.

Registry reconciliation after OPS-SYNC-001 (2026-07-25, source-side build — destination reset not yet executed):
- Added OPS-SYNC-001 to Open — Committed: automated AI-state mirror publishing AGENTS.md and four new structured artifacts (PROJECT_STATE.yaml, ROADMAP.yaml, OPEN_DECISIONS.yaml, CEO_BRIEF.md) plus SPRINT_HISTORY/ to `jaiaFoster/lux-core` after every push to main.
- Created the project-state artifact contract itself this patch — none of the 5 required artifacts existed before OPS-SYNC-001; all are derived from this file's existing content, not a new source of truth.
- Confirmed `LUX_STATE_REPO_TOKEN` already exists as a secret on this repository (provisioned 2026-07-25) and that `jaiaFoster/lux-core` is a real, independent (non-fork) repository — an abandoned initial project scaffold from 2026-06-28, 2 commits, 61 files — not an unrelated or currently-active repository.
- Did **not** execute the destination-repository reset or the first synchronization run: per this project's standing discipline on destructive/hard-to-reverse actions against previously unexamined state, and because the ticket's own `automated_updates`/`reset_commit` authorization does not substitute for a same-session explicit go-ahead, that step is held pending Jaia's confirmation in chat.
- Did not honor the ticket's `merge_policy.source_repository.auto_merge_authorized: true` — unchanged from SPRINT-001's precedent, Jaia merges this PR, per Critical Rule #10.
- No ticket deleted, renumbered, or silently overwritten. No production system, data, or scoring behavior was touched by this patch, and `jaiaFoster/lux-core` was only read (via `gh repo view`/`gh api`), never written to, during this patch.

---

## Who Owns What

| Person | Role | Owns |
|---|---|---|
| Jaia | COO | All PRs. Merges everything. Final say on architecture. |
| Fox (fsassaman) | CEO | UI, GitHub org, Vercel, Supabase deployment/config. |
| Kyle | CTO | Data architecture, adapters, Pinellas pipeline, buy-box matching. |
| Colton | Data/ML | Scraping, database, AI/ML support. |
| Claude (AI) | Architect | Handoffs, architecture decisions, ticket system. |
| Codex | Coding agent | Implements scoped tickets only. Never self-merges. |

Jaia merges all PRs. Never self-merge.

---

## Approved Operational Policy

Codex may use the authenticated GitHub CLI (`gh`) to trigger the following without
additional approval, provided Jaia has merged the OPS-AUTO-001 branch:

- Bounded parcel ingestion **dry-runs** (any chunk, any page range)
- Bounded parcel ingestion **write mode** only after the matching dry-run passes validation
- Evidence audits (`audit_asset_link_evidence.py`)
- Transaction-to-Asset linker **dry-runs**

**Authorized exception — OPS-AUTO-002 (Tim/Fox, 2026-07-25):** the OPS-AUTO-002
scheduled coverage loop MAY automatically commit deterministic transaction→Asset
links each week with no per-run human approval. This is sanctioned because every
such write is deterministic-only (exact, unique folio/PIN/STRAP/legal match — no
fuzzy/name/price/date), bounded (candidate_limit 2/pair, commit_max_pairs cap),
backed by an in-job immutable reviewed candidate artifact (DATA-006K1),
rollback-logged, and hard-aborted on any invalid Asset FK or link conflict.
Kill-switch/throttle: set repo variable `OPS_AUTO_002_SCHEDULE_MODE` to `report`
(pause all writes) or `ingest` (pause link writes). Jaia to be kept informed.
This is the ONLY sanctioned automatic linker write; the rule below still applies
to every other linker/scoring/matching write.

Codex must never automatically trigger:

- Linker **write mode** (transaction.asset_id updates) — requires Jaia's explicit approval, EXCEPT the OPS-AUTO-002 loop above
- Scoring or matching writes
- Outreach, contact enrichment, skip-tracing
- Destructive DB operations, production cleanup
- Any action not listed above

---

## Critical Rules

1. Core never imports from adapters/. Adapters import Core schemas only.
2. Every DB schema change goes through Alembic. Never manual production DB edits.
3. Prefer Alembic autogenerate; hand-edit migrations only for data migration logic or verified migration defects, and document why in the review packet.
4. `dry_run=True` / `DRY_RUN=true` must never write to the database. Ever.
5. Flask is gone. API layer is Vercel serverless in `api/` at repo root.
6. Before writing any fix, cite the file and line number as evidence.
7. No code behavior change without a verification plan.
8. No secrets in files, PRs, logs, or chat.
9. Never fabricate Asset links. Unresolved is better than false resolution.
10. Never self-merge. Jaia merges.

---

## Repo Structure

```text
api/                    Vercel serverless endpoints (one file = one route)
core/models/            Canonical entity schemas — Participant, Asset, Transaction, Signal
core/scoring/           ScoringEngine + runner — weighted signal scoring
core/matching/          MatchingEngine + runner — signal overlap buyer matching
core/crm/               CRM service layer — deals, contacts, outreach
core/db/                SQLAlchemy ORM models, session, Alembic migrations
core/logger.py          Canonical logger — always use get_logger(__name__)
adapters/real_estate/   Real estate adapter — ingestion, parsing, classification, normalization
ingestion/              Runtime-independent ingestion orchestration used by CLI/future workers
scripts/                Local run scripts — ingestion, Hillsborough, scoring, matching, schema checks
ui/                     React/Vite dashboard — Fox owns
data/raw/               Gitignored — local temp cache only
data/output/            Gitignored — CSV outputs from scoring and matching
docs/                   PRD, architecture docs, handoff standard, audits
.github/workflows/      Notion roadmap sync, manual migrations, bounded ingestion workflows
```

Supabase Storage bucket:

```text
lux-raw-files
└── hillsborough/[filename]   raw county files, permanent
```

---

## Live API Endpoints

Base URL:

```text
https://lux-core-sepia.vercel.app
```

| Method | Endpoint | Description | Key Params |
|---|---|---|---|
| GET | /api/health | Service status check | none |
| GET | /api/opportunities | Top 50 scored participants | none |
| GET | /api/matches | Ranked buyer→opportunity matches | none |
| GET | /api/deals | List deals | `?status=lead|contacted|under_contract|closed|dead` |
| POST | /api/deals | Create deal | body: `{title, status, participant_id, buyer_id, asset_address, asking_price, notes}` |
| PATCH | /api/deals | Update deal | body: `{id, ...fields}` |
| GET | /api/contacts | List contacts | `?contact_type=owner|buyer|agent|attorney|contractor` |
| POST | /api/contacts | Create contact | body: `{name, contact_type, phone, email, participant_id, notes}` |
| GET | /api/outreach | List outreach logs | `?deal_id=`, `?contact_id=` |
| POST | /api/outreach | Log outreach activity | body: `{outreach_type, deal_id, contact_id, direction, status, notes}` |
| GET | /api/dev/status | Dev diagnostic — DB counts, pipeline health | `?token=[LUX_DEV_TOKEN]` |
| GET | /api/data/readiness | Public read-only DB/archive/resolution readiness | none |
| GET | /api/data/ingestion | Recent pipeline runs and integrity summaries | `?limit=10` (max 250) |
| GET | /api/data/assets | Canonical Asset query (canonical-Asset-only; `resolved=false` returns HTTP 400, see `/api/data/unresolved`) | `?limit=&offset=&source_county=` |
| GET | /api/data/transactions | Transaction and Asset-linkage query | `?limit=&offset=&with_asset=&document_number=` |
| GET | /api/data/unresolved | Explicit unresolved transaction work queue | `?limit=&offset=` |

Example API calls:

```bash
BASE="https://lux-core-sepia.vercel.app"

curl "$BASE/api/health"

curl "$BASE/api/opportunities"

curl -X POST "$BASE/api/deals" \
  -H "Content-Type: application/json" \
  -d '{"title": "123 Main St", "status": "lead", "asset_address": "123 Main St Tampa FL"}'

curl -X POST "$BASE/api/outreach" \
  -H "Content-Type: application/json" \
  -d '{"outreach_type": "call", "status": "attempted", "notes": "Left voicemail"}'
```

### Additional Live Endpoints (Intelligence, Graph, Ops, Lead Engine, Outreach)

The table above predates the INTEL/GRAPH/OPS/Lead-Engine/Outreach work and is
kept for historical accuracy. The current live surface also includes:

| Area | Endpoints | Purpose |
|---|---|---|
| Graph (GRAPH-001) | `GET /api/graph/summary`, `GET /api/graph/linked-assets`, `GET /api/graph/assets/[asset_id]`, `GET /api/graph/assets/[asset_id]/timeline`, `GET /api/graph/transactions/[transaction_id]` | Read-only computed graph queries over canonical tables — linked-asset counts, per-asset detail, property timelines, per-transaction graph context. No separate graph database. |
| Intelligence (INTEL-001/002) | `GET /api/intel/pressure`, `GET /api/intel/buyers` | Read-only seller-pressure and buyer-demand projections with full signal lineage. |
| Matching (DATA-009/MATCH-001) | `GET /api/opportunities`, `GET /api/matches` (`?source=snapshot` for persisted candidates), `PATCH /api/matches` (outcome transitions only) | Versioned INTEL-001×INTEL-002 opportunity/match projections; legacy unversioned scoring excluded. |
| Operations (OPS-002) | `GET /api/ops/summary`, `GET /api/ops/sources`, `GET /api/ops/runs`, `GET /api/roadmap` | Live pipeline health, per-source freshness, run history, and the machine-readable roadmap the dashboard reads. |
| Lead Engine (LEADGEN-001) | `GET/POST /api/leads`, `GET/PATCH /api/leads/[lead_id]`, `POST /api/leads/[lead_id]/activities`, `GET/POST /api/trace_jobs`, `GET /api/trace_jobs/[job_id]`, `POST /api/phones/[phone_id]/suppress` | Property import, skip-trace job lifecycle, and compliance suppression. Runs on mock providers until Lead Engine go-live — see "Buyer Validation Strategy." |
| Compliance (LEADGEN-001/003) | `GET/POST /api/compliance/attest`, `POST /api/compliance/rescrub`, `GET /api/compliance/summary` | Lawful-use attestation gate, DNC/litigator re-scrub, compliance posture summary. Skip-trace jobs cannot enqueue until an attestation exists. |
| Outreach (OUTREACH-001) | `GET /api/outreach_drafts`, `POST /api/outreach_drafts`, `PATCH /api/outreach_drafts/[draft_id]` | Human-reviewed, compliance-gated outreach draft queue (pending → approved → sent / rejected). Nothing auto-sends. |
| Reporting / audit | `GET /api/exports`, `GET /api/reports`, `GET /api/audit`, `GET /api/duplicate_owners` | Compliance-gated lead exports, reporting views, append-only audit log, duplicate-owner detection. |

This table records purpose and file location, not full request/response
contracts — read the linked file under `api/` for exact parameters before
integrating against one. Fully documenting this surface to the same detail
level as the original five-endpoint table above is an open gap, not a
settled decision.

---

## Database

Provider: Supabase PostgreSQL  
Connection: `DATABASE_URL` in Vercel/GitHub Actions/local env — never hardcoded

### Tables

| Table | Model | Description |
|---|---|---|
| participants | ParticipantModel | Current participant/entity predecessor table |
| assets | AssetModel | Properties and other transactable assets |
| transactions | TransactionModel | Recorded deed transfers and sales; asset_id nullable for unresolved asset linkage |
| signals | SignalModel | Derived indicators of transaction likelihood |
| scores | ScoreModel | Computed opportunity scores |
| deals | DealModel | Active deal pipeline |
| contacts | ContactModel | Contact records linked to participants |
| outreach | OutreachModel | Outreach activity log |
| source_files | SourceFileModel | Legacy/source manifest table |
| pipeline_runs | PipelineRunModel | Durable ingestion and processing run record |
| raw_evidence | RawEvidenceModel | Immutable raw evidence metadata and content hash |
| source_records | SourceRecordModel | Source-faithful normalized upstream records |
| observations | ObservationModel | Sourced claims and measurements |
| events | EventModel | Generic sourced occurrences linked to records/assets |

### Additional Tables (Matching + Lead Engine)

| Table | Model | Description |
|---|---|---|
| matches | MatchModel | Persisted ranked buyer↔seller candidate matches with outcome workflow (candidate → reviewed → contacted → responded → converted / dead, enforced at the API layer, not the schema) |
| lead_properties | LeadPropertyModel | Imported property records feeding the Lead Engine |
| leads | LeadModel | Lead records derived from matched opportunities |
| lead_activities | LeadActivityModel | Activity log per lead |
| trace_jobs | TraceJobModel | Skip-trace job lifecycle; hard-blocked from enqueuing until a lawful-use attestation exists |
| trace_results | TraceResultModel | Skip-trace provider results |
| lead_phones | LeadPhoneModel | Phone numbers with callable/suppressed state |
| lead_emails | LeadEmailModel | Email addresses with callable/suppressed state |
| lead_suppressions | LeadSuppressionModel | Global DNC/litigator/manual suppression list |
| lead_exports | LeadExportModel | Compliance-gated export records |
| compliance_settings | ComplianceSettingsModel | Lawful-use attestation record |
| audit_log | AuditLogModel | Append-only audit trail |
| outreach_drafts | OutreachDraftModel | OUTREACH-001 human-reviewed draft queue |

Schema head as of this document: `d7f3a9b1c2e4` (leadgen + outreach_drafts).
Forbidden fields (SSN, DOB, financial data) are never persisted by the Lead
Engine, by design — see LEADGEN-005.

Quick DB inspection:

```python
from sqlalchemy import inspect
from core.db.session import engine

print(inspect(engine).get_table_names())
```

Session usage:

```python
from core.db.session import get_session
from core.db.models import ParticipantModel

session = get_session()
participants = session.query(ParticipantModel).limit(10).all()
session.close()
```

---

## Core Entity Schemas

Defined in `core/models/entities.py`. Adapters output these. Core consumes these.

Current predecessor schemas include:

```python
Participant(id, name, normalized_name, participant_type, source_adapter,
            source_county, first_seen, last_seen, confidence, metadata)

Asset(id, asset_type, source_adapter, address, location, valuation, metadata)

Transaction(id, asset_id, buyer_id, seller_id, transaction_type,
            transaction_date, price, source_adapter, source_file, metadata)

Signal(id, subject_id, subject_type, signal_type, value, weight,
       source_adapter, detected_at, explanation, metadata)
```

Architecture direction:
- Participant will evolve toward Entity.
- Roles move toward Participation.
- BuyerProfile and SellerCandidate are projections.

---

## Running Pipelines Locally

```bash
# Install deps
pip install -r requirements.txt

# Set env
cp .env.example .env
# Fill in DATABASE_URL and other needed vars

# Schema check
python scripts/check_schema.py

# Bounded Hillsborough ingestion
python scripts/run_ingestion.py \
  --adapter real_estate \
  --source hillsborough \
  --mode latest \
  --max-files 3 \
  --max-source-records 100 \
  --max-events 50 \
  --max-observations 200 \
  --max-transactions 20

# Legacy/local scripts where still supported
DRY_RUN=true python3 scripts/run_hillsborough.py
python3 scripts/run_hillsborough.py

DRY_RUN=true python3 scripts/run_scoring.py
python3 scripts/run_scoring.py

DRY_RUN=true python3 scripts/run_matching.py
python3 scripts/run_matching.py
```

Always dry run first where supported. `DRY_RUN=true` never writes to DB.

---

## Migrations

```bash
# Generate new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head

# Inspect current migration
alembic current
```

Rules:

- Every schema change goes through Alembic.
- Never edit production DB manually.
- Prefer generated migrations.
- Hand-edit migrations only for data migration logic or verified migration-order/schema defects.
- Always commit migration files.
- Production migrations run through the manual GitHub Actions migration workflow unless Jaia explicitly chooses otherwise.

---

## Logging

```python
from core.logger import get_logger

logger = get_logger(__name__)

logger.info("message")
logger.warning("message")
logger.error("message")
```

Prefer logger over print in application code.

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| POSTGRES_URL | Vercel / Supabase integration | Pooler connection string where available |
| DATABASE_URL | Vercel / GitHub Actions / local | Primary/fallback PostgreSQL connection string |
| CRON_SECRET | Vercel env vars | Protects cron endpoint |
| LUX_DEV_TOKEN | Vercel env vars | Required token for dev diagnostics; no default |
| LOG_LEVEL | Vercel env vars | INFO default; DEBUG for verbose |
| DRY_RUN | Script env var | true = no DB writes where supported |
| DAYS_BACK | Script env var | How many days back to pull county records |
| SUPABASE_URL | Vercel + GitHub Actions secrets | Supabase project URL for raw archive |
| SUPABASE_SERVICE_KEY | Vercel + GitHub Actions secrets | Supabase service role key, not anon key |
| SUPABASE_STORAGE_BUCKET | Vercel + GitHub Actions secrets/config | Defaults/target bucket if supported; expected bucket `lux-raw-files` |
| BATCHDATA_API_KEY | Vercel env vars (pending, LEADGEN-004) | Skip-trace provider key. Not yet provisioned — providers fall back to safe mocks without it |
| DNC_API_KEY | Vercel env vars (pending, LEADGEN-004) | DNC.com scrub provider key. Not yet provisioned — the DNC.com adapter refuses to instantiate without it (fail-safe) |
| DNC_SAN | Vercel env vars (pending, LEADGEN-004) | DNC.com Subscriber Account Number, required alongside DNC_API_KEY |

Never print or commit secrets.

---

## Infrastructure

| Service | Provider | Owner |
|---|---|---|
| Hosting | Vercel | Fox |
| Database | Supabase PostgreSQL | Fox / Kyle |
| Object Storage | Supabase Storage | Fox |
| Repo | GitHub — fsassaman-commits/lux-core | Fox |
| Notion Roadmap | Notion | Jaia |
| Domain | TBD | TBD |

---

## Smoke Test

Claude cannot reliably reach Vercel domains directly. Jaia runs smoke tests manually.

Standard smoke test after every merge:

```bash
BASE="https://lux-core-sepia.vercel.app"

curl -s "$BASE/api/health"
curl -s "$BASE/api/deals"
curl -s "$BASE/api/opportunities"
curl -s "$BASE/api/matches"
curl -s "$BASE/api/dev/status?token=$LUX_DEV_TOKEN" | python3 -m json.tool
```

Expected basics:
- `/` returns 200
- `/api/health` returns 200
- `/api/opportunities` returns 200
- `/api/matches` returns 200
- invalid dev token returns 401
- valid dev token returns diagnostic payload

---

## Dev Diagnostics

```text
GET /api/dev/status?token=[LUX_DEV_TOKEN]
```

Returns:
- DB connection status
- Row counts for operational tables
- Last processed file + timestamp
- Last score run timestamp
- data_ready flag
- Top scored opportunity when available

Rules:
- `LUX_DEV_TOKEN` is required.
- No fallback token.
- Missing/wrong token must not expose diagnostics.

---

## Adapter Boundary — Never Violate This

```text
adapters/ → transforms source data → outputs Core schemas
core/     → consumes Core schemas → never sees raw adapter data
```

If a function imports from `adapters/` and lives in `core/` → WRONG.  
If a function imports from `core/models/` and lives in `adapters/` → CORRECT.

Real-estate-specific parcel/address rules live adapter-side where practical. Canonical truth stays Core.

---

## Handoff Standard

All coding-agent handoffs follow the template in `docs/HANDOFF.md`.

Key rules:
- Cite file + line number for every root cause.
- Verification section must have exact commands and expected output.
- `dry_run` must be verified explicitly when relevant.
- Review packet ends with explicit `proceed?`.
- Jaia merges — never self-merge.
- One consolidated review packet at the end of each patch.
- Confirm deployed commit matches expected before starting production-impacting work.
- Every PR must reconcile this AGENTS.md Ticket Registry.

---

## Notes From Reconciliation

This AGENTS.md intentionally keeps the useful generic governance from the second uploaded agent proposal:

- AGENTS.md update policy
- Merge rules
- Living open-ticket list requirement
- Review packet requirements

It intentionally excludes project-specific ASA / trading content from that proposal, including:
- Strategy serialization policy
- Robinhood re-auth
- Options-strategy tickets
- ASA/Railway-specific deployment notes

Those belong to the ASA project, not LUX.
