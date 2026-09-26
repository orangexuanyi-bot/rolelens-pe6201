# RoleLens v2 — AI and Commercial Product Manager Role Analysis

RoleLens is an English-language PM career-preparation prototype. It accepts a job description with the **product manager title on the first line** and a fictional or properly authorized anonymized profile. It maps role-relevant product capabilities, highlights three preparation gaps, and links evidence. Its two supported role families are **AI product management** and **commercialization, monetization, subscriptions or ads product management**. It does not assess hiring suitability or require PMs to personally write model, retrieval, backend or algorithm code.

The local comparison is a deliberately simple keyword baseline. An optional Gemini path retrieves three short, author-written notes linked to official documentation, requests structured JSON through OpenRouter, then rejects outputs with invalid IDs or non-exact evidence quotations. This exact-text check cannot establish that an interpretation, profile status or gap ranking is semantically correct. Role scope is a first-line title and topic heuristic; it may reject valid JDs with unusual headings or miss a misleading title. Non-English JDs are outside this prototype's tested scope.

## Current evidence status

| Item | Verified status |
|---|---|
| Code | CLI, Streamlit UI, baseline, PM scope guard, two-family lexical retrieval, optional OpenRouter adapter and deterministic validator implemented. Thirteen offline tests passed on Python 3.12.14 with Streamlit 1.64.0 and pypdf 6.19.0. |
| Primary v2.1 inputs | Ten **new** original fictional JD cards (five AI PM, five commercial PM), paired with ten fictional CVs. Case IDs `RLV2F-01`–`RLV2F-10`, source hashes and taxonomy code hash frozen before any primary prediction. |
| Student reference labels | **PENDING.** The blind packet has full inputs, source URLs and a general taxonomy; all ten `decisions.csv` rows have empty gap, reason, date and reviewer fields. No baseline or model answer is shown. |
| Primary Top-3 agreement, coverage, model comparison | **NOT_RUN / NOT_EVALUABLE** until the student independently completes all ten references and the finalizer locks them. No 80% target or 20-point improvement is claimed as achieved. |
| Independent synthetic API smoke | An AI PM demo call passed structured evidence validation: 635 input tokens, 1,501 output tokens, 15.591 s and OpenRouter response-reported cost US$0.006105. A later commercial PM UI demo returned a validated answer in 6.064 s with response-reported cost US$0.005778. An earlier separate AI demo call was correctly rejected for a nonempty quote under `not_evidenced` despite HTTP success. These are demo observations, not a ten-case benchmark. The latest response-length cap and concision prompt were changed after these demo calls and have not been retested on a public synthetic demo. |
| Real CV sanity slice | **Private, excluded from this repository.** Real personal materials and derived case outputs remain outside Git; `--private-cv` is local baseline only. Sending a real CV to OpenRouter needs separate, specific permission for third-party AI processing. Any findings belong in a private submission appendix, separate from synthetic metrics. |

The submitted problem statement proposed 80% Top-3 Gap Agreement and a 20 percentage-point improvement over a keyword baseline. Those remain targets. The previously exposed AI-only pilot cases and their baseline suggestions were archived outside this repository and are not the primary v2 reference set.

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

The app runs on localhost; use its fictional example for an offline demonstration. The core CLI uses the Python standard library. Streamlit is for the interface and pypdf is only for text-layer local PDF input. `requirements.txt` gives supported dependency ranges; the versions above are the environment in which this snapshot was tested.

For an **independent synthetic-only** OpenRouter demo, set `OPENROUTER_API_KEY` in the process environment using a local secret manager, then run:

```powershell
.\.venv\Scripts\python.exe -m rolelens.cli analyze --jd demo\jd.txt --profile demo\profile.txt --knowledge data\knowledge_notes.jsonl --mode ai --allow-external-processing
Remove-Item Env:OPENROUTER_API_KEY
```

The explicit flag and the Streamlit checkbox authorize the specific API call. A basic contact-detail detector blocks obvious email and phone strings but cannot guarantee anonymity. The program does not write raw profile text, prompts, keys or model responses to disk. OpenRouter and its model provider may process transmitted text under their own policies. Never put a key in source, command arguments, a report, or Git.

The adapter requests `google/gemini-3.7-flash` JSON-schema output. It records token usage, response-reported `usage.cost` when present, and a separately calculated listed-rate estimate. Response cost is preferred for observed spend, but it is not an invoice. Standard listed prices checked 2026-09-26 were US$0.75/M input and US$3.75/M output tokens; the older proposal's US$0.375/M and US$1.875/M figures were batch rates. Failed validation may still incur a provider charge, so usage and cost are retained for such responses.

## Blinded ten-case student review

The primary input file is `data/primary_cases_v2.jsonl`; `data/primary_cases_v2_lock.json` fixes every byte and record hash. `data/primary_protocol_v2.json` records the 5+5 composition, pairing, source-file hashes and taxonomy code hash. The first, pre-evaluation v2.0 freeze was revised for two scope reasons before any prediction or student label: a source role title was corrected to a clear PM posting, and one engineer profile was replaced by an unused product-coordinator profile. Final case IDs are new. Running the build command now only verifies the existing freeze:

```powershell
.\.venv\Scripts\python.exe scripts\build_primary_cases_v2.py
.\.venv\Scripts\python.exe scripts\build_blind_review_v2.py
```

The second command creates `private\review_packet_v2\review_packet.md`, `decisions.csv`, and `packet_manifest.json` on a fresh checkout. It refuses to overwrite an existing decisions file. The packet includes each complete fictional JD and CV, the linked official source role, and the shared 14-ID product capability taxonomy. **It contains no proposed gap answers.** The student must open each source, read all ten input pairs, independently enter three distinct IDs plus an evidence-based reason, their name, and a `YYYY-MM-DD` date. No row is premarked reviewed.

After the student personally completes the ten rows, validate and freeze the private reference:

```powershell
.\.venv\Scripts\python.exe scripts\finalize_blind_review_v2.py --decisions private\review_packet_v2\decisions.csv --packet-manifest private\review_packet_v2\packet_manifest.json
New-Item -ItemType Directory private\results -Force | Out-Null
.\.venv\Scripts\python.exe -m rolelens.cli evaluate --cases private\reviewed_reference_v2\human_reference_cases_v2.jsonl --lock private\reviewed_reference_v2\human_reference_cases_v2_lock.json --knowledge data\knowledge_notes.jsonl --mode baseline > private\results\baseline_v2.json
```

The finalizer checks IDs, blank fields, dates, reasons and frozen input hashes. The evaluator also checks finalizer metadata and exact JD/profile identity before producing predictions. These structural checks **cannot prove** who made the review judgments; the student must attest authorship truthfully. Evaluation on pending `data/primary_cases_v2.jsonl` is blocked in both modes. Do not run generic `analyze` on primary cases before finishing blind review.

If synthetic-input external processing is authorized after reference freeze, the matching AI run is:

```powershell
.\.venv\Scripts\python.exe -m rolelens.cli evaluate --cases private\reviewed_reference_v2\human_reference_cases_v2.jsonl --lock private\reviewed_reference_v2\human_reference_cases_v2_lock.json --knowledge data\knowledge_notes.jsonl --mode ai --allow-external-processing > private\results\ai_v2.json
```

Both modes then use the same ten fictional inputs. The output reports Top-3 set overlap (a case passes with at least two of three IDs matching the student-entered reference), coverage, abstentions, latency and, for model runs, usage and cost. This is **agreement with a limited human-reviewed synthetic reference**, not proof of candidate benefit, skill, job fit or real-world generalization. Ten cases and one reviewer are too small for a robust performance claim.

For a consented and de-identified real CV local sanity check, use `analyze --jd <local PM JD.txt> --private-cv <local CV.txt or PDF> --knowledge data\knowledge_notes.jsonl --mode baseline`. This path prints only aggregate counts, cannot invoke the model and never writes the CV. Image-only PDFs/JPGs require local OCR and careful human redaction first. Do not put CVs or derived text in this repository.

## Data and provenance

- `data/synthetic_jds_v2.json`: ten original fictional PM cards informed by linked public job pages. These are not employer text or live vacancies.
- `data/synthetic_profiles/profiles.json`: 30 original fictional CV-style profiles with generation prompt and deterministic builder; ten are used in the primary set. No real candidate text is included.
- `data/source_manifests/pm_v2_source_candidates.json`: 18 checked official PM posting links (five AI PM and 13 commercial PM possibilities), of which ten inform the cards. The older `jd_sources.json` contains 30 broader PM links; these are URL metadata, **not** 30 collected full JD texts. The four Perplexity links in that older file were API-listed rather than detail-page verified.
- `data/source_manifests/ai_docs.json` and `commercial_knowledge_sources.json`: 20 official AI documentation links and ten official commercial/ads/pricing/measurement links. `data/knowledge_notes.jsonl` indexes **30 author-written short summaries**, not official passages or copied pages. Retrieval filters AI and commercial role families before lexical ranking; a hybrid role reserves a note from each family when matching notes exist.
- `demo/`: separate fictional examples for smoke tests, never primary reference cases.
- `private/`: generated review decisions, finalized reference, outputs and any local personal material; ignored by Git.

This implementation, documentation and fictional fixtures were prepared with GPT-6 Codex assistance. The student must review, explain and attribute the work and personally supply the ten independent reference decisions. Provider observations, offline tests, synthetic reference agreement and any real-CV sanity findings must be reported separately. The repository contains no CapCut App Store review text, real CVs, API credentials, or copied employer JD/article bodies.

Implementation references: [OpenRouter Chat Completions](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request), [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [OpenRouter Gemini 3.7 Flash](https://openrouter.ai/google/gemini-3.7-flash).
