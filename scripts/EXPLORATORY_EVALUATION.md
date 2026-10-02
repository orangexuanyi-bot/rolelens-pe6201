# Separate AI-reference exploration

This runner measures agreement with **Codex AI-generated labels**, not human
accuracy or correctness. It does not run the original human-reviewed primary
evaluation, finalize student decisions, or change the pending source records.
AI references are not ground truth; shared model assumptions may inflate agreement.

From the repository root, with Python 3.11 or later:

```powershell
python -m rolelens.exploratory --references PATH_TO_AI_REFERENCE.json --out-dir private/exploratory_baseline
```

The default is the local keyword baseline. An external run still requires the
existing `OPENROUTER_API_KEY` environment variable and explicit consent:

```powershell
python -m rolelens.exploratory --references PATH_TO_AI_REFERENCE.json --out-dir private/exploratory_ai --mode ai --allow-external-processing
```

The reference JSON must contain `reference_kind: "ai_generated_exploratory"`,
`human_reviewed: false`, `producer: "Codex AI"`, an ISO `generated_date`,
`input_file_sha256` matching the original `data/primary_cases_v2.jsonl`, and
`cases` with all ten unique `case_id` values and three distinct valid taxonomy
IDs in each `gap_ids` list. Reasons and evidence annotations may be included.
Do not add human reviewer fields or assert a human-reviewed status.

Before prediction, the runner saves the exact reference bytes and a manifest
with source-input, input-lock, protocol, knowledge and code hashes. Run directories
are specific to one reference artifact and one mode/model. Completed case files
are written atomically and hash-checked on resume; rerunning the same command
reuses them. An interrupted request leaves a `.pending.json` marker. If it has no
completed result, the runner stops because the charge/outcome may be unknown.
Preserve that marker and investigate rather than automatically issuing a duplicate
request. Recovery of an already durable result safely clears its leftover marker.

`summary.json` reports mean overlap across all ten cases (abstention contributes
zero), the fraction of all cases with at least two overlapping IDs, coverage,
accepted-only agreement, abstention reasons and latency. Response-reported costs
include invalid/abstained responses; unknown costs remain unknown. Per-case files
preserve pipeline output and usage, while omitting raw full input documents.
Checksums detect changes but do not independently prove when labels were created
or who made any judgment. No automated test sends a live API request.
