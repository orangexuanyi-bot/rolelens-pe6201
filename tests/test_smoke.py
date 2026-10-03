"""Meaningful offline checks; primary evaluation remains locked pending review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from project_core.evidence import verify_lock, write_lock  # noqa: E402
from rolelens.cli import _evaluate  # noqa: E402
from rolelens.pipeline import analyze  # noqa: E402
from rolelens.provider import DEFAULT_MODEL, call_openrouter  # noqa: E402
from rolelens.retrieval import load_knowledge  # noqa: E402
from rolelens.taxonomy import BY_ID, evidence_for  # noqa: E402
from rolelens.validation import validate_analysis  # noqa: E402
from scripts.finalize_blind_review_v2 import finalize  # noqa: E402


class RoleLensV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ai_jd = (ROOT / "demo" / "jd.txt").read_text(encoding="utf-8")
        cls.ai_profile = (ROOT / "demo" / "profile.txt").read_text(encoding="utf-8")
        cls.commercial_jd = (ROOT / "demo" / "commercial_jd.txt").read_text(encoding="utf-8")
        cls.commercial_profile = (ROOT / "demo" / "commercial_profile.txt").read_text(encoding="utf-8")
        cls.knowledge = ROOT / "data" / "knowledge_notes.jsonl"

    def test_two_independent_offline_demos_use_relevant_notes(self) -> None:
        for jd, profile, bucket, domain in (
            (self.ai_jd, self.ai_profile, "AI_PM", "ai_product"),
            (self.commercial_jd, self.commercial_profile, "COMMERCIAL_PM", "commercial_product"),
        ):
            with self.subTest(bucket=bucket):
                result = analyze(jd, profile, self.knowledge)
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["scope_bucket"], bucket)
                self.assertEqual(len(result["baseline"]["top_gaps"]), 3)
                self.assertEqual(len(result["retrieved_knowledge"]), 3)
                self.assertTrue(all(doc["domain"] == domain for doc in result["retrieved_knowledge"]))
                for item in result["baseline"]["capabilities"]:
                    self.assertIn(item["jd_quote"], jd)
                    if item["profile_quote"]:
                        self.assertIn(item["profile_quote"], profile)

    def test_primary_inputs_are_frozen_and_have_no_reference_labels(self) -> None:
        cases = verify_lock(ROOT / "data" / "primary_cases_v2.jsonl", ROOT / "data" / "primary_cases_v2_lock.json")
        protocol = json.loads((ROOT / "data" / "primary_protocol_v2.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 10)
        self.assertEqual([case["bucket"] for case in cases], ["AI_PM"] * 5 + ["COMMERCIAL_PM"] * 5)
        self.assertEqual([case["id"] for case in cases], protocol["case_ids"])
        self.assertEqual([case["profile_id"] for case in cases], protocol["profile_ids"])
        self.assertTrue(all(case["reference_status"] == "PENDING_STUDENT_REVIEW" for case in cases))
        self.assertTrue(all("reference_gaps" not in case for case in cases))
        self.assertEqual(protocol["taxonomy_sha256_at_freeze"], hashlib.sha256((ROOT / "rolelens" / "taxonomy.py").read_bytes()).hexdigest())

    def test_primary_evaluation_rejects_unreviewed_inputs_before_prediction(self) -> None:
        args = argparse.Namespace(
            cases=ROOT / "data" / "primary_cases_v2.jsonl",
            lock=ROOT / "data" / "primary_cases_v2_lock.json",
            knowledge=self.knowledge,
            mode="baseline",
            allow_external_processing=False,
        )
        with patch("rolelens.cli.analyze", side_effect=AssertionError("Primary prediction was called")):
            with self.assertRaisesRegex(ValueError, "student independently reviews"):
                _evaluate(args)

    def test_self_marked_review_without_decision_fields_is_rejected(self) -> None:
        cases = verify_lock(ROOT / "data" / "primary_cases_v2.jsonl", ROOT / "data" / "primary_cases_v2_lock.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "fake_review.jsonl"
            lock_path = Path(temp_dir) / "fake_review_lock.json"
            for case in cases:
                case["reference_status"] = "human_reviewed"
                case["reference_gaps"] = ["PRODUCT_STRATEGY", "AI_EVALUATION", "MONETIZATION_PRICING"]
            data_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in cases), encoding="utf-8")
            write_lock(data_path, lock_path, dataset_name="RoleLens v2 ten student-reviewed fictional PM references", provenance="Student-entered blind review; see private dated decisions CSV")
            args = argparse.Namespace(cases=data_path, lock=lock_path, knowledge=self.knowledge, mode="baseline", allow_external_processing=False)
            with patch("rolelens.cli.analyze", side_effect=AssertionError("Prediction must not run")):
                with self.assertRaisesRegex(ValueError, "independent-review provenance"):
                    _evaluate(args)

    def test_blind_packet_contains_full_inputs_and_empty_decisions(self) -> None:
        first_case = verify_lock(ROOT / "data" / "primary_cases_v2.jsonl", ROOT / "data" / "primary_cases_v2_lock.json")[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "build_blind_review_v2.py"), "--out-dir", str(out_dir)], cwd=ROOT, check=True, capture_output=True, text=True)
            packet = (out_dir / "review_packet.md").read_text(encoding="utf-8")
            self.assertIn(first_case["jd"], packet)
            self.assertIn(first_case["profile"], packet)
            self.assertIn(first_case["jd_source_url"], packet)
            self.assertNotIn("Baseline candidate Top 3", packet)
            manifest = json.loads((out_dir / "packet_manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(all("candidate_top3" not in item for item in manifest["cases"]))
            with (out_dir / "decisions.csv").open("r", encoding="utf-8-sig", newline="") as handle:
                decisions = list(csv.DictReader(handle))
            self.assertEqual(len(decisions), 10)
            self.assertTrue(all(not row["gap_1"] and not row["review_reason"] for row in decisions))
            with self.assertRaisesRegex(ValueError, "choose three"):
                finalize(out_dir / "decisions.csv", out_dir / "packet_manifest.json", out_dir / "finalized")

    def test_pm_scope_rejects_engineer_title_even_if_body_mentions_pm(self) -> None:
        jd = "Machine Learning Engineer\nWork alongside product managers on AI evaluation and pricing, but the job owns model training and algorithm implementation."
        with patch("rolelens.pipeline.call_openrouter", side_effect=AssertionError("Unexpected API call")):
            result = analyze(jd, self.ai_profile, self.knowledge, mode="ai", allow_external_processing=True)
        self.assertEqual(result["status"], "abstain")
        self.assertIn("NOT_A_PRODUCT_MANAGER_ROLE", result["reason_codes"])

    def test_negated_skill_list_is_not_positive_evidence(self) -> None:
        text = "I did not own pricing, subscriptions, paid conversion experiments, or go-to-market launches."
        self.assertEqual(evidence_for(text, BY_ID["MONETIZATION_PRICING"], ignore_negated=True), [])
        self.assertEqual(evidence_for(text, BY_ID["GO_TO_MARKET"], ignore_negated=True), [])

    def test_external_processing_requires_opt_in_and_redaction(self) -> None:
        with patch("rolelens.pipeline.call_openrouter", side_effect=AssertionError("Unexpected API call")):
            no_consent = analyze(self.ai_jd, self.ai_profile, self.knowledge, mode="ai")
            with_contact = analyze(self.ai_jd, self.ai_profile + "\nContact: person@example.com", self.knowledge, mode="ai", allow_external_processing=True)
        self.assertIn("EXTERNAL_PROCESSING_NOT_AUTHORIZED", no_consent["reason_codes"])
        self.assertIn("PROFILE_CONTACT_DETAILS_DETECTED", with_contact["reason_codes"])

    def test_validator_checks_exact_substrings_but_not_semantic_truth(self) -> None:
        quote = "You will define a product strategy for AI-assisted creative workflows and make prioritization trade-offs with design and engineering partners."
        docs = load_knowledge(self.knowledge)[:1]
        ids = ["PRODUCT_STRATEGY", "AI_PRODUCT_LITERACY", "AI_EVALUATION"]
        report = {
            "summary": "A fictional PM preparation summary.",
            "responsibilities": [{"statement": "Set product direction", "jd_quote": quote}],
            "capabilities": [{"capability_id": identifier, "jd_quote": quote, "profile_status": "not_evidenced", "profile_quote": ""} for identifier in ids],
            "top_gaps": [{"capability_id": identifier, "why_now": "Review the role requirement.", "prep_action": "Prepare a product example."} for identifier in ids],
            "knowledge_citations": [{"doc_id": docs[0]["id"], "quote": docs[0]["text"]}],
            "limitations": ["Exact text checks do not prove a correct interpretation."],
        }
        self.assertEqual(validate_analysis(report, self.ai_jd, self.ai_profile, docs), [])
        report["capabilities"][0]["jd_quote"] = "Fabricated requirement."
        self.assertIn("CAPABILITY_JD_QUOTE", validate_analysis(report, self.ai_jd, self.ai_profile, docs))

    def test_validator_rejects_unhashable_model_fields_without_crashing(self) -> None:
        docs = load_knowledge(self.knowledge)[:1]
        quote = "You will define a product strategy for AI-assisted creative workflows and make prioritization trade-offs with design and engineering partners."
        report = {
            "summary": "A PM summary.",
            "responsibilities": [{"statement": "Set direction", "jd_quote": quote}],
            "capabilities": [
                {"capability_id": ["PRODUCT_STRATEGY"], "jd_quote": quote, "profile_status": "not_evidenced", "profile_quote": ""},
                {"capability_id": "AI_EVALUATION", "jd_quote": quote, "profile_status": ["partial"], "profile_quote": ""},
                {"capability_id": "SAFETY_PRIVACY", "jd_quote": quote, "profile_status": "not_evidenced", "profile_quote": ""},
            ],
            "top_gaps": [{"capability_id": {}, "why_now": "Needed", "prep_action": "Practice"}] * 3,
            "knowledge_citations": [{"doc_id": [docs[0]["id"]], "quote": docs[0]["text"]}],
            "limitations": [],
        }
        errors = validate_analysis(report, self.ai_jd, self.ai_profile, docs)
        self.assertTrue({"CAPABILITY_ID", "PROFILE_STATUS", "GAP_UNSUPPORTED", "CITATION_DOC_ID"}.issubset(errors))

    def test_provider_keeps_usage_when_response_json_is_invalid(self) -> None:
        seen_payload = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps({
                    "model": "mock-model",
                    "choices": [{"message": {"content": "not-json"}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "cost": 0.0003},
                }).encode("utf-8")

        def fake_urlopen(request, timeout):
            self.assertEqual(timeout, 75)
            seen_payload.update(json.loads(request.data.decode("utf-8")))
            return FakeResponse()

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-test-key"}):
            with patch("rolelens.provider.urllib.request.urlopen", side_effect=fake_urlopen):
                answer, meta = call_openrouter(self.ai_jd, self.ai_profile, load_knowledge(self.knowledge)[:3])
        self.assertIsNone(answer)
        self.assertEqual(meta["provider_error"], "OPENROUTER_INVALID_JSON_RESPONSE")
        self.assertEqual(meta["usage"]["total_tokens"], 120)
        self.assertEqual(meta["billed_cost_usd"], 0.0003)
        self.assertTrue(seen_payload["provider"]["require_parameters"])
        self.assertIn("max_completion_tokens", seen_payload)
        self.assertEqual(set(seen_payload["response_format"]["json_schema"]["schema"]["properties"]["top_gaps"]["items"]["properties"]["capability_id"]["enum"]), set(BY_ID))

    def test_provider_rejects_malformed_http_success_body_without_crashing(self) -> None:
        class FakeResponse:
            def __init__(self, body):
                self.body = body

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return self.body

        for body in (b"[]", b"<html>error</html>"):
            with self.subTest(body=body):
                with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-test-key"}):
                    with patch("rolelens.provider.urllib.request.urlopen", return_value=FakeResponse(body)):
                        answer, meta = call_openrouter(self.ai_jd, self.ai_profile, load_knowledge(self.knowledge)[:3])
                self.assertIsNone(answer)
                self.assertEqual(meta["provider_error"], "OPENROUTER_INVALID_RESPONSE")

    def test_provider_estimates_only_a_model_with_verified_rates(self) -> None:
        class FakeResponse:
            def __init__(self, returned_model):
                self.returned_model = returned_model

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps({
                    "model": self.returned_model,
                    "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.0123},
                }).encode("utf-8")

        for requested, returned, expected in (
            (DEFAULT_MODEL, DEFAULT_MODEL, 0.00015),
            ("another/model", "another/model", None),
            (DEFAULT_MODEL, "another/model", None),
        ):
            with self.subTest(requested=requested, returned=returned):
                with patch.dict(os.environ, {"OPENROUTER_API_KEY": "offline-test-key"}):
                    with patch("rolelens.provider.urllib.request.urlopen", return_value=FakeResponse(returned)):
                        _, meta = call_openrouter(self.ai_jd, self.ai_profile, load_knowledge(self.knowledge)[:3], model=requested)
                self.assertEqual(meta["estimated_cost_usd"], expected)
                self.assertEqual(meta["billed_cost_usd"], 0.0123)
                if expected is None:
                    self.assertIn("estimate unavailable", meta["price_basis"])

    @unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit optional dependency not installed")
    def test_streamlit_demo_path(self) -> None:
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        next(button for button in app.button if button.label == "Use synthetic example").click().run()
        next(button for button in app.button if button.label == "Analyze role").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.warning), 0)

    @unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit optional dependency not installed")
    def test_streamlit_rejected_paid_answer_still_shows_cost(self) -> None:
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=20).run()
        next(button for button in app.button if button.label == "Use real role example").click().run()
        app.radio[0].set_value("Gemini semantic analysis").run()
        app.checkbox[0].check().run()
        metadata = {
            "model_requested": "offline-mock",
            "model_returned": "offline-mock",
            "latency_ms": 123.0,
            "billed_cost_usd": 0.0123,
            "estimated_cost_usd": None,
            "provider_error": "OPENROUTER_INVALID_JSON_RESPONSE",
        }
        with patch("rolelens.pipeline.call_openrouter", return_value=(None, metadata)) as provider:
            next(button for button in app.button if button.label == "Analyze role").click().run()
        self.assertEqual(provider.call_count, 1)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("OPENROUTER_INVALID_JSON_RESPONSE", app.warning[0].value)
        self.assertTrue(any("response-reported cost USD 0.0123" in item.value for item in app.caption))


if __name__ == "__main__":
    unittest.main()
