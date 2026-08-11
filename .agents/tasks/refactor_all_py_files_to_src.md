# Task: 프로젝트 내 모든 Python 파일 기능별 src/ 폴더 수집 및 모듈화

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/refactor_all_py_files_to_src.md

## 목표
루트 디렉토리에 혼재되어 있는 모든 `.py` 파일들을 기능별로 `src/` 하위 모듈(`src/modes/`, `src/db/`, `src/web/`) 및 `tests/` 폴더로 분리 수집하여 프로젝트 가독성 및 유지보수성을 극대화한다.

## 대상 파일 기능별 이동 및 분류 규칙 (`Coder-Cline` 워크스페이스 기준)

### 1. 기능별 이동 분류표

| 기존 파일 위치 | 이동 후 위치 | 기능 설명 |
| :--- | :--- | :--- |
| `stock_predictor.py` | `src/modes/mode_1_stock_predictor.py` | Mode 1 예측 모델 |
| `two_year_predictor.py` | `src/modes/mode_2_two_year_predictor.py` | Mode 2 예측 모델 |
| `model3_predictor.py` | `src/modes/mode_3_gap_predictor.py` | Mode 3 예측 모델 |
| `pattern_predictor.py` | `src/modes/mode_4_pattern_predictor.py` | Mode 4 예측 모델 |
| `database.py` | `src/db/database.py` | 데이터베이스 & 캐시 처리 모듈 |
| `app.py` | `src/web/app.py` | Flask 메인 웹 애플리케이션 |
| `test_2yr_web.py` | `tests/test_2yr_web.py` | 웹 통합 테스트 스크립트 |
| `test_server.py` | `tests/test_server.py` | 서버 헬스체크 테스트 스크립트 |

---

### 2. 패키지 내보내기 정의 (`__init__.py`)

#### ① `src/modes/__init__.py`
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

#### ② `src/db/__init__.py`
```python
from .database import *
```

#### ③ `src/web/__init__.py`
```python
from .app import app
```

---

### 3. Import 경로 및 DB 경로 업데이트

- `src/web/app.py` 내부 import 구문:
  ```python
  import sys
  import os
  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

  from src.db import database as db
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
- `src/db/database.py` DB 경로 업데이트:
  `DB_PATH = os.path.join(BASE_DIR, 'data', 'stock_cache.db')`

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] `Coder-Cline` 워크스페이스 내 `src/modes/`, `src/db/`, `src/web/`, `tests/` 구조 완성
- [ ] `py -c "from src.web.app import app; print('All py files refactored successfully!')"` 실행 시 성공
- [ ] `py tests/test_2yr_web.py` 실행 시 정상 작동

---

## Coder 지시문

```
작업 디렉토리: C:\Users\gosys\orca\workspaces\my_stock_auto\Coder-Cline
브랜치: Younseob/Coder-Cline

.agents/tasks/refactor_all_py_files_to_src.md 명세를 읽고 모든 .py 파일들을 기능별로 src/ 및 tests/ 하위 폴더로 이동 후 import 수정을 진행하고 커밋해줘.
```
