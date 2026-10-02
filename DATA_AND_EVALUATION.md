# RoleLens data and evaluation guide

This file explains what the public data means, how it was evaluated, and how to inspect or reproduce the evidence. It accompanies the [product documentation](PRODUCT_DOCUMENTATION.md) and [setup commands](README.md).

## Public data inventory

| Artifact | Count and purpose | Origin and restrictions |
| --- | --- | --- |
| `data/synthetic_jds_v2.json` | Ten fictional PM role cards: five AI and five commercial roles. | Original wording informed by ten official PM posting links; not scraped employer JD bodies or live vacancy claims. |
| `data/source_manifests/pm_v2_source_candidates.json` | Eighteen checked PM source links informing the ten cards. | URLs and author-written metadata, with source/check dates. |
| `data/source_manifests/jd_sources.json` | Thirty earlier background posting links. | A source manifest, not thirty collected JDs or thirty evaluated cases. |
| `data/synthetic_profiles/profiles.json` | Thirty fictional English profiles: twenty ordinary and ten challenge records; ten selected for evaluation. | GPT-6 Codex-authored fixture, CC0-1.0 as recorded per profile. No real candidate text. |
| `data/synthetic_profiles/GENERATION_PROMPT.md` | Generation recipe and constraints. | Documents authoring instructions; does not claim a separate API batch produced the fixture. |
| `data/synthetic_profiles/build_profiles.py` | Deterministic fixture export and checks. | Recreates the supplied version from authored source records without a model call. |
| `data/knowledge_notes.jsonl` | Thirty short notes: twenty AI and ten commercial/ads. | Author-written summaries linked to official documentation, not official quoted passages. |
| `data/source_manifests/ai_docs.json`, `commercial_knowledge_sources.json` | The thirty knowledge-source links and metadata. | Source dates are retained; websites may change. |
| `data/primary_cases_v2.jsonl` | Ten fixed JD/profile pairs, `RLV2F-01` through `RLV2F-10`. | Fixed before predictions; historical human-review fields remain unchanged. |
| `data/primary_cases_v2_lock.json`, `primary_protocol_v2.json` | Input IDs, byte/record hashes and original pairing protocol. | Integrity evidence and historical plan, not a completed independent human experiment. |
| `data/ai_reference_exploratory_v1.json` and its lock | Three capability IDs per case, exact excerpts, rationale, alternatives and confidence. | Codex-drafted reference judgments fixed before prediction; the at-run `human_reviewed=false` state is preserved. |
| `data/student_review_confirmation_20261003.json` | Student's confirmed personal check and acceptance of all ten reference sets, with zero changes. | Separate confirmation after the exploratory run; no backdating or replacement of frozen run artifacts. |
| `data/exploratory_protocol_v1.json` | Run rules and metric definitions. | Fixed exploratory design; historical statements describe the state when the run began. |
| `demo/` | Two fictional integration examples. | Separate from the ten-case comparison. |

From each fixture, only the JD and profile texts enter the model request, together with the three selected knowledge notes. Fixture challenge tags and reference IDs are excluded. Source manifests contain links and metadata, not redistribution of restricted third-party articles or job descriptions. See the source-specific [manifest notes](data/source_manifests/README.md) and [profile notes](data/synthetic_profiles/README.md).

## Private sanity slice

Three supplied CVs were summarized into de-identified English text, with explicit permission for OpenRouter/Gemini processing. Raw CVs stayed local. Neither the originals, summaries nor personal model responses are published here. The public fictional fixtures allow the repository to run without private data.

Two initial AI responses passed validation. One initial response was truncated at a 2,500-token cap and rejected; a documented retry with a 4,000-token cap and concise-output instruction passed. The three accepted responses contained 61/61 checked literal JD/profile quotations, but AI qualitative inspection found weak semantic support and blurred individual/team ownership. The local baseline returned three gaps on two cases and abstained on one. This is a small qualitative sanity check with no reference accuracy estimate. No private-case content is required to reproduce the public study.

## Exploratory evaluation procedure

1. Fix the ten fictional input pairs and common capability taxonomy. The input SHA-256 is `0943cbe3daa2c348082553acc3b3ab47c49aa85bc8679868317ffe5814f68a2e`.
2. Draft and check three reference IDs per case with evidence before predictions. The reference SHA-256 is `11afd47863c48bcdf6358c16062b27ac28792343b01fdda02063bac988911f29`.
3. Snapshot references, protocol, inputs, knowledge and relevant code hashes. Run one baseline attempt and one Gemini attempt per case, with no result-driven retuning or retries.
4. Apply the same production quote/schema validator to AI outputs. Retain failures and abstentions in the denominator and available charges in cost.
5. Save each result atomically, then summarize all ten cases. Completed cases are reused on resume; a request with an unknown interrupted outcome is not automatically repeated.
6. Record the student's later personal check separately. I personally checked all ten reference cases and accepted their three capability IDs without changes. The check followed the exploratory run; it does not supply an independent pre-run human benchmark.

The reference producer and fixture/taxonomy author share the Codex assistant family, while Gemini is the tested model. That difference does not make the references ground truth. The original plan for 30 independently reviewed held-out cases was reduced to a ten-case exploratory study. The historical primary evaluator and blind-review finalizer were not used for this comparison. The exposed earlier v1 pilot is excluded.

## Metric definitions and results

For case `i`, let `r_i` be the three reference IDs and `p_i` the accepted three predicted IDs. If a run abstains, its overlap is zero.

- **Coverage:** accepted complete outputs / all ten cases.
- **Individual gap overlap:** sum of `|r_i intersect p_i|` / 30.
- **Case agreement:** number of cases with overlap at least two / all ten cases.
- **Accepted-only overlap:** total overlapping IDs / accepted cases; always read alongside coverage.
- **Latency:** measured end-to-end pipeline time per attempted case.
- **Cost:** sum of response-reported API charges, including available charges for rejected responses. Missing cost stays unknown. This is not an invoice.

| Measure | Keyword baseline | Gemini |
| --- | ---: | ---: |
| Accepted / attempted | 9/10 | 10/10 |
| Abstained / attempted | 1/10 | 0/10 |
| Case agreement, at least 2 of 3 | 7/10 (70%) | 8/10 (80%) |
| Individual gap overlap | 18/30 (60%) | 19/30 (63.3%) |
| Mean overlap across all cases | 1.8/3 | 1.9/3 |
| Mean overlap among accepted cases | 2.0/3 | 1.9/3 |
| Median latency | 12.985 ms | 8,069.285 ms |
| Total response-reported API cost | No external call | US$0.08174175 |

The proposed improvement target was at least 20 percentage points. The observed improvement was 10 points, and the dataset/reference design differs from the proposal. Consequently, the original target is not achieved or validated. The baseline abstained on `RLV2F-04` because fewer than three candidate gaps were available under its rule. This abstention does not establish what a forced third answer would have been or whether it would have been wrong.

Gemini recovered that abstention but matched fewer reference IDs on three other cases. Ten cases mean one changed case moves the headline by ten percentage points. The result does not establish a reliable superiority claim, correctness rate, hiring benefit or user value.

## Saved results and how to inspect them

`results/exploratory_20261003/` contains separate `baseline/` and `gemini/` directories:

| File | What to inspect |
| --- | --- |
| `manifest.json` | Mode/model/settings and hashes of source inputs, locks, protocol, references, knowledge and code at run time. |
| `reference_snapshot.json` | The exact reference snapshot used by that run. |
| `RLV2F-01.json` through `RLV2F-10.json` | Per-case pipeline result, status, baseline, retrieved note IDs, accepted analysis when available, usage/cost and payload checksum. Evidence excerpts are fictional. |
| `summary.json` | All-case and accepted-only metrics, failure reasons, cost coverage, latency and per-case overlap. |

The software and results were produced with Codex assistance. Run-time files retain historical provenance; the dated student confirmation documents the later personal review. Hashes detect byte changes but do not independently prove when a judgment was made or by whom.

### Reproduce locally

From the repository root after the README setup:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_exploratory_v1.json --out-dir private\new_baseline_run
```

An authorized fictional-input Gemini rerun additionally needs `OPENROUTER_API_KEY` in the process environment and explicit external-processing consent:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_exploratory_v1.json --out-dir private\new_gemini_run --mode ai --allow-external-processing
Remove-Item Env:OPENROUTER_API_KEY
```

A fresh paid run is optional: inspect the committed records to review the original observations. Live outputs may differ because the remote service can change. Use a new result directory for a new experiment. See [runner behavior](scripts/EXPLORATORY_EVALUATION.md) for interruption and resume rules. Do not edit the original labels or results to improve scores.

Original run core code is preserved at commit `5c42db7ef5ef0953799fc9b2ed9459631f2097a9`. The later final audit fixed UI cost display for rejected answers and model-specific price estimation. The provider hash in a new run will therefore differ from the original manifest; original manifest hashes were verified against the named historical commit. These cost-handling fixes were tested offline, without rerunning the paid study.

## Quality checks and remaining limitations

The final audited code passed 20 offline tests (18 before the two cost-reporting regressions were added). Recorded AI outputs were revalidated offline: 77 JD quotes, 32 profile quotes and 19 knowledge-note quotes were exact substrings. Those checks establish text occurrence, not correct interpretation. AI qualitative review still identified negated experience used as positive partial evidence, overly broad transfer of safety evidence, and insufficient ownership caveats.

Retrieval relevance, independent human correctness, subgroup fairness and preparation-time savings remain unmeasured. The system has no calibrated confidence score; its current abstention is triggered by explicit rules, insufficient retrieval or failed validation. Improving semantic checking requires a new documented version and evaluation, while preserving this run as evidence.
