# Task: 9_260812_feature_correlation_korean_labels_and_descriptions.md - 상관관계 분석 지표 영문 약어 한글화 및 상세 의미 카드 렌더링

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/9_260812_feature_correlation_korean_labels_and_descriptions.md
> 생성일: 2026-08-12

## 목표
상관관계 분석 결과 카드에 표시되는 영어 약어 지표명(`ret_3d`, `vol_ratio`, `rsi` 등 10개 피쳐)을 처음 보는 사용자도 직관적으로 이해할 수 있도록 **"한글 명칭 (영문약어) + 수치 해석(양수/음수) + 친절한 지표 설명"** 포맷으로 렌더링을 강화한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. 지표 맵핑 딕셔너리 구축 (`templates/index.html`)
영어 약어 키값을 한글 명칭과 설명으로 매핑하는 JS 객체 추가:
- `ret_3d`: **최근 3일간 누적 수익률** (최근 3일 급등 시 차익실현 하락 가능성 반영)
- `vol_ratio`: **거래량 폭발 비율** (5일 평균 대비 당일 거래량 급증 강도, 상승 에너지)
- `rsi`: **RSI 과매수/과매도 심리지수** (70 이상 단기 과열 경계, 30 이하 반등)
- `relative_strength`: **시장 대비 상대강도** (코스피 지수 대비 종목 우위 주도주 여부)
- `kospi_chg`: **코스피 지수 변동률** (전체 증시 대세 상승/하락 동조화 영향)
- `kospi_gap`: **코스피 시가 갭 변동률** (전체 시장의 장 시작 수급 모멘텀)
- `kospi_intraday`: **코스피 장중 변동폭** (시장 전체의 장중 흔들림 변동성)
- `kospi_close_pos`: **코스피 종가 위치** (시장 지수의 고가/저가 대비 종가 마감 위치)
- `close_chg`: **전일 대비 종가 변동률** (당일 종가의 일별 상승/하락폭)
- `close_position`: **당일 캔들 종가 위치** (고가/저가 캔들 내에서 매수세가 마감된 위치)

### 2. Frontend 렌더링 강화 (`templates/index.html`)
- 상관관계 리스트 렌더링 시 단순히 `ret_3d: -0.2012`로 출력하는 대신:
  - **한글 뱃지/라벨**: `최근 3일 누적 수익률 (ret_3d)`
  - **상관관계 수치**: `-0.2012` (음수: 붉은색/연보라, 양수: 초록색/파란색)
  - **지표 의미 도움말**: 마우스 호버(Tooltip) 또는 하단 상세 가이드 카드로 설명 노출.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 웹 화면 상관관계 피쳐 리스트에 `ret_3d` 대신 "최근 3일 누적 수익률 (ret_3d)" 등 한글 명칭 정상 노출
- [ ] 10개 지표 전체에 대한 친절한 해석 가이드 정상 표시
- [ ] `py -m unittest tests/test_web_server_live.py` 100% PASS 검증

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -m unittest tests/test_web_server_live.py
```
