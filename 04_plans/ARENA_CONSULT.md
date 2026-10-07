# ERUDITE — PRINCIPAL-ENGINEER CONSULT: FORMAL SPEC, ADVERSARIAL REVIEW, DATA-INTEGRITY STRATEGY

`audience=MONARQ (principal engineer + decision scientist review)` · `date=2026-10-07` · `branch=arena/49e69040-erudite`
`status=consult; decisions recommended, not imposed` · `supersedes-in-part=04_plans/SONNET_ERUDITE_PLAN.md`

**Discipline note (the product's own rule, applied to this document):** every number below carries a
source tag. `[repo:<path>]` = a claim made by this repository (not independently re-verified this session).
`[verified:<method> <date>]` = checked in this session. `[unverified]` = could not check; treat as hypothesis.
Where the repo itself is the source, the repo may itself be wrong — that is the point of §C.

---

## PART A — FORMAL SPECIFICATION OF THE TAILORING CORE

### A.0 Epistemic architecture: narrative canon, typed ledger, deterministic compute

The repo states a deliberate philosophy (`AGENTS.md`, Knowledge-base philosophy): the dossiers are
**intentionally narrative**; strict JSON flattening destroys the conditions and caveats that make advice
good. The Sonnet plan (`04_plans/SONNET_ERUDITE_PLAN.md`, Part 1.1 and Build Instructions §1–2) goes the
other way: schema-first, Pydantic-strict, prose converted to JSON at ingest. **These two documents
contradict each other. This section resolves the contradiction without picking the wrong side.**

Three substrates, strictly layered (arrows point from derived to source):

```
S3  DETERMINISTIC COMPUTE LAYER   R5/R6/portfolio scores — reads ONLY S2 claims with status=verified
        ▲
S2  CLAIM LEDGER (derived index)  typed claims, each bound to a span of S1 text + provenance + status
        ▲  extraction with span anchors; append-only; never edited, only superseded
S1  NARRATIVE CANON (source of truth)
        full prose dossiers + archived primary artifacts (CDS PDFs, aid pages)
        immutable, hash-addressed, versioned
```

Rules:

1. **S1 is canonical.** A claim in S2 that disagrees with S1 is wrong by definition. Corrections create a
   new S1 revision and supersede, never mutate.
2. **S2 is an index, not knowledge.** It exists so deterministic code and the citation gate have something
   typed to read. Any S2 field that cannot be anchored to an S1 span (or an archived primary artifact) is
   `status=staging` and is invisible to S3 and to the gate.
3. **S3 never reads prose, never reads an LLM.** It reads S2 values + intervals + provenance. Its outputs
   are re-derivable: `score = f(code_hash, input_claim_ids)`.
4. **Synthesis (the LLM) reads S1 prose + S3 outputs + S2 metadata.** It may reason over nuance the
   ledger cannot hold; but every factual claim it emits must cite an S2 claim id (gate in §C.7). Nuance
   without a factual claim is allowed; a factual claim without a citation is blocked.

This is how "rich unstructured knowledge yields auditable advice": the prose keeps the caveats;
the ledger keeps the audit; compute keeps the determinism; the LLM narrates — in that order of authority,
inverted from the legacy engine where the LLM narrated first and nothing audited at all
(`05_code/erudite-v2/backend/services/gemini.py` [repo:gemini.py — no gate, no ledger]).

### A.1 Feature vectors

**Student vector** `s` (intake form, never inferred — §B failure F13):

| Field | Type / domain | Acquisition |
|---|---|---|
| `curriculum` | enum {SSC_HSC, AL, IB, OTHER} + subjects + grades | form |
| `gpa_equiv` | float 0–100 percentile, curriculum-specific scale + conversion table id | form + conversion table (each row sourced) |
| `sat`, `act` | optional ints | form |
| `english` | {IELTS, TOEFL, DUOLINGO, EXEMPT} + score | form |
| `income_usd_yr`, `assets_usd`, `capacity_usd_yr` (= max family payment/yr) | floats, self-reported, BDT→USD at stated rate | form; FX rate + date recorded |
| `loan_tolerance_usd_yr` (`L`) | float ≥ 0 | form (elicitation protocol §E.12) |
| `risk_tol` | ρ ∈ [0,1] from a 3-question lottery-choice elicitation, not a vibes slider | form |
| `major_cat` | enum; `stem_intensity` ∈ [0,1] | form |
| `activities[]` | typed honors (olympiad level, leadership, service) with evidence grade | form |
| `first_gen`, `gender`, `urban`, `school_tier` (pipeline/non-pipeline per R4), `constraints[]` | bools/enum | form |

**School trait vector** `x_k` per school `k` — every component is a *pointer to S2 claims*, not a value:
`policy_type ∈ {A,B,C,D,E,unknown}` [R2]; `coa_y`, `h6 = {r, ā, B}` [R3]; derived
`coverage = r/E_intl`, `budget_per_intl = B/E_intl`; `loan_component`; `four_yr_guarantee`;
`sat_p25/p75`, `test_policy`, `ed_policy`; `curriculum_gate[track] ∈ {open, conditional, blocked, unknown}`;
`documentation_friendliness ∈ {high, medium, low}`; `south_asian_signal`; `bd_evidence[]`;
`intl_admit_rate` (with derivation or `unknown`); `deadlines[]`. **Every component carries status + interval.**

### A.2 Admission-probability model (calibrated to the data we actually have)

**What data exists** [repo:02_school_reports, ERUDITE_REPORT §5.1]: aggregate international admit rates
for a few schools (MIT: 136/6,926 ≈ 1.96% [repo:02_school_reports/mit.md]); SAT middle-50 of admits;
CDS C.125/C.126/C.127 for some schools via collegedata.fyi raw layer (with known mis-extractions);
analyst-invented `p_admit` tables in `mit.profile.json` labeled ESTIMATE. **What does not exist: a
single (applicant features → outcome) labeled example.** So a fitted logistic model
(`arXiv:2202.04987`, cited in ERUDITE_REPORT §5.3 [repo:ERUDITE_REPORT.md]) is not identifiable today.
Anyone shipping one would be fitting noise. The honest construction:

**Step 1 — anchor.** Base rate `α_k` = international admit rate. Sources in priority order:
school-published (mit.md pattern) > C.126/C.125 derived (after §C validation) > overall admit rate ×
international penalty factor `[unknown — quarantine]`. Never invent. If none: `α_k = unknown` and the
school is eligible only for qualitative counsel, not scoring.

**Step 2 — likelihood ratio from the admit-score distribution.** Model scores of *admits* as
`f_A(t) = N(m_k, σ_k)` with `m_k ≈ (P25+P75)/2`, `σ_k ≈ (P75−P25)/1.349` (normal-quantile identity;
MIT: P25≈1520, P75≈1580 are ESTIMATES [repo:mit.profile.json]). The applicant-pool score distribution
`f_P(t)` is **unobserved** — this is the core epistemic hole. Do not assume it away: sweep a family of
pool assumptions `f_P ∈ {N(m_k−Δ, σ_p) : Δ ∈ [0, 150]}` and propagate.

**Step 3 — Bayes inversion:**

```
LR_k(t) = f_A(t) / f_P(t)
p_k(t)  = α_k · LR_k(t) / (1 + α_k · (LR_k(t) − 1))          (exact identity from base rate + LR)
```

**Step 4 — gates and clutch terms (on the logit):**

```
if curriculum_gate_k(s.curriculum) == blocked:      p_k ← 0  (hard gate, R4)
if test_policy_k == required and s.sat is None:     p_k ← 0  (flagged, reversible by plan: "take the SAT")
logit(p′_k) = logit(p_k) + Σ_j θ_jk · c_j(s)                  (clutch factors R6, each θ an interval
                                                                 with evidence grade; clamp p′ ∈ [ε, 1−ε])
```

**Output contract:** `p_k` is always an **interval** `[p_lo, p_hi]` (from Δ-sweep + parameter intervals),
reported as median + 80% band. **Never a bare point estimate.** Category labels are quantile cuts on the
median: reach < 0.15 ≤ target < 0.45 ≤ safety — and these labels are **provisional until funding
conditionality re-ranks them** (A.3), which is the entire point of R5.

**Calibration protocol (the part the plan omits):** with zero outcome labels today, the validity claim is
*monotonicity + anchor consistency*, not Brier score. Stand up the outcome ledger from day one (§E.1);
at N ≥ 200 labeled applications, refit Step 3's adjustment as logistic regression with isotonic
recalibration, and publish before/after Brier + reliability curves. Until then every probability in the
UI carries the tag `model-anchored estimate, not a forecast`.

**Where it breaks:** (i) test-optional/no-score applicants fall back to the GPA proxy with 3× wider
intervals — the model must say so; (ii) `f_A` normality is unverified for any school; (iii) at α ≈ 1–2%
the posterior is dominated by the prior — i.e., *the applicant's non-score features, which this model
barely sees*; (iv) the 6-dossier corpus is too small to estimate θ clutch terms — θ starts as curated
intervals and is fit only when outcome data exists; (v) yield-protection and demonstrated-interest
effects are unmodeled (flagged in output).

### A.3 Funding reliability and R5 expected utility

Definitions, for school `k`, student with annual capacity `C` and loan tolerance `L`:

```
need        N_k = COA_k − C
gap         G_k = max(0, N_k − Aid_k)                    (Aid = grant+scholarship, loans excluded)
funded      F_k = [G_k ≤ L]                              "meaningful funding" per R5
EFC-infl.   δ_k ∈ [0, 0.30] · N_k                        scenario multiplier, evidence from
                                                          documentation_friendliness (R4); default 0.10
                                                          for unknown — UNVALIDATED DEFAULT, tunable
stability   S_k ∈ {1.00 explicit 4-yr guarantee; 0.85 annual re-eval, no negative evidence;
                   0.70 unknown/risky}                   [repo: framework R6-Clutch-6; MIT annual
                                                          re-eval, repo:mit.md]
```

**P(funded | admit)** by policy type (R2), each with its evidence basis:

| Type | P(F|admit) | Basis |
|---|---|---|
| A/B | 0.90–0.975 | institutional commitment; residual = need-analysis misread of BD finances (R4). mit.profile.json uses 0.95 [repo:mit.profile.json] |
| C | clamp(`funded_slots_k / intl_admits_k`) with wide interval | explicit scarcity disclosures where they exist: Vanderbilt "91 students, 50 countries, $24,587–$97,566" [repo:framework R5]; Duke "20–25 funded internationals/yr" [repo:framework R5]; Williams "≈70% of intl receive aid, >$80k avg" [repo:framework R5]. Else coverage-rate proxy from H6 — flagged as proxy |
| D | low; model the *gap distribution* instead | E[Aid] = coverage × ā_H6, then decompose ā for loans/merit-classified-as-need per R1; Monte-Carlo gap scenarios p25/p50/p75 |
| E | treat as D with `policy_trap` flag | Georgetown/Columbia patterns [repo:framework R2] |
| unknown | **refuse to score funding; qualitative counsel only** | |

**Expected utility (mean form):**

```
EU_k = p_k · [ P(F|admit)_k · U_attend,k + (1 − P(F|admit)_k) · U_gap,k ] · S_k − fee_k
U_attend,k = V_k                                    (multi-attribute value, A.4)
U_gap,k    = −λ · E[max(0, G_k − L)]                (λ ≥ 1; default 2 — UNVALIDATED DEFAULT)
```

**Chance-constrained form (primary for high-need students — recommended):**
high-need utility is not well captured by an expectation over catastrophic tails; use the safety-first
probability directly:

```
Score_k = p_k · P(G_k ≤ L | admit, k)        = probability of (admit AND affordable)
```

Report `EU_k` and `Score_k` side by side; **portfolio selection (A.5) uses `Score_k`**, because a
portfolio that maximizes expected utility can still have a fat probability of *zero affordable outcomes*,
which for this user population is the worst failure mode. This formalizes the R5 inversion: a funded
reach (high P(F|admit), low p) can dominate an unfunded target whenever its `Score_k` is larger — e.g.,
MIT `p ≈ 0.008, P(F|admit) ≈ 0.95` → Score ≈ 0.0076 vs. a gapping school `p ≈ 0.30, P(F|admit) ≈ 0.10`
→ Score ≈ 0.030; the inversion is *not* automatic, it is computed, which is the point.

**Where it breaks:** H6 `ā` includes loans and merit-classified-as-need [repo:framework R3] — using it
as grant expectation without the R1 decomposition overstates aid at merit-heavy schools; `EFC_inflation`
is a prior with no school-level measurements yet (§E); FX/PPP distortion of self-reported `C`
(BDT income ≠ USD purchasing power) shifts every gap by ±20% easily — mitigate with banded `C`
(low/mid/high) and report recommendations robust across the band, not a single number.

### A.4 Multi-criteria weighting: reject AHP as specified, keep TOPSIS as a picture only

The plan inherits AHP weights + TOPSIS ranking (`ERUDITE_REPORT.md` §5.3 cites DOI:10.3390/su13073998
for this [repo:ERUDITE_REPORT.md]). Adversarial read:

- **AHP's pairwise weights have no accountable decision-maker here.** The "customer" is a population
  (high-need BD students), not one expert; Saaty-scale judgments would be made by the builders, encoding
  *their* preferences with false precision and no provenance. Weight provenance is exactly the audit
  property this product sells.
- **TOPSIS is normalization-sensitive and rank-reversal-prone** when alternatives are added/removed —
  portfolios change every session.
- `pymcdm` (MIT) and `scikit-criteria` (BSD-3) remain fine *implementations*
  [verified:api.github.com 2026-10-07 — kotbaton/pymcdm MIT 25★; quatrope/scikit-criteria BSD-3 105★].

**Recommended replacement — additive multi-attribute value with declared, sensitivity-tested weights:**

```
attributes j:  affordability_score (gap band), funding_reliability, admit_odds,
               major/fit, visa/OPT pathway, BD community & documentation friendliness
r_kj  = benefit-normalized value in [0,1] (intervals propagated)
V_k   = Σ_j w_j · r_kj        with default w = (0.40, 0.25, 0.15, 0.10, 0.05, 0.05)
```

Weights are (a) declared defaults justified by the mission (affordability-first for high-need), (b)
user-adjustable via direct sliders (SMART/SMARTER direct rating, not AHP), and (c) **obligatorily
sensitivity-tested**: re-rank over `w ± 20%` hypercube; report Kendall-W rank stability; if the top-3
set changes inside the perturbation, the UI says "these three are statistically indistinguishable for
you" — an honest sentence AHP cannot produce. TOPSIS may render the final frontier as a visualization,
never as the selector (selection = A.5 portfolio step on `Score_k`).

### A.5 Portfolio as constraint satisfaction under an application budget

Decision variables: `y_k ∈ {0,1}` (apply), `e_k ∈ {ED1, ED2, EA, RD}` (round).

```
maximize   Σ_k y_k · EU_k − Σ_k fee_k · y_k                      (or maximize worst-case P(≥1 funded admit))
subject to
  Σ_k fee_k · y_k ≤ B                      application budget (fees are real for intl: Common App +
                                           CSS fees; fee-waiver availability per school is a claim field)
  Σ_k [e_k ∈ {ED1, ED2}] ≤ 1               ED is exclusive; ED2 schools only if RD fallback exists
  y_k = 0 if gate_k(s.curriculum) = blocked     (R4 hard gate)
  y_k = 0 if test_policy_k = required ∧ ¬s.sat  (unless plan includes the test — plan module coupling)
  P(≥ 1 funded admit) ≥ 1 − δ              chance constraint, δ default 0.10
  composition: ≥2 safety-band, ≥2 target-band schools among y=1 *after funding-conditionality relabel*
  high-need guard: Σ_k y_k · [policy_type_k ∈ {D,E}] ≤ 1         (gapping-trap cap)
  wildcard: optionally reserve 1 slot for argmax variance(EU_k) s.t. p_k < 0.10
```

**Computing the chance constraint exactly and cheaply** — admissions are Bernoulli with different `q_k =
p_k·P(F|admit)_k`; `P(≥1 funded admit) = 1 − Π`-style computation via Poisson-binomial dynamic program:

```python
def p_at_least_one_funded(q: list[float]) -> float:
    dp = [1.0] + [0.0]*len(q)          # dp[i] = P(exactly i funded admits)
    for qk in q:
        for i in range(len(q), 0, -1):
            dp[i] = dp[i]*(1-qk) + dp[i-1]*qk
        dp[0] *= (1-qk)
    return 1 - dp[0]
```

**Correlation caveat (the plan ignores it):** admit events are positively correlated through unobserved
applicant quality, so the independence DP **overstates** portfolio safety. Bounds while no outcome data
exists: Fréchet `P(all fail) ≥ max(0, 1 − Σ q_k)` and `≤ Π(1−q_k)`; report the band; once outcome data
exists, estimate a one-factor copula and replace independence. For the high-need guard, use the
*pessimistic* end of the band.

**Robustness under interval probabilities:** each `q_k ∈ [q_lo, q_hi]`; adopt a budgeted-uncertainty
(Bertsimas–Sim style) objective: worst case with at most Γ schools at their `q_lo` (Γ = ⌈0.3·|portfolio|⌉
default). N ≤ 40 schools ⇒ OR-Tools CP-SAT (Apache-2.0 [verified:api.github.com 2026-10-07 —
google/or-tools Apache-2.0, 14,157★]) solves this exactly in milliseconds.

```python
# sketch — OR-Tools CP-SAT over precomputed interval scores
from ortools.sat.python import cp_model
m = cp_model.CpModel()
y = {k: m.NewBoolVar(k) for k in schools}
m.Add(sum(fee[k]*y[k] for k in schools) <= budget_cents)
m.Add(sum(y[k] for k in schools if ed[k]) <= 1)
for k in blocked_or_gated: m.Add(y[k] == 0)
m.Maximize(sum(int(EU_lo[k]*1000)*y[k] for k in schools))   # worst-case objective
# composition & chance-constraint enforced via generated cuts from p_at_least_one_funded()
```

**Where it breaks:** independence (above); fee-waiver availability is itself a claim that needs
provenance; ED strategy interacts with aid timing (Columbia-pattern "admitted with funding" declarations
lock aid decisions at application time [repo:framework R2] — the constraint set must include
`aid_declaration_required_at_application` as an ED-compatibility flag); the model assumes the student can
execute the plan (deadlines, documents) — the Plan module must check feasibility, or the portfolio is
fiction.

---

## PART B — ADVERSARIAL REVIEW OF `04_plans/` AND THE SCHEMA

Ranked by expected harm = probability × severity for a high-need BD student. Every item names the fix.

**F1. Unverified numbers feeding deterministic scores — expected harm: CRITICAL, probability: near-certain.**
The ingest plan ("Human QC … the 5–6 most consequential numeric fields … a 15-minute task per school",
Build Instructions §2 [repo:04_plans/SONNET_ERUDITE_PLAN.md]) is exactly the process that would ship the
collegedata.fyi Harvard `H.605 = 66,826,244` mis-extraction [repo:ERUDITE_REPORT.md §5.1]: it is the
*consequential* field, spot-checked against *what*, when the checker's only comparison source is the same
aggregator? The LLM-extraction pass (`qwen3.8-max` [model name unverified]) converts prose→JSON with no
arithmetic cross-check. Meanwhile `mit.profile.json` already contains analyst-invented `p_admit` values
(0.001/0.003/0.008/0.025 [repo:mit.profile.json]) labeled ESTIMATE that will flow into compute.py and a
"ReachabilityChart" and read as measurement. **Fix:** §C pipeline (two-extractor reconciliation +
arithmetic invariants + quarantine); estimates enter the ledger only as intervals with
`origin=analyst_prior`; UI must render intervals and the origin tag.

**F2. The provenance chain is already broken at the source — CRITICAL, already true.**
All six dossiers contain unresolved deep-research citation tokens built from private-use-area characters
(U+E200/U+E201/U+E202), e.g. `cite⟨PUA⟩turn23view0turn12view0`: mit.md 53, nyu.md 65, yale.md 58,
mount_holyoke.md 51, vanderbilt.md 25, amherst.md 24 [verified:byte-level scan of
02_school_reports/*.md 2026-10-07]. These tokens resolve only inside the original research session; they
are citation-*shaped* but cite *nothing*. Recovery asymmetry, also verified: in **mit.md, 100% of tokens
sit within ~400 chars of an inline `Source URL:` list** → rule-based re-anchoring works. In the **other
five files, 0% of tokens have nearby URLs** — their URLs exist only as unanchored lists (e.g.,
amherst.md's escaped URL block in its "Structured JSON Profile" appendix: 10 URLs for 24 tokens) → the
per-sentence link is *lost*, and those claims need source re-fetching or must enter as `staging`. A gate
keyed on `(school_id, field_path)` will either block everything or, if loosened to pass these tokens,
launder dead tokens into "verified" UI citations. **The corpus is not citation-gateable as-is.**
**Fix:** §C.6 rescue pass before anything else; budget re-research for the five non-MIT files.

**F3. The citation gate checks key existence, not claim fidelity — CRITICAL, high probability.**
`gate.py` (Build Instructions §4.1) validates that a cited `(school_id, field_path)` exists in the
provenance set. An executor that cites a real field with the **wrong value** passes. It also passes
vacuously on a response with zero claims — which is the exact shape of the `faithfulness=1.0` on
"Insufficient context" bug already caught once (I13 [repo:ERUDITE_REPORT.md §3]). **Fix:** three-level
gate §C.7: key-existence + value fidelity (numeric tolerance / categorical exact / NLI entailment for
prose) + refusal taxonomy where REFUSED is a first-class status that can never score as VERIFIED.

**F4. Schema flattening contradicts the stated KB philosophy and silently drops conditions — HIGH.**
Build Instructions §1.1 models `need_blind_intl: bool`. The corpus shows why a boolean is a lie:
Georgetown (blind, no full-need guarantee), Columbia ("admitted with funding" language), NYU Promise
(NY-campus first-years only), Mount Holyoke Type E "not verified need-blind"
[repo:framework R2; 02_school_reports]. NYU's dossier is a *contradiction managed in prose*: current
policy (2024 Promise) vs legacy 2022-23 H6 (505 recipients, $29,387 avg, 6.7% coverage
[repo:02_school_reports/nyu.md]) — flattening to one `avg_intl_aid_award` field must silently choose a
side. **Fix:** §A.0 layering: prose stays canonical; ledger fields are enums-with-unknown
(`{true, false, unknown}` never coerced to bool), multi-valued with `effective_from`, conditions kept as
span-bound clauses. Also note the schema in the plan (`v3.1`) and `data_architecture.yaml` (`v3.0`) and
the O2 schema in the framework (`v2.0`) are **three different schemas in one repo**; the reconciliation
work is unowned.

**F5. Judge and executor from the same model family; judge audits math it cannot check — HIGH.**
Plan assigns DeepSeek as both executor and adversarial judge (Build Instructions §0, §4.2). Correlated
errors survive; an LLM cannot reliably verify R5 arithmetic or staleness dates — those are unit-test
territory. **Fix:** deterministic invariant tests + property tests (EU monotone in p; funded-reach can
beat unfunded-target fixture; gate counterexample suite) run before any judge; judge must be a different
model family, blinded to the executor's confidence values.

**F6. Point-estimate false precision at the decision-critical place — HIGH.**
`ReachabilityChart` visualizing `eu_score` per SAT band (Build Instructions §6) turns priors into
"science" for a family making a life decision. **Fix:** intervals + assumption provenance in the UI, or
no chart.

**F7. Visa × funding interaction unmodeled — HIGH, product-gap.**
A student with a funding gap cannot demonstrate full first-year funding for the F-1 I-20/visa file; a
gapped admit is often a *visa-ineligible* admit, not merely an expensive one. The plan never couples the
two; `visa_flags` in schema v3 is decorative (`f1_approval_rate_bangladesh: null` [repo:data_architecture.yaml]).
**Fix:** `gap > 0 ⇒ visa_proof_gap_flag`; portfolio constraint: a "safety" with unfunded gap cannot count
toward the safety floor (§E.2).

**F8. Staleness deferred to "later" — HIGH.**
Plan §3 row "Temporal + citation gate: gate now, temporal later". But the corpus already contains the
temporal trap (NYU legacy H6 vs 2024 Promise), R7 has explicit thresholds [repo:framework R7], and every
dossier stamps retrieval 2026-05-21/22 [repo:02_school_reports/README.md] — expiry is ~2027-05. A gate
without `effective_from` ships stale confidence as current. **Fix:** temporal is part of the gate from
day one; R7 thresholds enforced in code (§C.7).

**F9. Tier-1 "stuff all dossiers into 1M context and shortlist" rests on unverified model claims — MEDIUM.**
`qwen3.8-max` model id and DeepSeek context-window sizes in the plan are unverified (I could not check
from this environment); lost-in-middle at 100k+ context is documented behavior in the literature the repo
itself cites as a risk area [repo:ERUDITE_REPORT.md §7]. Latency and per-query token burn for a
shortlisting pass are unbounded in the plan. **Fix:** shortlist by structured filters (SQL over ledger:
policy_type, gate status, COA band, need level) — deterministic, free, auditable; reserve LLM passes for
synthesis only. This also removes a model dependency from the critical path.

**F10. Security/privacy posture of the legacy code is inherited by default — MEDIUM-HIGH.**
`main.py`: `allow_origins=["*"]` with credentials [repo:05_code/erudite-v2/backend/main.py];
`dev-token` auth (I9 [repo:ERUDITE_REPORT.md §3]); hardcoded project id fallbacks; the fallback payload
in `gemini.py` fabricates authoritative-looking `audit_feedback` ("Indexing in progress…") on error —
the system talks confidently while empty, the exact I14/I2 failure signature. The plan adds family
financial data flowing into free-tier LLM APIs **with no review of those providers' data-use terms**
(unverified), no retention policy, no consent flow, and Bengali uploads = a prompt-injection surface
straight into the citation path. **Fix:** PII minimization at intake (bands not raw income where
possible), provider data-use review before first real query, error states that refuse instead of
fabricate, upload sanitization + injection suite (§E.5).

**F11. Fairness: pipeline-school features can encode class bias — MEDIUM, mission-critical.**
R4's pipeline caveat is honest about the world but dangerous in the model: feeding `school_tier`
(Viqarunnisa vs. provincial Sylhet example [repo:framework R4]) into p_admit or into "documentation
friendliness"-driven recommendations can systematically downgrade rural/non-pipeline students — the
exact population this product exists for. `arXiv:2009.05609` is already in the prior-art list
[repo:ERUDITE_REPORT.md §5.3]. **Fix:** fairness audit defined before launch: for matched academic
profiles, recommendation-set quality must not differ by school_tier/urban beyond a declared ε; report
the audit with the product.

**F12. Bengali path is unbudgeted and unbenchmarked — MEDIUM.**
Repo confirms no public Bengali long-doc benchmark and no admissions QA dataset
[repo:ERUDITE_REPORT.md §5.4]; plan defers OCR while uploads are in the wishlist; bge-m3 `bn` support is
real (MIRACL) but reranker quality on Bengali admissions prose is unverified. **Fix:** authored bn eval
set + native-reviewer budget line (§E.10); uploads gated behind sanitization until then.

**F13. Intake assumes truthful, complete self-reports — MEDIUM.**
`family_capacity`, risk tolerance, even curriculum grades are self-reported under family pressure; the
wish-list names family constraints and gender dynamics. The plan has no elicitation protocol, no
sensitivity of advice to ±20% misreport. **Fix:** banded inputs + fragility flags (§E.5), elicitation
protocol (§E.12).

**F14. Legacy corpus bleed — known but re-verifiable only by test — LOW cost, HIGH severity if missed.**
I14: the deployed demo answered from the clinical-safety store
[repo:ERUDITE_REPORT.md §3; 03_product/erudite_v2_handoff.txt literally shows an SAE/clinical example
served by the "admissions counselor"]. The plan's answer is infrastructure separation; the only real
answer is a canary test suite: queries that *must* refuse ("what are the SAE reporting rules?") run in CI
against every deployment.

---

## PART C — DATA-INTEGRITY STRATEGY: SOURCE → VERIFY → PROVENANCE

Premise: our best source is partly wrong (collegedata.fyi mis-extractions
[repo:ERUDITE_REPORT.md §5.1]) and the fields we most need exist in no machine form anywhere
(international admit rate, need-blind status, curriculum gates [repo:ERUDITE_REPORT.md §5.1]).
Therefore: **never trust an extracted value; trust only a value that survived reconciliation against an
archived artifact and declared invariants.**

### C.1 Source registry (S0)

One row per source artifact: `artifact_id, url, sha256(snapshot), retrieved_at, http_etag/last_modified,
license, tier (T1–T4 per framework O1), school_id, field_scope`. Snapshots stored WORM (content-addressed
by sha256). collegedata.fyi [verified:api.github.com 2026-10-07 — bolewood/collegedata-fyi, MIT, pushed
2026-10-06; README: 6,322 institutions, 4,071 archived CDS docs, 262,537 cds_fields rows per its
2026-08-06 audit] is used as the **locator** (its `archive_url`, `ipeds_id`, `canonical_year`,
`value_status` are gold) — **not as the value authority**. Note: ERUDITE_REPORT §5.1 says 333,131 rows;
the repo's own later audit says 262,537 [verified:collegedata-fyi README 2026-10-07] — even our report
about the source drifted. Provenance discipline applies to our own documents too.

### C.2 Deterministic extraction first, LLM second (S1–S2)

CDS documents have a canonical 1,105-field schema keyed by stable question numbers
[verified:collegedata-fyi README — "CDS Initiative publishes a canonical machine-readable schema …
1,105 fields"]. That makes rule-based extraction feasible and *more precise than LLMs* for numerics:

1. Unflattened fillable PDFs: `pypdf.get_fields()` — collegedata.fyi's README states this tier "matches
   ground truth perfectly" [verified:README 2026-10-07]. Use it.
2. Flattened PDFs/HTML: layout parse (docling — license not re-verified this session [unverified]) +
   per-question-id regex/table grammars with unit tests pinned to archived artifacts.
3. LLM extractor runs **as a second, independent opinion**, not the primary.

### C.3 Reconciliation: two-extractor agreement + invariant battery (S3)

```
auto_verified   if |v_det − v_llm| ≤ tol(field) and invariants pass
quarantine      otherwise → human adjudication queue with side-by-side archived-artifact view
```

Invariant battery (each one is a unit test; each would have caught a known error):

- **H6 identity:** `H.604 × H.605 ≈ H.606 (±1%)` — catches Harvard's `H.605 = 66,826,244`
  [repo:ERUDITE_REPORT.md §5.1] instantly.
- **C-chain monotonicity:** `C.125 ≥ C.126 ≥ C.127`; `intl_admit_rate = C.126/C.125 ∈ (0,1)` — catches
  Harvard C.126 = total-admitted and Amherst C.126 implausible [repo:ERUDITE_REPORT.md §5.1].
- **Coverage sanity:** `coverage = r/E_intl ∈ [0,1]`; `budget_per_intl` within plausible band.
- **Year-over-year drift:** `|Δ| > threshold` → not an error but a *staleness/quarantine flag* (policy
  may have changed — that's a story, not a typo).
- **Cross-source:** COA vs IPEDS/Scorecard [Scorecard = public domain, free key, 1,000 req/IP/hr
  — repo:ERUDITE_REPORT.md §5.1]; enrollment vs IPEDS; aid-page marketing claim vs H6 (R3 Step 6).

### C.4 Claim ledger (S5) — the citation gate's substrate

```jsonc
{
  "claim_id": "mit.cds.h6_avg_award.2024-25",
  "school_id": "mit", "field_path": "cds.h6_avg_award",
  "value": 77266, "unit": "USD", "interval": null,
  "span": {"doc_sha256": "…", "paragraph": 41, "char_offsets": [102,180], "span_sha256": "…"},
  "source": {"artifact_id": "…", "url": "https://ir.mit.edu/projects/2024-25-common-data-set/",
             "tier": "T1", "retrieved": "2026-05-22"},
  "effective_from": "2024-08", "as_of": "2026-05-22",
  "extraction": {"method": "pypdf.acroform+invariants", "second_opinion": "llm.agree"},
  "verification": {"status": "verified", "verified_by": "human:initials", "verified_at": "…"},
  "superseded_by": null
}
```

Append-only. Corrections supersede. Numeric claims may carry intervals and `origin ∈
{measurement, derivation, analyst_prior}` — `analyst_prior` claims (the ESTIMATEs) are visible to
synthesis with mandatory tags, invisible to scoring unless a human promotes them.

### C.5 Prose-only facts (policy type, curriculum gate, 4-yr guarantee) (S6)

No machine source exists [repo:ERUDITE_REPORT.md §5.1]. Curation protocol: claim requires **(a)** the
school's international-specific page text archived in S1 + **(b)** one independent corroboration or an
explicit recorded absence ("searched X on date; not found" is itself a claim with provenance), +
**(c)** human sign-off. Status enum `{confirmed, best_effort, unknown}` — **`unknown` is never coerced
to `false`** (bool-defaulting is how Type E traps ship as "need-blind: no" or "need-blind: yes").

### C.6 Rescue pass for the six existing dossiers

1. **mit.md:** strip PUA tokens; re-anchor each to the adjacent inline `Source URL:` list — verified
   100% adjacency (53/53 tokens within ~400 chars of a URL list [verified:byte-scan 2026-10-07]);
   quarantine any straggler the rule misses.
2. **amherst/yale/vanderbilt/mount_holyoke/nyu:** per-sentence anchoring is not recoverable (0% token
   adjacency; URLs exist only as unanchored appendix lists). Two options per claim: (a) re-fetch the
   listed URLs and re-verify the sentence (preferred — the URL lists are short: 8–36 per file
   [verified:grep 2026-10-07]); (b) enter as `status=staging`, visible to synthesis with mandatory
   "unre-verified 2026-05 corpus" tag, invisible to scoring. Nothing from these five files should reach
   the UI as `verified` without (a).
3. Re-run C.2–C.3 extraction over the prose to build the initial ledger; every `ESTIMATE` and every
   `DATA NOT PUBLICLY AVAILABLE` (25 in amherst.md alone [verified:grep 2026-10-07]) becomes an explicit
   ledger status, not a string.
4. `mit.profile.json` enters as `origin=analyst_prior`, re-verified field by field before any scoring use.

### C.7 Citation gate v2 (three levels + temporal)

```
G1 key-existence      every cited (school_id, claim_id) exists and is not superseded/stale
G2 value fidelity     numeric: |claimed − ledger| ≤ tol; categorical: exact;
                      prose: NLI entailment of claim against supporting span
                      (e.g., DeBERTa-v3-base MNLI-class model — license MIT per upstream project,
                       NOT re-verified this session [unverified]); score < τ ⇒ block + rewrite
G3 completeness       response ∈ {ANSWERED(cited), PARTIAL(cited+gaps declared), REFUSED_NO_CONTEXT};
                      REFUSED must never emit faithfulness-style PASS metrics;
                      zero-claim response ⇒ REFUSED, never VERIFIED
G4 temporal           claim.effective_from/as_of vs R7 thresholds ⇒ visible staleness banner,
                      or block for policy-type claims past 12 months without re-verification
```

### C.8 Release gate + freshness automation

- Golden set: ≥200 hand-verified field values across ≥10 schools from archived artifacts. Release rule:
  numeric extraction **precision ≥ 0.99 on the golden set** before auto-publish; quarterly re-audit.
- Scheduler re-crawls the source registry (CDS annually, aid pages quarterly); sha256 diff on archived
  pages ⇒ change event ⇒ auto-quarantine affected claims (this operationalizes R7's "early warning
  signals" [repo:framework R7] for ~zero cost).

---

## PART D — OPEN DECISIONS, RANKED BY LEVERAGE

| # | Decision | Recommendation | The ONE tradeoff that decides it |
|---|---|---|---|
| 1 | **Corpus assembly** | collegedata.fyi as locator + our own re-extraction from its archived artifacts; 6 dossiers re-anchored (§C.6); IPEDS/Scorecard as federal cross-check | Coverage vs. verification cost — every school we *don't* re-verify is a liability, so coverage grows only as fast as the adjudication queue |
| 2 | **Retrieval backend** | Tier-0 context-stuffing with span-level citations now (corpus ≪ context); vector DB deferred to >~30–40 schools, then pgvector/sqlite-vec + bge-m3 | Infra-now vs. infra-later; but the real risk either way is **provenance-preserving chunking** — naive chunking severs claims from spans and breaks the gate regardless of backend |
| 3 | **Synthesis model** | whichever free/cheap tier whose **data-use terms permit non-training on prompts**, decided before the first real query carries family financial data; model names in the plan (`gemini-3.5-flash`, `qwen3.8-max`, DeepSeek versions) are all unverified from here [unverified] | Cost vs. privacy policy — free tiers typically log/train; a student's declared family income is exactly the data you cannot afford to leak |
| 4 | **Judge** | deterministic invariant/property tests first; LLM judge second, **different model family** than executor, blind to executor confidence | Independence vs. cost — a same-family judge is a cheaper illusion of safety |
| 5 | **Storage** | git-versioned prose (S1) + append-only SQLite claim ledger (S2) now; Postgres only when multi-writer | Simplicity vs. query power — at 6–40 schools SQLite is not a compromise, it is the correct size |
| 6 | **Embeddings/rerank (when needed)** | bge-m3 + bge-reranker-v2-m3 per ERUDITE_REPORT §5.4 (MIT/Apache-2.0 per that 2026-09 check [repo:ERUDITE_REPORT.md]; not re-verified this session) | Multilingual coverage vs. serving a ~568M model on scale-to-zero compute |
| 7 | **OCR** | defer (agree with plan); explicit trigger = first scanned upload; then license-check at that moment | Zero current need vs. wishlist includes uploads — name the trigger instead of silently deferring forever |
| 8 | **Framework** | bespoke pipeline (the surface is small: gate + ledger + compute + one synth call); LlamaIndex/Haystack (MIT/Apache) only if retrieval grows | Control/auditability vs. maintenance — a framework between you and your gate makes the gate harder to prove |

---

## PART E — WHAT YOU'RE MISSING (the embarrass-us-later list)

**E.1 The outcome loop — the single biggest hole.** Nothing in the repo ever observes whether a recommended
student was admitted or funded. Without it, §A.2's probabilities are eternal priors, R5 is unfalsifiable,
and the product cannot claim to be better than a pamphlet. Build the consented outcome ledger now (even
manual CSV + counselor follow-ups): school, round, aid offer, decision, visa outcome. Every module should
be designed so that in 18 months the first recalibration is a data drop, not a re-architecture.

**E.2 Visa × funding coupling** (§B-F7): gapped admits are frequently F-1-ineligible admits. No module in
the plan sees this. It belongs in the portfolio constraints and in every financial-aid answer as a
mandatory check.

**E.3 Portfolio risk formalism.** The plan has no notion of correlated admissions; §A.5's Fréchet band +
Poisson-binomial DP + budgeted-uncertainty robustness is the missing formal layer. Without it, "P(≥1
funded admit) ≥ 0.9" is optimism dressed as arithmetic.

**E.4 A baseline to beat + decision-theoretic evaluation.** Define the naive baseline ("apply to the ~9
need-blind-intl schools [repo:framework R2, 'as of 2025' — re-verify] + cheapest near-open safeties")
and require the optimizer to beat it on expected affordable-admits in simulation before any student sees
it. Add calibration curves + decision-curve analysis once E.1 data exists. A product that cannot beat
the free heuristic has no product.

**E.5 Red-team & fragility evaluation set.** The repo knows no admissions QA dataset exists anywhere
[repo:ERUDITE_REPORT.md §5.4] — so author three suites: (a) adversarial: prompt injection via uploads,
ghostwriting solicitation, fabrication elicitation, out-of-bank schools (must refuse), visa-fraud-adjacent
asks; (b) counterfactual fragility: income ±10–20%, SAT ±50, curriculum swap — if a recommendation flips,
the answer must carry a fragility warning; (c) the clinical-corpus canary (F14) in CI.

**E.6 Model-risk management for compute.py.** The deterministic score is the product's credit score.
Version it like a regulated model: `(code_hash, ledger_claim_ids, profile_hash) → score`, property tests
(monotonicity, funding-dominance fixtures), regression suite, changelog. If a number a family acted on
changes, you must be able to say exactly why and when.

**E.7 Data-modeling traps:** multi-campus institutions (NYU's Promise is NY-campus-only
[repo:02_school_reports/nyu.md] — but also university systems with 2–3 campuses share IPEDS ids); CDS
academic-year vs COA-year mismatch already present in mit.profile.json ("2024-25 estimated" H6 against
2026-27 COA [repo:mit.profile.json]). The ledger needs `effective_from` per claim *and* a "year-alignment
warning" derivation rule, or gap math quietly mixes years.

**E.8 Liability & ethics wrapper.** Financial-aid and visa guidance to minors' families: disclaimers are
table stakes; beyond that, decide now what Erudite *never does* (draft submittable essays, promise
outcomes, advise on misrepresenting finances — the last is a real risk when families ask how to present
informal income). Norms for AI advising tools are shifting [unverified — no current citations from this
environment]; a written ethics one-pager costs an afternoon and is uncopyable by competitors.

**E.9 Essay & interview integrity by construction.** The essay module should emit frameworks, questions,
and critique — never submittable prose. Interview prep must ground questions in the ledger or label them
synthetic; an ungrounded "the alum will ask X" is the I2 failure mode in costume.

**E.10 Bengali evaluation budget.** Authored bn set needs paid native-expert review; the plan has no line
item. Also: measure explanation quality in Bengali, not just retrieval (the differentiator for this
population is *understanding*, not retrieval).

**E.11 Change-detection automation** (§C.8) — cheap page-hash diffing turns R7 from a discipline into a
daemon. Nobody will manually notice Dartmouth-sized policy shifts across 40 schools.

**E.12 Validated risk/preference elicitation.** `ρ` and `L` currently would be vibes. Three lottery-choice
questions + banded capacity takes 5 minutes of intake and makes §A.3's λ and the chance-constraint's δ
honest inputs instead of invented ones.

---

## VERIFICATION LOG (this session, 2026-10-07)

| Check | Method | Result |
|---|---|---|
| Repo read: ERUDITE_REPORT, AGENTS, framework R1–R7, schema v3, Sonnet plan, 6 dossiers, mit.profile.json, legacy code, product docs | read_file | as cited |
| Citation-token corruption in all 6 dossiers | byte-level scan (python) | PUA-char `cite…turn…` tokens everywhere (mit 53, nyu 65, yale 58, mhc 51, vanderbilt 25, amherst 24); resolve nowhere; mit.md 100% re-anchorable to adjacent URLs, other five 0% adjacency (appendix URL lists only) |
| `DATA NOT PUBLICLY AVAILABLE` density | grep | amherst.md 25, nyu.md 11, mount_holyoke.md 5, yale.md 2, vanderbilt.md 2, mit.md 1 |
| License: bolewood/collegedata-fyi | api.github.com | MIT, pushed 2026-10-06; README: 4,071 CDS docs, 262,537 cds_fields rows (2026-08-06 audit), AcroForm tier = deterministic |
| License: CollegeOS | api.github.com | `NOASSERTION` (no standard license detected) — consistent with repo's Elastic-2.0 verdict; non-reusable either way |
| Licenses: admission-skills MIT; EDU_financial_aid_agent Apache-2.0; mcp-college-counselor **none**; AdmissionAgent MIT; uni-admission-ai MIT; or-tools Apache-2.0 (14,157★); ragflow Apache-2.0 (91,758★); kotbaton/pymcdm MIT; quatrope/scikit-criteria BSD-3 | api.github.com | as listed |
| Discrepancy: ERUDITE_REPORT says collegedata.fyi has 333,131 cds_fields rows; source README audit says 262,537 | both documents | unresolved — re-check before quoting either |
| Model names in plan (`qwen3.8-max`, `gemini-3.5-flash`, DeepSeek context sizes), HF model licenses, collegedata.fyi live values (Harvard H.605 etc.) | not reachable from this environment | **unverified** — flagged in text |

## BUILD-ORDER DIFF (what to do Monday, in order)

1. §C.6 rescue pass on the 6 dossiers — mit.md re-anchorable by rule (hours); the other five need URL
   re-fetch/re-verify or demotion to `staging` (days; unblocks everything provenance-shaped either way).
2. Claim-ledger schema + append-only store + `effective_from` (the gate's substrate; §C.4/C.7).
3. Invariant battery as unit tests against archived CDS artifacts (§C.3) — before any new school ingest.
4. Golden set ≥200 fields (§C.8) — before trusting any extractor, LLM or otherwise.
5. compute.py with intervals + property tests (§A.3/A.5) — before any UI chart.
6. Portfolio optimizer on `Score_k` with Fréchet band (§A.5).
7. Outcome ledger schema (§E.1) — before the first real student query, so data starts accruing.
8. Only then: synthesis-model choice (after data-use review, D.3), frontend, vector DB when corpus demands.

*This document applies Erudite's own rule to itself: where it could not verify, it says so.*
