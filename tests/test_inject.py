from datetime import date, timedelta

import pytest

from core.schemas import Complaint, Review
from experiments.inject import assign_dates, inject_spike, week_start_of


def _reviews(n: int, prefix: str = "r") -> list[Review]:
    return [Review(review_id=f"{prefix}{i}", product_id="P1", text="t") for i in range(n)]


def test_assign_dates_in_range_and_reproducible():
    start = date(2026, 9, 2)  # 수요일 → 그 주 월요일 8/31로 맞춰진다
    a = assign_dates(_reviews(200), start, weeks=8, seed=1)
    b = assign_dates(_reviews(200), start, weeks=8, seed=1)
    first = week_start_of(start)
    assert first == date(2026, 8, 31)
    assert all(first <= r.created_at < first + timedelta(weeks=8) for r in a)
    assert [r.created_at for r in a] == [r.created_at for r in b]


def test_assign_dates_does_not_mutate_input():
    src = _reviews(3)
    assign_dates(src, date(2026, 9, 1), weeks=2)
    assert all(r.created_at is None for r in src)


def test_inject_spike_adds_to_target_week_only():
    dated = assign_dates(_reviews(100), date(2026, 8, 31), weeks=8, seed=0)
    pool = _reviews(10, prefix="pack")
    target = date(2026, 10, 5)  # 월요일
    out, truth = inject_spike(dated, pool, Complaint.PACKAGING, target, n_inject=15, seed=0)

    injected = [r for r in out if r.review_id.startswith("inj-")]
    assert len(out) == 115 and len(injected) == 15
    assert all(week_start_of(r.created_at) == target for r in injected)
    assert truth.week_start == target and truth.n_injected == 15
    assert len({r.review_id for r in out}) == len(out)  # ID 중복 없음


def test_inject_requires_pool():
    with pytest.raises(ValueError):
        inject_spike(_reviews(1), [], Complaint.DELIVERY, date(2026, 9, 1), 1)
