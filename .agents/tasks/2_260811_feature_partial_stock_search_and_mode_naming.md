# Task: 2_260811_feature_partial_stock_search_and_mode_naming.md - 종목 부분 검색/다중 종목 선택 및 Mode Naming 적용

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/2_260811_feature_partial_stock_search_and_mode_naming.md
> 생성일: 2026-08-11

## 목표
1. 웹 UI 및 API 상에서 `src/models/` 내 예측 모델들을 `Mode 1`, `Mode 2`, `Mode 3`, `Mode 4`로 직관적으로 구분 표기한다.
2. 종목명 일부 키워드 검색("하이닉스" $\rightarrow$ "SK하이닉스")을 지원하는 API(`/api/search_stock`)를 추가하고, 검색된 후보가 다수일 경우(예: "삼성" 입력 시) 웹 UI에서 사용자가 하나를 선택할 수 있도록 드롭다운/선택 모달 UI를 구현한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. 예측 모델 명칭 Mode 식별자 정리 (`src/models/__init__.py` & `src/web/app.py`)
- 웹 UI 및 API 결과 JSON에 Mode 명칭 추가:
  - **Mode 1**: 기본 1년 워크포워드 백테스트 (`predict_stock`)
  - **Mode 2**: 2년 기간 주간 예측 분석 (`predict_two_year`)
  - **Mode 3**: 시가 갭상승 & 기술지표 고도화 예측 (`predict_model3`)
  - **Mode 4**: 차트 패턴 유사도 매칭 예측 (`PatternPredictor`)

### 2. 종목 부분 검색 (Partial Search) API 구현 (`src/web/app.py`)
- 라우트: `GET /api/search_stock?query=<키워드>`
- 로직:
  - pykrx의 전체 종목 이름 목록 중 `query` 키워드가 부분 포함(contains / substring match)된 종목들을 리스트로 검색.
  - 예: `query="하이닉스"` $\rightarrow$ `[{"name": "SK하이닉스", "ticker": "000660"}]`
  - 예: `query="삼성"` $\rightarrow$ `[{"name": "삼성전자", "ticker": "005930"}, {"name": "삼성SDI", "ticker": "006400"}, ...]`
- 반환 포맷:
  ```json
  {
    "status": "success",
    "count": 2,
    "items": [
      {"name": "SK하이닉스", "ticker": "000660"}
    ]
  }
  ```

### 3. 웹 UI 다중 종목 선택 드롭다운/목록 구현 (`templates/index.html`)
- 검색어 입력 후 검색 시:
  - 1개 종목만 매칭되면 자동 선택되어 예측 실행.
  - 여러 개 종목이 매칭되면 검색창 하단에 **"연관 종목 선택" 드롭다운/목록**이 노출되어 사용자가 클릭하여 1개 종목을 최종 확정.
- 모드 구분 탭/배지 표시: `Mode 1`, `Mode 2`, `Mode 3`, `Mode 4` 배지 탭 추가.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] `/api/search_stock?query=하이닉스` 호출 시 `SK하이닉스 (000660)` 반환 확인
- [ ] `/api/search_stock?query=삼성` 호출 시 다수의 삼성 관련 종목 목록 반환 확인
- [ ] 웹 UI에서 부분 검색 및 다중 종목 선택 드롭다운 정상 클릭 작동
- [ ] Mode 1 ~ Mode 4 표기 정상 노출 확인

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -c "from src.web.app import app; print('App initialized for stock search & mode naming!')"
```
