# Task: <기능명>
> Orchestrator → Cline 구현 명세 전달 파일
> 경로: .agents/tasks/<task_name>.md

## 목표
<무엇을 구현하는가 — 한 문장으로 명확하게>

## 대상 파일 (pearlside worktree 기준)
- `<파일명>.py` — 신규 생성 / 수정 여부 명시

## 구현 명세

### 입력 (Input)
```
<파라미터명>: <타입> — <설명>
```

### 출력 (Output)
```
<반환값 형식 및 구조>
```

### 핵심 로직 (Core Logic)
1. <처리 단계 1>
2. <처리 단계 2>
3. <처리 단계 3>

### 사용 라이브러리
- `pykrx` — 주가 데이터 수집
- `pandas`, `numpy` — 데이터 처리
- `sklearn` / `lightgbm` — ML 모델
- 기타: <추가 라이브러리>

### 제약 조건
- NaN 값 처리: 반드시 안전하게 처리할 것
- Windows 인코딩: `sys.stdout.reconfigure(encoding='utf-8')` 최상단 적용
- pykrx 오류: try/except로 graceful fallback 처리

## 테스트 조건
Cline이 아래 명령을 실행하고 모두 통과해야 함:

- [ ] `py <파일명>.py --name 씨에스윈드` 실행 → exit code 0
- [ ] 출력에 에러 없음 (traceback 없음)
- [ ] 결과값이 합리적인 범위 내 (예: 적중률 0~100%, 수익률 -100%~+500%)
- [ ] JSON 직렬화 오류 없음 (NaN 없음)

## Cline 실행 가이드

```
작업 디렉토리: C:\Users\gosys\orca\workspaces\my_stock_auto\pearlside
브랜치: pearlside

이 파일(Task 명세)을 읽고 위 명세에 따라 구현해줘.
구현 완료 후 반드시 테스트 조건을 모두 실행하고 결과를 알려줘.
테스트 실패 시 스스로 수정하고 재테스트해줘.
```

## 완료 기준
- 모든 테스트 체크박스 통과
- pearlside 브랜치에 커밋 완료
- Orchestrator Reviewer에게 결과 보고 (적중률, 수익률 등 수치 포함)
