# Multi-Agent Workflow Rule: Cline Worktree 기반 구조

> ⚠️ **이 규칙은 Antigravity에서 실행되는 모든 모델(Gemini, Claude, 기타)에 예외 없이 적용됩니다.**

---

## 🚨 절대 원칙 (ABSOLUTE RULES)

1. **Orchestrator는 소스 코드 파일을 직접 작성하거나 편집하지 않는다.**
   - `write_to_file`, `replace_file_content`, `multi_replace_file_content` 도구를 소스 코드(`.py`, `.html`, `.js` 등)에 사용하는 것은 **규칙 위반**이다.
   - 예외: `.agents/tasks/`, `AGENTS.md`, `rules/*.md` 등 문서 파일은 Orchestrator가 직접 작성 가능.

2. **모든 코드 구현과 테스트는 Cline Agent (pearlside worktree)에 위임한다.**
   - Cline의 작업 디렉토리: `C:\Users\gosys\orca\workspaces\my_stock_auto\pearlside`
   - Cline이 사용하는 브랜치: `pearlside`

3. **Orchestrator는 `.agents/tasks/<task>.md` 파일에 구현 명세를 작성하고 Cline에 전달한다.**

4. **Cline은 pearlside 브랜치에서 자율적으로 구현/테스트/수정을 반복한다.**
   - 테스트 실패 시 Orchestrator가 직접 수정하지 않는다. Cline에 재위임한다.

5. **Orchestrator가 APPROVED 판정을 내리면 pearlside → master merge한다.**
   ```bash
   git -C C:\Users\gosys\orca\projects\my_stock_auto merge pearlside --no-ff -m "feat: <기능명>"
   ```

---

## 📁 Worktree 경로

| 브랜치 | 경로 | 용도 |
|:---|:---|:---|
| `master` | `C:\Users\gosys\orca\projects\my_stock_auto` | 안정 코드, 서비스 실행 |
| `pearlside` | `C:\Users\gosys\orca\workspaces\my_stock_auto\pearlside` | Cline 작업 공간 |

---

## 📋 역할별 실행 방법

### Orchestrator (Planner)
1. 요구사항 분석 & 아키텍처 설계
2. `.agents/tasks/<task_name>.md` 작성 (TASK_TEMPLATE.md 참조)
3. Cline에 태스크 지시:
   ```
   pearlside 경로에서 .agents/tasks/<task_name>.md를 읽고 구현해줘.
   ```

### Cline Agent (Coder + Tester)
1. 태스크 파일 읽기
2. `pearlside` 브랜치에서 파일 직접 구현
3. 터미널에서 테스트 실행 (자율 반복)
4. 완료 후 pearlside 커밋 + Orchestrator에 결과 보고

### Orchestrator (Reviewer)
1. pearlside 코드 검토 (읽기 전용)
2. 판정: **APPROVED** → master merge / **수정 필요** → 태스크 업데이트 후 Cline 재위임

---

## 🚫 이전 워크플로우 (ollama_agent.js) 폐기 이유

| 항목 | ollama_agent.js (폐기) | Cline worktree (현행) |
|:---|:---|:---|
| 파일 작성 | ❌ Orchestrator가 직접 | ✅ Cline이 직접 |
| 코드 실행 | ❌ 불가 | ✅ 터미널 직접 실행 |
| 자율 수정 | ❌ 수동 | ✅ 자동 (에러 보고 → 재수정) |
| 브랜치 격리 | ❌ master에 직접 영향 | ✅ pearlside 격리 후 merge |
| Orca 통합 | ❌ 느슨한 연결 | ✅ 네이티브 worktree 구조 |
