# 데이터 형식과 함수 약속

각자 개발해도 합칠 수 있도록 고정한 약속이다. 실제 정의는 `core/schemas.py`이고, 둘이 다르면 코드가 기준이다.

## 전체 흐름

```
CSV·엑셀 업로드
  → read_table()                  표 (pandas DataFrame)
  → 화면에서 열 지정 (ColumnMapping)
  → to_reviews()                  list[Review] + 경고
  → unlabeled()                   아직 분류 안 된 리뷰만
  → classify_reviews()            list[ReviewLabel]   ← Gemini, 50건씩 묶음
  → save_reviews()
  → load_all()                    전체 리뷰 + 분류 결과
  → aggregate_by_period()         list[PeriodStat]
  → detect_spikes()               list[SpikeAlert]    ← core.stats.judge_change
  → compare_before_after()        list[BeforeAfter]   ← core.stats.judge_change
  → 대시보드, 보고서
```

## 함수

| 함수 | 위치 | 입력 | 출력 | 담당 |
|---|---|---|---|---|
| `read_table(data, filename)` | `ingest.csv_loader` | `bytes`, `str` | `DataFrame` | B |
| `to_reviews(df, mapping)` | `ingest.csv_loader` | `DataFrame`, `ColumnMapping` | `(list[Review], list[str])` | B |
| `classify_reviews(reviews)` | `engine` | `list[Review]` | `list[ReviewLabel]` (같은 순서·개수) | A |
| `save_reviews(reviews, labels)` | `storage.db` | | `int` (새로 저장한 수) | B |
| `unlabeled(reviews)` | `storage.db` | `list[Review]` | `list[Review]` | B |
| `load_all(product_id=None)` | `storage.db` | | `(list[Review], list[ReviewLabel])` | B |
| `aggregate_by_period(reviews, labels, freq="W")` | `analysis.trends` | | `list[PeriodStat]` | A |
| `detect_spikes(stats)` | `analysis.trends` | `list[PeriodStat]` | `list[SpikeAlert]` | A |
| `compare_before_after(reviews, labels, product_id, change_date, window_days=None)` | `analysis.trends` | | `list[BeforeAfter]` | A |
| `judge_change(base_count, base_total, target_count, target_total, increase_only=False)` | `core.stats` | | `(p값 또는 None, Verdict)` | 완료 |
| `call_llm_json(prompt, schema, system=None, temperature=0.0)` | `core.llm` | | `schema` 인스턴스 | 완료 |

분류 엔진은 `from engine import classify_reviews`로 가져온다. `engine.mock`이나 `engine.classify`를 직접 가져오지 않는다.

## 데이터 모델 요약

### Review
`review_id: str`, `product_id: str = "default"`, `text: str`, `rating: int | None`, `created_at: date | None`

### ReviewLabel
`review_id: str`, `sentiment: positive | negative | neutral`, `complaints: list[Complaint]`, `source: "ai" | "human:<이름>" | "consensus"`

AI 결과와 사람 라벨이 같은 형식이라 바로 대조할 수 있다.

### Complaint (불만 유형)
`delivery` 배송, `defect` 품질·불량, `mismatch` 사이즈·설명 불일치, `price` 가격, `packaging` 포장, `service` 고객응대·교환반품, `other` 기타. 정의는 `labeling/LABEL_GUIDE.md`.

### PeriodStat
`product_id`, `period_start: date`, `total: int`, `complaint_counts: dict[Complaint, int]` (모든 유형 키 포함, 없으면 0)

### RateChange → SpikeAlert, BeforeAfter
`product_id`, `complaint`, `base_count`, `base_total`, `target_count`, `target_total`, `base_rate`, `target_rate`, `p_value: float | None`, `verdict`
- `SpikeAlert`: + `period_start`. base = 직전 기간, target = 이번 기간
- `BeforeAfter`: + `change_date`. base = 조치 전, target = 조치 후

### Verdict
`increased` 의미 있는 증가, `decreased` 의미 있는 감소, `no_change` 변화 없음, `insufficient_data` 표본 부족

## 판정 규칙 (`core/stats.py`)

- 어느 한 구간이라도 리뷰가 `MIN_PERIOD_REVIEWS`(20)건 미만 → `insufficient_data`
- Fisher 정확 검정. 급증은 단측(증가만), 전후 비교는 양측
- p < `ALPHA`(0.05) **그리고** 비율 차이 ≥ `MIN_RATE_DELTA`(5%p)일 때만 증가·감소
- 값은 `core/config.py`에서만 바꾼다

## 규칙

- 집계와 판정은 LLM에 맡기지 않는다.
- 형식을 바꿔야 하면 이슈를 열고 팀장이 `core/schemas.py`, 이 문서, `engine/mock.py`, 테스트를 함께 고친다.
