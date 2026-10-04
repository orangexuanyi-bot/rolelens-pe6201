# RoleLens — AI and Commercial Product Manager Preparation

RoleLens compares one product manager job description and one fictional or properly authorized anonymized profile. It links role requirements and profile evidence, then suggests three preparation gaps. Supported target roles are **AI PM and commercialization, monetization, subscription or advertising PM**. A gap means limited evidence for an important requirement; it does not prove missing ability or determine hiring suitability.

The product has a transparent keyword baseline and an optional single-call Gemini path. The AI route retrieves three short author-written source notes, requests structured JSON through OpenRouter, and validates IDs and exact quotations. Literal quotation checks do not establish that the interpretation or ranking is correct. The first-line PM-title scope heuristic can reject unusual valid headings; only English JDs were tested.

## Documentation map

- [Product documentation](PRODUCT_DOCUMENTATION.md): persona, input/output contracts, architecture, design alternatives, module guide, target metrics and observed results.
- [Data and evaluation](DATA_AND_EVALUATION.md): public fixtures, private-data boundaries, reference method, metric definitions, saved results and reproduction.
- [Evaluation runner](scripts/EXPLORATORY_EVALUATION.md): command options, frozen evidence and interrupted-run handling.

## Final evidence as of 3 October 2026

The final experiment uses **30 real employer requirement summaries + 30 synthetic profiles**, 15 AI PM and 15 commercial PM. [Browse all thirty official sources](data/REAL_ROLE_SOURCES.md). The UI can load each source-linked role and its fictional candidate.

| Measure, all 30 real-role pairs | Keyword baseline | Gemini |
| --- | ---: | ---: |
| Accepted / attempted | 13/30 (43.3%) | 30/30 (100.0%) |
| Cases matching at least 2 of 3 reference IDs | 7/30 (23.3%) | 19/30 (63.3%) |
| Matched reference IDs, abstention = 0 | 17/90 (18.9%) | 55/90 (61.1%) |
| Median end-to-end latency | 3.865 ms | 7.157 s |
| Response-reported API cost | No external call | US$0.24741375 total; $0.008247/attempt |

Difference: **40.0 percentage points**. The 80% case-agreement threshold was not reached; the +20 percentage-point difference was reached on this AI-reference dataset. Neither establishes an independent correctness target. These figures are **agreement with AI-authored references, not correctness**. The weak alias baseline abstains frequently on natural phrasing. See [complete results and limitations](results/real_roles_30_20261003/README.md).

- **Software:** 23 offline tests; CLI and Streamlit; lexical retrieval; structured output and quote validation. Tests check behavior, not advice quality.
- **Reference chronology:** new real-role inputs and references frozen at `98997be` before prediction; profiles reused from older tests, so this is not an original unseen holdout.
- **Personal ten-case check:** I checked the original ten reference cases and accepted the judgments unchanged. That check followed the earlier run. [Record](data/student_review_confirmation_20261003.json). It does not apply to the thirty new real-role references.
- **Private sanity slice:** three consented de-identified CV summaries, stored separately and not public.
- **Course handoff:** repository and report are prepared; the student recorded a 4-minute-39-second face-and-screen demonstration on 4 October 2026. The video is held locally for course upload. Final NTULearn submission and receipt remain pending. GitHub publication is not course submission.

Historical fictional-role experiments remain in `results/exploratory_20261003/`, `results/expansion20_20261003/` and `results/evaluation_30_20261003/`; do not combine them with this real-role phase.

## Run locally

Python 3.11+ is required. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m rolelens.cli analyze --jd demo\jd.txt --profile demo\profile.txt --knowledge data\knowledge_notes.jsonl --mode baseline
.\.venv\Scripts\python.exe -m rolelens.cli analyze --jd demo\commercial_jd.txt --profile demo\commercial_profile.txt --knowledge data\knowledge_notes.jsonl --mode baseline
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

The interface runs on localhost. The core CLI uses Python's standard library. Streamlit powers the UI; pypdf supports text-layer PDF input. Tested environment: Python 3.12.14, Streamlit 1.64.0, pypdf 6.19.0. Dependency ranges are in `requirements.txt`.

For a one-page course presentation, open `http://localhost:8501/?demo=1` after starting Streamlit. This view uses the source-linked Spotify subscription PM summary and a synthetic profile. Its single button runs the local baseline; the adjacent Gemini panel reads the saved 3 October result and makes no new API call. The full input texts are available in an expander. This presenter route is not a separate evaluation run.

### Reproduce the final comparison

No credentials are needed for a new baseline run:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_real_roles_30.json --cases data\real_role_cases_30.jsonl --case-lock data\real_role_cases_30_lock.json --protocol data\real_role_protocol_30.json --out-dir private\new_real30_baseline
```

For Gemini, load `OPENROUTER_API_KEY` privately into the process environment, use a new output directory and append `--mode ai --allow-external-processing`. The model receives requirement summaries, synthetic profile text and selected notes, never reference labels. No new call is needed to inspect saved results. Interrupted unknown outcomes block automatic retries. See [runner instructions](scripts/EXPLORATORY_EVALUATION.md).

The provider is `google/gemini-3.7-flash`: structured JSON, temperature 0, 4,000-token output cap. Standard listed rates checked 3 October 2026 were US$0.75/M input and US$3.75/M output. A 10,000/2,000-token scenario is US$0.015 before other costs. Recorded response cost is preferred to the estimate. A paid answer can still fail validation.

## Reference provenance and version history

The final real-role run uses code at commit `98997be`, with relevant module hashes stored in each manifest. Later UI/document changes do not change that evidence. Original ten-case core code is preserved at `5c42db7ef5ef0953799fc9b2ed9459631f2097a9`; later provider cost handling and flexible case-count support explain its different code hashes. Original input/reference/result bytes remain intact.

The original human-reference evaluator and finalizer still reject missing human-review fields. They were not relaxed to certify an independent human benchmark. New experiments use the explicitly AI-reference runner. Hashes establish integrity, not independent proof of authorship or time.

## Data, sources and privacy

- `data/real_role_sources_30.json` and `real_role_cases_30.jsonl`: final source-linked official requirement summaries and thirty input pairs. Employer wording is paraphrased; check full listings for all qualifications.
- `data/synthetic_jds_v2.json`: historical fictional cards, excluded from the final real-role phase.
- `data/synthetic_profiles/profiles.json`: thirty fictional profiles with generation instructions; all thirty used in the final study. No real candidate text.
- `data/source_manifests/pm_v2_source_candidates.json`: eighteen checked PM links informing ten cards. Older manifests contain broader source metadata, not collected JD bodies.
- `data/knowledge_notes.jsonl`: thirty short **author-written** summaries linked to official documents (twenty AI, ten commercial), not official passages. Retrieval filters role family then ranks lexical matches; hybrid roles reserve notes from both families when possible.
- `demo/`: fictional integration examples outside this ten-case study.
- `private/`: ignored local outputs and personal materials. Never commit CVs, summaries, keys or personal model responses.

The explicit CLI flag and UI checkbox control external processing. Email/phone detection is a partial contact-detail guard, not proof of anonymity. Real CV processing requires specific permission for OpenRouter and its provider. The `--private-cv` CLI path permits only the local baseline and prints aggregate counts. The ordinary application does not save inputs; the exploratory harness intentionally saves fictional evidence-bearing results for audit.

This educational prototype, fictional data, AI judgments, tests, evaluation, documentation and draft presentation were prepared with **GPT-6 Codex assistance**. The student remains responsible for reviewing, understanding and attributing the work. There is no measured hiring benefit, semantic correctness rate or deployment readiness claim.

Implementation sources: [OpenRouter Chat Completions](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Gemini 3.7 Flash listing](https://openrouter.ai/google/gemini-3.7-flash).
