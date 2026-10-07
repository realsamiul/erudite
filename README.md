# ERUDITE — Bangladesh Applicant Intelligence System

Organization of all current Erudite content, extracted and de-duplicated from the
MONARQ archives. Built 2026-09-28.

`status=research-bank-complete · code=legacy-deployed · product=spec-only · plan=sonnet-unlocked`

---

## Provenance (source archives)

| Ref | Archive | Role |
|---|---|---|
| A | `docrag-v2.zip` | canonical V2 code (`docrag-v2/erudite-v2/`) |
| B | `TermiusGemini-main 2.zip` | Erudite framework + 6 reports + product specs |
| C | `DocRag all files.zip` | Erudite Plan B (schema v3, GEMINI.md), positioning copy |
| D | `EruditeFinal.md` | Sonnet build plan (Erudite-first recommendation) |

Per-file source paths + sha256 hashes: see `PROVENANCE.tsv`.

---

## Tree

```
erudite/
├── README.md                       ← this file
├── AGENTS.md                       ← orientation for agents working in the repo
├── ERUDITE_REPORT.md               ← consolidated technical report (entry point)
├── ARENA_AGENT_PROMPT.md           ← brief for an external frontier agent (arena.ai)
├── PROVENANCE.tsv                  ← dest → source → sha256
├── 01_framework/                   ← the reasoning IP (R1–R7)
│   ├── BANGLADESHI_APPLICANT_INTELLIGENCE_SYSTEM.txt
│   ├── MASTER_RESEARCH_PROMPT.md
│   ├── data_architecture.yaml      ← schema v3, 11 layers
│   ├── GEMINI.md                   ← agent context / research agent spec
│   └── gemini_upgrade_notes.txt
├── 02_school_reports/              ← THE RESEARCH BANK (6 done)
│   ├── README.md
│   ├── mit.md + mit.profile.json
│   ├── nyu.md
│   ├── yale.md
│   ├── amherst.md
│   ├── mount_holyoke.md
│   ├── vanderbilt.md
│   └── _raw_mit_wrapped.json       ← MIT source was JSON-wrapped
├── 03_product/                     ← specs, handoff, positioning
│   ├── erudite_v2_design_spec.md
│   ├── erudite_v2_handoff.txt
│   ├── erudite_v2_positioning.md
│   └── landing_copy_stitchmark.md
├── 04_plans/
│   └── SONNET_ERUDITE_PLAN.md      ← EruditeFinal.md (3 docs: strategy, build-out, build instructions)
├── 05_code/
│   └── erudite-v2/                 ← legacy deployed backend (points at WRONG corpus)
└── 06_ops_history/
    ├── gcp_startup_grant_proposal.txt          ← Erudite + DocRAG funding pitch (Channel B = Erudite)
    └── technical_journey_and_platform_audit.txt ← deployment coords + bug resolutions (§B = Erudite V2)
```

## Completeness audit (2026-09-28)

Swept **all archives** in `/home/ubuntu/MONARQ` including nested ones:

| Archive | Status |
|---|---|
| `docrag-v2.zip` (A) | fully extracted |
| `TermiusGemini-main 2.zip` (B) | fully extracted |
| `DocRag all files.zip` (C) | fully extracted |
| ↳ nested `docrag-v2.zip`, `docrag-v2-archive-main.zip`, `erudite-v2.zip`, `Erudite Plan B/files.zip`, `docrag_and_erudite_v2_backup.tar.gz` | all extracted + searched |

Search performed: (1) every path matching `erudite`/`applicant`/`admission`/`dossier`;
(2) file **contents** matching `erudite` (24 text files); (3) school names + `applicant
intelligence` + `need-blind` + `common data set` to catch unlabelled content.
**Result: no Erudite content left behind.** Cross-cutting hits added to `06_ops_history/`.
Only false positives: `Uploads/documents/GITHUB_REPOS_DEEP_DEPLOYMENT_GUIDE.md`
(`FunctionName`) and `floodanddisease/.../script_1.py` ("Hospital admissions").

Cross-references (not copied, DocRAG-primary but mention Erudite):
`C/…# Erudite V2…` is copied as `03_product/erudite_v2_positioning.md`;
`C/DocRAG-Legal · Leveling…md` mentions Erudite only as a backup filename.

---

## Status / known defects (from DOCRAG_ERUDITE_REPORT.md)

- `!` **Research bank = 6 school reports, not 8.** The archives contain exactly
  Vanderbilt, NYU, Mount Holyoke, Amherst, Yale, MIT. No 7th/8th report exists in
  any archive. If two more are expected, they are not in these zips.
- `!` **Admissions corpus was never ingested.** The deployed `erudite-backend-719705716921`
  demoed against the *clinical-safety* store (`I14`).
- `!` **The `erudite-v2/` code inherits the shared engine defects** (`I1` wrong corpus,
  `I2` no citation gate, `I3` retrieval returns metadata not text). See report §4.
- `!` Legacy IDs/paths are hardcoded (`project-a1f62154…`, `/home/realsamkarim/…`).
- `~` `05_code/` excludes `seed_docs/*.pdf` (known-wrong clinical/SA corpus) and
  `__pycache__`/`.pyc`.

---

## Objective (the wishlist)

An AI agent that uses this knowledge base to deliver **genuinely powerful advice tailored to
distinct Bangladeshi student backgrounds** — financial aid, visa, essay, plan, school selection,
and interview prep — where the advice changes materially with the student's real situation
(income/need, SSC/HSC vs A-levels, major, scores, risk tolerance, family constraints).

`!` **Knowledge-base philosophy (deliberate):** the dossiers are intentionally **narrative prose,
not rigid JSON**. Strict JSON schemas were **dispensed with because they flatten away the
complexity** (nuance, conditions, caveats, R1–R7 reasoning) that makes the advice good.
`01_framework/data_architecture.yaml` is *one optional lens*, not the data contract. Retrieval and
reasoning operate over full prose, while provenance and the citation gate still hold. Any JSON is
transport/output only, never the epistemic source.

## What each layer is for

- **01_framework** — R1 claim-decomposition, R2 five-tier policy topology (A–E),
  R3 CDS-H6 forensic chain, R4 nationality-decomposition proxy, R5
  reachability-funding inversion (expected-utility), R6 clutch factors, R7 staleness.
- **02_school_reports** — forensic dossiers, one per school, as **rich narrative** (the only
  proprietary asset; keep the prose, do not collapse it to JSON).
- **03_product** — V2 design spec, production handoff, landing/positioning copy.
- **04_plans** — Sonnet's Erudite-first plan (recommendations, none locked).
- **05_code** — the deployed-but-defective V2 backend to be refactored.

## Next (unresolved)

1. Ingest the 6 dossiers as narrative into an OSS retrieval store (keep prose intact).
2. Human QC on the facts that drive money math (`admit_rate`, `avg_intl_aid_award`, `need_blind_intl`).
3. Deterministic R5/R6 computation layer + **hard citation gate** over the narrative KB.
4. Stand up retrieval (OSS bge-m3/pgvector on Modal, per plan) — no GCP Discovery Engine.
