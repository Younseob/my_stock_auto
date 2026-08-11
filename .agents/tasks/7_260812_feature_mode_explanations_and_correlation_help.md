# Task: 7_260812_feature_mode_explanations_and_correlation_help.md - Mode 1~4 상세 설명 및 상관관계 지표 도움말 추가

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/7_260812_feature_mode_explanations_and_correlation_help.md
> 생성일: 2026-08-12

## 목표
1. 처음 방문한 사용자도 한눈에 이해할 수 있도록 웹 UI(`templates/index.html`)에 **Mode 1 ~ Mode 4 예측 모델별 직관적인 쉬운 설명 안내 카드/도움말 모달**을 추가한다.
2. 분석 결과 카드 내의 **피쳐 중요도 및 상관관계 지표(RSI, MACD, 외국인/기관 수급, 갭비율 등)가 의미하는 바를 자세히 설명하는 안내 도움말 표/툴팁**을 구현한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. Mode 1 ~ Mode 4 쉬운 설명 가이드 카드 (`templates/index.html`)
- 상단 모드 선택 탭 하단에 **"💡 Mode별 분석 가이드"** 서브 카드/안내 박스 추가:
  - **Mode 1 (1년 백테스팅기)**: *"1년간 주가 데이터를 기반으로 AI가 매일 매매하는 가상 전략을 검증하고, 내일 상승/하락 확률을 예측합니다."*
  - **Mode 2 (2년 주간분석기)**: *"최근 2년간의 주간 단위 흐름을 종합 분석하여 중장기적인 투자 승률과 이번 주 주가 향방을 제시합니다."*
  - **Mode 3 (시가 갭상승 & 수급분석기)**: *"코스피 지수, 외국인/기관 수급, 거래량을 기계학습으로 분석하여 다음날 장 시작 시 시가 갭상승(시가 변동) 가능성을 예측합니다."*
  - **Mode 4 (차트 패턴 매칭기)**: *"과거 10년간의 주가 차트 중 현재 주가 흐름과 가장 유사한 top 5 과거 차트 패턴을 찾아내어 내일의 움직임을 추정합니다."*

### 2. 상관관계 및 피쳐 중요도 항목 상세 도움말 (`templates/index.html`)
- 피쳐 분석 결과 영역 하단에 **"🔍 상관관계 & 피쳐 지표 상세 설명"** 안내Accordion 또는 Modal/Help Box 추가:
  - **외국인/기관 순매수 (Foreigner/Institution Net Buying)**: 주가 상승을 이끄는 메이저 주포 세력의 수급 유입 여부 (양수일수록 상승 영향력 높음).
  - **RSI (상대강도지수, Relative Strength Index)**: 주가의 과매수(70 이상) / 과매도(30 이하) 상태를 나타내는 기술적 지표.
  - **MACD (이동평균수렴조음)**: 단기 이동평균선과 장기 이동평균선의 교차를 통해 추세 전환점을 포착하는 지표.
  - **시가 갭비율 (Open Gap Pct)**: 전일 종가 대비 당일 시가 형성 형성 폭 (수급 강도 반영).
  - **코스피 변동률 (KOSPI Return)**: 전체 시장 대세 상승/하락 분위기가 해당 종목에 미치는 커플링 영향력.
  - **볼린저 밴드 (Bollinger Bands)**: 주가의 변동성 범위 상한/하한 이탈 여부 측정.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 웹 화면 상단에 Mode 1~4 친절 설명 안내 영역 정상 노출
- [ ] 분석 결과 하단에 상관관계 지표 상세 설명 도움말 정상 노출
- [ ] `py -m unittest tests/test_web_server_live.py` 100% PASS 검증

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -m unittest tests/test_web_server_live.py
```
