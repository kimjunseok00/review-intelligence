"""변화 판정 규칙을 고정한다. 이 테스트가 깨지면 서비스의 핵심 판정이 바뀐 것이다."""

import pytest

from core import config
from core.schemas import Verdict
from core.stats import fisher_one_sided, judge_change


def test_fisher_matches_known_value():
    # 차 맛 감별 예제: [[3,1],[1,3]]의 단측 p = 17/70
    p = fisher_one_sided(base_count=1, base_total=4, target_count=3, target_total=4, greater=True)
    assert p == pytest.approx(17 / 70, abs=1e-12)
    p_less = fisher_one_sided(1, 4, 3, 4, greater=False)
    assert p_less == pytest.approx(69 / 70, abs=1e-12)


def test_fisher_rejects_bad_counts():
    with pytest.raises(ValueError):
        fisher_one_sided(5, 4, 1, 4, greater=True)


def test_insufficient_sample():
    small = config.MIN_PERIOD_REVIEWS - 1
    p, v = judge_change(0, small, 10, 100)
    assert p is None and v == Verdict.INSUFFICIENT


def test_clear_spike_detected():
    # 포장 불만 100건 중 5건 → 100건 중 25건
    p, v = judge_change(5, 100, 25, 100, increase_only=True)
    assert v == Verdict.INCREASED and p < config.ALPHA


def test_small_fluctuation_not_alerted():
    # 100건 중 5건 → 100건 중 8건: 우연한 변동 범위
    _, v = judge_change(5, 100, 8, 100, increase_only=True)
    assert v == Verdict.NO_CHANGE


def test_significant_but_tiny_delta_not_alerted():
    # 표본이 아주 크면 1%p 차이도 유의하지만, MIN_RATE_DELTA 미만이면 알리지 않는다
    p, v = judge_change(1000, 100_000, 2000, 100_000, increase_only=True)
    assert p < config.ALPHA and v == Verdict.NO_CHANGE


def test_before_after_decrease():
    # 개선 전 100건 중 30건 → 개선 후 100건 중 8건
    _, v = judge_change(30, 100, 8, 100)
    assert v == Verdict.DECREASED


def test_increase_only_never_reports_decrease():
    _, v = judge_change(30, 100, 8, 100, increase_only=True)
    assert v == Verdict.NO_CHANGE
