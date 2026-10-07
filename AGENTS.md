# AGENTS.md — how to work in this repository

This repo is **Erudite**: a grounded, citation-gated admissions + financial-aid advisor for
high-need Bangladeshi applicants to US universities. Built by MONARQ Labs.

## Start here (read order)
1. `ERUDITE_REPORT.md` — the consolidated technical report. Read this first; it is the map.
2. `01_framework/BANGLADESHI_APPLICANT_INTELLIGENCE_SYSTEM.txt` — the reasoning IP (rules R1–R7). Read in full.
3. `01_framework/data_architecture.yaml` — schema v3 (11 layers). **One optional lens, not the contract** (see Knowledge-base philosophy).
4. `02_school_reports/` — the 6 finished school dossiers (the only proprietary asset).
5. `04_plans/SONNET_ERUDITE_PLAN.md` — architecture plan. **Recommendations only; decisions are NOT locked.**
6. `05_code/erudite-v2/` — legacy backend (deployed but defective; see defects below).

## Hard facts
- **6 school reports, not 8**: MIT, Yale, Amherst, Vanderbilt, Mount Holyoke, NYU. No others exist.
- The 6 dossiers are **intentionally narrative prose** (only MIT has a `.profile.json`). Do not force them into rigid JSON — see Knowledge-base philosophy.
- The legacy backend demoed against the **clinical-safety** corpus, never admissions. The engine has
  known defects (no citation gate; retrieval returned metadata not text; dev-token auth; hardcoded IDs).
- Source archives are NOT in this repo; provenance for every file is in `PROVENANCE.tsv`.

## Recommended prior art / do not reinvent
- Data: `collegedata.fyi` (`bolewood/collegedata-fyi`, MIT) — CDS archive + per-field provenance;
  H6 intl-aid fields exist at the raw CDS layer. **Validate every value against `archive_url`** (known mis-extractions).
- Formal models + libraries: see `ERUDITE_REPORT.md` §5–§6 (logistic admit-prob, R5 expected-utility,
  MCDA via `pymcdm`, portfolio via OR-Tools, bge-m3/multilingual-e5/bge-reranker-v2-m3).
- The genuine invention area is the **Bangladeshi-student × university-trait mapping** — no OSS equivalent exists.

## Objective (the wishlist)
An AI agent that uses this knowledge base to give **powerful advice tailored to distinct Bangladeshi
student backgrounds** — across financial aid, visa, essay, plan, school selection, and interview prep —
where advice changes materially with the student's real situation (income/need, SSC/HSC vs A-levels,
major, scores, risk tolerance, family constraints).

## Knowledge-base philosophy (deliberate)
The dossiers are **intentionally narrative, not rigid JSON.** Strict JSON schemas were **dispensed with
because they flatten away the complexity** (nuance, conditions, caveats, R1–R7 reasoning) that makes the
advice good. `01_framework/data_architecture.yaml` is one optional lens, not the epistemic source.
Retrieve and reason over full prose; keep provenance and the citation gate. Any JSON is transport/output only.

## Rules for agents
- **Read-only on facts unless told to build.** Do not invent numbers; every claim needs a source URL + access date.
- Do not commit secrets. Reference environment variables only.
- Any advisory output must pass a **citation gate**: every claim must trace to a provenance record
  (`school_id` + `field_path`); otherwise block. Separate "refusal" from `faithfulness=1.0`.
- Keep licenses intact: adopt MIT/Apache-2.0/CC-BY; `CollegeOS` is Elastic-2.0 (study, don't copy).
