# Task: 4_260811_change_default_stock_to_samsung.md - 기본 입력 종목 '삼성전자' 변경

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/4_260811_change_default_stock_to_samsung.md
> 생성일: 2026-08-11

## 목표
웹 UI 초기 로딩 시 검색창 기본 입력값(default value) 및 초기 안내 예시 종목을 기존 종목에서 **"삼성전자" (ticker: 005930)**로 변경한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. Frontend UI 기본값 변경 (`templates/index.html`)
- 검색어 입력 `<input id="stockInput" ...>` 의 기본 `value` 속성을 `"삼성전자"` 로 변경.
- 초기 안내 Placeholder 또는 예시 텍스트를 `"예: 삼성전자, SK하이닉스, 현대차"` 로 수정.
- 초기 로딩 시 렌더링 카드/배너의 기본 텍스트에 "삼성전자" 반영.

### 2. Backend Default Fallback 검증 (`app.py` / `src/web/app.py`)
- 기본 요청 종목명이 비어있을 시 fallback 종목을 `"삼성전자"` 로 보장.

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 웹 페이지 접속 초기 렌더링 시 검색창에 `"삼성전자"` 가 기본값으로 입력되어 있음.
- [ ] [분석 실행] 버튼 클릭 시 "삼성전자" (005930) 주가 예측 분석이 즉시 실행됨.

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -c "import app; print('Default stock changed to 삼성전자 successfully!')"
```
