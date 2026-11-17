"""기간별 집계, 급증 탐지, 전후 비교. (이슈 #6, 팀원 A)

통계 판정 자체는 core.stats.judge_change()가 한다. 이 파일은 데이터를 모아서 넘기는 역할이다.
"""

from datetime import date

from core.schemas import BeforeAfter, PeriodStat, Review, ReviewLabel, SpikeAlert


def aggregate_by_period(
    reviews: list[Review], labels: list[ReviewLabel], freq: str = "W"
) -> list[PeriodStat]:
    """상품별·기간별로 전체 리뷰 수와 불만 유형별 리뷰 수를 센다.

    Args:
        reviews: created_at이 있는 리뷰. 없는 리뷰는 제외하고, 제외한 수를 로그로 남긴다.
        labels: reviews와 review_id로 매칭되는 분류 결과.
        freq: "W"(주, 월요일 시작) 또는 "M"(월). pandas 기간 문자열과 같다.

    Returns:
        (product_id, period_start) 순으로 정렬된 PeriodStat 목록.
        리뷰가 0건인 기간도 total=0으로 포함한다(급증 판정에서 '직전 기간'을 놓치지 않기 위함).
        complaint_counts에는 모든 Complaint 키가 있어야 한다(없으면 0).

    구현 안내: pandas DataFrame으로 바꿔 groupby + resample 하면 짧다.
    """
    raise NotImplementedError("이슈 #6에서 구현")


def detect_spikes(stats: list[PeriodStat]) -> list[SpikeAlert]:
    """각 상품·불만 유형마다 '직전 기간 → 이번 기간'을 비교해 급증을 판정한다.

    Returns:
        모든 (상품, 유형, 기간)의 SpikeAlert. 화면에서 verdict == INCREASED만 골라 보여준다.
        첫 기간은 비교 대상이 없으므로 만들지 않는다.

    구현 안내: core.stats.judge_change(..., increase_only=True)를 쓴다.
    """
    raise NotImplementedError("이슈 #6에서 구현")


def compare_before_after(
    reviews: list[Review],
    labels: list[ReviewLabel],
    product_id: str,
    change_date: date,
    window_days: int | None = None,
) -> list[BeforeAfter]:
    """개선 조치 날짜 전후로 불만 유형별 비율을 비교한다.

    Args:
        change_date: 판매자가 입력한 개선 조치 날짜. 이 날짜부터 '후'로 센다.
        window_days: 전후 각각 이 일수만 본다. None이면 전체 기간.

    Returns:
        불만 유형마다 BeforeAfter 하나.

    구현 안내: core.stats.judge_change(..., increase_only=False)를 쓴다.
    주의: 결과는 '변화'일 뿐 '개선 효과'가 아니다. 계절, 할인, 구매자층 변화도 영향을 준다.
    """
    raise NotImplementedError("이슈 #6에서 구현")
