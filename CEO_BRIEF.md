# CEO Brief — LUX

*Last updated: 2026-07-25. Derived from AGENTS.md; regenerate whenever the Ticket Registry's Current Project Status changes.*

## What LUX is

LUX (Linked Unified Exchange) is a market-intelligence platform: it turns
scattered public records into canonical evidence, scores that evidence into
seller and buyer intelligence, ranks buyer↔seller matches, and routes the
best matches into a human-reviewed outreach queue. Residential real estate
(Tampa Bay, FL) is the first validation vertical — **this is not a real
estate app**; real estate proves out a market-agnostic intelligence engine.

## Where we are

The infrastructure phase is complete and has been operationally proven in
production: canonical data model, public-record ingestion, immutable
provenance, deterministic Transaction→Asset linking, and read-only graph
queries are all live. Seller-pressure and buyer-demand scoring (INTEL-001,
INTEL-002) are live and generating ranked, persisted matches (MATCH-001).
Human-reviewed outreach drafting (OUTREACH-001) shipped 2026-07-22.

**The current bottleneck is not intelligence — it's real, compliant
contacts.** Outreach is currently running against mock contact providers.
The path to real contacts is the Lead Engine go-live sequence
(LEADGEN-002 through LEADGEN-005), which is the direct blocker on this
company's one named milestone.

## The one milestone that matters: MVP-001 — First Dollar

Close one real wholesale transaction entirely sourced and matched through
LUX. A qualified lead and an approved outreach packet are steps on this
path, not the milestone itself. Every ticket should be evaluated against:
does this move LUX closer to that first real transaction?

## What's next, in order

1. **LEADGEN-002** — run the production database migration (unblocks
   everything else in this list).
2. **LEADGEN-003** — record the lawful-use attestation (skip-trace is
   hard-blocked without it).
3. **LEADGEN-004** — provision paid skip-trace/DNC-scrub provider accounts
   and keys.
4. **LEADGEN-005** — activate live providers, run the first bounded live
   skip-trace batch.
5. **OUTREACH-003** — feed real, compliant contacts into the existing
   OUTREACH-001 approval queue.
6. **MVP-001** — the first actual closed transaction.

## Geographic expansion (SPRINT-001 findings, 2026-07-24)

Research validated the existing plan rather than changing it, and added
execution detail:
- **Florida**: keep expanding. Evidence-ranked next counties: Pinellas
  (already in progress), Orange, Pasco, Duval.
- **Phoenix (Maricopa County, AZ)**: keep as the first out-of-state
  architecture-validation target — evidence fully supports the original
  rationale.
- **Troy (Rensselaer County, NY)**: keep, but with an honest risk note —
  population has been declining since 2020 and it has the weakest data
  access (permits, probate) of any market researched. Frame it explicitly
  as a non-revenue architecture-validation bet, which is how the project
  already treats it.
- Deprioritized: Austin, TX and Salt Lake County, UT — both are
  non-disclosure states, which breaks LUX's evidence-based model
  regardless of their macro appeal.

## What needs a decision from you right now

See `OPEN_DECISIONS.yaml` for the full, structured list. Highlights:
- Three new proposals from SPRINT-001's research (a cheap new vacancy
  signal, a heir/inherited-property signal, and a proposed `core/` schema
  change for multi-jurisdiction support) are all sitting unscoped, awaiting
  your call.
- **This mirror repository itself (OPS-SYNC-001)**: the initial reset of
  `jaiaFoster/lux-core` (an abandoned early project scaffold) needs your
  explicit go-ahead before it happens.

## Standing rules that don't change

Jaia merges every PR to the canonical repository. No agent — human-directed
AI or otherwise — self-merges, ever. This mirror repository
(`jaiaFoster/lux-core`) is a read-only, automatically generated snapshot for
AI/executive inspection; it is not a place for direct development, and
nothing here is a substitute for reading `AGENTS.md` in the canonical
repository when precision matters.
