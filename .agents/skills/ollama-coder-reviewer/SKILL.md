---
name: ollama-coder-reviewer
description: >
  Run local Coder and Tester agents using Ollama qwen2.5-coder:14b.
  The Orchestrator (any Antigravity model: Gemini, Claude, etc.) acts as Planner & Reviewer ONLY.
  ALL code writing and testing MUST be delegated to qwen2.5-coder:14b via ollama_agent.js.
---

# Multi-Agent Workflow: Planner → Coder → Tester → Reviewer

> ⚠️ **MANDATORY**: The Orchestrator (Antigravity active model, regardless of whether it is
> Gemini Flash, Claude Sonnet, or any other model) **MUST NOT write code files directly**.
> All code implementation and testing is delegated to Local Ollama `qwen2.5-coder:14b`.

---

## Roles

| Role | Agent | Allowed Actions |
|:---|:---|:---|
| **Planner** | Orchestrator (Antigravity) | Requirements analysis, architecture design, task spec writing |
| **Coder** | `qwen2.5-coder:14b` (Local Ollama) | Code writing, file editing, refactoring |
| **Tester** | `qwen2.5-coder:14b` (Local Ollama) | Test execution, bug reporting, edge case verification |
| **Reviewer** | Orchestrator (Antigravity) | Final code review, security audit, APPROVED or re-work |

---

## Workflow Execution

### Step 1 — Planner writes the spec (Orchestrator only — no code!)
Define inputs, outputs, constraints, and file targets.

### Step 2 — Delegate to Coder
```bash
node .agents/scripts/ollama_agent.js coder "<Implementation Spec>"
```

### Step 3 — Delegate to Tester
```bash
node .agents/scripts/ollama_agent.js tester "<Test Spec & Validation Conditions>"
```
Repeat Steps 2–3 until all tests pass (100% pass rate).

### Step 4 — Reviewer approves (Orchestrator only)
Review the final code for architecture fit, security, and conventions.
Declare: **APPROVED** or request re-work (→ back to Step 2).

---

## Violation Warning

If the Orchestrator uses `write_to_file`, `replace_file_content`, or `multi_replace_file_content`
on source code files without delegating through `ollama_agent.js` first, this is a **workflow violation**.

Exception: Documentation files (AGENTS.md, rules/*.md, SKILL.md) may be edited directly by the Orchestrator.
