"""Reproducible selective-classification and ranking metrics."""

from __future__ import annotations

from collections import Counter
from statistics import median


def safe_ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
    return ordered[index]


def latency_summary(milliseconds: list[float]) -> dict:
    return {
        "n": len(milliseconds),
        "median_ms": median(milliseconds) if milliseconds else None,
        "p95_ms": percentile(milliseconds, 0.95),
    }


def classification_metrics(gold: list[str], predicted: list[str | None], labels: list[str]) -> dict:
    if len(gold) != len(predicted):
        raise ValueError("Gold and prediction lengths differ")
    if not gold:
        raise ValueError("No evaluation records")
    if any(value not in labels for value in gold):
        raise ValueError("Unknown gold label")
    if any(value is not None and value not in labels for value in predicted):
        raise ValueError("Unknown predicted label")
    decided = sum(value is not None for value in predicted)
    correct = sum(g == p for g, p in zip(gold, predicted))
    matrix = {label: {target: 0 for target in [*labels, "ABSTAIN"]} for label in labels}
    for g, p in zip(gold, predicted):
        matrix[g][p or "ABSTAIN"] += 1
    per_label = {}
    for label in labels:
        true_positive = matrix[label][label]
        false_positive = sum(matrix[other][label] for other in labels if other != label)
        false_negative = sum(matrix[label][other] for other in labels if other != label)
        false_negative += matrix[label]["ABSTAIN"]
        precision = safe_ratio(true_positive, true_positive + false_positive)
        recall = safe_ratio(true_positive, true_positive + false_negative)
        f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else 0.0
        per_label[label] = {"precision": precision, "recall": recall, "f1": f1, "support": gold.count(label)}
    return {
        "n": len(gold),
        "decided": decided,
        "abstained": len(gold) - decided,
        "coverage": decided / len(gold),
        "selective_accuracy": safe_ratio(correct, decided),
        "overall_correct_rate": correct / len(gold),
        "macro_f1_abstain_as_miss": sum(item["f1"] for item in per_label.values()) / len(labels),
        "confusion": matrix,
        "per_label": per_label,
    }


def ranking_metrics(relevant_ids: list[set[str]], ranked_ids: list[list[str]], *, k: int = 3) -> dict:
    if len(relevant_ids) != len(ranked_ids) or not relevant_ids:
        raise ValueError("Ranking records are empty or misaligned")
    hits = Counter()
    reciprocal = []
    for relevant, ranked in zip(relevant_ids, ranked_ids):
        if not relevant or len(ranked) != len(set(ranked)):
            raise ValueError("Each ranking needs nonempty gold and unique predictions")
        hits["hit_at_1"] += bool(ranked and ranked[0] in relevant)
        hits[f"hit_at_{k}"] += bool(set(ranked[:k]) & relevant)
        position = next((i + 1 for i, item in enumerate(ranked[:k]) if item in relevant), None)
        reciprocal.append(1 / position if position else 0.0)
    n = len(relevant_ids)
    return {
        "n": n,
        "hit_at_1": hits["hit_at_1"] / n,
        f"hit_at_{k}": hits[f"hit_at_{k}"] / n,
        f"mrr_at_{k}": sum(reciprocal) / n,
    }


def gap_agreement_at_k(reference: list[list[str]], predicted: list[list[str] | None], *, k: int = 3) -> dict:
    """Agreement with a human-reviewed reference, with abstention explicit.

    A case passes when at least 2 of the 3 selected capability IDs overlap.
    This is a *reference-agreement* metric, never proof of candidate benefit.
    """
    if len(reference) != len(predicted) or not reference or k != 3:
        raise ValueError("Need aligned nonempty top-3 reference/prediction lists")
    if any(len(row) != k or len(set(row)) != k for row in reference):
        raise ValueError("Reference top-3 IDs must be unique")
    decided = 0
    pass_count = 0
    overlap_total = 0
    exact_count = 0
    for gold, choice in zip(reference, predicted):
        if choice is None:
            continue
        if len(choice) != k or len(set(choice)) != k:
            raise ValueError("Predicted top-3 IDs must be unique")
        decided += 1
        overlap = len(set(gold) & set(choice))
        overlap_total += overlap
        pass_count += overlap >= 2
        exact_count += set(gold) == set(choice)
    return {
        "n": len(reference),
        "decided": decided,
        "abstained": len(reference) - decided,
        "coverage": decided / len(reference),
        "agreement_at_least_2_of_3_on_decided": safe_ratio(pass_count, decided),
        "agreement_at_least_2_of_3_all_cases": pass_count / len(reference),
        "mean_overlap_on_decided": safe_ratio(overlap_total, decided),
        "exact_set_match_on_decided": safe_ratio(exact_count, decided),
    }
