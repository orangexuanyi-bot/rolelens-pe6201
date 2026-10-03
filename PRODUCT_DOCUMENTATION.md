# RoleLens product documentation

## Purpose and persona

RoleLens helps an early-career **AI or commercial product manager** prepare for a role. It compares one job description (JD) with one candidate profile, links the role's requirements to supplied evidence, and proposes three preparation gaps. A gap means that the supplied profile offers limited evidence for an important requirement; it is not proof that the person lacks the ability.

**Primary persona:** Mei is preparing for an AI PM interview in three days. She has product experience but uneven AI-domain exposure. She needs to decide which three topics deserve her next preparation session, and to inspect the evidence behind those priorities. Monetization, subscription and advertising PM candidates are also in scope. The target job is a PM role even when the candidate previously worked in another function.

The intended change is a focused preparation plan rather than an unstructured list of JD keywords. Preparation-time savings and usefulness have not yet been measured. Resume rewriting, automatic applications, hiring recommendations, protected-trait inference, and assessment for engineering or algorithm jobs are outside this prototype's scope.

## Input and output

| Item | Contract |
| --- | --- |
| JD | English text, 80-20,000 characters after trimming. Put a supported product-manager title on the first nonempty line. The title/domain heuristic can reject unusually formatted valid roles. |
| Candidate profile | English evidence bullets or narrative, 30-12,000 characters after trimming. Use fictional data or appropriately authorized, de-identified material. Removing contact details alone does not establish anonymity. |
| Interface | Streamlit accepts pasted text. The CLI reads `.txt`, `.md`, and text-layer `.pdf` files; image-only files need separate local OCR. |
| Local output | Keyword-matched capabilities, source phrases and up to three gap IDs. Fewer than three candidate gaps produces an abstention, although partial baseline information remains visible. |
| AI output | Role summary, responsibilities with JD quotes, capability evidence labeled `strong`, `partial`, or `not_evidenced`, exactly three gaps with preparation actions, local knowledge-note citations, and limitations. |
| Failure output | A visible abstention and reason codes; rejected model calls can still have a cost. |

The AI path sends the JD, profile and three knowledge notes to OpenRouter/Gemini only after explicit external-processing consent. An obvious email/phone detector checks the profile, but does not replace consent or de-identification. API credentials come from the process environment. Ordinary analysis does not save inputs; the evaluation harness separately saves fictional result excerpts for reproducibility.

## Architecture

```mermaid
flowchart TD
    U[Candidate: one English PM JD and one profile] --> UI[Local Streamlit UI or Python CLI]
    UI --> G[Length and PM-scope checks]
    G --> B[Deterministic keyword baseline]
    T[Local taxonomy: 14 PM capabilities] --> B
    G --> R[Local lexical retrieval: select 3 notes]
    K[30 author-written knowledge notes with source URLs] --> R
    B --> O[Local result: baseline and evidence]
    R --> C{AI mode and permission?}
    C -->|No| O
    C -->|Yes; contact and retrieval checks pass| P[Prompt plus JSON schema]
    T --> P
    P --> OR[External OpenRouter API]
    OR --> GM[External Gemini 3.7 Flash]
    GM --> OR
    OR --> V[Local schema, ID and exact-quote validator]
    V -->|Pass| A[Evidence-linked report, 3 preparation gaps, cost and latency]
    V -->|Fail| X[Abstain with reason codes and available cost]
    A --> UI
    X --> UI
```

Text equivalent: **input -> local scope/baseline/retrieval -> permission check -> OpenRouter -> Gemini -> local validation -> report or abstention**. Official source websites provide reading links; this pipeline does not browse them during an analysis. It uses no vector database, trained classifier, automatic tool loop, or external action tool.

### Build versus buy

| Layer | Choice and reason | Main cost or limitation |
| --- | --- | --- |
| Interface | Build a small Streamlit UI using an existing library. It exposes evidence and the baseline alongside results. | Local prototype; no production authentication or multiuser serving design. |
| Orchestration and validation | Own Python code for permission, scope, output contracts, cost reporting and abstention. | Rules need maintenance and cannot establish semantic correctness. |
| Model | Rent `google/gemini-3.7-flash` through OpenRouter, one request per AI analysis. | Provider dependency, token charges and model latency. |
| Retrieval | Own a lexical index over short source-linked notes. It is inspectable and easy to run. | Misses synonyms and has no measured retrieval-quality benchmark. |
| Evaluation | Own frozen fixtures, reference metadata, deterministic metrics and saved run records. | Synthetic candidates, summarized real requirements, profile reuse and shared-author bias limit validity. |

The simple baseline is the measured alternative. Narrow ML was not trained because stable labeled training data is unavailable. The original embedding-retrieval plan was reduced to lexical retrieval for a small corpus and simpler setup. A general chatbot lacks this prototype's reproducible baseline and deterministic evidence contract. A low-code workflow could connect a form to an LLM; Python was chosen to keep the validator and evaluation behavior explicit and versioned. No low-code prototype or measured time-to-deploy comparison is claimed. An agent loop is unnecessary because the task needs one analysis, not autonomous actions.

## Targets and observed results

The proposal specified thirty official JDs and thirty held-out comparisons, with at least 80% case agreement and a +20 point improvement. The final experiment now covers thirty real employer requirement summaries and thirty synthetic profiles. It is an exploratory study with AI references and previously used profiles; it does not establish the originally proposed independent holdout validity.

| Measure, all 30 real-role pairs | Keyword baseline | Gemini |
| --- | ---: | ---: |
| Accepted / attempted | 13/30 (43.3%) | 30/30 (100.0%) |
| Cases matching at least 2 of 3 reference IDs | 7/30 (23.3%) | 19/30 (63.3%) |
| Matched reference IDs, abstention = 0 | 17/90 (18.9%) | 55/90 (61.1%) |
| Median end-to-end latency | 3.865 ms | 7.157 s |
| Response-reported API cost | No external call | US$0.24741375 total; $0.008247/attempt |

The 80% case-agreement threshold was not reached; the +20 percentage-point difference was reached on this AI-reference dataset. Neither establishes an independent correctness target. The observed case-agreement difference is 40.0 points. A high difference against an alias baseline with many abstentions is not proof of reliable superiority over stronger alternatives. Full provenance and historical results appear in [data and evaluation](DATA_AND_EVALUATION.md).

## File and module guide

| File or module | Role |
| --- | --- |
| `streamlit_app.py` | Pasted-text interface, permission checkbox, evidence display, abstention, model usage. |
| `rolelens/cli.py` | File-based analysis and local private-CV aggregate mode; preserves the original separately gated human-reference evaluator. |
| `rolelens/pipeline.py` | Coordinates input/scope checks, baseline, retrieval, permission, provider and validator. |
| `rolelens/scope.py` | First-line PM-title and AI/commercial-domain heuristics. |
| `rolelens/taxonomy.py` | Fourteen versioned PM capability IDs, keyword aliases and lexical evidence extraction. |
| `rolelens/baseline.py` | Deterministic weighted keyword ranking and baseline abstention. |
| `rolelens/retrieval.py` | Loads notes, filters by role family, scores lexical overlap and selects three. Hybrid roles reserve both families when possible. |
| `rolelens/provider.py` | System prompt, structured JSON schema, single OpenRouter request, token/cost/latency metadata. |
| `rolelens/validation.py` | Checks output shape, valid IDs, exact quotations, citation IDs and three supported gap selections. |
| `rolelens/exploratory.py` | Reproducible exploratory runner, snapshots, atomic result files, safe resume and summaries. |
| `project_core/evidence.py` | SHA-256 data locks and record integrity checks. |
| `project_core/metrics.py` | Shared evaluation utilities; exploratory interpretation is controlled by the exploratory runner. |
| `scripts/build_knowledge_notes.py` | Builds the versioned author-written knowledge-note corpus. |
| `scripts/build_primary_cases_v2.py` | Constructs the fixed fictional JD/profile pairs. |
| `scripts/freeze_dataset.py` | Creates and verifies data locks. |
| `scripts/build_blind_review_v2.py`, `scripts/finalize_blind_review_v2.py` | Original student-review packet/finalization workflow; not used to certify the exploratory results. |
| `tests/test_smoke.py`, `tests/test_exploratory.py` | Offline behavior tests; no live API call or proof of advice quality. |
| `data/`, `results/` | Fixtures, source/reference provenance, protocols and recorded results; explained in `DATA_AND_EVALUATION.md`. |

## Known rough edges and next decisions

- Exact quotations can still be interpreted incorrectly: negation, weak ownership and transfer across domains need semantic checking.
- The first-line scope rule and English lexical retrieval can miss valid roles or useful passages.
- Domain expertise, experience requirements and work authorization are not separately scored by the fourteen-capability taxonomy. Senior employer examples are capability references, not a personal application shortlist.
- The three real-profile sanity cases were private convenience samples; they do not establish representativeness.
- No product-benefit test was run. A next study should use unseen cases, independent human references and observed preparation decisions.

See the [README](README.md) for setup and runnable commands. This product, code and documentation were developed with Codex assistance; detailed reference provenance is recorded with the evaluation artifacts.
