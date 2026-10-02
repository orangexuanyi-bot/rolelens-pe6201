"""Offline provenance, denominator and no-repeat-spend checks for exploration."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from project_core.evidence import verify_lock, write_lock  # noqa: E402
from rolelens.exploratory import CASES, LOCK, _exclusive_run, agreement_metrics, evaluate  # noqa: E402
from rolelens.pool_exploratory import pool_runs  # noqa: E402
from rolelens.taxonomy import BY_ID  # noqa: E402


class ExploratoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reference = self.root / "ai_reference.json"
        self.output = self.root / "run"
        self.ids = list(BY_ID)[:4]
        self.payload = {
            "reference_kind": "ai_generated_exploratory",
            "human_reviewed": False,
            "producer": "Codex AI",
            "generated_date": "2026-10-03",
            "input_file_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
            "cases": [{"case_id": row["id"], "gap_ids": self.ids[:3], "reason": "Offline test fixture only"}
                      for row in verify_lock(CASES, LOCK)],
        }
        self.write_reference(self.payload)

    def write_reference(self, payload):
        self.reference.write_text(json.dumps(payload), encoding="utf-8")

    def result(self, *, accepted=True, cost=0.02):
        return {
            "status": "ok" if accepted else "abstain",
            "reason_codes": [] if accepted else ["OPENROUTER_INVALID_JSON_RESPONSE"],
            "baseline": {"abstained": False, "top_gaps": self.ids[:3]},
            "analysis": {"top_gaps": [{"capability_id": item} for item in self.ids[:3]]} if accepted else {},
            "model_run": {"billed_cost_usd": cost, "estimated_cost_usd": 0.01,
                          "usage": {"prompt_tokens": 10, "completion_tokens": 20}},
        }

    def custom_phase(self, count=20, *, repeated_profile=False, unsafe_id=False):
        source = self.root / "expansion.jsonl"
        lock = self.root / "expansion_lock.json"
        protocol = self.root / "expansion_protocol.json"
        reference = self.root / "expansion_reference.json"
        original = verify_lock(CASES, LOCK)
        cases = []
        for index in range(count):
            row = copy.deepcopy(original[index % len(original)])
            row.update({"id": f"RLX-{index + 1:02}",
                        "profile_id": f"TEST-P{index + 1:02}",
                        "reference_status": "INPUT_ONLY_FROZEN"})
            cases.append(row)
        if repeated_profile:
            cases[0]["profile_id"] = original[0]["profile_id"]
        if unsafe_id:
            cases[0]["id"] = "../escape"
        source.write_text("".join(json.dumps(row) + "\n" for row in cases), encoding="utf-8")
        write_lock(source, lock, dataset_name="Offline expansion test fixture", provenance="Unit test; not real evaluation data")
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        protocol.write_text(json.dumps({
            "case_count": count, "case_ids": [row["id"] for row in cases],
            "phase_id": "offline_test_expansion", "freeze_date": "2026-10-03",
            "taxonomy_sha256_at_freeze": sha(ROOT / "rolelens" / "taxonomy.py"),
            "input_file_sha256": sha(source), "input_case_lock_sha256": sha(lock),
            "input_reference_status": "INPUT_ONLY_FROZEN", "predictions_run_at_freeze": False,
        }), encoding="utf-8")
        payload = copy.deepcopy(self.payload)
        payload["input_file_sha256"] = sha(source)
        payload["cases"] = [{"case_id": row["id"], "gap_ids": self.ids[:3]} for row in cases]
        reference.write_text(json.dumps(payload), encoding="utf-8")
        return reference, {"cases_path": source, "lock_path": lock, "protocol_path": protocol}

    def test_mislabeled_references_rejected_before_prediction(self):
        bad = []
        for key, value in (("human_reviewed", True), ("human_reviewed", 0),
                           ("reference_kind", "human_reviewed"), ("producer", "Student"),
                           ("input_file_sha256", "0" * 64)):
            payload = copy.deepcopy(self.payload)
            payload[key] = value
            bad.append(payload)
        for key, value in (("gap_ids", [self.ids[0]] * 3), ("gap_ids", ["ENGINEERING", *self.ids[:2]]),
                           ("case_id", "UNKNOWN"), ("reviewer", "Student"),
                           ("human_reviewed", True), ("reference_status", "human_reviewed")):
            payload = copy.deepcopy(self.payload)
            payload["cases"][0][key] = value
            bad.append(payload)
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            for payload in bad:
                with self.subTest(payload=payload):
                    self.write_reference(payload)
                    with self.assertRaises(ValueError):
                        evaluate(self.reference, self.output)
            analyze_mock.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_all_case_metrics_include_abstentions_without_inflating_coverage(self):
        a, b, c, d = self.ids
        metrics = agreement_metrics([[a, b, c]] * 3, [[a, b, d], None, [a, b, c]])
        self.assertEqual(metrics["accepted_count"], 2)
        self.assertAlmostEqual(metrics["coverage"], 2 / 3)
        self.assertAlmostEqual(metrics["mean_overlap_all_cases_abstain_zero"], 5 / 3)
        self.assertAlmostEqual(metrics["mean_overlap_fraction_all_cases_abstain_zero"], 5 / 9)
        self.assertEqual(metrics["case_pass_at_least_two_of_three_count"], 2)
        self.assertAlmostEqual(metrics["case_pass_at_least_two_of_three_all_cases"], 2 / 3)
        self.assertEqual(metrics["accepted_only_mean_overlap"], 2.5)
        self.assertEqual(metrics["accepted_only_pass_at_least_two_of_three"], 1)
        empty = agreement_metrics([[a, b, c]], [None])
        self.assertEqual(empty["mean_overlap_all_cases_abstain_zero"], 0)
        self.assertIsNone(empty["accepted_only_mean_overlap"])

    def test_consent_gate_prevents_calls_and_invalid_response_cost_is_preserved(self):
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            with self.assertRaisesRegex(ValueError, "allow-external-processing"):
                evaluate(self.reference, self.output, mode="ai")
            analyze_mock.assert_not_called()
        initial_source = CASES.read_bytes()

        def fake_analysis(*_args, **kwargs):
            self.assertTrue(kwargs["allow_external_processing"])
            self.assertEqual(kwargs["mode"], "ai")
            self.assertEqual((self.output / "reference_snapshot.json").read_bytes(), self.reference.read_bytes())
            manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["labels_frozen_before_predictions"])
            index = len(list(self.output.glob("RLV2F-??.json")))
            return self.result(accepted=index > 0, cost=0.08 if index == 0 else 0.02)

        with patch("rolelens.exploratory.analyze", side_effect=fake_analysis) as analyze_mock:
            summary = evaluate(self.reference, self.output, mode="ai", allow_external_processing=True)
            self.assertEqual(analyze_mock.call_count, 10)
        self.assertEqual(CASES.read_bytes(), initial_source)
        self.assertFalse(summary["human_reviewed"])
        self.assertAlmostEqual(summary["total_response_reported_cost_usd"], 0.26)
        self.assertEqual(summary["response_reported_cost_case_count"], 10)
        self.assertEqual(summary["requested_mode_ai_reference_agreement"]["accepted_count"], 9)
        self.assertEqual(summary["abstention_reason_counts"], {"OPENROUTER_INVALID_JSON_RESPONSE": 1})
        first = json.loads((self.output / "RLV2F-01.json").read_text(encoding="utf-8"))
        self.assertEqual(first["result"]["model_run"]["usage"]["completion_tokens"], 20)
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            resumed = evaluate(self.reference, self.output, mode="ai", allow_external_processing=True)
            analyze_mock.assert_not_called()
        self.assertEqual(summary, resumed)

    def test_resume_rejects_changed_reference_and_tampered_saved_results(self):
        with patch("rolelens.exploratory.analyze", return_value=self.result()):
            evaluate(self.reference, self.output)
        changed = copy.deepcopy(self.payload)
        changed["cases"][0]["gap_ids"] = self.ids[1:4]
        self.write_reference(changed)
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            with self.assertRaisesRegex(ValueError, "changed"):
                evaluate(self.reference, self.output)
            self.write_reference(self.payload)
            first_path = self.output / "RLV2F-01.json"
            record = json.loads(first_path.read_text(encoding="utf-8"))
            record["result"]["baseline"]["top_gaps"] = self.ids[1:4]
            first_path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                evaluate(self.reference, self.output)
            analyze_mock.assert_not_called()

    def test_interrupted_request_stops_resume_without_duplicate_call(self):
        with patch("rolelens.exploratory.analyze", side_effect=RuntimeError("simulated interruption")) as analyze_mock:
            with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                evaluate(self.reference, self.output, mode="ai", allow_external_processing=True)
            self.assertEqual(analyze_mock.call_count, 1)
        self.assertTrue((self.output / "RLV2F-01.pending.json").exists())
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            with self.assertRaisesRegex(RuntimeError, "outcome is unknown"):
                evaluate(self.reference, self.output, mode="ai", allow_external_processing=True)
            analyze_mock.assert_not_called()

    def test_custom_inputs_require_complete_matching_pre_prediction_freeze(self):
        reference, paths = self.custom_phase()
        protocol_path = paths["protocol_path"]
        original_protocol = protocol_path.read_text(encoding="utf-8")
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            with self.assertRaisesRegex(ValueError, "together"):
                evaluate(reference, self.output, cases_path=paths["cases_path"])
            for field, invalid in (("case_count", 30), ("input_file_sha256", "0" * 64),
                                   ("input_case_lock_sha256", "0" * 64),
                                   ("predictions_run_at_freeze", True),
                                   ("input_reference_status", "human_reviewed")):
                with self.subTest(field=field):
                    protocol = json.loads(original_protocol)
                    protocol[field] = invalid
                    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        evaluate(reference, self.output, **paths)
            analyze_mock.assert_not_called()
        self.assertFalse(self.output.exists())
        reference, paths = self.custom_phase(unsafe_id=True)
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            with self.assertRaisesRegex(ValueError, "filenames"):
                evaluate(reference, self.output, **paths)
            analyze_mock.assert_not_called()

    def test_twenty_case_expansion_and_thirty_case_pool_keep_denominators_and_costs(self):
        with patch("rolelens.exploratory.analyze", return_value=self.result(cost=0.01)) as analyze_mock:
            evaluate(self.reference, self.output, mode="ai", allow_external_processing=True)
            self.assertEqual(analyze_mock.call_count, 10)
        reference, paths = self.custom_phase()
        expansion_output = self.root / "expansion_run"
        source_before = paths["cases_path"].read_bytes()
        results = [self.result(accepted=False, cost=0.05), self.result(cost=None)]
        results.extend(self.result() for _ in range(18))
        with patch("rolelens.exploratory.analyze", side_effect=results) as analyze_mock:
            expansion = evaluate(reference, expansion_output, mode="ai", allow_external_processing=True, **paths)
            self.assertEqual(analyze_mock.call_count, 20)
        self.assertEqual(paths["cases_path"].read_bytes(), source_before)
        self.assertEqual(expansion["requested_mode_ai_reference_agreement"]["case_count"], 20)
        self.assertEqual(expansion["requested_mode_ai_reference_agreement"]["accepted_count"], 19)
        self.assertEqual(expansion["response_reported_cost_missing_case_count"], 1)
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            resumed = evaluate(reference, expansion_output, mode="ai", allow_external_processing=True, **paths)
            analyze_mock.assert_not_called()
        self.assertEqual(expansion, resumed)
        phases = [(self.output, CASES, LOCK),
                  (expansion_output, paths["cases_path"], paths["lock_path"])]
        with patch("rolelens.exploratory.analyze") as analyze_mock:
            pooled = pool_runs(phases, expected_case_count=30)
            analyze_mock.assert_not_called()
        self.assertEqual(pooled["case_count"], 30)
        self.assertEqual(pooled["unique_profile_count"], 30)
        self.assertEqual(pooled["bucket_counts"], {"AI_PM": 15, "COMMERCIAL_PM": 15})
        self.assertEqual([phase["case_count"] for phase in pooled["phase_summaries"]], [10, 20])
        self.assertAlmostEqual(pooled["requested_mode_ai_reference_agreement"]["coverage"], 29 / 30)
        self.assertAlmostEqual(pooled["requested_mode_ai_reference_agreement"]["mean_overlap_fraction_all_cases_abstain_zero"], 87 / 90)
        self.assertAlmostEqual(pooled["total_response_reported_cost_usd"], 0.51)
        self.assertEqual(pooled["response_reported_cost_case_count"], 29)
        self.assertEqual(pooled["response_reported_cost_missing_case_count"], 1)
        with self.assertRaisesRegex(ValueError, "expected total"):
            pool_runs(phases, expected_case_count=20)
        with self.assertRaisesRegex(ValueError, "repeat"):
            pool_runs([phases[0], phases[0]])
        damaged_path = expansion_output / "RLX-01.json"
        damaged = json.loads(damaged_path.read_text(encoding="utf-8"))
        damaged["result"]["model_run"]["billed_cost_usd"] = 0
        damaged_path.write_text(json.dumps(damaged), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "payload hash"):
            pool_runs(phases)

    def test_pool_rejects_reused_profile_and_runner_rejects_concurrent_directory(self):
        with patch("rolelens.exploratory.analyze", return_value=self.result()):
            evaluate(self.reference, self.output)
        reference, paths = self.custom_phase(repeated_profile=True)
        expansion_output = self.root / "expansion_run"
        with patch("rolelens.exploratory.analyze", return_value=self.result()):
            evaluate(reference, expansion_output, **paths)
        with self.assertRaisesRegex(ValueError, "repeat"):
            pool_runs([(self.output, CASES, LOCK),
                       (expansion_output, paths["cases_path"], paths["lock_path"])])
        with _exclusive_run(self.output):
            with self.assertRaisesRegex(RuntimeError, "Another exploratory run"):
                with _exclusive_run(self.output):
                    self.fail("Concurrent lock was incorrectly acquired")


if __name__ == "__main__":
    unittest.main()
