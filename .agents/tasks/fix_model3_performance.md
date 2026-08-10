# Task: Model 3 성능 최적화 및 Render 504 타임아웃 방지

## 원인 분석
Render 무료 서버(0.1 vCPU)에서 `/api/predict_model3` 최초 계산 시:
1. `walk_forward_backtest` 루프 165회에서 매번 `GradientBoostingClassifier(n_estimators=100)` 트리를 16,500개 순차 생성함.
2. 연산 시간이 30초를 초과하여 Render 리버스 프록시가 504 Gateway Timeout HTML 페이지(`<html>...`)를 반환함.
3. 웹 프론트엔드가 HTML 응답을 JSON으로 파싱하려다 `SyntaxError: Unexpected token '<'` 발생.

## 목표
- Model 3 연산 속도를 **30초 이내(약 3~5초)**로 10배 이상 단축
- 웹 프론트엔드에서 HTML 에러 응답 시 예외 처리 강화

## 대상 파일
- `model3_predictor.py`
- `templates/index.html`

## 구현 명세

### 1. `model3_predictor.py` 최적화
- **Walk-Forward 재학습 주기 변경**: 매일(1일) 재학습 $\rightarrow$ **5영업일(주 1회) 간격 재학습** (루프 165회 $\rightarrow$ 33회로 80% 감소)
- **GradientBoostingClassifier 파라미터 경량화**: `n_estimators=40`, `max_depth=3`, `learning_rate=0.1`
- **데이터 기간 조절**: 수집 데이터 `days=300` (1년 영업일 250일 기준 충분)

### 2. `templates/index.html` 에러 처리 강화
- `fetch` 응답이 JSON이 아닌 HTML(504/502 등)일 경우 "서버 응답 시간 초과(Timeout). 다시 시도해 주세요." 경고창 표시

## 테스트 조건
- [ ] `py model3_predictor.py --name 씨에스윈드` 실행 5초 이내 완료 확인
- [ ] 백테스트 적중률, 수익률 정상 출력 확인
- [ ] `git push origin master` 후 Render 자동 배포 및 웹 동작 확인
