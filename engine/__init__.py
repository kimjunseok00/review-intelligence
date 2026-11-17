"""분류 엔진 진입점. 다른 코드는 항상 `from engine import classify_reviews`로 가져온다.

USE_MOCK=1이면 가짜 구현이, 0이면 Gemini 구현이 연결된다.
함수 이름과 입출력을 똑같이 맞춰 두었으므로 호출하는 쪽은 어느 쪽인지 몰라도 된다.
"""

from core import config

if config.USE_MOCK:
    from engine.mock import classify_reviews
else:
    from engine.classify import classify_reviews

__all__ = ["classify_reviews"]
