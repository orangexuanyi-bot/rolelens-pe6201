# RoleLens data and evaluation

## Final dataset

| Artifact | Meaning |
| --- | --- |
| `data/real_role_sources_30.json`, `REAL_ROLE_SOURCES.md` | Thirty verified official employer detail pages, short faithful requirement summaries, source URLs and collection metadata. Fifteen AI and fifteen commercial PM roles from eight employers. |
| `data/real_role_cases_30.jsonl` and lock | Thirty summaries paired deterministically with thirty synthetic profiles; input-only records, no reference gap labels sent to the tested model. |
| `data/real_role_protocol_30.json` | Pairing rule, date, hashes, metrics, chronology and limitations fixed before this phase. |
| `data/ai_reference_real_roles_30.json` and lock | Three Codex-authored reference priorities and reasons per pair, fixed before Gemini predictions. AI-authored reference, not human ground truth. |
| `data/synthetic_profiles/` | Thirty authored synthetic profiles (twenty ordinary, ten challenge cases), generation instructions and deterministic exporter. All thirty used here. |
| `data/knowledge_notes.jsonl` | Thirty author-written notes linked to official sources: twenty AI and ten commercial. Lexical retrieval selects three; no vector database. |
| `results/real_roles_30_20261003/` | Thirty baseline and thirty Gemini result records, reference snapshots, manifests, progress and summaries. |

Requirement summaries are paraphrases of the actual postings, not fictional roles merely linked to companies. Full source pages were inspected and local snapshots retained privately; short attributed summaries are public. Quotes are checked against the supplied summaries, so this check cannot verify that summarization retained every condition. Full employer qualifications, tenure, domain specialization and eligibility remain outside the capability score.

First fifteen sources use odd-positioned profiles, last fifteen use even-positioned profiles. Input and reference hashes are recorded in the protocol and committed at `98997be` before this phase. All profiles were used in prior fictional-JD experiments. This is a new set of real-JD pairs, not a fresh unseen or preregistered holdout. The same assistant family contributed summaries, profiles, taxonomy and references; a different tested model does not make references true.

## Procedure and metrics

1. Read thirty employer pages, summarize requirements, pair profiles and author reference gaps before this phase predictions.
2. Freeze input/reference files and protocol; commit. Snapshot input, reference, knowledge and relevant code hashes per mode.
3. Run one attempt per case and mode, without outcome-driven tuning or successful retries. Preserve failed calls and paid usage.
4. Compute coverage = accepted / 30; case agreement = at least two of three IDs match / 30; individual overlap = matched IDs / 90. Abstentions count as zero overlap.
5. Report accepted-only results alongside coverage. Latency includes each attempted case. Charges are response-reported, not invoices; unavailable cost is unknown.

| Measure, all 30 real-role pairs | Keyword baseline | Gemini |
| --- | ---: | ---: |
| Accepted / attempted | 13/30 (43.3%) | 30/30 (100.0%) |
| Cases matching at least 2 of 3 reference IDs | 7/30 (23.3%) | 19/30 (63.3%) |
| Matched reference IDs, abstention = 0 | 17/90 (18.9%) | 55/90 (61.1%) |
| Median end-to-end latency | 3.865 ms | 7.157 s |
| Response-reported API cost | No external call | US$0.24741375 total; $0.008247/attempt |

The 80% case-agreement threshold was not reached; the +20 percentage-point difference was reached on this AI-reference dataset. Neither establishes an independent correctness target. The observed difference is 40.0 points. The baseline abstained in 17 cases because it could not extract three supported gaps. Natural wording and alias coverage strongly affect this comparison. [Full case-level results](results/real_roles_30_20261003/README.md).

## Personal review and historical experiments

I personally checked the original ten reference cases and accepted all judgments. The check happened after their run; the separate [confirmation](data/student_review_confirmation_20261003.json) applies only to `RLV2F-01..10`. It does not establish a pre-run independent blind review or cover the new thirty reference sets. The instructor's suggested pre-freeze personal-check timing was therefore not followed in the original phase; this is a disclosed methodological limitation.

| Historical phase | Data / results | Status |
| --- | --- | --- |
| Original ten fictional pairs | `primary_cases_v2.jsonl`, `ai_reference_exploratory_v1.json`, `results/exploratory_20261003/` | Baseline 7/10 and Gemini 8/10 case agreement; later personal check of all ten. Input bytes and pending fields preserved for the original lock. |
| Additional twenty fictional pairs | `expansion20_cases.jsonl`, `ai_reference_expansion20.json`, `results/expansion20_20261003/` | Later AI-reference extension, 20/20 attempted in both modes. No student personal-review claim. |
| Historical synthetic pool | `results/evaluation_30_20261003/` | Record-level 10+20 pool; Gemini 27/30 and baseline 7/30 case agreement. Not the final real-role dataset. |

The original `rolelens.cli evaluate` and student finalizer retain their human-review gates. They were not used to certify these AI-reference comparisons. The earlier exposed v1 pilot is excluded. Hashes detect changes but do not independently prove judgment authorship or time.

## Three private real-CV sanity cases

Three supplied CVs were summarized into de-identified English text with explicit permission for OpenRouter/Gemini. Raw CVs stayed local. Originals, summaries and derived personal outputs are excluded from GitHub. Two initial model outputs passed validation; one was truncated and rejected before a documented retry with a larger output cap. Three accepted outputs had 61 literal JD/profile quotations, but qualitative inspection found ownership and semantic-support weaknesses. The baseline returned three gaps for two cases and abstained on one. This convenience slice is qualitative, not an accuracy benchmark, and is separate from the thirty synthetic candidates.

## Reproduce or inspect

Setup is in [README](README.md). A local baseline requires no API credentials:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_real_roles_30.json --cases data\real_role_cases_30.jsonl --case-lock data\real_role_cases_30_lock.json --protocol data\real_role_protocol_30.json --out-dir private\new_real30_baseline
```

For an authorized Gemini rerun, use a private environment variable and a new output directory, then append `--mode ai --allow-external-processing`. The final thirty run at commit `98997be`; manifests record the exact relevant code hashes. UI and document updates after the run do not alter stored evidence. Historical ten-case code is `5c42db7ef5ef0953799fc9b2ed9459631f2097a9`; subsequent cost handling and configurable case-count changes are versioned.

The 23 offline tests check software behavior. Exact quotes, structured fields and valid IDs do not establish correct interpretation. Retrieval relevance, repeat-run stability, subgroup fairness, preparation-time savings and hiring outcomes remain unmeasured. The current abstention is rule-based, not calibrated confidence. See [runner details](scripts/EXPLORATORY_EVALUATION.md) for safe resume and pending-request handling.
