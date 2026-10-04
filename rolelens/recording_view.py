"""One-page, evidence-labeled presenter view for the PE6201 product demo.

The local baseline runs on demand. The Gemini panel reads a committed result
from the completed evaluation; it makes no network call or new AI inference.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from rolelens.pipeline import analyze
from rolelens.taxonomy import BY_ID


CASE_ID = "RLR30-23"


def _load_example(root: Path) -> tuple[dict, dict]:
    cases = (
        json.loads(line)
        for line in (root / "data" / "real_role_cases_30.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    )
    case = next(row for row in cases if row["id"] == CASE_ID)
    saved = json.loads(
        (root / "results" / "real_roles_30_20261003" / "gemini" / f"{CASE_ID}.json")
        .read_text(encoding="utf-8")
    )
    if saved["case_id"] != case["id"] or saved["result"]["status"] != "ok":
        raise ValueError("Presenter example and saved result do not match")
    return case, saved["result"]


def render_recording_view(root: Path, knowledge_path: Path) -> None:
    """Show one authentic PM-role example and the frozen 30-case outcome."""
    case, saved = _load_example(root)
    report = saved["analysis"]

    st.title("RoleLens · Product manager preparation")
    st.caption(
        "One-page course demo · Commercial PM example · The candidate is synthetic; "
        "the employer requirements are summarized from a real listing."
    )

    st.subheader("1 · Inputs")
    st.markdown(
        f"**Role:** {case['jd'].splitlines()[0]} · "
        f"[Official employer listing]({case['jd_source_url']})"
    )
    left, right = st.columns(2)
    with left:
        st.info(
            "**What the role requires**\n\n"
            "Grow free-to-Premium acquisition and activation; use funnel experiments "
            "and cohorts; balance subscriber value with revenue."
        )
    with right:
        st.info(
            "**Candidate RL-P16 (fictional)**\n\n"
            "Built internal factory tools, did field research, and worked with "
            "engineers. The profile has no direct consumer subscription evidence."
        )
    with st.expander("Inspect the exact input texts used in this case"):
        st.text("ROLE REQUIREMENTS SUMMARY\n" + case["jd"])
        st.text("SYNTHETIC CANDIDATE PROFILE\n" + case["profile"])

    st.subheader("2 · Evidence-linked output")
    st.caption(
        "Click once to run the local keyword comparator. The Gemini panel is a "
        "saved result from 3 October 2026, not a live call in this recording."
    )
    if st.button("Run local baseline", type="primary"):
        st.session_state["presenter_baseline"] = analyze(
            case["jd"], case["profile"], knowledge_path, mode="baseline"
        )

    baseline_column, gemini_column = st.columns(2)
    with baseline_column:
        st.markdown("**Local keyword baseline · live, no API**")
        baseline_result = st.session_state.get("presenter_baseline")
        if baseline_result is None:
            st.write("Press the button above to show this case's local result.")
        elif baseline_result["status"] == "abstain":
            st.warning("Abstained: no supported three-gap output.")
        else:
            baseline = baseline_result["baseline"]
            for index, identifier in enumerate(baseline["top_gaps"], 1):
                st.write(f"{index}. {BY_ID[identifier]['label']}")
            st.caption("Keyword evidence is a proxy for experience.")
    with gemini_column:
        st.markdown("**Gemini · saved evaluated result, no new API call**")
        for index, gap in enumerate(report["top_gaps"], 1):
            st.write(f"{index}. {BY_ID[gap['capability_id']]['label']}")
        st.caption("Preparation priorities, not a hiring recommendation.")

    st.markdown("**One evidence link to inspect**")
    evidence = next(
        item for item in report["capabilities"]
        if item["capability_id"] == "GROWTH_LIFECYCLE"
    )
    st.write(f"Role says: “{evidence['jd_quote']}”")
    st.write(
        "Candidate status: " + evidence["profile_status"].replace("_", " ")
        + ". Suggested preparation: " + report["top_gaps"][0]["prep_action"]
    )

    st.subheader("3 · How it works and what the evaluation found")
    st.write(
        "Role summary + anonymized profile → 14-capability taxonomy → "
        "three retrieved public knowledge notes → one Gemini call → "
        "schema and exact-quote checks → ranked preparation gaps or abstention."
    )
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Gemini accepted", "30/30", "Baseline: 13/30")
    metric_b.metric("At least 2 of 3 reference IDs", "19/30", "Baseline: 7/30")
    metric_c.metric("30-call reported cost", "US$0.2474")
    st.caption(
        "Agreement with AI-authored references is not correctness. The 80% "
        "case-agreement target was missed; the keyword baseline abstained 17 times. "
        "The 30 new reference sets were not personally reviewed. "
        "See the repo's data, evals, and report for full method and limitations."
    )
