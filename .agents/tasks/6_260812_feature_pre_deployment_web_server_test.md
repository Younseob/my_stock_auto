# Task: 6_260812_feature_pre_deployment_web_server_test.md - 배포 전 실제 웹 구동 검증 유닛 테스트 작성 및 Tester 검증

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/6_260812_feature_pre_deployment_web_server_test.md
> 생성일: 2026-08-12

## 목표
배포 전 매번 실제 로컬 웹 서버(`app.py`)가 오류 없이 렌더링(HTTP 200 OK)되고 API가 구동되는지 보장하기 위해, **Coder가 실 웹 구동 유닛 테스트(`tests/test_web_server_live.py`)를 작성**하고 **Tester가 구동 검증(100% PASS)**을 전담하도록 한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. Coder: 실 웹 구동 유닛 테스트 파일 작성 (`tests/test_web_server_live.py`)
- `Flask` 테스트 클라이언트를 사용하여 다음 3가지 검증 구현:
  1) `GET /`: 메인 웹 화면 HTTP 200 OK 및 `<!DOCTYPE html>` 렌더링 검증
  2) `GET /api/search_stock?query=삼성전자`: 종목 부분 검색 API HTTP 200 OK 검증
  3) `GET /api/modes`: Mode 1~4 메타데이터 API HTTP 200 OK 검증

### 2. Tester: 배포 전 실 웹 구동 런타임 통과 검증 (`Tester-Cline` 수행)
- 아래 명령을 실행하여 로컬 웹 구동이 100% PASS 되는지 검증:
  ```bash
  py -m unittest tests/test_web_server_live.py
  ```

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] `tests/test_web_server_live.py` 의 3개 유닛 테스트 100% OK 통과
- [ ] `GET /` 렌더링 시 `jinja2.exceptions.TemplateNotFound` 에러 전혀 없음 보장

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -m unittest tests/test_web_server_live.py
```
