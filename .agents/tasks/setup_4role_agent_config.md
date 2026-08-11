# Task: 4-Role 에이전트 자동 설정 Python 스크립트 구현

> Orchestrator → Cline 구현 명세 전달 파일
> 경로: .agents/tasks/setup_4role_agent_config.md

## 목표
Orca ADE 3-Workspace 환경에서 아래 4-Role 에이전트 설정을 자동으로 검증, 생성 및 동기화하는 Python 스크립트(`.agents/scripts/setup_agent_config.py`)를 구현한다.

- **Manager**: Antigravity Gemini Flash (Planner - 아키텍처 설계 & Task 명세 작성 | `master`)
- **Coder**: Cline Qwen2.5-coder-14b (Coder - 소스 코드 개발 & 작성 | `Coder-Cline` 워크스페이스)
- **Tester**: Cline Qwen2.5-coder-14b (Tester - 자동 테스트 & 검증 | `Tester-Cline` 워크스페이스)
- **Reviewer**: Antigravity Gemini Flash (Reviewer - 코드 리뷰 & master merge 승인 | `master`)

## 대상 파일
- `.agents/scripts/setup_agent_config.py` — 신규 생성
- `.agents/config/agent_roles.json` — 자동 생성/업데이트 관리

## 구현 명세

### 입력 (Input)
CLI argument:
- `--check` : 현재 4-Role 에이전트 설정 상태 및 3-Workspace / Ollama `qwen2.5-coder:14b` 환경 검증
- `--apply` : 4-Role 에이전트 구성 JSON (`.agents/config/agent_roles.json`) 자동 적용 및 동기화
- `--json-out` : JSON 포맷으로 결과 출력

### 출력 (Output)
- status 0 (성공) 및 설정 완료 리포트 (콘솔 출력 및 JSON 파일 업데이트)

### 핵심 로직 (Core Logic)
1. **인코딩 설정**: 최상단에 `sys.stdout.reconfigure(encoding='utf-8')` 적용하여 Windows 한글 깨짐 방지.
2. **에이전트 역할 구성 JSON 작성/확인**:
   ```json
   {
     "roles": {
       "manager": {
         "agent": "Antigravity",
         "model": "Gemini Flash",
         "workspace": "master",
         "responsibilities": ["Architecture Design", "Task Spec Generation (.agents/tasks/)"]
       },
       "coder": {
         "agent": "Cline",
         "model": "qwen2.5-coder:14b",
         "workspace": "Coder-Cline",
         "responsibilities": ["Code Implementation", "Feature Branch Management"]
       },
       "tester": {
         "agent": "Cline",
         "model": "qwen2.5-coder:14b",
         "workspace": "Tester-Cline",
         "responsibilities": ["Automated Execution & Testing", "Self-Debugging"]
       },
       "reviewer": {
         "agent": "Antigravity",
         "model": "Gemini Flash",
         "workspace": "master",
         "responsibilities": ["Code Review", "Master Branch Merge Approval"]
       }
     }
   }
   ```
3. **환경 점검 함수**:
   - `git worktree list` 및 `git branch -a` 명령어를 실행하여 `master`, `Coder-Cline`, `Tester-Cline` 워크스페이스/브랜치 존재 여부 검증.
   - `ollama list` 명령어 실행하여 `qwen2.5-coder:14b` 모델 설치 여부 검증.
   - `.agents/tasks/` 및 `AGENTS.md` 파일 존재 검증.
4. **결과 리포트 출력**:
   - 4-Role 구성 상태 콘솔 출력 및 `.agents/config/agent_roles.json` 파일 생성/업데이트.

### 제약 조건
- Windows 환경 인코딩 (`utf-8`) 처리 필수.
- 외부 명령어 (`git`, `ollama`) 실행 시 `subprocess.run`에서 오류가 나더라도 스크립트가 크래시되지 않도록 `try/except` 처리.

## 테스트 조건
Cline이 아래 명령을 실행하고 모두 통과해야 함:

- [ ] `py .agents/scripts/setup_agent_config.py --check` 실행 → exit code 0 및 환경 검증 결과 출력
- [ ] `py .agents/scripts/setup_agent_config.py --apply` 실행 → exit code 0 및 `.agents/config/agent_roles.json` 정상 생성
- [ ] 생성된 `.agents/config/agent_roles.json` 파일 내용 확인 (4-Role 및 3-Workspace 매칭 정상)

## Cline 실행 가이드

```
.agents/tasks/setup_4role_agent_config.md 파일(Task 명세)을 읽고 위 명세에 따라 구현해줘.
구현 완료 후 반드시 테스트 조건을 모두 실행하고 결과를 알려줘.
테스트 실패 시 스스로 수정하고 재테스트해줘.
```

## 완료 기준
- 모든 테스트 체크박스 통과
- `.agents/scripts/setup_agent_config.py` 구현 및 커밋
- Orchestrator Reviewer에게 결과 보고
