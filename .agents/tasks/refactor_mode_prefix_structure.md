# Task: 어제 작성된 Mode/Model 스크립트 단일 폴더 이동 및 파일 Prefix 통일

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/refactor_mode_prefix_structure.md

## 목표
Git 이력 확인 결과 어제(8월 11일) 추가된 4개 예측 모드(Mode) 스크립트들을 단일 폴더(`src/modes/` 또는 `src/models/`)로 수집하고, 파일명 Prefix를 `mode_` 형태로 명확하게 통일하여 가독성을 높인다.

## Git 이력 분석 결과 (어제 작성된 4개 Mode 스크립트)
1. `stock_predictor.py` → Mode 1: 1년 워크포워드 백테스팅 기본 예측기
2. `two_year_predictor.py` → Mode 2: 2년 기간 주간 수익률 분석 예측기
3. `model3_predictor.py` → Mode 3: 시가 갭상승 및 기술지표 고도화 예측기
4. `pattern_predictor.py` → Mode 4: 차트 패턴 유사도 매칭 예측기

## 대상 변경 파일 및 Prefix 통일 규칙 (`Coder-Cline` 워크스페이스 기준)

### 1. 단일 폴더 위치: `src/modes/` (또는 `src/models/`)
모든 모드 스크립트의 파일명 Prefix를 `mode_<번호>_` 형식으로 일치시킵니다:

| 기존 파일명 | 변경 후 통일 파일명 (`src/modes/` 내) | 모드 설명 |
| :--- | :--- | :--- |
| `stock_predictor.py` | **`mode_1_stock_predictor.py`** | Mode 1: 1년 백테스팅 기본 예측기 |
| `two_year_predictor.py` | **`mode_2_two_year_predictor.py`** | Mode 2: 2년 데이터 주간 예측기 |
| `model3_predictor.py` | **`mode_3_gap_predictor.py`** | Mode 3: 갭상승 & 기술지표 고도화 예측기 |
| `pattern_predictor.py` | **`mode_4_pattern_predictor.py`** | Mode 4: 차트 패턴 유사도 매칭 예측기 |

### 2. `src/modes/__init__.py` 모듈 내보내기 작성
```python
from .mode_1_stock_predictor import (
    get_ticker_by_name,
    fetch_market_data,
    feature_engineering,
    run_walk_forward_backtest
)
from .mode_2_two_year_predictor import (
    fetch_2year_data,
    analyze_2year_weekly_predictions
)
from .mode_3_gap_predictor import (
    run_model3,
    get_ticker_by_name as get_ticker_m3
)
from .mode_4_pattern_predictor import PatternPredictor

__all__ = [
    'get_ticker_by_name',
    'fetch_market_data',
    'feature_engineering',
    'run_walk_forward_backtest',
    'fetch_2year_data',
    'analyze_2year_weekly_predictions',
    'run_model3',
    'get_ticker_m3',
    'PatternPredictor'
]
```

### 3. `app.py` Import 구문 수정
변경된 `mode_` Prefix 통일 스크립트 이름에 맞추어 `app.py` 상단 import 구문을 수정:
```python
from src.modes import (
    get_ticker_by_name,
    fetch_market_data,
    feature_engineering,
    run_walk_forward_backtest,
    fetch_2year_data,
    analyze_2year_weekly_predictions,
    run_model3,
    get_ticker_m3,
    PatternPredictor
)
```

---

## 테스트 조건 (`Tester-Cline` 검증 조건)
- [ ] `Coder-Cline` 워크스페이스 내 `src/modes/` 폴더에 `mode_1_stock_predictor.py`, `mode_2_two_year_predictor.py`, `mode_3_gap_predictor.py`, `mode_4_pattern_predictor.py` 4개 파일이 정확히 생성됨.
- [ ] `py -c "import app; print('Mode prefix refactor success!')"` 명령 실행 시 에러 없이 성공 메시지 출력.
- [ ] `py tests/test_2yr_web.py` 실행시 정상 작동.

---

## Coder 실행 가이드 (Cline Agent)

```
작업 디렉토리: C:\Users\gosys\orca\workspaces\my_stock_auto\Coder-Cline
브랜치: Younseob/Coder-Cline

.agents/tasks/refactor_mode_prefix_structure.md 파일(Task 명세)을 읽고
어제 생성된 4개 mode 스크립트를 src/modes/ 폴더로 수집하고 mode_<번호>_ prefix로 변경해줘.
수정 후 app.py import 경로도 변경하고 커밋해줘.
```
