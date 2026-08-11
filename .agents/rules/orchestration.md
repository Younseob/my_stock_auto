# Orchestration Workflow Rules: Auto-Approval Protocol

> ⚠️ **이 규정은 Reviewer가 Coder/Tester 완수 통보 수신 시 100% 자율 자동 실행하도록 보장합니다.**

---

## ⚡ 100% 원스톱 자율 진행 수칙 (Non-Interactive Auto-Approve)

1. **사용자에게 다시 묻지 않기 (No Double-Asking)**:
   - Coder와 Tester가 명세서에 따른 구현 및 검증을 마치면, Reviewer(Antigravity Gemini 3.6 Flash)는 **사용자에게 "진행할까요?", "승인할까요?" 하고 다시 묻지 않습니다.**

2. **자동 원스톱 파이프라인 마감 (One-Stop Auto Execution)**:
   - 알림 수신 즉시:
     ① Manager 당초 명세서와 Coder 구현 소스(git diff) 1:1 비교 검토
     ② 설계 일치 확인 시 자율 `APPROVED` 판정
     ③ `git merge Younseob/Coder-Cline` 자동 실행
     ④ `git push origin master` 자동 완료
     ⑤ 최종 완성 결과 사용자 보고

3. **막힘없는 자동화 준수**:
   - 도구 실행 시 대기나 승인 팝업 요청 없이 시스템 내에서 즉각 마감까지 진행합니다.
