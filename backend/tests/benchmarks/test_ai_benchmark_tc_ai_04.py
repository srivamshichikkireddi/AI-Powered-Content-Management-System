import pytest
from backend.app.services.ai_service import classify_category
from backend.tests.benchmarks.benchmark_corpus import LABELED_CORPUS


def test_ai_categorization_accuracy_benchmark_tc_ai_04():
    """
    TC-AI-04: Evaluate multi-class classification accuracy against held-out labelled test corpus.
    Requirement: AICMS-NF-009 (Accuracy >= 80%).
    """
    total = len(LABELED_CORPUS)
    correct = 0
    per_category = {}

    print(f"\n{'='*70}\n[TC-AI-04] AI Categorization Accuracy Benchmark\nEvaluated on {total} reviewed documents\n{'='*70}")

    for item in LABELED_CORPUS:
        gt = item["ground_truth"]
        predicted, confidence = classify_category(item["text"])

        if gt not in per_category:
            per_category[gt] = {"total": 0, "correct": 0, "confidences": []}

        per_category[gt]["total"] += 1
        per_category[gt]["confidences"].append(confidence)

        is_match = (predicted == gt)
        if is_match:
            correct += 1
            per_category[gt]["correct"] += 1

        mark = "✓" if is_match else "✗"
        print(f"[{mark}] {item['id']:<8} GroundTruth: {gt:<16} Predicted: {predicted:<16} Conf: {confidence:.2f}")

    overall_accuracy = (correct / total) * 100.0

    print(f"\n{'-'*70}\nPer-Category Accuracy Breakdown:")
    for cat, stats in per_category.items():
        cat_acc = (stats["correct"] / stats["total"]) * 100.0
        avg_conf = sum(stats["confidences"]) / len(stats["confidences"])
        print(f"  - {cat:<18}: {stats['correct']}/{stats['total']} ({cat_acc:.1f}%) | Avg Confidence: {avg_conf:.2f}")

    print(f"{'-'*70}")
    print(f"OVERALL TOP-1 ACCURACY: {correct}/{total} ({overall_accuracy:.2f}%)")
    print(f"TARGET REQUIREMENT:     >= 80.00% (AICMS-NF-009)")
    print(f"BENCHMARK STATUS:       {'PASS' if overall_accuracy >= 80.0 else 'FAIL'}")
    print(f"{'='*70}\n")

    assert overall_accuracy >= 80.0, f"Categorization accuracy {overall_accuracy:.2f}% below 80% SLA!"
