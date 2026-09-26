# RoleLens synthetic candidate profile generation prompt

This is a **reusable prompt specification** for creating a new version of the fixture. The supplied `profiles.json` was authored by GPT-6 Codex on 2026-09-26 and then checked with `build_profiles.py`; the prompt below is a documented recipe, not a claim that an API batch was run. Any regeneration creates a new dataset version and must be re-reviewed before evaluation.

```text
Create 30 English, fully fictional CV-style candidate profiles for testing an early-career AI Product Manager role-analysis assistant. No actual person, employer, contact detail, CV, or scraped text may be used. Use only fictional candidate IDs RL-P01 through RL-P30. The candidate profile is the input to a system that will later compare it with job descriptions and produce evidence-linked capability analysis and three gaps. Do not create gap labels, fit scores, ideal answers, or job descriptions in this task.

Write 150-300 words in each cv_text, with plausible chronology, specific responsibilities, imperfect but natural evidence, boundaries of ownership, tools, education, and caveats where appropriate. Make them read like varied real-world CV narratives, not a checklist copied from a capability taxonomy. Vary sentence structure, seniority, industries, role titles, and the way evidence is disclosed. Avoid repetitive templates and avoid making every candidate unusually careful or knowledgeable about AI.

Make 20 ordinary profiles spanning product, operations, analytics, design, support, and technical roles. Make 10 deliberate challenge profiles. Include synonym-only evidence; keyword-rich but unevidenced skill lists; adjacent technical or commercial experience without product ownership; a career switch; an attractive metric with unclear attribution; explicit negations such as not deployed; certificate-only claims; research without product release; senior programme management with little hands-on product work; and an AI PM title attached to a thin internship or demo. Some challenge profiles should be genuine partial matches, not all obviously weak.

For every record return id, cohort (normal or hard), variation_tags, synthetic=true, provenance="generated with GPT-6 Codex on 2026-09-26" (change model/date on any future run), license="CC0-1.0; authored for this project", and cv_text. Do not infer protected traits or include names, email addresses, phone numbers, schools, or identifiable organisations. Do not claim that an outcome was measured when it was not. Where a model pilot is described, distinguish candidate contribution from team contribution and prototype from production. Use fictional or generic employer descriptions.

Return a JSON array only. Then run independent checks for 30 unique IDs, 20/10 cohort counts, 150-300 words each, text uniqueness, parse validity, and absence of unintended personal data. Human-review the content for accidental taxonomy mirroring and unrealistic uniformity. Freeze the file and hash it before any evaluation run.
```

## Use in the evaluation

These profiles carry **no ground-truth fit or gap labels**. The role and the specific job description determine what is relevant. Only after the job-description set is frozen should a separate human review process label a selected case sample. A second model can draft reference answers but is not ground truth; a person should check at least ten reference cases before freezing, in line with the instructor's feedback.
