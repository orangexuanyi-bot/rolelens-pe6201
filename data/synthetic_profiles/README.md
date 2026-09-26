# RoleLens synthetic candidate-profile fixture

`profiles.json` contains 30 fictional English CV-style profiles, 20 ordinary and 10 challenge cases. Each record is 181-210 words. All profiles were authored for this project with GPT-6 Codex on 2026-09-26, are marked `synthetic`, and are offered under CC0-1.0. The data contains no real candidate CVs and was not scraped. The record ID is a fictional identifier, not a name.

The content follows the submitted RoleLens problem statement: a JD plus a candidate profile enters the system; RoleLens returns evidence-linked requirements, matches, and three gaps. The profiles alone do not establish a correct gap ranking. This fixture intentionally includes indirect evidence, omitted evidence, mixed outcomes, and ownership caveats so an evaluator cannot rely on title or keyword overlap alone.

## Files

- `profiles.json`: versioned data records for evaluation. The `cv_text` is the sole candidate input; metadata should be kept out of model prompts unless a test explicitly needs it.
- `build_profiles.py`: editable source and deterministic JSON export. Run it to recreate `profiles.json` without any network or model call.
- `GENERATION_PROMPT.md`: reusable generation recipe and validation rules for a future version.

## Rebuild and verify

```powershell
python .\build_profiles.py
python -m json.tool .\profiles.json > $null
```

The builder asserts unique IDs and text hashes, 20/10 cohort counts, and 150-300 words per `cv_text`; each JSON record stores the resulting word count and SHA-256 of its text. For evaluation, first freeze the JSON file hash and JD inputs, then make a separate JD/profile pairing manifest and human-reviewed reference set. Do not represent the synthetic profiles as the 3-5 real anonymised CV sanity slice recommended by the instructor. Any such real CVs need the owner's consent, de-identification, private storage, and separate reporting.

## Record fields

`id`, `cohort`, `variation_tags`, `synthetic`, `provenance`, `license`, `cv_text`, `word_count`, `sha256_cv_text`.

Challenge tags are dataset-design metadata, not reference fit labels. They can be used to stratify an error review but must not be included in model input for ordinary performance runs.
