# Orchestration Workflow Rules: Master → Coder → Tester → Reviewer

> ⚠️ **이 오케스트레이션 규칙은 프로젝트의 모든 자동화 작업 시 무조건 적용됩니다.**

---

## 🔄 표준 오케스트레이션 자동화 파이프라인 (End-to-End Loop)

```
[1. Manager (Antigravity)]
  - .agents/tasks/순번_YYMMDD_내용.md 명세서 작성
  - 작성 완료 즉시 `invoke_subagent`로 Coder 에이전트 파이프라인 자동 호출
            │
            ▼ (자동 호출)
[2. Coder & Tester (Subagent Pipeline)]
  - Coder: Coder-Cline 워크스페이스에서 소스 코드 구현 & 커밋
  - Tester: Tester-Cline 워크스페이스에서 자동 테스트 & 검증
  - 완료 시 Manager/Reviewer에게 결과 알림 송신
            │
            ▼ (자동 알림 수신)
[3. Reviewer (Antigravity Gemini 3.6 Flash)]
  - Manager가 당초 설계한 명세서 요구사항과 Coder의 커밋(git diff) 1:1 비교 검토
  - 설계 요구사항과 100% 일치 확인 시 APPROVED
  - `git merge Younseob/Coder-Cline` 최종 반영 및 보고 완료
```

---

## 🚨 각 역할별 오케스트레이션 수칙

1. **Manager (Planner)**:
   - 요구사항 수신 시 명세서만 `.agents/tasks/`에 작성.
   - 명세서 작성 후 자동으로 `invoke_subagent`를 실행하여 Coder 파이프라인 트리거.
   - 절대로 소스 파일(`src/`, `.py`)을 직접 작성/수정하지 않음.

2. **Coder & Tester**:
   - `Coder-Cline` 워크스페이스에서 명세에 맞춰 구현 및 커밋.
   - `Tester-Cline` 워크스페이스에서 코드 실행 및 정상 통과 검증.

3. **Reviewer**:
   - Coder/Tester 완수 알림 수신 즉시 읽기 전용 검토 수행.
   - Manager의 당초 설계 명세서와 구현 코드가 100% 일치함을 확인하고 `master`에 Merge.
