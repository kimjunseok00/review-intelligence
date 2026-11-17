import pytest

from experiments.metrics import (
    accuracy,
    binary_prf,
    cohen_kappa,
    fleiss_kappa,
    multilabel_report,
)


def test_cohen_kappa_hand_computed():
    # 일치 3/4 = 0.75, 우연 일치 0.5 → kappa 0.5
    assert cohen_kappa([1, 1, 0, 0], [1, 0, 0, 0]) == pytest.approx(0.5)


def test_cohen_kappa_perfect():
    assert cohen_kappa(["a", "b", "a"], ["a", "b", "a"]) == pytest.approx(1.0)


def test_fleiss_kappa_hand_computed():
    # P̄ = 0.75, Pe = (3/8)² + (5/8)² = 34/64 → kappa = 7/15
    ratings = [["a", "a"], ["a", "b"], ["b", "b"], ["b", "b"]]
    assert fleiss_kappa(ratings) == pytest.approx(7 / 15)


def test_fleiss_kappa_three_raters_perfect():
    ratings = [["neg"] * 3, ["pos"] * 3, ["neu"] * 3]
    assert fleiss_kappa(ratings) == pytest.approx(1.0)


def test_fleiss_rejects_uneven_raters():
    with pytest.raises(ValueError):
        fleiss_kappa([["a", "a"], ["a"]])


def test_binary_prf():
    r = binary_prf([True, True, False, False], [True, False, True, False])
    assert r["precision"] == pytest.approx(0.5)
    assert r["recall"] == pytest.approx(0.5)
    assert r["f1"] == pytest.approx(0.5)


def test_multilabel_macro_skips_absent_labels():
    true = [{"delivery"}, {"delivery", "defect"}, set()]
    pred = [{"delivery"}, {"delivery"}, set()]
    r = multilabel_report(true, pred, ["delivery", "defect", "price"])
    assert r["per_label"]["delivery"]["f1"] == pytest.approx(1.0)
    assert r["per_label"]["defect"]["f1"] == 0.0
    # price는 정답에 없으므로 평균에서 빠진다 → (1.0 + 0.0) / 2
    assert r["macro_f1"] == pytest.approx(0.5)


def test_accuracy():
    assert accuracy(["a", "b"], ["a", "a"]) == pytest.approx(0.5)
