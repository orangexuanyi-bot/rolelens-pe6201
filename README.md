# RoleLens — AI and Commercial Product Manager Preparation

RoleLens compares one product manager job description and one fictional or properly authorized anonymized profile. It links role requirements and profile evidence, then suggests three preparation gaps. Supported target roles are **AI PM and commercialization, monetization, subscription or advertising PM**. A gap means limited evidence for an important requirement; it does not prove missing ability or determine hiring suitability.

The product has a transparent keyword baseline and an optional single-call Gemini path. The AI route retrieves three short author-written source notes, requests structured JSON through OpenRouter, and validates IDs and exact quotations. Literal quotation checks do not establish that the interpretation or ranking is correct. The first-line PM-title scope heuristic can reject unusual valid headings; only English JDs were tested.

## Documentation map

- [Product documentation](PRODUCT_DOCUMENTATION.md): persona, input/output contracts, architecture, design alternatives, module guide, target metrics and observed results.
- [Data and evaluation](DATA_AND_EVALUATION.md): public fixtures, private-data boundaries, reference method, metric definitions, saved results and reproduction.
- [Evaluation runner](scripts/EXPLORATORY_EVALUATION.md): command options, frozen evidence and interrupted-run handling.

## Evidence as of 3 October 2026

| Item | Observed status |
| --- | --- |
| Implementation | CLI, Streamlit interface, two-family lexical retrieval, PM scope guard, structured model adapter, deterministic validation, and reproducible evaluation. **20 offline tests passed** after the final cost-reporting fixes. |
| Ten fictional input pairs | Five AI PM and five commercial PM pairs fixed by IDs and hashes on 26 September. Inputs and taxonomy have not changed. |
| Reference judgments | **Codex AI-generated exploratory references**, fixed on 3 October before predictions. Includes reasons, input excerpts, alternatives, and subjective confidence. `human_reviewed=false` records their state at prediction time; see the later review below. |
| Personal ten-case check | **Completed:** I checked all ten cases and accepted the judgments unchanged. The check followed the exploratory run. [Review record](data/student_review_confirmation_20261003.json). |
| Live exploratory comparison | One attempt per case and mode. Results below are **agreement with AI references, not correctness**. Ten Gemini responses passed schema/quote validation; one baseline case abstained. |
| Private CV sanity slice | Three permissioned de-identified summaries processed separately; source CVs, summaries and derived outputs remain outside this repository. |
| Presentation/submission | Report and disclosure accepted. The final 2–8 minute video must show the student's face and screen. Its recording and final course submission remain pending. |

### Exploratory results

| Measure, all ten cases | Keyword baseline | Gemini path |
| --- | ---: | ---: |
| Coverage | 9/10 (90%) | 10/10 (100%) |
| Matched reference IDs, abstention = 0 | 18/30 (60%) | 19/30 (63.3%) |
| Cases matching at least 2 of 3 IDs | 7/10 (70%) | 8/10 (80%) |
| Mean overlap among accepted cases | 2.0/3 | 1.9/3 |
| Median end-to-end latency | 12.985 ms | 8,069.285 ms |
| Response-reported API cost | No external model call | US$0.08174175 total; US$0.008174175/case |

Gemini recovered the baseline abstention but matched fewer reference IDs on three other cases. The case-agreement difference is **10 percentage points**, below the proposal's 20-point improvement target even in this exploratory study. Human-reference targets are not validated by these figures. The assistant family helped generate the fixtures, taxonomy and references; shared assumptions can inflate agreement. Ten subjective cases and one run provide weak evidence of generalization or user value.

See [`data/exploratory_protocol_v1.json`](data/exploratory_protocol_v1.json), [`data/ai_reference_exploratory_v1.json`](data/ai_reference_exploratory_v1.json), and [`results/exploratory_20261003/`](results/exploratory_20261003/). The archive includes manifests, frozen reference snapshots, per-case pipeline results, and summaries. Saved outputs contain **fictional evidence excerpts only**. Rejected calls remain in coverage and cost calculations; missing costs remain unknown. Response-reported costs are not invoices.

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

### Reproduce the exploratory comparison

An independent local baseline run needs no credentials:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_exploratory_v1.json --out-dir private\my_baseline_run
```

For an authorized **fictional-input** model run, load `OPENROUTER_API_KEY` into the process environment using a private secret manager, then enable external processing:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_exploratory_v1.json --out-dir private\my_gemini_run --mode ai --allow-external-processing
Remove-Item Env:OPENROUTER_API_KEY
```

The runner freezes label bytes, input/code/knowledge hashes and settings before predictions. Completed case files are reused on resume. An interrupted request with unknown outcome blocks automatic retry to prevent duplicate charges. Never change labels or code to improve a reported result; use a new version and disclose later iterations. See [`scripts/EXPLORATORY_EVALUATION.md`](scripts/EXPLORATORY_EVALUATION.md).

The provider is `google/gemini-3.7-flash`: structured JSON, temperature 0, 4,000-token output cap. Standard listed rates checked 3 October 2026 were US$0.75/M input and US$3.75/M output. A 10,000/2,000-token scenario is US$0.015 before other costs. Recorded response cost is preferred to the estimate. A paid answer can still fail validation.

## Reference provenance and human validation

`data/primary_cases_v2.jsonl` retains its historical filename and pending human-review fields so the original byte lock remains intact. New AI labels occupy a **separate** artifact. The original `rolelens.cli evaluate` and student finalizer still reject missing human review; neither was relaxed or used to certify this run.

AI-drafted references were fixed before prediction and personally checked by the student afterward, without label changes. The separate review record preserves that chronology; the study does not establish an independent human correctness benchmark. Historical input fields remain intact, and the exposed older v1 pilot is excluded.

## Final audit changes

The recorded model study used core code at commit `5c42db7ef5ef0953799fc9b2ed9459631f2097a9`. The final audit made two later fixes: rejected model answers still display available charges/latency, and models without a verified price table return an unknown estimate instead of inheriting Gemini rates. Twenty offline tests pass. All ten saved AI reports revalidate; all twenty saved result checksums match; the local baseline reproduces the recorded gap sets. No additional paid model run was made for these fixes.

The old manifests intentionally retain the original `rolelens/provider.py` hash. Current code has a different provider hash because of the price-estimation fix; input/reference locks and original result bytes are unchanged. Inspect the named commit for the exact original core code, or use the current commands in a new output directory for a new run.

## Data, sources and privacy

- `data/synthetic_jds_v2.json`: ten original fictional PM cards informed by official role links, not employer wording or live vacancies.
- `data/synthetic_profiles/profiles.json`: thirty fictional profiles with generation instructions; ten used in this study. No real candidate text.
- `data/source_manifests/pm_v2_source_candidates.json`: eighteen checked PM links informing ten cards. Older manifests contain broader source metadata, not collected JD bodies.
- `data/knowledge_notes.jsonl`: thirty short **author-written** summaries linked to official documents (twenty AI, ten commercial), not official passages. Retrieval filters role family then ranks lexical matches; hybrid roles reserve notes from both families when possible.
- `demo/`: fictional integration examples outside this ten-case study.
- `private/`: ignored local outputs and personal materials. Never commit CVs, summaries, keys or personal model responses.

The explicit CLI flag and UI checkbox control external processing. Email/phone detection is a partial contact-detail guard, not proof of anonymity. Real CV processing requires specific permission for OpenRouter and its provider. The `--private-cv` CLI path permits only the local baseline and prints aggregate counts. The ordinary application does not save inputs; the exploratory harness intentionally saves fictional evidence-bearing results for audit.

This educational prototype, fictional data, AI judgments, tests, evaluation, documentation and draft presentation were prepared with **GPT-6 Codex assistance**. The student remains responsible for reviewing, understanding and attributing the work. There is no measured hiring benefit, semantic correctness rate or deployment readiness claim.

Implementation sources: [OpenRouter Chat Completions](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Gemini 3.7 Flash listing](https://openrouter.ai/google/gemini-3.7-flash).
