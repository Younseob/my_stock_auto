# Workspace Multi-Agent Architecture Configuration (Orca + Antigravity)

> ⚠️ **이 문서는 프로젝트의 모든 AI 에이전트(Manager, Coder, Tester, Reviewer)가 반드시 준수해야 하는 최상위 오케스트레이션 영구 제약 수칙입니다.**

---

## 🚨 [절대 엄금] Antigravity Manager 툴 호출 완전 금지 규칙 (STRICT PROHIBITION)

### 📌 차후 터미널/세션 재시작 시에도 100% 준수되는 영구 제약 수칙

1. **`invoke_subagent` 도구 호출 100% 절대 금지**:
   - Manager(Antigravity)는 어떠한 경우에도 내장 서브에이전트 생성 도구(`invoke_subagent`)를 호출하지 않는다.
   - internal subagent를 부르는 것은 Orca ADE 엔진과 로컬 Ollama GPU의 개입을 차단하는 심각한 구멍이므로 **절대 엄금**한다.

2. **명세서 작성 후 즉시 턴 종료 (STRICT END TURN)**:
   - Manager는 오직 `.agents/tasks/순번_YYMMDD_내용.md` 명세서 파일 1개만 작성한다.
   - **명세서 작성 직후 더 이상 어떠한 도구도 부르지 않고 즉시 턴을 마감(Stop calling tools / End Turn)하여 제어권을 Orca ADE 엔진으로 100% 이관한다.**

3. **로컬 RTX 5080 Ollama Coder 자동 구동**:
   - Manager가 턴을 마감하면 Orca ADE 엔진이 `AGENTS.md`를 파싱하여 `Coder-Cline` 워크스페이스에서 **실제 로컬 RTX 5080 GPU의 Ollama `qwen2.5-coder:14b` Coder Agent**를 실행한다.

---

## 🗺️ Worktree & Branch 1:1 격리 구조

| 브랜치 / 워크스페이스 | 담당 에이전트 / 모델 | 주요 책무 |
| :--- | :--- | :--- |
| `master`<br/>(`orca/projects/my_stock_auto`) | **Manager & Reviewer**<br/>(Antigravity Gemini 3.6 Flash) | • 명세서 작성 후 **즉시 턴 종료 (invoke_subagent 금지)**<br/>• Orca ADE가 Coder/Tester 완수 후 제어권 반환 시 **Merge & Push 자율 수행** |
| `Younseob/Coder-Cline`<br/>(`orca/workspaces/.../Coder-Cline`) | **Real Coder**<br/>(Local RTX 5080 Ollama Qwen2.5-coder-14b) | • Orca ADE 엔진이 직접 호출하여 소스 코드 구현 & 커밋 전담 |
| `Tester-Cline`<br/>(`orca/workspaces/.../Tester-Cline`) | **Real Tester**<br/>(Local RTX 5080 Ollama Qwen2.5-coder-14b) | • Orca ADE 엔진이 직접 호출하여 자동 실행 & 100% PASS 검증 전담 |
