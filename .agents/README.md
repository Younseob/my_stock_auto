# 🤖 Orca ADE Multi-Agent System Configuration (.agents)

이 디렉토리는 **my_stock_auto** 프로젝트의 4-Role 멀티 에이전트 체계 및 워크플로우 구성을 관리하는 최상위 가버넌스 폴더입니다.

---

## 🏛️ 4-Role 멀티 에이전트 가버넌스 구조

| 역할 (Role) | 담당 에이전트 / 모델 | 매칭 워크스페이스 / 브랜치 | 주요 책임 (Responsibilities) |
| :--- | :--- | :--- | :--- |
| **Manager** | **Antigravity (Gemini Flash)** | `master` | 프로젝트 아키텍처 설계, 요구사항 분석, Task 명세서 작성 |
| **Coder** | **Cline (qwen2.5-coder:14b)** | `Coder-Cline` | `.agents/tasks/` 명세를 읽고 소스 코드 구현 및 기능 커밋 |
| **Tester** | **Cline (qwen2.5-coder:14b)** | `Tester-Cline` | 터미널 실행, 자동 테스트 수행 및 자율 디버깅/수정 |
| **Reviewer** | **Antigravity (Gemini Flash)** | `master` | Coder/Tester 구현 코드 리뷰, 검증 및 `master` 브랜치 Merge 승인 |

---

## 📁 `.agents` 디렉토리 구조 및 서브 시스템

```
.agents/
├── config/
│   └── agent_roles.json           # 4-Role 에이전트 및 3-Workspace 설정 JSON
├── rules/
│   └── multi_agent.md             # 멀티 에이전트 작업 원칙 및 강제 규정
├── tasks/                         # Orchestrator(Manager) → Cline 지시 명세서 모음
│   ├── TASK_TEMPLATE.md           # Task 명세 표준 템플릿
│   ├── setup_4role_agent_config.md# [Task 1] 에이전트 설정 파이썬 스크립트 명세
│   └── refactor_project_structure.md# [Task 2] 소스 코드 디렉토리 구조 리팩토링 명세
├── skills/
│   └── ollama-coder-reviewer/     # Cline Worktree 기반 4-Role 스킬 가이드
└── scripts/
    └── setup_agent_config.py      # 에이전트 설정을 자동 검증/등록하는 파이썬 스크립트
```

---

## 🚀 프로젝트 관리자 (Manager) 작업 수행 지침

1. **소스 코드 직접 편집 금지**: Manager(Antigravity)는 `.py`, `.js` 소스 코드를 직접 수정하지 않고, 반드시 `.agents/tasks/<task>.md` 명세서를 통해 작업 내용을 Coder(Cline)에게 위임합니다.
2. **Task 명세 기반 실행**: 모든 기능 추가/수정/리팩토링은 `TASK_TEMPLATE.md` 포맷에 따라 명세서를 작성한 뒤 지시합니다.
3. **최종 코드 승인**: Coder 및 Tester가 작업을 완료하면, Reviewer(Antigravity)가 읽기 전용 검토 후 이상이 없을 때 `master` 브랜치로 Merge를 최종 승인합니다.
