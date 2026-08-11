# Multi-Agent Workflow Rule: 문의 vs 코드 수정 분기 및 4-Role 루프 규칙

> ⚠️ **이 규칙은 Antigravity에서 실행되는 모든 모델에 예외 없이 적용됩니다.**

---

## 🚨 100% 절대 원칙 (ABSOLUTE MANDATORY RULES)

### 1. Master(Manager) 세션의 두 가지 처리 분기

* **[분기 A] 단순 문의 / 설명 / 질의응답**:
  - `master` 세션(Antigravity)에서 소스 코드를 읽어 직접 분석하고 사용자에게 답변합니다.
  - 이 경우 Coder/Tester 루프를 호출하지 않습니다.

* **[분기 B] 코드 수정 / 파일 이동 / 리팩토링 / 기능 추가**:
  - **`master` 세션에서 절대로 소스 코드를 직접 편집/이동하지 않습니다.**
  - 반드시 `Manager`가 명세서(`.agents/tasks/<task>.md`) 작성 $\rightarrow$ `Coder` 구현 $\rightarrow$ `Tester` 검증 $\rightarrow$ `Reviewer` 승인 & Merge 루프를 사용합니다.

---

## 📁 Worktree 1:1 매칭 경로

| 브랜치 | 경로 | 담당 및 역할 |
| :--- | :--- | :--- |
| `master` | `C:\Users\gosys\orca\projects\my_stock_auto` | Manager/Reviewer 전용 (단순 문의 답변, 명세 작성, 코드 리뷰 & Merge) |
| `Younseob/Coder-Cline` | `C:\Users\gosys\orca\workspaces\my_stock_auto\Coder-Cline` | Coder 전용 (소스 코드 직접 작성, 리팩토링, 파일 이동 및 커밋) |
| `Tester-Cline` | `C:\Users\gosys\orca\workspaces\my_stock_auto\Tester-Cline` | Tester 전용 (터미널 실행, 자동 테스트, 자율 수정) |
