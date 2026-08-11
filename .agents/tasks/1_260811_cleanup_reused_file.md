# Task: 1_260811_cleanup_reused_file.md - 루트 디렉토리 구 버전 잔재 파일 클린업

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/1_260811_cleanup_reused_file.md
> 생성일: 2026-08-11

## 목표
`src/` 하위 모듈(`src/modes/`, `src/db/`, `src/web/`, `tests/`, `data/`)로 성공적으로 이관된 후, 루트 디렉토리에 중복으로 남아있는 구 버전 파이썬 파일 및 DB 잔재 파일들을 완전히 정리(`git rm`)하여 깔끔한 모듈 구조를 완성한다.

---

## 삭제 정제 대상 파일 목록 (`Coder-Cline` 워크스페이스 기준)

| 루트 잔재 파일명 | 현재 이관된 위치 | 조치 사항 |
| :--- | :--- | :--- |
| `stock_predictor.py` | `src/modes/mode_1_stock_predictor.py` | `git rm stock_predictor.py` |
| `two_year_predictor.py` | `src/modes/mode_2_two_year_predictor.py` | `git rm two_year_predictor.py` |
| `model3_predictor.py` | `src/modes/mode_3_gap_predictor.py` | `git rm model3_predictor.py` |
| `pattern_predictor.py` | `src/modes/mode_4_pattern_predictor.py` | `git rm pattern_predictor.py` |
| `database.py` | `src/db/database.py` | `git rm database.py` |
| `stock_cache.db` (루트) | `data/stock_cache.db` | `git rm stock_cache.db` (루트 파일만 제거) |
| `test_2yr_web.py` (루트) | `tests/test_2yr_web.py` | `git rm test_2yr_web.py` |
| `test_server.py` (루트) | `tests/test_server.py` | `git rm test_server.py` |

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 루트 디렉토리에 구 버전 파이썬 파일(`*_predictor.py`, `database.py`)이 전혀 존재하지 않음.
- [ ] `py -c "from src.web.app import app; print('Cleaned up successfully!')"` 정상 구동 확인.
- [ ] `py tests/test_2yr_web.py` 실행 시 이상 없음.

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
git rm stock_predictor.py two_year_predictor.py model3_predictor.py pattern_predictor.py database.py stock_cache.db test_2yr_web.py test_server.py -f
git commit -m "chore: cleanup redundant root python and db files after src/ refactoring"
```
