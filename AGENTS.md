# AI 코딩 도구용 규칙 (Review Intelligence)

이 저장소에서 코드를 작성하는 모든 AI 도구는 아래 규칙을 따른다.
작업 전 `docs/DATA_FORMAT.md`와 `core/schemas.py`를 먼저 읽는다.

## 프로젝트
- 온라인 판매자가 리뷰 CSV를 올리면 AI가 감정·불만 유형을 분류하고,
  불만 비율이 '의미 있게' 늘었는지(급증)와 개선 조치 전후로 바뀌었는지를 판정한다.
- Python 3.11 이상, 화면 Streamlit, 분석 pandas, 시각화 Plotly, LLM Gemini(`google-genai`), 저장 SQLite.
- 3명이 각자 AI 도구로 개발한 뒤 합친다. 그래서 형식과 경로 규칙이 가장 중요하다.

## 반드시 지킬 것
1. **데이터 형식은 `core/schemas.py`만 사용한다.** 새 dict 형식을 임의로 만들지 않는다. 바꿔야 하면 코드를 고치지 말고 사용자에게 알린다.
2. **함수 이름과 입출력은 `docs/DATA_FORMAT.md`와 일치해야 한다.** 이미 있는 함수의 이름, 인자, 반환형을 바꾸지 않는다.
3. **LLM 호출은 `core/llm.py`의 `call_llm_json()`으로만 한다.** 다른 파일에서 `google.genai`를 import하지 않는다. 다른 LLM SDK를 추가하지 않는다.
4. **변화 판정은 `core/stats.py`의 `judge_change()`로만 한다.** 임계값을 코드에 따로 쓰지 않는다(`core/config.py`의 값을 쓴다). LLM에게 "급증인지" 묻지 않는다.
5. **담당 경로 밖의 파일을 수정하지 않는다.**
   - 엔진·분석: `engine/`, `analysis/`, `prompts/`, `tests/test_engine_*.py`, `tests/test_analysis_*.py`
   - 화면·입출력: `app.py`, `ui/`, `ingest/`, `storage/`, `tests/test_ui_*.py`, `tests/test_ingest_*.py`, `tests/test_storage_*.py`
   - 실험: `experiments/`, `labeling/`, `docs/EXPERIMENTS.md`
   - `core/`, `docs/DATA_FORMAT.md`, `AGENTS.md`, `requirements.txt`는 팀장만 수정한다.
6. **라이브러리를 새로 추가하지 않는다.** 꼭 필요하면 이유와 함께 사용자에게 제안만 한다.
7. **API 키와 비밀 값은 코드에 쓰지 않는다.** `core/config.py`를 통해 `.env`에서 읽는다.
8. **프롬프트 문구는 `prompts/`의 텍스트 파일에 둔다.** 파이썬 코드 안에 긴 프롬프트를 넣지 않는다.
9. **리뷰를 웹에서 크롤링하는 코드를 만들지 않는다.** 데이터는 업로드된 파일과 공개 데이터셋만 쓴다.

## 화면 문구 규칙
- 전후 비교 결과에 '효과', '덕분에', '개선되었습니다'를 쓰지 않는다. '변화', '감소', '증가'만 쓴다. 변화의 원인은 판단하지 않는다.
- 판정이 `insufficient_data`면 수치 대신 "표본 부족 (판단 보류)"를 보여준다.
- 화면과 보고서의 불만 유형 이름은 `COMPLAINT_KO`, 판정 이름은 `VERDICT_KO`를 쓴다.

## 코드 스타일
- 타입 힌트를 쓴다. 공개 함수에는 한국어 docstring으로 의도와 입출력을 적는다.
- 주석은 "왜 이렇게 했는지"를 한국어로 쓴다.
- 예외를 삼키지 않는다. 사용자에게 보여줄 오류는 화면 쪽에서 처리한다.
- 추측으로 코드를 쓰지 않는다. 라이브러리 사용법이 확실하지 않으면 공식 문서를 확인하거나, 확인이 필요하다고 사용자에게 말한다.

## 개발 시
- 화면·분석 개발은 `.env`의 `USE_MOCK=1`로 한다. 가짜 엔진이 연결되어 API 키 없이 돌아간다.
- 엔진은 리뷰를 `config.BATCH_SIZE`개씩 묶어 한 번에 보낸다. 리뷰마다 호출하지 않는다.

## 작업을 마칠 때
- `pytest`를 실행해 통과를 확인한다.
- 무엇을 바꿨고 어떻게 확인했는지 3줄 이내로 요약한다. 이 요약이 PR 설명이 된다.
