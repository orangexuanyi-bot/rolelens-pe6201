# Final evaluation: thirty real employer requirement pairs

**30/30 attempts completed in each mode on 3 October 2026.** One attempt per case, no score-driven retries or label changes. The inputs are faithful summaries of thirty official employer PM listings, paired with thirty synthetic profiles. Reference labels are AI-authored and frozen before this phase at commit `98997be`; results measure agreement, not correctness.

| Measure, all 30 real-role pairs | Keyword baseline | Gemini |
| --- | ---: | ---: |
| Accepted / attempted | 13/30 (43.3%) | 30/30 (100.0%) |
| Cases matching at least 2 of 3 reference IDs | 7/30 (23.3%) | 19/30 (63.3%) |
| Matched reference IDs, abstention = 0 | 17/90 (18.9%) | 55/90 (61.1%) |
| Median end-to-end latency | 3.865 ms | 7.157 s |
| Response-reported API cost | No external call | US$0.24741375 total; $0.008247/attempt |

The case-agreement difference is **40.0 percentage points**. The 80% case-agreement threshold was not reached; the +20 percentage-point difference was reached on this AI-reference dataset. Neither establishes an independent correctness target.

Baseline abstentions reflect its limited alias coverage: it could not find three supported gap IDs in 17 cases. This weak comparator, summary wording and shared author framing limit any superiority claim. Accepted-only mean overlap was 1.308/3 for baseline and 1.833/3 for Gemini; read this alongside coverage.

## Inspect the evidence

- [Real sources](../../data/REAL_ROLE_SOURCES.md), [requirements and source metadata](../../data/real_role_sources_30.json), [inputs](../../data/real_role_cases_30.jsonl).
- [Protocol](../../data/real_role_protocol_30.json), [AI references](../../data/ai_reference_real_roles_30.json).
- [Baseline summary](baseline/summary.json), [Gemini summary](gemini/summary.json). Each directory also contains the exact reference snapshot, run manifest, progress record and 30 individual results.
- Coverage = accepted / 30; case agreement = at least two IDs match / 30; individual overlap = matched IDs / 90. Abstentions remain zero-overlap observations. Available charges for rejected outputs remain in the cost total; missing charges are unknown, not zero. Recorded costs are provider-response reports, not invoices.

## Chronology and limits

This final phase was added after fictional-JD experiments of ten and then twenty cases. It reuses those synthetic profiles with new real-requirement pairings, so it is not an originally preregistered thirty-case unseen holdout. References, profiles and taxonomy share Codex authorship; Gemini is the tested model. All references were fixed before this phase predictions. No personal review is claimed for these thirty new reference sets.

The student personally checked the original ten cases and accepted their labels after that earlier run; the [separate confirmation](../../data/student_review_confirmation_20261003.json) remains scoped to `RLV2F-01..10`. Three private real-CV sanity cases are qualitative and excluded from these denominators.

The sample is English, senior-heavy and curated from eight employers. The capability taxonomy does not score specialist scientific/security expertise, tenure or legal eligibility. Exact quotation checks validate occurrence in summaries and profiles, not the quality of interpretation or advice. No hiring benefit or measured preparation-time saving is claimed.

## Qualitative disagreement audit

In RLR30-11 (Human Data Platform), the three reference priorities and Gemini priorities had zero overlap. The model mapped vendor coordination to commercial partnerships, which may overstate the requirement. In RLR30-16 (Advertising), the reference itself may overextend campaign performance into monetization/pricing. These are disputed interpretations requiring independent adjudication, not evidence that every non-match is a model error. Frozen references were not changed after predictions.

Offline audit: 60 payload checksums verified; both summary computations reproduced; all 30 baseline predictions reproduced; all 30 accepted AI reports revalidated, including 232 JD, 88 profile and 52 knowledge-note literal quotations. See `offline_audit.json`. Text occurrence still does not establish semantic support.
