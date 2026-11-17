"""CSV·엑셀 업로드를 Review 목록으로 바꾼다. (이슈 #1, 팀원 B)"""

import pandas as pd

from core.schemas import ColumnMapping, Review


class IngestError(ValueError):
    """파일을 읽을 수 없거나 열 지정이 잘못됐을 때. 화면에서 안내 문구로 보여준다."""


def read_table(data: bytes, filename: str) -> pd.DataFrame:
    """업로드된 파일을 표로 읽는다.

    - .csv: UTF-8(BOM 포함)로 먼저 읽고, 실패하면 CP949로 다시 읽는다(한국 엑셀에서 저장한 CSV).
    - .xlsx: 첫 번째 시트를 읽는다. (openpyxl이 필요하면 팀장에게 requirements 추가를 요청)
    - 그 외 확장자, 빈 파일은 IngestError.
    """
    raise NotImplementedError("이슈 #1에서 구현")


def to_reviews(df: pd.DataFrame, mapping: ColumnMapping) -> tuple[list[Review], list[str]]:
    """표와 열 지정을 받아 Review 목록을 만든다.

    Returns:
        (리뷰 목록, 경고 목록). 경고 예: "본문이 빈 행 12개를 건너뜀", "날짜를 읽지 못한 행 3개".
        빈 본문 행은 건너뛴다. 날짜를 못 읽은 행은 created_at=None으로 둔다.

    구현 안내:
        - 날짜는 pd.to_datetime(errors="coerce")로 읽는다. "2026.11.03", "2026-11-03 14:22" 등 형식이 섞여 있다.
        - 평점은 정수로 바꾸고, 1~5 밖이면 None.
        - review_id 열이 없으면 "row-<행번호>"로 만든다.
        - mapping에 적힌 열이 표에 없으면 IngestError.
    """
    raise NotImplementedError("이슈 #1에서 구현")
