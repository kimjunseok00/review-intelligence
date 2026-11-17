"""Gemini로 리뷰를 묶음 분류한다. (이슈 #2, 팀원 A)"""

from core.schemas import Review, ReviewLabel


def classify_reviews(reviews: list[Review]) -> list[ReviewLabel]:
    """리뷰 목록을 감정과 불만 유형으로 분류한다.

    Args:
        reviews: 분류할 리뷰. 순서와 개수 제한 없음.

    Returns:
        입력과 같은 순서, 같은 개수의 ReviewLabel(source="ai").

    구현 안내:
        - config.BATCH_SIZE개씩 묶어 core.llm.call_llm_json(prompt, LLMBatch)로 한 번에 보낸다.
          리뷰마다 한 번씩 부르면 무료 한도가 금방 바닥난다.
        - 묶음 안에서는 review_id 대신 0부터 시작하는 idx를 붙여 보내고, 돌아온 idx로 다시 매칭한다.
        - 돌아온 idx가 보낸 것과 다르면(누락, 중복, 범위 밖) 빠진 리뷰만 다시 보낸다.
          두 번째도 실패하면 LLMError를 낸다. 조용히 건너뛰지 않는다.
        - 리뷰가 config.MAX_REVIEW_CHARS를 넘으면 잘라서 보낸다.
        - 분류 기준은 labeling/LABEL_GUIDE.md를 따른다. 사람 라벨과 같은 기준이어야 대조가 의미 있다.
          프롬프트는 prompts/classify.txt에 둔다.
        - temperature=0으로 호출한다.
        - 감정이 긍정인데 불만 유형이 붙은 경우는 허용한다("좋은데 배송이 느려요").
    """
    raise NotImplementedError("이슈 #2에서 구현")
