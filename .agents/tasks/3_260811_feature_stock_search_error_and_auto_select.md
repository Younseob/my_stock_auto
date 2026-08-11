# Task: 3_260811_feature_stock_search_error_and_auto_select.md - 종목 검색 오타 에러 처리, 단일 종목 자동 이동 및 다중 종목 선택 UI

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/3_260811_feature_stock_search_error_and_auto_select.md
> 생성일: 2026-08-11

## 목표
1. 존재하지 않는 종목명이나 오타 입력(예: "하이닉시") 시, 서버 크래시 없이 **"검색된 종목이 없습니다." 에러 알림**을 웹 화면에 명확히 표시한다.
2. 매칭되는 종목이 단 1개일 경우(예: "하이닉스" $\rightarrow$ "SK하이닉스") 클릭 필요 없이 **자동으로 해당 종목 분석 실행 화면으로 이동**한다.
3. 매칭되는 종목이 여러 개일 경우(예: "삼성" $\rightarrow$ "삼성전자", "삼성SDI" 등) 화면에 **종목 선택 리스트/드롭다운을 제공**하여 사용자가 원하는 종목을 직접 선택할 수 있게 한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. Backend Search API 강화 (`src/web/app.py` 또는 `app.py`)
- `GET /api/search_stock?query=<키워드>`
  - 키워드로 pykrx 종목 목록 부분 매칭 검색 (대소문자 구분 없음, 공백 제거 처리).
  - **매칭 0개일 경우**: `{ "status": "error", "message": "'하이닉시'에 해당하는 종목을 찾을 수 없습니다. 정확한 종목명을 입력하세요." }` 404/200 반환.
  - **매칭 1개일 경우**: `{ "status": "single", "item": { "name": "SK하이닉스", "ticker": "000660" } }`
  - **매칭 2개 이상일 경우**: `{ "status": "multiple", "count": 3, "items": [...] }`

### 2. Frontend 검색 및 자동 이동/선택 UI (`templates/index.html`)
- **검색창 입력 이벤트 처리**:
  - 검색어 입력 후 [분석 실행] 버튼 클릭 또는 엔터 키 입력 시 `/api/search_stock?query=` 비동기 호출.
  - **`status == 'error'`**: 빨간색 경고 알림(`alert-danger`) 노출.
  - **`status == 'single'`**: 검색창 입력값을 매칭된 정식 종목명(예: "SK하이닉스")으로 자동 대입하고 **즉시 주가 예측 API 호출 및 분석 화면으로 자동 이동**.
  - **`status == 'multiple'`**: 검색창 하단에 연관 종목 선택 리스트(버튼 그룹 또는 드롭다운)를 표시하고, 사용자가 종목을 클릭하면 해당 종목으로 설정 후 분석 실행.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 오타 검색어 `query=하이닉시` 입력 시 에러 알림 메시지 노출 확인 (서버 500 에러 없음)
- [ ] `query=하이닉스` 입력 시 `SK하이닉스`로 자동 선택되어 1년/2년/Model3 예측 화면으로 자동 이동
- [ ] `query=삼성` 입력 시 다중 선택 종목 리스트 노출 및 클릭 시 선택 종목 예측 정상 구동

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -c "import app; print('Stock search & auto select feature ready!')"
```
