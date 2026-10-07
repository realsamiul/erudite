# MONARQ · ERUDITE — Consolidated Technical Report
`mode=handoff` · `audience=LLM (Sonnet)` · `scope=Erudite only` · `status=research-complete; plans-recommended-not-locked` · `date=2026-09-28`

Erudite = grounded, citation-gated admissions + financial-aid advisor for high-need
Bangladeshi applicants to US universities. Shared engine with DocRAG-Legal; this report
covers Erudite only. All paths below are under `/home/ubuntu/MONARQ/erudite/` unless absolute.

---

## §0 · ARTIFACT INVENTORY (what exists right now)

| Path | What it is |
|---|---|
| `01_framework/BANGLADESHI_APPLICANT_INTELLIGENCE_SYSTEM.txt` | The reasoning IP: rules R1–R7 (42 KB) |
| `01_framework/MASTER_RESEARCH_PROMPT.md` | Per-school research prompt/template |
| `01_framework/data_architecture.yaml` | Schema v3, 11 layers (20 KB) |
| `01_framework/GEMINI.md` | Research-agent context (40 KB) — search templates, anti-hallucination checklist |
| `01_framework/gemini_upgrade_notes.txt` | Notes on how GEMINI.md/schema were derived |
| `02_school_reports/{mit,nyu,yale,amherst,mount_holyoke,vanderbilt}.md` | 6 forensic school dossiers |
| `02_school_reports/mit.profile.json` | Structured MIT fields (21 keys) — only machine-readable dossier |
| `03_product/erudite_v2_design_spec.md` | V2 product/tech spec |
| `03_product/erudite_v2_handoff.txt` | Production handoff (live coords, structured contract) |
| `03_product/erudite_v2_positioning.md` | Landing copy / page-flow / "anti-chatbot" framing |
| `03_product/landing_copy_stitchmark.md` | Marketing copy (DocRAG+Erudite shared) |
| `04_plans/SONNET_ERUDITE_PLAN.md` | This session's Sonnet plan (3 docs: strategy, build-out, build instructions) |
| `05_code/erudite-v2/` | Legacy deployed backend (18 files) |
| `06_ops_history/gcp_startup_grant_proposal.txt` | Funding pitch; "Channel B" = Erudite |
| `06_ops_history/technical_journey_and_platform_audit.txt` | Ops history, deployment URLs, bug resolutions |
| `PROVENANCE.tsv` | dest→source-archive→sha256 for every copy |

Source archives: A=`docrag-v2.zip`, B=`TermiusGemini-main 2.zip`, C=`DocRag all files.zip`
(+ 5 nested archives, all swept — see `README.md` completeness audit).

`!` **Research bank = 6 schools, not 8.** No 7th/8th report exists in any archive.
`!` Canonical code = `05_code/erudite-v2/` (clone of DocRAG V2). `02_school_reports/` is the only proprietary asset.

---

## §1 · HOW IT WAS MADE (reconstructed)

1. **Framework authored** — `BANGLADESHI APPLICANT INTELLIGENCE SYSTEM` defines:
   - R1 claim-decomposition; R2 five-tier policy topology (A–E); R3 CDS-H6 forensic chain;
     R4 nationality-decomposition proxy; R5 reachability-funding inversion (expected-utility);
     R6 clutch factors; R7 staleness rules.
2. **Research pipeline** — `MASTER_RESEARCH_PROMPT.md` + `GEMINI.md` → manual deep-research
   session per school → prose markdown report. No automation, no schema validation at capture time.
3. **6 dossiers produced** — sources retrieved **2026-05-21/22 (Asia/Dhaka)**. Sizes 26–46 KB.
4. **Schema v3** — `data_architecture.yaml` (11 layers) designed as target structure, adds
   curriculum gate, nationality decomposition, reachability, visa flags, essay-advisory seeds,
   staging/confirmed patterns, migration path. **Never enforced.**
5. **Product V2** — `erudite-v2/` backend cloned from DocRAG V2 engine: FastAPI + Discovery
   Engine retrieval + Gemini synthesis (structured JSON: greeting/quick_stats/charts/audit_feedback)
   + Modal persistence. Deployed to Cloud Run `erudite-backend-719705716921.us-central1.run.app`.
6. **Positioning** — dossier-not-chatbot framing; "older-sibling" counselor voice.

**Provenance/quotes:** 42863 B framework; reports cite source URLs inline; all reports stamp retrieval date.

---

## §2 · WHAT IT ACHIEVED

`+` Genuine, differentiated domain IP (not generic "legal/admissions chatbot"):
taxonomy A–E, CDS-H6 forensic method, R5 expected-utility (a funded reach can outrank an
unfunded target), R6 non-obvious swing factors, R7 staleness discipline.
`+` 6 real forensic dossiers with per-school policy classification:

| School | Policy type | Notable |
|---|---|---|
| MIT | A (need-blind intl, full need, no-loan) | intl admit ~1.96%, Class of 2029 |
| Yale | A | |
| Amherst | A | |
| Vanderbilt | C (need-aware intl, full-need if admitted) | |
| Mount Holyoke | E (meets need for admitted intl; not verified need-blind) | |
| NYU | need-aware intl; "NYU Promise" 100% need, NY-campus first-years | CDS Part H missing 2024-25 → H6 from 2022-23 |

`+` Deployed, working backend (structured JSON, adversarial judge hook, provenance chain).
`-` **Corpus never ingested.** The live demo ran against the **clinical-safety** store (`I14`).
`-` Reports are analyst prose, not schema-valid JSON → cannot be ingested or citation-gated as-is.
`-` Only MIT has a structured `.profile.json`; the other 5 need conversion.

---

## §3 · DEFECTS CARRIED OVER (from `DOCRAG_ERUDITE_REPORT.md` §4)

| # | Issue | Impact on Erudite |
|---|---|---|
| I2 | No citation-integrity gate; fabricated § presented as grounded | critical — core trust claim |
| I3 | Retrieval returned GCS metadata not text ("Insufficient context") | critical |
| I7 | Sync `modal.Function.remote()` on async loop | blocking |
| I8 | Gemini 1.5 404 Model Garden lock → `gemini-3.5-flash` @ `global` | env |
| I9 | Auth = `dev-token` bypass; Firebase never wired | high |
| I10 | Duplicate codebases; `.pyc`/`__MACOSX` committed | medium |
| I11 | Hardcoded `project-a1f62154…`, `/home/realsamkarim/…` | medium |
| I13 | `faithfulness=1.0` on "Insufficient context" = misleading PASS | medium |
| I14 | Erudite points at clinical corpus; admissions never ingested | high |
| I16 | Static HTML frontend, hardcoded values | medium |
| I17 | Assumed $1,000 App-Builder credit absent on current project | high |

`!` Even fixed, **I1 (wrong corpus) is Erudite-specific via I14** — the fix is data-loading
(§5.1 gives the sources), not engineering.

---

## §4 · PLANS ON THE TABLE (Sonnet `EruditeFinal.md`; NOT locked)

**Strategy:** ship Erudite **first** (content exists; no licensing/OCR/scraping); move retrieval
**off GCP Discovery Engine** to OSS `bge-m3`+`pgvector` on Modal; synthesis on AI Studio Gemini /
DashScope Qwen free tier; DeepSeek for executor + judge; GCP untouched (preserve $80 for DocRAG).
**Budget use:** Modal $60 = compute; DeepSeek = per-query volume; DashScope = batch ingestion.

**Architecture (3 tracks):**

1. **Schema-first (the real risk).** Convert schema v3 → strict **versioned JSON Schema**; three
   field classes: *structured/numeric* → Postgres relational (deterministic lookups, R5/R6, charts);
   *narrative/analytical* → chunked + embedded (RAG "why"); *provenance/meta* → 1:1 per claim
   (citation gate, R7). Every fact carries provenance. **No exceptions.**
2. **Ingestion.** Convert 6 reports → dossiers once, via DashScope 1M-context single-shot per school
   (`qwen3.8-max`, `response_format=json_object`); Pydantic raises on invalid. Mandatory human QC on
   numeric fields (`admit_rate`, `avg_intl_aid_award`, `need_blind_intl`) — LLM number extraction is
   where silent errors hide.
3. **Query engine (tiered).**
   - Tier 0: ≤4 schools → plain context-stuffing, **no vector DB** (corpus ~60–150K tokens).
   - Tier 1: >4 → DashScope 1M-context shortlist → then execute. Add embeddings only past ~40–50 schools.
   - **Deterministic `compute.py`** for R5 (`admit_probability × funding_reliability → expected_utility → bucket`)
     and R6. Heuristics **commented with source assumptions** (audit trail).
   - **Citation gate** (`gate.py`): executor JSON must include a `citations[]` array
     (`school_id`+`field_path`); any claim not in the provenance set → `BLOCKED_UNVERIFIED_CLAIM`.
     **Hard block, not a score.**
   - **Adversarial judge** runs *after* the gate (not instead): critiques R5 correctness, staleness, confidence.
4. **Frontend.** Next.js on Vercel: profile intake **form** (not chat); dossier view; comparison view;
   always-visible `AuditPanel` + `CitationDrawer`; free-text box secondary, same pipeline.
5. **Deploy.** FastAPI on Modal (`modal.asgi_app`), data on Modal Volume, `modal deploy`. Build order:
   schema → ingest → QC → compute+tests → gate/judge (Tier 0) → deploy+curl → frontend.

`!` All of the above is **recommendation**; §8 decisions remain open.

---

## §5 · RESEARCH INSIGHTS (this session — the "leg up" / adopt list)

Dispatched 5 read-only lanes (DeepSeek-v4.1-flash; papers/HF on Gemini keys; 1 lane 503-failed → retried).
No invented solution should be built before checking these.

### 5.1 Data layer — **the single biggest leg-up**

`+` **collegedata.fyi** (`github.com/bolewood/collegedata-fyi`, **MIT** code, live 2026-09) — archives
school-published **Common Data Set** documents and extracts them into the CDS canonical **1,105-field**
schema, with **per-field provenance** (`archive_url`, `ipeds_id`, `canonical_year`, `value_status`).
Stats: 735 schools, 4,071 CDS docs, 333,131 `cds_fields` rows. **Self-verified live:** friendly API
returns provenance-tagged facts (e.g. `amherst` IPEDS finance row with `source_table=F2324_F2`).
Endpoints: `/api/schools/{id}/facts`, `/api/schools/{id}/sources`, `/api/compare`, `/api/fields`,
`/api/mcp` (no-auth), snapshots `/snapshots/latest/school_facts.jsonl`.
`+` **CDS Section H6 international aid exists at the raw CDS layer**: H.604 count / H.605 average award /
H.606 total (~164–250 docs), plus C.125/C.126/C.127 intl applied/admitted/enrolled (~520–536 rows).
`!` **Nuance (verified):** the *friendly* API **withholds low-confidence admissions fields**
(MIT `applied/admitted/enrolled/acceptance_rate` all returned `null`, `flag=low_confidence_extract`)
and `/api/compare` does **not** expose H.604/H.605/C.126 (empty columns). H6 is only reachable via the
raw CDS layer. `!` Known extraction errors: Harvard 2024-25 `C.126`=16,760 (= total admitted);
Amherst `C.126`=5,664 (implausible); Harvard `H.605`=66,826,244 (= H.606 total). **Reconcile every
value against `archive_url` before trusting.** This is a **source+validation** asset, not a turnkey corpus.

`+` **College Scorecard API** (public domain; free data.gov key; 1,000 req/IP/hr):
`api.data.gov/ed/collegescorecard/v1/schools`; outcomes/cost/net-price; intl only
`non_resident_alien` enrollment share (0.1459 at Harvard). **No intl admit rate, no intl aid.**
`+` **IPEDS / NCES** (public domain) — identity/crosswalk + federal baseline. `paulgp/ipeds-database`
(**MIT**, DuckDB, ~1 GB, 27M rows, 1997–2024, 23 tables) = one-command ingest.
`+` **IIE Open Doors** — intl enrollment/volume by origin (free XLSX; "all rights reserved"; attribute, don't redistribute).
`~` **CDS canonical schema** @ commondataset.org (1,105 fields; no ToS; schools own their filings).
`-` Kaggle `theriley106/college-common-data-sets` (CC0, 173 schools) — **stale (2018)**.
`!` **No free source gives a verified intl admit rate** → compute from C.125/126/127 (ourselves, validated).
`!` **Need-blind vs need-aware (intl) is NOT a machine field** anywhere → prose curation / LLM-rule layer.
`!` **Curriculum requirements (A-levels vs SSC/HSC) absent from all sources** → per-school curation (R4 gate).

### 5.2 OSS prior art (no end-to-end product exists; adopt patterns)

| Repo | License | Stars/activity | Adopt |
|---|---|---|---|
| `emili-kosik/admission-skills` | MIT | tiny, 2026-07 | Counselor **skill taxonomy** (`college-list`, `research`, `financial-aid`, `scholarships`, `international`, `testing`, `essay-coach`, `decision-day`) + `sources.json`/`last_verified` citation discipline; F-1 support; blocks essay drafting |
| `ASUCICREPO/Admissions-AI-Agent` (ASU) | MIT | 5★, 2026-02 | Agent **tool decomposition**: `retrieve_tool`, `advisor_handoff_tool`, `translate_tool`, `session_utils`; Next.js chat UX |
| `virtualryder/EDU_financial_aid_agent` | Apache-2.0 | 0★, 2026-09 | **Policy-based grounding gate** (Cedar, deny-by-default) + WORM audit; "verify+estimate+draft, not adjudicate" scoping |
| `ultramagnus23/CollegeOS` | **Elastic License 2.0 — NOT reusable** | 1★ | **Blueprint only:** retrieval→ranking→R/T/S/Wildcard diversification→explainability; logistic chancing `P=f(SAT vs median, GPA, logit(accept rate))`; `probability_source` stamped. Code reuse blocked. |
| `bienwithcode/AdmissionAgent` | MIT | 6★, Go | Hybrid **vector+graph** retrieval (prereq/eligibility relations) |
| `21spl/uni-admission-ai` | MIT | 5★ | Multi-role: validator, shortlister, career counsellor, **loan-eligibility**, admissions officer |
| `sdivyanshu90/mcp-college-counselor` | **no license** | 1★ | MCP tool schema + **bounded** tool-calling loop |
| `pipeworx-io/mcp-college-scorecard` | MIT | 2026-09 | Scorecard-as-MCP grounding tool |

`!` Verdict: **no maintained, license-clean, end-to-end intl admissions+aid advisor exists** (all ≤6★, solo,
or unlicensed). Adopt patterns + `collegedata.fyi` data; the tailoring core remains our invention.

### 5.3 Academic prior art (formalize the tailoring core)

`=` Admission probability: logistic/MLE — `arXiv:2202.04987`. `P(admit)=σ(β₀+Σβᵢxᵢ)`; evaluate AUC/PR.
`=` Expected-utility college choice — `DOI:10.1007/s10640-019-00320-7`. Utility = f(expected aid, fit, outcomes).
`=` Hybrid university recommender (content + collaborative) — `arXiv:2307.06782`; Top-N, diversity metrics.
`=` MCDA (AHP for weights, TOPSIS for ranking) in school choice — `DOI:10.3390/su13073998`.
`=` Fairness in algorithmic admissions — `arXiv:2009.05609` (demographic parity, equal opportunity; mitigation).
`=` Reach/Target/Safety as supervised classification — `arXiv:2106.15830`.
`=` College-application **portfolio optimization** (MIP) — `DOI:10.1287/ited.2017.0189`. Maximize expected utility s.t. app budget.
`!` Some 2025–26 "LLM advising eval" IDs (`arXiv:2402.04944`) marked **low-confidence** — verify before relying.

### 5.4 Models / eval / HF (grounded bilingual retrieval)

`=` Embeddings: **`BAAI/bge-m3`** (MIT; ~568M; hybrid dense+sparse+ColBERT; 100+ langs, MIRACL incl. `bn`),
**`intfloat/multilingual-e5-large`** (MIT; 560M; `bn` explicit in tags).
`=` Reranker: **`BAAI/bge-reranker-v2-m3`** (Apache-2.0; 568M; multilingual; `bn` inferred via XLM-R).
Permissive alts: `Alibaba-NLP/gte-multilingual-reranker-base` (Apache-2.0), `mixedbread-ai/mxbai-rerank-large-v2`.
`=` Eval: **RAGAS** (Apache-2.0) — but non-LLM metrics are **English-biased** (open multilingual issues);
**DeepEval** (Apache-2.0), **TruLens** (MIT); **LRAGE** (MIT, legal), **LightEval** (MIT).
`=` Bengali benchmarks (all confirmed `bn`): `miracl/miracl`, `castorini/mr-tydi`, `google-research-datasets/tydiqa`,
`ai4bharat/IndicQA`, `CohereLabs/Global-MMLU`, `facebook/belebele`, `mrlbenchmarks/global-piqa-parallel`;
**MMTEB** (Apache-2.0, 250+ langs) + `mteb/indic_sts` (CC0).
`!` **No admissions/financial-aid QA dataset** (esp. Bangladeshi/intl) exists on HF → we author it.
`!` **No Bengali long-document benchmark** (MLDR excludes `bn`) → unbenchmarkable with public data.

### 5.5 Tailoring / optimization / RAG stack (assemble, don't invent)

`=` MCDA: **pymcdm** (MIT; TOPSIS/AHP), **scikit-criteria** (BSD-3), **pyDecision** (GNU). Explainable scoring.
`=` Optimization: **Google OR-Tools** (Apache-2.0; MIP portfolio), **cvxpy** (Apache-2.0), PuLP (EPL).
`=` Recommender: LightFM (MIT), RecBole (Apache-2.0), implicit (MIT).
`=` RAG frameworks: LlamaIndex (MIT), Haystack (Apache-2.0), txtai (Apache-2.0).
`=` Structured output: Pydantic (MIT), Instructor (MIT), outlines (Apache-2.0), guidance (MIT).
`!` No single library combines MCDA+optimization+RAG → **assemble**; no production example found.

---

## §6 · THE CREATIVE CORE — tailoring as a deterministic pipeline

Research says the proven decomposition is:

```
school dossier (structured facts + provenance)          applicant profile (goals/status)
        │                                                          │
        ▼                                                          ▼
feature vector per school ──► admission prob (logistic, calibrated) × funding reliability (R5)
        │                                                          │
        ▼                                                          ▼
expected_utility = P(admit) × E[funding]  ──►  MCDA ranking (AHP weights + TOPSIS)  [pymcdm]
        │                                                          │
        ▼                                                          ▼
portfolio optimization → reach/target/safety/wildcard sets  [OR-Tools MIP, constraints: app budget,
curriculum gate (R4), need-blind/aware, test policy]           │
                                                               ▼
                     LLM narrates the decision with citations[] → citation gate → adversarial judge
```

- **Adopt:** CollegeOS R/T/S architecture + `probability_source` discipline (study only; Elastic license);
  admission-prob logistic (`2202.04987`); MIP portfolio (`10.1287/ited.2017.0189`); AHP/TOPSIS (`10.3390/su13073998`);
  pymcdm + OR-Tools; `admission-skills` skill taxonomy; `EDU_financial_aid_agent` deny-by-default gate pattern.
- **Invent only:** the **Bangladeshi-student × university-trait mapping** (R4 nationality decomposition,
  curriculum gate, R5 funding inversion as *risk-adjusted* utility). This is the genuine differentiator and
  has no OSS equivalent.

---

## §7 · RISKS / UNKNOWNS

`!` collegedata.fyi per-value accuracy unreliable (self-flagged `low_confidence_extract`; verified mis-extractions) → validate vs `archive_url`.
`!` H6 coverage partial (~164–250 of ~4,000 docs); many schools blank.
`!` No structured source for intl admit rate, need-blind/aware policy, or curriculum gate → curation/LLM layer.
`!` Licensing: CollegeOS (Elastic — no managed-service rights), IIE Open Doors (all-rights), some HF datasets (no declared license), `uni-admission-ai`/others MIT but solo/low-stars.
`!` Eval frameworks not proven on Bengali; no admissions-QA eval set → we author.
`!` Plans are **recommendations**; nothing locked. Cost/credits: GCP ~$80, Modal $60, DashScope ~20×1M tokens, DeepSeek funded.

---

## §8 · OPEN DECISIONS (unlocked — Sonnet to resolve)

| Topic | Options |
|---|---|
| Retrieval backend | Discovery Engine vs OSS bge-m3+pgvector-on-Modal (plan favors OSS) |
| Synthesis LLM | Gemini 3.5 Flash (AI Studio) vs Qwen (DashScope) vs both |
| Judge | Gemini Flash vs DeepSeek vs Qwen |
| Corpus assembly | collegedata.fyi (validate) ∪ bespoke CDS parse ∪ authors' 6 reports |
| Structured storage | Postgres+pgvector (Supabase/Neon) vs SQLite+files (≤40 schools) |
| OCR (Bengali uploads) | docling+EasyOCR vs defer (corpora already text) |
| Temporal + citation gate | include now (plan: gate now, temporal later) |
| Scope | Erudite-first (plan) vs parallel with DocRAG |

---

## §9 · LLM HANDOFF NOTES (terse)

- `canonical-framework`=`01_framework/data_architecture.yaml` (schema v3) + `BANGLADESHI APPLICANT INTELLIGENCE SYSTEM.txt` (R1–R7).
- `canonical-research-bank`=`02_school_reports/` (6; only `mit.profile.json` structured).
- `canonical-plan`=`04_plans/SONNET_ERUDITE_PLAN.md`; `canonical-code`=`05_code/erudite-v2/`.
- `biggest-leg-up`=`collegedata.fyi` (MIT) — CDS archive + per-field provenance + H6 at raw layer; **must validate**.
- `dead-ends`: CollegeOS code (Elastic), sdivyanshu MCP repo (no license), stale Kaggle CDS, no OSS end-to-end advisor.
- `do-not-trust`: collegedata friendly API admissions fields (withheld/unreliable); any "intl aid in Scorecard/IPEDS" claim (false); some 2026 arXiv IDs (unverified).
- `trusted`: bge-m3/multilingual-e5/bge-reranker-v2-m3 licenses+multilinguality; MIRACL/Global-MMLU/Belebele `bn`; College Scorecard API; IPEDS; pymcdm/OR-Tools.
- `verification-gate`: executor JSON must emit `citations[]`; block any claim absent from provenance. Separate "refusal" from `faithfulness=1.0`.
- `cost-safety`: cap `max_tokens`; Modal scale-to-zero; prefer AI Studio/DashScope free tiers; no GCP Discovery Engine spend until corpus hash-verified.
- `next`: author the intl-admissions eval set (HF gap) + convert 6 reports to schema v3 + build validated CDS ingest.
