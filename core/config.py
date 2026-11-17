"""환경 설정을 한 곳에서 읽는다.

다른 파일은 os.environ을 직접 읽지 않고 이 모듈의 상수를 쓴다.
설정이 흩어지면 사람마다 다른 값으로 돌려 놓고 원인을 못 찾기 때문이다.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# 1이면 engine이 가짜 구현(engine/mock.py)으로 연결된다. API 키 없이 개발할 때 쓴다.
USE_MOCK: bool = os.getenv("USE_MOCK", "1") == "1"

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# --- 분류 ---
# 한 번의 LLM 호출에 묶어 보내는 리뷰 수. 무료 한도를 아끼려고 묶는다.
# 응답이 잘리거나 형식이 깨지면 줄인다.
BATCH_SIZE: int = 50
# 리뷰 한 건의 최대 글자 수. 넘으면 잘라서 보낸다.
MAX_REVIEW_CHARS: int = 500

# --- 변화 판정 (core/stats.py) ---
# 기간 하나에 리뷰가 이보다 적으면 비율이 불안정하므로 '표본 부족'으로 판정한다.
MIN_PERIOD_REVIEWS: int = 20
# 유의수준. p값이 이보다 작아야 '변화 있음'으로 본다.
ALPHA: float = 0.05
# 통계적으로 유의해도 비율 차이가 이보다 작으면 판매자에게 의미가 없다고 보고 알리지 않는다.
# 0.05 = 5%p. 실험하며 조정한다.
MIN_RATE_DELTA: float = 0.05
