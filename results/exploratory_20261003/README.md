# Exploratory comparison, 3 October 2026

Ten fictional PM JD/profile pairs were compared against frozen Codex AI-generated references. This is **AI-reference agreement**, not human accuracy. At prediction time there was no student review. The student later confirmed checking all ten AI-drafted reference judgments and accepting them unchanged; see [the separate post-run confirmation](../../data/student_review_confirmation_20261003.json). Historical JSON records remain unchanged, and the comparison is still exploratory AI-reference agreement.

Each mode has the exact reference snapshot, code/input/knowledge hash manifest, ten per-case pipeline records and summary. Outcomes are from one attempt per case; no primary-case prompt tuning or reruns were used. All records contain fictional materials only. Private CVs and credentials are excluded. Original full inputs remain under data; saved per-case records include synthetic evidence excerpts.

The baseline accepted 9/10 and abstained on RLV2F-04; Gemini accepted 10/10. All-case matched IDs are 18/30 and 19/30; at least two of three match in 7/10 and 8/10 cases. Accepted-only mean overlap is 2.0/3 for baseline and 1.9/3 for Gemini. The small aggregate difference does not establish general superiority.

Gemini response-reported cost totals US$0.08174175 across all ten responses, with no missing cost records. Median end-to-end latency is 8,069.285 ms. These costs are not invoices, and these timings are not a production benchmark.

Independent **AI** offline verification recomputed metrics, hashes and retrieval and reran the unchanged quote/schema validator. It confirmed 77 JD, 32 profile and 19 knowledge quotations as literal substrings. This still does not establish semantic support: AI qualitative inspection flagged negative experience interpreted as partial ability, domain-specific safety experience generalized to enterprise permissions, and participation interpreted without enough ownership context. No human semantic correctness rate is claimed.

The runner's code hashes refer to the core code at commit `5c42db7ef5ef0953799fc9b2ed9459631f2097a9`. The later final audit fixed UI cost display on rejection and model-specific price estimation; only the latter changes a core code hash (`rolelens/provider.py`). These fixes were tested offline. All original records, locks and metrics remain unchanged. Reproduction instructions are in ../../scripts/EXPLORATORY_EVALUATION.md. A rerun can differ because model providers are not perfectly deterministic; preserve a new run separately.
