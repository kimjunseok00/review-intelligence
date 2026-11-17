"""약속(데이터 형식, 가짜 엔진의 입출력)이 깨지지 않았는지 확인한다."""

from datetime import date

from core.schemas import (
    COMPLAINT_KO,
    BeforeAfter,
    Complaint,
    LLMBatch,
    PeriodStat,
    Review,
    ReviewLabel,
    Sentiment,
    Verdict,
)
from engine import mock


def test_every_complaint_has_korean_name():
    assert set(COMPLAINT_KO) == set(Complaint)


def test_mock_returns_same_order_and_count():
    reviews = [
        Review(review_id="a", text="배송이 너무 늦어요", rating=2),
        Review(review_id="b", text="좋아요 추천합니다", rating=5),
        Review(review_id="c", text="포장 박스가 찢어져 왔고 제품도 불량"),
    ]
    labels = mock.classify_reviews(reviews)
    assert [lab.review_id for lab in labels] == ["a", "b", "c"]
    assert Complaint.DELIVERY in labels[0].complaints
    assert labels[1].sentiment == Sentiment.POSITIVE and labels[1].complaints == []
    assert {Complaint.PACKAGING, Complaint.DEFECT} <= set(labels[2].complaints)


def test_label_roundtrip_json():
    lab = ReviewLabel(review_id="x", sentiment=Sentiment.NEGATIVE, complaints=[Complaint.PRICE])
    assert ReviewLabel.model_validate_json(lab.model_dump_json()) == lab


def test_period_stat_enum_keys_roundtrip():
    s = PeriodStat(
        product_id="P1",
        period_start=date(2026, 10, 5),
        total=40,
        complaint_counts={c: 0 for c in Complaint},
    )
    assert PeriodStat.model_validate_json(s.model_dump_json()) == s


def test_llm_batch_parses_enum_strings():
    raw = '{"items":[{"idx":0,"sentiment":"negative","complaints":["delivery","packaging"]}]}'
    batch = LLMBatch.model_validate_json(raw)
    assert batch.items[0].complaints == [Complaint.DELIVERY, Complaint.PACKAGING]


def test_before_after_model():
    b = BeforeAfter(
        product_id="P1", complaint=Complaint.PACKAGING,
        base_count=30, base_total=100, target_count=8, target_total=100,
        base_rate=0.3, target_rate=0.08, p_value=0.0001,
        verdict=Verdict.DECREASED, change_date=date(2026, 10, 15),
    )
    assert b.verdict == Verdict.DECREASED
