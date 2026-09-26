"""Local RoleLens interface: streamlit run streamlit_app.py."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from rolelens.pipeline import analyze
from rolelens.taxonomy import BY_ID

ROOT = Path(__file__).resolve().parent
KNOWLEDGE = ROOT / "data" / "knowledge_notes.jsonl"

st.set_page_config(page_title="RoleLens", page_icon="🔎", layout="wide")
st.title("RoleLens")
st.caption("English-language AI and commercial product manager role preparation with evidence links. Put the PM title on the first JD line. This prototype supports candidate preparation, not hiring decisions.")

with st.expander("Load fictional demonstration inputs"):
    if st.button("Use synthetic example"):
        st.session_state["jd"] = (ROOT / "demo" / "jd.txt").read_text(encoding="utf-8")
        st.session_state["profile"] = (ROOT / "demo" / "profile.txt").read_text(encoding="utf-8")

left, right = st.columns(2)
with left:
    jd = st.text_area("Product manager job description", key="jd", height=300, placeholder="Paste an AI PM or commercialization, monetization, or ads PM description")
with right:
    profile = st.text_area("Anonymized profile evidence", key="profile", height=300, placeholder="Paste evidence bullets without contact details")

mode = st.radio("Analysis mode", ["Local keyword baseline", "Gemini semantic analysis"], horizontal=True)
use_ai = mode.startswith("Gemini")
if use_ai:
    st.info("Gemini mode sends the JD, anonymized profile and three curated knowledge notes to OpenRouter. Use only material you have permission to send.")
    consent = st.checkbox("I have permission to send this anonymized profile to OpenRouter for this analysis")
else:
    consent = False

if st.button("Analyze role", type="primary"):
    with st.spinner("Analyzing role..."):
        result = analyze(jd, profile, KNOWLEDGE, mode="ai" if use_ai else "baseline", allow_external_processing=consent)
    if result["status"] == "abstain":
        st.warning("No validated analysis was returned. " + ", ".join(result["reason_codes"]))
    baseline = result.get("baseline")
    if baseline:
        with st.expander("Deterministic keyword baseline", expanded=not use_ai):
            st.caption(baseline["limitation"])
            if baseline["top_gaps"]:
                st.write("**Top preparation gaps by keyword rule**")
                for identifier in baseline["top_gaps"]:
                    st.write("• " + BY_ID[identifier]["label"])
            for item in baseline["capabilities"]:
                st.markdown(f"**{item['label']}** — {item['profile_status'].replace('_', ' ')}")
                st.caption("JD evidence: " + item["jd_quote"])
                if item["profile_quote"]:
                    st.caption("Profile evidence: " + item["profile_quote"])
    report = result.get("analysis")
    if report:
        st.subheader("AI analysis")
        st.write(report["summary"])
        st.write("**Top three preparation gaps**")
        for gap in report["top_gaps"]:
            st.markdown(f"**{BY_ID[gap['capability_id']]['label']}** — {gap['why_now']}")
            st.caption("Preparation: " + gap["prep_action"])
        with st.expander("Evidence and source notes"):
            for item in report["capabilities"]:
                st.markdown(f"**{BY_ID[item['capability_id']]['label']}** — {item['profile_status']}")
                st.caption("JD: " + item["jd_quote"])
                if item["profile_quote"]:
                    st.caption("Profile: " + item["profile_quote"])
            for item in report["knowledge_citations"]:
                st.markdown(f"[{item['title']}]({item['url']}) (accessed {item['accessed_at']})")
                st.caption("Curated note: " + item["quote"])
        st.caption("Limitations: " + " ".join(report["limitations"]))
        st.caption("Quote validation checks exact text occurrence, not whether the interpretation or ranking is correct.")
        metadata = result.get("model_run", {})
        if metadata:
            cost = metadata.get("billed_cost_usd")
            cost_label = f"response-reported cost USD {cost}" if cost is not None else f"listed-rate estimate USD {metadata.get('estimated_cost_usd')}"
            st.caption(f"Model: {metadata.get('model_returned') or metadata['model_requested']} · latency {metadata['latency_ms']} ms · {cost_label}")
