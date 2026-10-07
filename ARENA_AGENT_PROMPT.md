# PROMPT FOR ARENA.AI AGENT — ERUDITE

> Paste the block below into arena.ai as the opening message to a frontier agent.

---

You are being handed one of the hardest applied-AI problems in education access. Read the whole brief before answering. This is a systems/architecture consult with mandatory adversarial review — not a tutorial, not a code-generation request you can satisfy with a generic RAG skeleton.

## MISSION
Design and pressure-test **Erudite**: a grounded, citation-gated admissions + financial-aid advisor that maps US university traits onto a specific high-need Bangladeshi applicant's goals and current status. Public repo (read it first): **https://github.com/realsamiul/erudite** — start with `ERUDITE_REPORT.md`, then `AGENTS.md`, `01_framework/BANGLADESHI_APPLICANT_INTELLIGENCE_SYSTEM.txt` (rules R1–R7), `01_framework/data_architecture.yaml` (schema v3), `04_plans/SONNET_ERUDITE_PLAN.md`.

## THE WISHLIST — WHAT "DONE" LOOKS LIKE
The objective: **an AI agent that uses our knowledge base to deliver genuinely powerful advice tailored to distinct Bangladeshi student backgrounds** — not generic, one-size-fits-all guidance. "Tailored" is the whole point: the advice must change materially with the student's actual reality (household income and need level, SSC/HSC vs A-levels vs IB, intended major, test scores, English level, risk tolerance, family constraints and pressures, urban/rural, gender dynamics). Coverage must span the full journey, at minimum:
- **Financial aid** — net-price reality, need-blind vs need-aware intl, expected aid and gaps, loan exposure, the R5 reachability-funding inversion.
- **Visa** — F-1 process, proof-of-funds/financial documentation, timelines, interview preparation, common refusal risks.
- **Essay** — narrative strategy, integrity constraints (fabrication and ghostwriting are out), school-specific framing.
- **Plan** — a realistic multi-year roadmap mapped to deadlines and the R4 curriculum gate.
- **School selection** — reach/target/safety/wildcard portfolio built on the traits×profile mapping, not magazine rankings.
- **Interview prep** — admissions/alumni/visa interview simulation with feedback.

## KNOWLEDGE-BASE PHILOSOPHY (deliberate — read before proposing a schema)
The knowledge base is **intentionally narrative and rich, not a rigid JSON field store.** We **dispensed with forcing the dossiers into strict JSON schemas because that flattening loses the complexity** — the nuance, conditions, caveats, and reasoning chains (R1–R7) that make the advice good and that a fixed schema cannot hold. Treat `01_framework/data_architecture.yaml` as *one optional lens*, not the data contract. Retrieval must operate over full prose and the advisor must reason over it — **while still enforcing provenance and the citation gate.** Do not "solve" this by demanding rigid JSON; instead design how rich, unstructured knowledge yields auditable, tailored advice. If JSON is used anywhere, it is an output/transport convenience, never the epistemic source.

## WHY THIS IS GENUINELY HARD — DO NOT FLATTEN IT
1. **The creative core has no off-the-shelf answer.** The differentiator is a *systematic mapping* from (many heterogeneous university traits: need-blind vs need-aware intl, meets-full-need, admit probability, COA, intl aid median, curriculum gate like A-levels vs SSC/HSC, test policy, deadline structure) to (one specific student's goals, constraints, risk tolerance, family finances). This is simultaneously probabilistic, multi-objective, constraint-satisfying, and explainability-critical. "Just ask an LLM" is disqualifying.
2. **The data is adversarial.** No free source publishes a verified *international* admit rate; need-blind/need-aware status is prose, not a machine field; curriculum requirements exist nowhere structured. The best public source (collegedata.fyi, MIT-licensed CDS archive) is live but **demonstrably mis-extracts values** (Harvard H.605 = 66,826,244; Amherst C.126 implausible) and self-flags low-confidence fields. Facts are sparse, stale-prone, and partly wrong — and the product's entire value depends on being right.
3. **Grounding is a hard gate, not a metric.** Every claim in any answer must trace to a provenance record (`school_id` + `field_path`); unverifiable claims must be **blocked**, not scored. The system must distinguish "I don't know" from a confident `faithfulness=1.0` on empty context (a real bug we've already caught).
4. **The decision is high-stakes and asymmetric.** A funded "reach" can dominate an unfunded "target"; expected utility must invert the naive reach/target/safety heuristic. Getting R5 wrong sends a high-need student to a school they can't afford or away from one they could. Fairness and harm matter here.
5. **Multilingual boundary.** English-first, but Bengali uploads and Bengali-language explanation are in scope; retrieval/reranking must work across scripts. Public Bengali long-document benchmarks do not exist, and no admissions/financial-aid QA dataset exists in any language — we must author our own evaluation.
6. **Every layer is constrained at once.** Provenance chain, license hygiene (some tempting repos are Elastic-2.0 or unlicensed), cost caps (free-tier LLMs, serverless scale-to-zero), staleness (R7), and an auditable deterministic score — all together, not one at a time.
7. **We already know the trap.** A prior deployed version of this system silently answered admissions questions from an unrelated clinical corpus and shipped unverified citations. Assume the same failure mode will reappear. Design against it.

## WHAT EXISTS (so you build on it, not beside it)
- Domain IP: rules **R1–R7** (claim decomposition, A–E policy topology, CDS-H6 forensics, nationality-decomposition proxy, reachability-funding inversion, clutch factors, staleness).
- **6** finished forensic school dossiers (MIT, Yale, Amherst, Vanderbilt, Mount Holyoke, NYU), one partially machine-readable.
- A schema (v3, 11 layers) designed but never enforced; a plan (schema-first, tiered context-stuffing → retrieval, deterministic R5/R6, hard citation gate, adversarial judge) that is recommended and **not locked**.

## WHAT I NEED FROM YOU — TAKE THE HARD PATH
Work at the level of a principal engineer + decision scientist combined. Deliver:
- **A. Formal specification of the tailoring core.** Define the feature vector, the admission-probability model and how to calibrate it with the data we actually have, the funding-reliability/expected-utility formulation (R5), the multi-criteria weighting (justify AHP/TOPSIS vs alternatives), and the portfolio/constraint-satisfaction formulation (reach/target/safety/wildcard under an application budget). Give equations and pseudocode. State every assumption and where it breaks.
- **B. Adversarial review.** Tear apart the plan in `04_plans/` and the schema. Where will it hallucinate, silently fail, or mislead a vulnerable user? Rank the failure modes by expected harm.
- **C. Data-integrity strategy.** Given that our best source is partly wrong and no source has international admit rates or need-blind flags, specify a concrete extraction + reconciliation + validation pipeline (source→verify→provenance) that yields defensible numbers.
- **D. Ranking of the hardest open decisions** (retrieval backend, synthesis model, judge, corpus assembly, storage) with the single most important tradeoff for each.
- **E. What we're missing.** Name the approach, dataset, formal method, or failure we have not considered — the thing that would embarrass us later.

## CONSTRAINTS
- Every number you cite must carry a source; if you cannot verify it, say "unverified" — do not invent. This is the same discipline the product requires.
- Prefer proven, permissively-licensed components; explicitly flag anything Elastic/non-commercial/unlicensed.
- Be brutally specific: equations, algorithms, schemas, pseudocode, named libraries/models. No motivational filler, no generic RAG tutorial, no restating the brief back to me.

## THE AMBITION (why the difficulty is the point)
We are not building a college chatbot. We are building the counselor that a high-need Bangladeshi student never had — one that takes an opaque, adversarial US financial-aid system and maps it, auditable claim by auditable claim, onto that specific student's reality. If that sounds over-scoped, it is: the difficulty is the differentiator, and the cost of getting it wrong is measured in a student's future. So tell us precisely where the design breaks under its own weight — and exactly how to make it hold.
