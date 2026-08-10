---
name: ollama-coder-reviewer
description: >
  Cline worktree(pearlside) 기반 4-Role 멀티에이전트 워크플로우.
  Orchestrator(Antigravity 활성 모델: Gemini, Claude 등)는 Planner & Reviewer만 담당.
  ALL code writing and testing은 Cline Agent(pearlside worktree, qwen2.5-coder:14b)에 위임.
---

# Multi-Agent Workflow: Planner → Cline(pearlside) → Reviewer

> ⚠️ **MANDATORY**: Orchestrator는 소스 코드를 직접 작성하지 않는다.
> Cline이 `pearlside` worktree에서 직접 구현, 실행, 테스트한다.

---

## Worktree 구조

| 브랜치 | 경로 | 담당 |
|:---|:---|:---|
| `master` | `C:\Users\gosys\orca\projects\my_stock_auto` | Orchestrator (읽기 전용 참조) |
| `pearlside` | `C:\Users\gosys\orca\workspaces\my_stock_auto\pearlside` | **Cline 작업 공간** |

---

## Workflow

### Step 1 — Planner (Orchestrator)
- 요구사항 분석 & 아키텍처 설계
- `.agents/tasks/<task>.md` 명세 파일 작성 (TASK_TEMPLATE.md 참조)
- Cline에 태스크 지시

### Step 2 — Cline (pearlside worktree에서 실행)
- 태스크 파일 읽기
- `pearlside` 브랜치에서 파일 직접 생성/수정
- 터미널에서 코드 실행 및 테스트
- 실패 시 자율 수정 → 재테스트 (loop)
- 완료 시 pearlside 커밋 + 결과 보고

### Step 3 — Reviewer (Orchestrator)
- pearlside 코드 읽기 전용 검토
- **APPROVED**: master merge
  ```bash
  git -C C:\Users\gosys\orca\projects\my_stock_auto merge pearlside --no-ff -m "feat: <기능명>"
  ```
- **수정 필요**: 태스크 파일 업데이트 → Step 2 재시작

---

## ❌ 폐기된 방식 (ollama_agent.js)

`node .agents/scripts/ollama_agent.js coder "..."` 방식은 **폐기**되었습니다.
Cline worktree 방식으로 완전 전환되었습니다.

이유:
- `ollama_agent.js`는 텍스트 응답만 반환 → Orchestrator가 직접 파일 작성 필요 → 규칙 위반 구조
- Cline은 파일 직접 편집 + 터미널 실행 + 자율 수정 가능 → 규칙 준수 구조
