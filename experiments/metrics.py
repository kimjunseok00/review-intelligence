"""라벨 일치도와 분류 성능 지표. (실험 1, 2)

scikit-learn을 추가하지 않으려고 직접 구현했다. 공식은 표준 정의를 따르며 tests/test_metrics.py로 고정했다.
"""

from collections import Counter
from collections.abc import Hashable, Sequence


def cohen_kappa(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    """두 평가자의 Cohen's kappa. 같은 순서의 라벨 목록 두 개를 받는다."""
    if len(a) != len(b) or not a:
        raise ValueError("두 목록의 길이가 같고 비어 있지 않아야 합니다.")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca.keys() | cb.keys()) / (n * n)
    if pe == 1.0:  # 두 사람이 모두 한 라벨만 썼다면 kappa가 정의되지 않는다
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(ratings: Sequence[Sequence[Hashable]]) -> float:
    """평가자 3명 이상의 Fleiss' kappa.

    Args:
        ratings: 항목마다 평가자들의 라벨 목록. 예) [["neg","neg","pos"], ["pos","pos","pos"], ...]
            모든 항목의 평가자 수가 같아야 한다.
    """
    if not ratings:
        raise ValueError("항목이 없습니다.")
    m = len(ratings[0])
    if m < 2 or any(len(r) != m for r in ratings):
        raise ValueError("모든 항목의 평가자 수가 같고 2명 이상이어야 합니다.")
    n_items = len(ratings)
    totals: Counter = Counter()
    p_bar = 0.0
    for r in ratings:
        counts = Counter(r)
        totals.update(counts)
        p_bar += (sum(c * c for c in counts.values()) - m) / (m * (m - 1))
    p_bar /= n_items
    p_e = sum((c / (n_items * m)) ** 2 for c in totals.values())
    if p_e == 1.0:
        return 1.0 if p_bar == 1.0 else 0.0
    return (p_bar - p_e) / (1 - p_e)


def binary_prf(y_true: Sequence[bool], y_pred: Sequence[bool]) -> dict[str, float]:
    """한 라벨에 대한 정밀도, 재현율, F1. 해당 없음(분모 0)은 0으로 둔다."""
    if len(y_true) != len(y_pred):
        raise ValueError("길이가 달라요.")
    tp = sum(t and p for t, p in zip(y_true, y_pred))
    fp = sum((not t) and p for t, p in zip(y_true, y_pred))
    fn = sum(t and (not p) for t, p in zip(y_true, y_pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "support": float(tp + fn)}


def multilabel_report(
    true_sets: Sequence[set], pred_sets: Sequence[set], labels: Sequence[Hashable]
) -> dict:
    """불만 유형처럼 여러 개가 붙는 라벨의 유형별 성능과 Macro F1.

    Returns:
        {"per_label": {라벨: {precision, recall, f1, support}}, "macro_f1": float}
        정답에 한 번도 등장하지 않은 라벨은 macro 평균에서 뺀다(support=0이면 F1이 무의미).
    """
    if len(true_sets) != len(pred_sets):
        raise ValueError("길이가 달라요.")
    per_label = {
        lab: binary_prf([lab in t for t in true_sets], [lab in p for p in pred_sets])
        for lab in labels
    }
    present = [v["f1"] for v in per_label.values() if v["support"] > 0]
    macro = sum(present) / len(present) if present else 0.0
    return {"per_label": per_label, "macro_f1": macro}


def accuracy(y_true: Sequence[Hashable], y_pred: Sequence[Hashable]) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("길이가 같고 비어 있지 않아야 합니다.")
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)
