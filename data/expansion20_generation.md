# RoleLens expansion20 generation notes

- Date: 2026-10-03, user-facing Asia/Shanghai date.
- Author: Codex AI, GPT-6 Codex family. No student authorship or review is claimed for these new twenty judgments.
- Status: root checked all 60 judgment quotations, capability IDs, PM scope, unchanged profile text, and 30 unique-profile coverage; frozen before expansion predictions. Public locks/protocol are authoritative.
- Case IDs: RLX20-01 through RLX20-20. Role-card IDs: PMJDX01 through PMJDX20.
- Target job families: ten AI PM and ten commercial PM. All target roles are product-management roles. Some candidates have engineering, research, administration, or executive histories, deliberately testing transfer and title/keyword false positives.
- Every one of the twenty profiles unused by the original ten cases is used exactly once. Profile text is byte-for-byte the `cv_text` string from the committed profiles.json. The original ten inputs and their references have not been changed.
- Each new job description is an original fictional role card. No external job description was fetched, copied, attributed, or claimed to be source-checked. Empty source URLs are intentional; `jd_provenance.external_job_source_used` is false.
- Inputs consulted: rolelens/taxonomy.py, data/synthetic_profiles/profiles.json, data/synthetic_jds_v2.json, data/primary_cases_v2.jsonl (used-profile IDs and input schema), and the old AI-reference schema/example. No saved baseline/Gemini predictions or evaluation metrics were read, and no application/pipeline/evaluation call was run.
- No API, credentials, real CV, or public repo file was accessed for mutation. The output authoring script writes only work/expansion20_* drafts.
- References were selected from the supplied text before any expansion20 prediction. Each contains three distinct IDs, an exact JD quotation and profile quotation for each, a Chinese explanation, a plausible alternative, and medium qualitative confidence.
- References and JDs are not independent human labels: a shared assistant family authored these materials. We did not tune inputs or labels to improve observed model results. The pairings are purposive examples designed to expose at least three important preparation gaps, so the synthetic distribution is not a market-representative sample.
- Root should validate all exact quotes, IDs, profile coverage, and target role families, freeze hashes before predictions, and report this extension separately from the earlier ten before any pooled 30-case summary. The later extension must not be backdated or described as the original preregistered held-out set.

## Pairing table

| Case | Family | Profile | Reference IDs |
|---|---|---|---|
| RLX20-01 | AI_PM | RL-P02 | AI_EVALUATION, METRICS_EXPERIMENTATION, MONETIZATION_PRICING |
| RLX20-02 | AI_PM | RL-P04 | AI_PRODUCT_LITERACY, METRICS_EXPERIMENTATION, GO_TO_MARKET |
| RLX20-03 | AI_PM | RL-P06 | AI_PRODUCT_LITERACY, MONETIZATION_PRICING, GROWTH_LIFECYCLE |
| RLX20-04 | AI_PM | RL-P08 | SAFETY_PRIVACY, MONETIZATION_PRICING, COMMERCIAL_PARTNERSHIPS |
| RLX20-05 | AI_PM | RL-P10 | AI_PRODUCT_LITERACY, AI_EVALUATION, METRICS_EXPERIMENTATION |
| RLX20-06 | AI_PM | RL-P18 | PRODUCT_STRATEGY, MONETIZATION_PRICING, GO_TO_MARKET |
| RLX20-07 | AI_PM | RL-P23 | USER_DISCOVERY, PRODUCT_STRATEGY, PRIORITIZATION |
| RLX20-08 | AI_PM | RL-P27 | USER_DISCOVERY, PRIORITIZATION, AI_EVALUATION |
| RLX20-09 | AI_PM | RL-P28 | USER_DISCOVERY, PRODUCT_STRATEGY, PRIORITIZATION |
| RLX20-10 | AI_PM | RL-P30 | AI_EVALUATION, SAFETY_PRIVACY, AI_PRODUCT_LITERACY |
| RLX20-11 | COMMERCIAL_PM | RL-P01 | PRODUCT_STRATEGY, MONETIZATION_PRICING, GO_TO_MARKET |
| RLX20-12 | COMMERCIAL_PM | RL-P03 | ADS_ECOSYSTEM, MONETIZATION_PRICING, COMMERCIAL_PARTNERSHIPS |
| RLX20-13 | COMMERCIAL_PM | RL-P05 | MONETIZATION_PRICING, METRICS_EXPERIMENTATION, GROWTH_LIFECYCLE |
| RLX20-14 | COMMERCIAL_PM | RL-P07 | MONETIZATION_PRICING, GO_TO_MARKET, COMMERCIAL_PARTNERSHIPS |
| RLX20-15 | COMMERCIAL_PM | RL-P09 | PRODUCT_STRATEGY, MONETIZATION_PRICING, GO_TO_MARKET |
| RLX20-16 | COMMERCIAL_PM | RL-P16 | MONETIZATION_PRICING, COMMERCIAL_PARTNERSHIPS, METRICS_EXPERIMENTATION |
| RLX20-17 | COMMERCIAL_PM | RL-P17 | MONETIZATION_PRICING, ADS_ECOSYSTEM, METRICS_EXPERIMENTATION |
| RLX20-18 | COMMERCIAL_PM | RL-P19 | MONETIZATION_PRICING, COMMERCIAL_PARTNERSHIPS, METRICS_EXPERIMENTATION |
| RLX20-19 | COMMERCIAL_PM | RL-P20 | MONETIZATION_PRICING, COMMERCIAL_PARTNERSHIPS, GO_TO_MARKET |
| RLX20-20 | COMMERCIAL_PM | RL-P29 | USER_DISCOVERY, ADS_ECOSYSTEM, DATA_DECISIONS |

## Authoring validation

- 20 cases, 10 per family; 20 unique profiles; no overlap with the original ten.
- All 60 JD quotations and 60 profile quotations are exact substrings.
- All new profile strings exactly equal the committed source profiles.
- Input draft SHA256: `40ba0eac80e6f7e164f7fdd8dd42c610ef8b0122fff594cb3dcbb29bc74c595f`.

## Public frozen artifacts

See `expansion20_cases.jsonl`, `expansion20_cases_lock.json`, `expansion20_protocol.json`, `ai_reference_expansion20.json`, and `ai_reference_expansion20_lock.json`. The draft hash above identifies the pre-freeze draft only; final hashes are in the public protocol. This expansion is a later phase, not the original preregistered 30-case experiment.
