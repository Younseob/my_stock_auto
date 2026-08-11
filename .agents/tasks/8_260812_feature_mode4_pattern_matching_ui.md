# Task: 8_260812_feature_mode4_pattern_matching_ui.md - Mode 4 차트 패턴 매칭 웹 UI 렌더링 연동

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/8_260812_feature_mode4_pattern_matching_ui.md
> 생성일: 2026-08-12

## 장애 및 부족 현상
백엔드(`app.py`)에는 `POST /api/predict_pattern` (Mode 4 차트 패턴 매칭 엔드포인트)가 정상 구현되어 있으나, 프론트엔드 웹 UI(`templates/index.html`)에 Mode 4 전용 결과 렌더링 영역 및 JS API 호출 로직이 누락되어 있어 웹에서 Mode 4 결과가 노출되지 않음.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. Frontend Mode 4 탭 선택 및 API 호출 연동 (`templates/index.html`)
- Mode 4 탭 선택 후 [분석 실행] 시 `/api/predict_pattern` 비동기 호출.
- Payload: `{ "stock_name": stockName }`

### 2. Mode 4 전용 결과 UI 카달로그 렌더링 (`templates/index.html`)
- **Mode 4 예측 결과 요약 카드**:
  - 내일 예측 방향 (`tomorrow_pred`: 상승 🔺 / 하락 🔻)
  - 평균 예상 수익률 (`avg_return` %)
  - 과거 패턴 매칭 상승 확률 (`up_prob` %)
- **Top 5 유사 차트 패턴 목록 테이블**:
  - 순위 (Rank 1~5)
  - 과거 기간 (`start_date` ~ `end_date`)
  - 유사도 점수 (`similarity` %)
  - 익일 주가 변동률 (`d_plus_1_return` %)
- **현재 차트 vs 유사 차트 시각화**:
  - `Chart.js`를 활용하여 현재 20일 주가 흐름과 Top 1 유사 차트 흐름 비교 라인 차트 렌더링.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] Mode 4 탭 선택 후 검색 시 `/api/predict_pattern` 정상 호출 및 200 OK
- [ ] Top 5 유사 과거 패턴 테이블 및 내일 예측 결과 카드 정상 노출
- [ ] `py -m unittest tests/test_web_server_live.py` 100% PASS 검증

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -m unittest tests/test_web_server_live.py
```
