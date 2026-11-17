"""가짜 분류 엔진. 실제 엔진과 함수 이름, 입출력이 같다.

용도: 화면·분석 담당이 API 키와 엔진 완성을 기다리지 않고 개발하기 위함.
단어 몇 개로 판단하는 엉터리 규칙이니 성능 비교에 쓰지 않는다.
"""

from core.schemas import Complaint, Review, ReviewLabel, Sentiment

_KEYWORDS: dict[Complaint, tuple[str, ...]] = {
    Complaint.DELIVERY: ("배송", "늦", "도착"),
    Complaint.DEFECT: ("불량", "고장", "찢어", "깨져", "망가"),
    Complaint.MISMATCH: ("사이즈", "작아", "커요", "달라", "사진과"),
    Complaint.PRICE: ("비싸", "가격"),
    Complaint.PACKAGING: ("포장", "박스", "뜯겨"),
    Complaint.SERVICE: ("응대", "교환", "반품", "환불", "문의"),
}
_POSITIVE_WORDS = ("좋아", "만족", "최고", "추천")
_NEGATIVE_WORDS = ("별로", "실망", "최악", "아쉽")


def _sentiment(review: Review, has_complaint: bool) -> Sentiment:
    if review.rating is not None:
        if review.rating >= 4:
            return Sentiment.POSITIVE
        if review.rating <= 2:
            return Sentiment.NEGATIVE
        return Sentiment.NEUTRAL
    if any(w in review.text for w in _NEGATIVE_WORDS) or has_complaint:
        return Sentiment.NEGATIVE
    if any(w in review.text for w in _POSITIVE_WORDS):
        return Sentiment.POSITIVE
    return Sentiment.NEUTRAL


def classify_reviews(reviews: list[Review]) -> list[ReviewLabel]:
    """단어가 들어 있으면 그 불만 유형을 붙인다."""
    labels: list[ReviewLabel] = []
    for r in reviews:
        complaints = [c for c, words in _KEYWORDS.items() if any(w in r.text for w in words)]
        labels.append(
            ReviewLabel(
                review_id=r.review_id,
                sentiment=_sentiment(r, bool(complaints)),
                complaints=complaints,
                source="ai",
            )
        )
    return labels
