# Research Bank — 6 School Reports

Forensic aid-intelligence dossiers produced against
`../01_framework/MASTER_RESEARCH_PROMPT.md` + `BANGLADESHI APPLICANT INTELLIGENCE SYSTEM.txt`.
All reports retrieved their sources **2026-05-21/22** (Asia/Dhaka), so all are
subject to R7 staleness review.

| File | School | Policy type (as stated) | Source date | Notes |
|---|---|---|---|---|
| `mit.md` | MIT | **Type A** (need-blind intl, full need, no-loan) | 2026-05-22 | unwrapped from `_raw_mit_wrapped.json`; has `mit.profile.json` |
| `yale.md` | Yale | **Type A** | 2026-05-22 | |
| `amherst.md` | Amherst College | **Type A** | 2026-05-22 | |
| `vanderbilt.md` | Vanderbilt | **Type C** (need-aware intl, full-need if admitted) | 2026-05-22 | |
| `mount_holyoke.md` | Mount Holyoke | **Type E** (meets need for admitted intl; not verified need-blind) | 2026-05-21 | |
| `nyu.md` | NYU (New York campus) | need-aware intl; "NYU Promise" = 100% demonstrated need, NY-campus first-years | 2026-05-22 | CDS Part H missing for 2024-25 → H6 stats from 2022-23 |

`mit.profile.json` — structured MIT fields (21 keys: `school_id`, `policy_type`,
`cds`, `coa`, `nationality_aid_profile`, `reachability`, `admissions`,
`bangladesh_profile`, `verdicts`, `data_quality`, …). Useful as the first
worked example of the target schema shape.

`_raw_mit_wrapped.json` — the original archive file; MIT's report shipped as a
JSON object `{"report": "...", "profile": {...}}` rather than markdown.

## Gaps

- **Expected "8" reports; only 6 exist in the archives.**
- These are analyst-readable prose, not schema-valid JSON → require conversion
  to `01_framework/data_architecture.yaml` (schema v3) before ingestion.
- No machine-readable provenance records per field yet (required by the citation gate).
