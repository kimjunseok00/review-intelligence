"""데이터 형식 정의. 모듈끼리 주고받는 모든 데이터는 여기 모델을 쓴다.

이 파일은 팀의 약속이다. 바꾸려면 팀장과 합의한 뒤 docs/DATA_FORMAT.md도 함께 고친다.
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    """리뷰 전체의 감정. 하나만 고른다."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Complaint(str, Enum):
    """불만 유형. 리뷰 하나에 여러 개가 붙을 수 있다. 정의는 labeling/LABEL_GUIDE.md."""

    DELIVERY = "delivery"  # 배송
    DEFECT = "defect"  # 품질·불량
    MISMATCH = "mismatch"  # 사이즈·규격·설명과 다름
    PRICE = "price"  # 가격
    PACKAGING = "packaging"  # 포장
    SERVICE = "service"  # 고객응대·교환·반품
    OTHER = "other"  # 기타 불만


# 화면과 보고서에 쓰는 한국어 이름
COMPLAINT_KO: dict[Complaint, str] = {
    Complaint.DELIVERY: "배송",
    Complaint.DEFECT: "품질·불량",
    Complaint.MISMATCH: "사이즈·설명 불일치",
    Complaint.PRICE: "가격",
    Complaint.PACKAGING: "포장",
    Complaint.SERVICE: "고객응대·교환반품",
    Complaint.OTHER: "기타",
}

SENTIMENT_KO: dict[Sentiment, str] = {
    Sentiment.POSITIVE: "긍정",
    Sentiment.NEGATIVE: "부정",
    Sentiment.NEUTRAL: "중립",
}


class ColumnMapping(BaseModel):
    """업로드한 CSV에서 어느 열이 무엇인지. 판매자가 화면에서 고른다.

    플랫폼마다 엑셀 열 이름이 다르므로 이름을 가정하지 않고 사용자가 지정하게 한다.
    """

    text: str = Field(description="리뷰 본문 열 이름 (필수)")
    created_at: str | None = Field(default=None, description="작성일 열. 없으면 기간 분석 불가")
    rating: str | None = None
    product_id: str | None = Field(default=None, description="없으면 전체를 상품 하나로 본다")
    review_id: str | None = Field(default=None, description="없으면 행 번호로 만든다")


class Review(BaseModel):
    """리뷰 한 건."""

    review_id: str
    product_id: str = "default"
    text: str
    rating: int | None = None
    created_at: date | None = None


class ReviewLabel(BaseModel):
    """리뷰 한 건의 분류 결과. AI 결과와 사람 라벨이 같은 형식을 쓴다(그래야 대조할 수 있다)."""

    review_id: str
    sentiment: Sentiment
    complaints: list[Complaint] = Field(default_factory=list)
    source: str = Field(default="ai", description="'ai', 'human:<이름>', 'consensus' 중 하나")


class PeriodStat(BaseModel):
    """상품 하나, 기간 하나의 집계."""

    product_id: str
    period_start: date
    total: int = Field(description="그 기간의 전체 리뷰 수")
    complaint_counts: dict[Complaint, int] = Field(description="불만 유형별 리뷰 수")


class Verdict(str, Enum):
    """비율 변화 판정 결과. core/stats.py가 만든다."""

    INCREASED = "increased"
    DECREASED = "decreased"
    NO_CHANGE = "no_change"
    INSUFFICIENT = "insufficient_data"  # 표본 부족으로 판단 보류


VERDICT_KO: dict[Verdict, str] = {
    Verdict.INCREASED: "의미 있는 증가",
    Verdict.DECREASED: "의미 있는 감소",
    Verdict.NO_CHANGE: "변화 없음",
    Verdict.INSUFFICIENT: "표본 부족 (판단 보류)",
}


class RateChange(BaseModel):
    """두 구간의 불만 비율 비교 결과."""

    product_id: str
    complaint: Complaint
    base_count: int
    base_total: int
    target_count: int
    target_total: int
    base_rate: float
    target_rate: float
    p_value: float | None = Field(description="표본 부족이면 None")
    verdict: Verdict


class SpikeAlert(RateChange):
    """직전 기간 대비 이번 기간의 급증 판정. base=직전 기간, target=이번 기간."""

    period_start: date


class BeforeAfter(RateChange):
    """개선 조치 전후 비교. base=조치 전, target=조치 후.

    주의: 변화가 개선 조치 '때문'인지는 판단하지 않는다. 화면 문구도 '변화'로만 쓴다.
    """

    change_date: date


# ---------------------------------------------------------------------------
# LLM 응답 전용 형식
# Gemini 응답 스키마는 기본값, Optional 등 일부 기능에서 오류가 날 수 있어
# LLM에게 받는 형식은 단순하게 따로 둔다. 엔진이 이 값을 ReviewLabel로 옮겨 담는다.
# ---------------------------------------------------------------------------


class LLMItem(BaseModel):
    idx: int  # 묶음 안에서 리뷰 순번(0부터). review_id 대신 짧은 번호로 토큰을 아낀다
    sentiment: Sentiment
    complaints: list[Complaint]


class LLMBatch(BaseModel):
    items: list[LLMItem]
