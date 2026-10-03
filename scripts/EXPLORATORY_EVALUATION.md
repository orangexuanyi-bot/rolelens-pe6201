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
`input_file_sha256` matching the selected input file, and
`cases` with all unique `case_id` values required by its protocol and three distinct valid taxonomy
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

`summary.json` reports mean overlap across all selected cases (abstention contributes
zero), the fraction of all cases with at least two overlapping IDs, coverage,
accepted-only agreement, abstention reasons and latency. Response-reported costs
include invalid/abstained responses; unknown costs remain unknown. Per-case files
preserve pipeline output and usage, while omitting raw full input documents.
Checksums detect changes but do not independently prove when labels were created
or who made any judgment. No automated test sends a live API request.

## Custom frozen datasets

Pass `--cases`, `--case-lock` and `--protocol` together. The protocol must define a positive case count and the exact IDs, hashes and frozen taxonomy. All three are mandatory for a custom phase. Defaults retain the historical ten-case inputs. The final dataset uses:

```powershell
.\.venv\Scripts\python.exe -m rolelens.exploratory --references data\ai_reference_real_roles_30.json --cases data\real_role_cases_30.jsonl --case-lock data\real_role_cases_30_lock.json --protocol data\real_role_protocol_30.json --out-dir private\new_real30_baseline
```

`rolelens.pool_exploratory` reproduces the historical 10+20 fictional-role pool; it must not combine the final real-role phase with historical phases because profiles are reused.
