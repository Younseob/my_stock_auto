# Multi-Agent Governance Rules & Strict Prohibition

> ⚠️ **이 규정은 차후 새로운 세션이나 터미널이 열려도 100% 강제 적용되는 영구 제약 수칙입니다.**

---

## 🚫 Manager (Antigravity) 행동의 절대금지 조항 (Strict Prohibition)

1. **`invoke_subagent` 도구 호출 금지**:
   - Manager는 `invoke_subagent` 도구를 호출할 권한이 없다.
   - 내장 서브에이전트를 호출하는 행위는 Orca ADE 상위 엔진과 로컬 Ollama GPU(`qwen2.5-coder:14b`)의 자동 개입을 차단하므로 **엄격히 금지**된다.

2. **명세서 작성 후 즉시 도구 호출 중단 (End Turn)**:
   - Manager는 `.agents/tasks/순번_YYMMDD_내용.md` 작성 후 **어떠한 도구도 연속 호출하지 않고 턴을 즉시 마감**한다.
   - 제어권을 Orca ADE 오케스트레이션 엔진으로 넘겨 로컬 RTX 5080 Ollama가 Coder 작업을 100% 전담하도록 보장한다.
