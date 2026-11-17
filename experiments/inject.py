"""급증 탐지 주입 실험 도구. (실험 4)

공개 리뷰에는 작성일이 없어서, 날짜를 가상으로 붙인 뒤 특정 주에 특정 불만 리뷰를
일부러 더 섞어 넣는다. 어디에 넣었는지 알고 있으므로 탐지기가 맞혔는지 채점할 수 있다.

발표 시 반드시 밝힐 것: 날짜는 가상이며, 이 실험은 '탐지 규칙'의 검증이지 실제 판매 현장 검증이 아니다.
"""

import random
from datetime import date, timedelta

from pydantic import BaseModel

from core.schemas import Complaint, Review


class InjectionTruth(BaseModel):
    """주입 실험의 정답."""

    product_id: str
    complaint: Complaint
    week_start: date  # 주입한 주의 월요일
    n_injected: int


def week_start_of(d: date) -> date:
    """d가 속한 주의 월요일."""
    return d - timedelta(days=d.weekday())


def assign_dates(reviews: list[Review], start: date, weeks: int, seed: int = 0) -> list[Review]:
    """리뷰마다 start 주부터 weeks주 사이의 날짜를 무작위로 고르게 붙인다(원본은 바꾸지 않음).

    start는 월요일로 맞춘다. 같은 seed면 항상 같은 결과가 나온다(실험 재현용).
    """
    if weeks < 1:
        raise ValueError("weeks는 1 이상이어야 합니다.")
    rng = random.Random(seed)
    first = week_start_of(start)
    span = weeks * 7
    return [
        r.model_copy(update={"created_at": first + timedelta(days=rng.randrange(span))})
        for r in reviews
    ]


def inject_spike(
    dated: list[Review],
    pool: list[Review],
    complaint: Complaint,
    week_start: date,
    n_inject: int,
    seed: int = 0,
) -> tuple[list[Review], InjectionTruth]:
    """week_start 주에 complaint 유형 리뷰 n_inject건을 추가한다.

    Args:
        dated: assign_dates()로 날짜를 붙인 기본 리뷰.
        pool: complaint 유형으로 '사람이 라벨링한' 리뷰 모음. 여기서 뽑아 복사해 넣는다.
            AI 라벨로 고른 리뷰를 쓰면 AI가 잘 맞히는 리뷰만 주입되어 결과가 부풀려지므로 쓰지 않는다.
        n_inject: 추가할 건수. pool보다 많으면 중복 허용으로 뽑는다.

    Returns:
        (주입 후 전체 리뷰, 정답). 주입 리뷰의 review_id는 "inj-"로 시작한다.
    """
    if not pool:
        raise ValueError("주입할 리뷰 모음(pool)이 비어 있습니다.")
    if not dated:
        raise ValueError("기본 리뷰가 비어 있습니다.")
    rng = random.Random(seed)
    week = week_start_of(week_start)
    product_id = dated[0].product_id
    picked = (
        rng.sample(pool, n_inject) if n_inject <= len(pool) else rng.choices(pool, k=n_inject)
    )
    injected = [
        r.model_copy(
            update={
                "review_id": f"inj-{i}-{r.review_id}",
                "product_id": product_id,
                "created_at": week + timedelta(days=rng.randrange(7)),
            }
        )
        for i, r in enumerate(picked)
    ]
    truth = InjectionTruth(
        product_id=product_id, complaint=complaint, week_start=week, n_injected=n_inject
    )
    return dated + injected, truth
