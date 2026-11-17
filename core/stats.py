"""불만 비율 변화 판정. LLM을 쓰지 않는 순수 계산이다.

이 서비스의 핵심 주장("우연한 변동이 아니라 의미 있는 변화만 알린다")이 이 파일에 있다.
판정이 매번 같고 테스트로 고정할 수 있어야 하므로 LLM에 맡기지 않는다.

검정 방법: Fisher 정확 검정(단측). 기간별 리뷰 수가 수십 건 수준이라
정규근사(z검정)가 부정확할 수 있어 정확 검정을 쓴다. scipy 없이 구현했다.
"""

from math import exp, lgamma

from core import config
from core.schemas import Verdict


def _log_comb(n: int, k: int) -> float:
    """log(nCk). 큰 수에서도 넘치지 않도록 로그로 계산한다."""
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def _hypergeom_pmf(k: int, total: int, successes: int, draws: int) -> float:
    """초기하분포 확률. total개 중 successes개가 '불만'일 때 draws개를 뽑아 k개가 불만일 확률."""
    if k < max(0, draws - (total - successes)) or k > min(draws, successes):
        return 0.0
    return exp(
        _log_comb(successes, k)
        + _log_comb(total - successes, draws - k)
        - _log_comb(total, draws)
    )


def fisher_one_sided(
    base_count: int, base_total: int, target_count: int, target_total: int, *, greater: bool
) -> float:
    """target 구간의 불만 비율이 base보다 크다(greater=True) 또는 작다(False)는 단측 p값.

    2x2 표:            불만   불만 아님
        target 구간    a      target_total - a
        base 구간      c      base_total - c
    귀무가설(두 구간 비율이 같다) 아래에서 a는 초기하분포를 따른다.
    """
    if not (0 <= base_count <= base_total and 0 <= target_count <= target_total):
        raise ValueError("건수는 0 이상, 전체 수 이하여야 합니다.")
    total = base_total + target_total
    successes = base_count + target_count
    lo = max(0, target_total - (total - successes))
    hi = min(target_total, successes)
    ks = range(target_count, hi + 1) if greater else range(lo, target_count + 1)
    p = sum(_hypergeom_pmf(k, total, successes, target_total) for k in ks)
    return min(1.0, p)  # 부동소수 오차로 1을 살짝 넘는 경우를 막는다


def judge_change(
    base_count: int,
    base_total: int,
    target_count: int,
    target_total: int,
    *,
    increase_only: bool = False,
) -> tuple[float | None, Verdict]:
    """두 구간의 불만 비율 변화를 판정한다.

    Args:
        base_*: 비교 기준 구간(직전 기간, 또는 개선 전).
        target_*: 살펴볼 구간(이번 기간, 또는 개선 후).
        increase_only: True면 증가만 본다(급증 탐지용 단측 검정).
            False면 증가·감소를 모두 본다(전후 비교용, 양측 p값 = 단측 p값의 2배).

    Returns:
        (p값, 판정). 표본 부족이면 (None, INSUFFICIENT).
        '의미 있는 변화'가 되려면 p < ALPHA이면서 비율 차이가 MIN_RATE_DELTA 이상이어야 한다.
    """
    if base_total < config.MIN_PERIOD_REVIEWS or target_total < config.MIN_PERIOD_REVIEWS:
        return None, Verdict.INSUFFICIENT

    base_rate = base_count / base_total
    target_rate = target_count / target_total
    delta = target_rate - base_rate

    p_inc = fisher_one_sided(base_count, base_total, target_count, target_total, greater=True)
    if increase_only:
        if p_inc < config.ALPHA and delta >= config.MIN_RATE_DELTA:
            return p_inc, Verdict.INCREASED
        return p_inc, Verdict.NO_CHANGE

    p_dec = fisher_one_sided(base_count, base_total, target_count, target_total, greater=False)
    p_two = min(1.0, 2 * min(p_inc, p_dec))
    if p_two < config.ALPHA and delta >= config.MIN_RATE_DELTA:
        return p_two, Verdict.INCREASED
    if p_two < config.ALPHA and -delta >= config.MIN_RATE_DELTA:
        return p_two, Verdict.DECREASED
    return p_two, Verdict.NO_CHANGE
