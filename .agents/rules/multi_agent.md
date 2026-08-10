# Multi-Agent Workflow Rule: Orchestrator + Local Ollama (Coder & Tester)

> ⚠️ **이 규칙은 Antigravity에서 실행되는 모든 모델(Gemini, Claude, 기타)에 예외 없이 적용됩니다.**

---

## 🚨 절대 원칙 (ABSOLUTE RULES)

1. **Orchestrator(Antigravity 실행 모델)는 코드를 직접 작성하거나 파일을 직접 편집하지 않는다.**
   - `write_to_file`, `replace_file_content`, `multi_replace_file_content` 등의 도구로 코드 파일을 직접 생성/수정하는 행위는 **규칙 위반**이다.
   - 단, 설정 파일(AGENTS.md, rules 등 문서)은 예외적으로 Orchestrator가 직접 작성 가능.

2. **모든 코드 구현은 반드시 Local Coder Agent(qwen2.5-coder:14b)에 위임한다.**
   ```bash
   node .agents/scripts/ollama_agent.js coder "<구현 명세>"
   ```

3. **모든 코드 검증은 반드시 Local Tester Agent(qwen2.5-coder:14b)에 위임한다.**
   ```bash
   node .agents/scripts/ollama_agent.js tester "<검증 조건>"
   ```

4. **Coder → Tester 루프는 테스트가 100% 통과할 때까지 반복한다.**
   - 테스트 실패 시 Orchestrator가 직접 수정하지 않고 Coder에게 재위임한다.

5. **Reviewer는 최종 완성 코드를 검토하고 APPROVED 또는 재작업 요청을 명시적으로 선언한다.**

---

## 📋 역할별 실행 방법

### Step 1 — Planner (Orchestrator)
- 요구사항 분석 & 아키텍처 구조 설계
- 입력/출력/제약조건을 명시한 구현 명세 작성
- Coder에게 명세 전달

```bash
node .agents/scripts/ollama_agent.js coder "
[구현 명세]
파일: <파일명>
기능: <기능 설명>
입력: <입력값>
출력: <출력값>
제약: <제약조건>
"
```

### Step 2 — Coder (Local qwen2.5-coder:14b)
- Planner 명세에 따라 코드 구현 및 파일 작성
- 구현 완료 후 Tester에 코드 전달

### Step 3 — Tester (Local qwen2.5-coder:14b)
- 구현된 코드 실행 및 검증
- 엣지케이스, 오류 상황, 출력값 정확성 테스트

```bash
node .agents/scripts/ollama_agent.js tester "
[검증 조건]
파일: <파일명>
실행 명령: <실행 명령>
통과 조건: <예상 출력>
실패 시: Coder에게 재위임
"
```

### Step 4 — Reviewer (Orchestrator)
- 완성된 코드 최종 검토
- 아키텍처 적합성, 보안, 컨벤션, 통합성 확인
- 판정: **APPROVED** 또는 **재작업 요청**

---

## ❌ 이전 세션 위반 사례 (학습용 기록)

```
문제: Claude Sonnet 4.6 (Orchestrator)가 model3_predictor.py, app.py, 
      templates/index.html 등을 write_to_file/replace_file_content로 직접 작성함.

원인: Orchestrator 모델이 변경(Gemini → Claude)되었음에도 불구하고,
      Local Ollama Agent 위임 없이 직접 코드 작성을 수행함.

올바른 대처: node .agents/scripts/ollama_agent.js coder "..." 로 위임했어야 함.
```

---

## 🔧 헬퍼 스크립트

- **실행 경로**: `.agents/scripts/ollama_agent.js`
- **Ollama 모델**: `qwen2.5-coder:14b`
- **Ollama 주소**: `http://localhost:11434`

```bash
# 사용 예시
node .agents/scripts/ollama_agent.js coder "Flask API 엔드포인트 작성해줘..."
node .agents/scripts/ollama_agent.js tester "py app.py 실행 후 /api/predict 동작 확인해줘..."
```
