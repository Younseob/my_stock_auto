# Multi-Agent Workflow Rule: 무조건 준수 4-Role 격리 수칙

> ⚠️ **이 규칙은 Antigravity에서 실행되는 모든 모델(Gemini, Claude, 기타)에 예외 없이 무조건(MANDATORY) 적용됩니다.**

---

## 🚨 100% 절대 원칙 (ABSOLUTE MANDATORY RULES)

1. **Manager/Orchestrator는 소스 코드(`src/`, `.py`, `.js` 등)를 master 브랜치에서 직접 작성, 편집, 이동하지 않는다.**
   - Manager가 `write_to_file`, `replace_file_content` 등의 도구를 소스 코드 파일에 직접 사용하는 것은 **중대한 규칙 위반**이다.
   - 예외: `.agents/tasks/`, `AGENTS.md`, `.agents/rules/*.md` 등 **프로젝트 관리 문서**는 Manager가 직접 작성 가능.

2. **모든 소스 코드 작성, 리팩토링, 파일 이동은 Coder Agent (`Coder-Cline` Worktree)에 무조건 위임한다.**
   - Coder 작업 디렉토리: `C:\Users\gosys\orca\workspaces\my_stock_auto\Coder-Cline`
   - Coder 사용 브랜치: `Younseob/Coder-Cline`

3. **모든 코드 테스트 및 검증은 Tester Agent (`Tester-Cline` Worktree)에 무조건 위임한다.**
   - Tester 작업 디렉토리: `C:\Users\gosys\orca\workspaces\my_stock_auto\Tester-Cline`
   - Tester 사용 브랜치: `Tester-Cline`

4. **Manager는 오직 `.agents/tasks/<task>.md` 파일에 명세를 작성하여 지시한다.**

5. **Reviewer의 APPROVED 판정 후에만 `Coder-Cline` → `master` Merge를 진행한다.**
   ```bash
   git -C C:\Users\gosys\orca\projects\my_stock_auto merge Younseob/Coder-Cline --no-ff -m "feat: <기능명>"
   ```

---

## 📁 Worktree 1:1 매칭 경로

| 브랜치 | 경로 | 담당 및 역할 |
| :--- | :--- | :--- |
| `master` | `C:\Users\gosys\orca\projects\my_stock_auto` | Manager/Reviewer 전용 (소스 직접 수정 금지, 문서 관리 및 Merge만 수행) |
| `Younseob/Coder-Cline` | `C:\Users\gosys\orca\workspaces\my_stock_auto\Coder-Cline` | Coder 전용 (소스 코드 직접 작성, 리팩토링, 파일 이동) |
| `Tester-Cline` | `C:\Users\gosys\orca\workspaces\my_stock_auto\Tester-Cline` | Tester 전용 (터미널 실행, 자동 테스트, 디버깅) |
