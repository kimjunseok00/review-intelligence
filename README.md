# Review Intelligence

온라인 판매자를 위한 리뷰 불만 변화 추적 서비스.
리뷰 CSV를 올리면 AI가 감정과 불만 유형을 분류하고, 불만 비율이 **우연한 변동이 아니라 의미 있게** 늘었는지 판정해 알려 준다.

- **급증 탐지**: 직전 기간 대비 특정 불만 비율이 통계적으로 의미 있게 늘었는지
- **전후 비교**: 판매자가 입력한 개선 조치 날짜 전후로 불만 비율이 바뀌었는지 (원인은 판단하지 않음)
- **보고서**: 상품별 문제 요약과 우선 확인 항목

## 실행 방법

Python 3.11 이상.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
streamlit run app.py
pytest
```

처음에는 `.env`의 `USE_MOCK=1` 상태라 API 키 없이 가짜 엔진으로 돌아간다.
실제 Gemini를 쓰려면 `.env`에 `GEMINI_API_KEY`를 넣고 `USE_MOCK=0`으로 바꾼다.

## 폴더 구조와 담당

| 경로 | 내용 | 담당 | 상태 |
|---|---|---|---|
| `core/schemas.py` | 데이터 형식 (팀의 약속) | 팀장 | 완료 |
| `core/llm.py` | Gemini 호출 함수 | 팀장 | 완료 |
| `core/stats.py` | 변화 판정 (Fisher 정확 검정) | 팀장 | 완료 |
| `engine/` | 리뷰 묶음 분류 | 팀원 A | `mock.py`만 완료 |
| `analysis/` | 기간 집계, 급증·전후 판정 연결 | 팀원 A | 빈 함수 |
| `ingest/` | CSV 읽기, 열 지정 | 팀원 B | 빈 함수 |
| `app.py`, `ui/` | 화면, 대시보드 | 팀원 B | 최소 화면 |
| `storage/` | SQLite 저장 | 팀원 B | 빈 함수 |
| `experiments/` | 일치도·성능 지표, 주입 실험 | 팀장 | 지표·주입 완료 |
| `labeling/` | 라벨 기준서, 라벨 파일 | 팀장 + 전원 | 기준서 초안 |
| `docs/` | 데이터 형식, 이슈, 실험 계획 | 팀장 | 완료 |

## 작업 규칙

1. `main`에 직접 올리지 않는다. 이슈마다 브랜치(`feat/2-batch-classify`)를 만들고 PR로 합친다.
2. 자기 담당 경로만 수정한다.
3. `.env`, API 키, 공개 데이터 원본은 올리지 않는다.
4. PR 설명에 "무엇을 어떻게 확인했는지"를 한 줄 쓴다.
5. PR 전에 `pytest`가 통과하는지 확인한다.

## AI 코딩 도구 사용법

- Claude Code, Codex 등 저장소를 읽는 도구: `AGENTS.md`(Claude Code는 `CLAUDE.md`)를 자동으로 읽는다.
- Claude, ChatGPT 채팅 화면: 대화 시작 시 `AGENTS.md`와 `docs/DATA_FORMAT.md`를 먼저 붙여 넣고, 자기 이슈 본문을 이어서 붙인다.

## 문서

- `docs/DATA_FORMAT.md`: 함수 이름, 입출력, 데이터 형식
- `docs/ISSUES.md`: 이슈 본문 (깃허브에 복사해서 등록)
- `docs/EXPERIMENTS.md`: 실험 계획과 사전에 정한 성공 기준
- `labeling/LABEL_GUIDE.md`: 사람과 AI가 함께 쓰는 분류 기준
