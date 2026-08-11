# Task: 프로젝트 디렉토리 구조 리팩토링 및 모델 패키지 모듈화

> Orchestrator → Cline 구현 명세 전달 파일
> 경로: .agents/tasks/refactor_project_structure.md

## 목표
루트 디렉토리에 혼재되어 있던 모델 스크립트, DB 모듈, 테스트 파일, 데이터베이스 파일들을 표준 Python 패키지 구조(`src/`, `tests/`, `data/`)로 리팩토링하여 코드 가독성 및 유지보수성을 극대화한다.

## 대상 변경 디렉토리 구조

```
my_stock_auto/
├── src/                          # 소스 코드 전용 모듈 디렉토리
│   ├── models/                   # 예측 모델 모듈 패키지
│   │   ├── __init__.py           # 모델 내보내기 (Import 래퍼)
│   │   ├── stock_predictor.py    # Model 1: 기본 예측 모델
│   │   ├── two_year_predictor.py # Model 2: 2년 기간 데이터 예측 모델
│   │   ├── model3_predictor.py   # Model 3: 거래량/기술지표 고도화 모델
│   │   └── pattern_predictor.py  # Model 4: 차트 패턴 매칭 예측 모델
│   ├── db/                       # 데이터베이스 모듈 패키지
│   │   ├── __init__.py
│   │   └── database.py           # SQLite DB 관리 모듈
│   └── web/                      # 웹 애플리케이션 패키지
│       ├── __init__.py
│       └── app.py                # Flask 메인 애플리케이션
├── tests/                        # 테스트 스크립트 디렉토리
│   ├── test_2yr_web.py
│   └── test_server.py
├── data/                         # 로컬 데이터 및 DB 캐시 디렉토리
│   └── stock_cache.db            # SQLite 데이터베이스 파일
├── templates/                    # HTML 템플릿
├── app.py                        # 루트 실행 엔트리포인트 (python app.py 호환용)
├── requirements.txt
├── Procfile
└── AGENTS.md
```

## 구현 명세

### 1. 디렉토리 생성 및 파일 이동
- `src/models/`, `src/db/`, `src/web/`, `tests/`, `data/` 디렉토리 생성
- `model3_predictor.py`, `pattern_predictor.py`, `stock_predictor.py`, `two_year_predictor.py` → `src/models/`로 이동
- `database.py` → `src/db/`로 이동
- `test_2yr_web.py`, `test_server.py` → `tests/`로 이동
- `stock_cache.db` → `data/`로 이동

### 2. `src/models/__init__.py` 작성 (모델 패키지 모듈화)
각 모델의 핵심 Predictor 함수/클래스를 한곳에서 깔끔하게 import 할 수 있도록 `__init__.py` 정의:
```python
from .stock_predictor import predict_stock
from .two_year_predictor import predict_two_year
from .model3_predictor import predict_model3
from .pattern_predictor import PatternPredictor

__all__ = [
    'predict_stock',
    'predict_two_year',
    'predict_model3',
    'PatternPredictor'
]
```

### 3. `src/db/__init__.py` 작성
```python
from .database import *
```

### 4. `app.py` 및 관련 파일 Import 경로 수정
- `import database as db` → `from src.db import database as db` (또는 `stock_cache.db` 경로를 `data/stock_cache.db`로 수정)
- `from stock_predictor import ...`, `from two_year_predictor import ...`, `from model3_predictor import ...` 
  → `from src.models import predict_stock, predict_two_year, predict_model3, PatternPredictor`로 변경
- 루트 `app.py`에서 `src/web/app.py`를 실행하거나 직접 `src` 패키지를 참조할 수 있도록 `sys.path` 설정 추가.

### 5. `data/stock_cache.db` 경로 호환성 처리
- `database.py` 내부의 DB 파일 지정 경로를 `data/stock_cache.db` 또는 상대 경로 대응으로 수정하여 DB 파일 이관 시 정상 접속 되도록 보장.

---

## 테스트 조건
Cline이 아래 테스트 명령을 실행하고 모두 통과해야 함:

- [ ] `py app.py` 또는 `py src/web/app.py` 실행시 에러 없이 서버 정상 시작 (exit code 0 또는 정상 대기)
- [ ] `py tests/test_2yr_web.py` 실행 시 정상 동작 확인
- [ ] Import Error (ModuleNotFoundError 등) 전혀 발생하지 않음 확인

---

## Cline 실행 가이드

```
.agents/tasks/refactor_project_structure.md 파일(Task 명세)을 읽고
프로젝트 디렉토리 구조 생성, 파일 이동, import 경로 수정을 순서대로 진행해줘.
모든 작업 완료 후 py app.py 및 py tests/test_2yr_web.py를 실행하여 오류가 없는지 테스트해줘.
```

## 완료 기준
- 디렉토리 구조 정상 변경 완료 (`src/models`, `src/db`, `src/web`, `tests`, `data`)
- 모든 파이썬 파일의 import 오류 해결
- 테스트 실행 통과 및 결과 Orchestrator에 보고
