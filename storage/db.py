"""리뷰와 분류 결과 저장. SQLite. (이슈 #8, 팀원 B)

저장하는 이유: 같은 리뷰를 다시 분류하지 않기 위해서다(무료 한도 절약).
다음 달 리뷰를 올리면 새 리뷰만 분류하고, 기존 결과와 합쳐 기간 비교를 한다.
"""

from core.schemas import Review, ReviewLabel


def save_reviews(reviews: list[Review], labels: list[ReviewLabel]) -> int:
    """리뷰와 AI 분류 결과를 저장한다. 이미 있는 review_id는 건너뛴다.

    Returns: 새로 저장한 건수.
    SQL은 반드시 ? 자리표시자를 쓴다(리뷰 본문은 외부 입력이다).
    """
    raise NotImplementedError("이슈 #8에서 구현")


def unlabeled(reviews: list[Review]) -> list[Review]:
    """reviews 중 아직 분류 결과가 저장되지 않은 것만 돌려준다."""
    raise NotImplementedError("이슈 #8에서 구현")


def load_all(product_id: str | None = None) -> tuple[list[Review], list[ReviewLabel]]:
    """저장된 리뷰와 분류 결과를 읽는다. product_id를 주면 그 상품만."""
    raise NotImplementedError("이슈 #8에서 구현")
