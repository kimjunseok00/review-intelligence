"""Streamlit 진입점. (팀원 B)

지금은 뼈대가 돌아가는지 확인하는 최소 화면이다: 예시 CSV → 가짜 분류 → 불만 유형별 건수.
이슈 #1(업로드·열 지정), #7(대시보드)에서 바꾼다.
"""

from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

from core import config
from core.schemas import COMPLAINT_KO, SENTIMENT_KO, Review
from engine import classify_reviews

SAMPLE = Path(__file__).parent / "samples" / "sample_reviews.csv"

st.set_page_config(page_title="Review Intelligence", page_icon="📈")
st.title("Review Intelligence")
st.caption("리뷰 불만이 언제, 얼마나 늘었는지 판정합니다.")

if config.USE_MOCK:
    st.info("가짜 엔진으로 실행 중입니다 (.env의 USE_MOCK=1).")

st.subheader("뼈대 동작 확인 (가상 예시 데이터)")
if st.button("예시 리뷰 분류하기"):
    df = pd.read_csv(SAMPLE)
    # 실제 업로드에서는 ingest.csv_loader.to_reviews()와 열 지정 화면을 쓴다.
    reviews = [
        Review(
            review_id=f"row-{i}",
            product_id=str(row["상품ID"]),
            text=str(row["리뷰내용"]),
            rating=int(row["평점"]),
            created_at=pd.to_datetime(row["작성일"]).date(),
        )
        for i, row in df.iterrows()
    ]
    labels = classify_reviews(reviews)

    sentiments = Counter(SENTIMENT_KO[lab.sentiment] for lab in labels)
    complaints = Counter(COMPLAINT_KO[c] for lab in labels for c in lab.complaints)
    st.write(f"리뷰 {len(reviews)}건")
    st.bar_chart(pd.Series(sentiments, name="리뷰 수"))
    st.dataframe(
        pd.DataFrame(complaints.most_common(), columns=["불만 유형", "리뷰 수"]),
        hide_index=True,
    )
