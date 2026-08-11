import sys
import os
import json
import subprocess
import argparse

# Windows 한글 인코딩 처리
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_PATH = os.path.join(".agents", "config", "agent_roles.json")

INITIAL_CONFIG = {
    "project_name": "my_stock_auto",
    "architecture": "4-Role Multi-Agent Worktree Pattern",
    "roles": {
        "manager": {
            "name": "Manager",
            "agent": "Antigravity",
            "model": "Gemini Flash",
            "workspace": "master",
            "responsibilities": [
                "Project Management & Architecture Design",
                "Task Specification Generation (.agents/tasks/)",
                "Workflow Governance"
            ]
        },
        "coder": {
            "name": "Coder",
            "agent": "Cline",
            "model": "qwen2.5-coder:14b",
            "workspace": "Coder-Cline",
            "responsibilities": [
                "Source Code Implementation",
                "Refactoring & Feature Branch Commits",
                "Reading Task Specifications"
            ]
        },
        "tester": {
            "name": "Tester",
            "agent": "Cline",
            "model": "qwen2.5-coder:14b",
            "workspace": "Tester-Cline",
            "responsibilities": [
                "Automated Test Execution",
                "Self-Debugging & Bug Fixing",
                "Test Report Generation"
            ]
        },
        "reviewer": {
            "name": "Reviewer",
            "agent": "Antigravity",
            "model": "Gemini Flash",
            "workspace": "master",
            "responsibilities": [
                "Code Quality Review (Read-only)",
                "Final Task Verification",
                "Master Branch Merge Approval"
            ]
        }
    },
    "workspaces": {
        "master": "C:/Users/gosys/orca/projects/my_stock_auto",
        "coder": "C:/Users/gosys/orca/workspaces/my_stock_auto/coder",
        "tester": "C:/Users/gosys/orca/workspaces/my_stock_auto/tester"
    }
}

def check_environment():
    print("=" * 60)
    print("🔍 Orca ADE 4-Role 에이전트 환경 검증 시작...")
    print("=" * 60)
    
    checks = {}
    
    # 1. Ollama 설치 및 qwen2.5-coder:14b 모델 확인
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if "qwen2.5-coder:14b" in res.stdout or "qwen2.5-coder" in res.stdout:
            print("[✅] Ollama Modell: qwen2.5-coder 모델 확인됨")
            checks["ollama_model"] = True
        else:
            print("[⚠️] Ollama Modell: qwen2.5-coder:14b 모델이 오프라인이거나 감지되지 않았습니다. ('ollama pull qwen2.5-coder:14b' 필요)")
            checks["ollama_model"] = False
    except Exception as e:
        print(f"[⚠️] Ollama CLI 실행 실패: {e}")
        checks["ollama_model"] = False
        
    # 2. Git 브랜치 및 Worktree 확인
    try:
        res = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        branches = res.stdout
        print("\n[📌] 감지된 Git 브랜치:")
        for line in branches.splitlines():
            print(f"  - {line.strip()}")
        checks["git_branches"] = True
    except Exception as e:
        print(f"[⚠️] Git 명령어 실행 실패: {e}")
        checks["git_branches"] = False

    # 3. .agents 구조 확인
    agents_dir_ok = os.path.exists(".agents")
    tasks_dir_ok = os.path.exists(os.path.join(".agents", "tasks"))
    config_dir_ok = os.path.exists(os.path.join(".agents", "config"))
    
    print("\n[📁] .agents 구조 점검:")
    print(f"  - .agents 디렉토리: {'✅ OK' if agents_dir_ok else '❌ Missing'}")
    print(f"  - .agents/tasks 디렉토리: {'✅ OK' if tasks_dir_ok else '❌ Missing'}")
    print(f"  - .agents/config 디렉토리: {'✅ OK' if config_dir_ok else '❌ Missing'}")
    
    checks[".agents_structure"] = agents_dir_ok and tasks_dir_ok and config_dir_ok

    print("\n" + "=" * 60)
    print("📋 4-Role 에이전트 매핑 상태:")
    print("=" * 60)
    for role_key, info in INITIAL_CONFIG["roles"].items():
        print(f" • [{info['name']:<8}] {info['agent']} ({info['model']}) -> Workspace: {info['workspace']}")
    
    print("=" * 60)
    return checks

def apply_configuration():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(INITIAL_CONFIG, f, indent=2, ensure_ascii=False)
    print(f"[✅] 에이전트 초기 설정이 성공적으로 동기화되었습니다: {CONFIG_PATH}")

def main():
    parser = argparse.ArgumentParser(description="Orca ADE 4-Role 에이전트 설정 스크립트")
    parser.add_argument("--check", action="store_true", help="환경 및 설정 검증 실행")
    parser.add_argument("--apply", action="store_true", help="초기 4-Role 설정 JSON 생성/동기화")
    parser.add_argument("--json-out", action="store_true", help="JSON 포맷으로 출력")

    args = parser.parse_args()

    if not any(vars(args).values()):
        # 기본 옵션 없으면 check + apply 둘 다 수행
        args.check = True
        args.apply = True

    if args.apply:
        apply_configuration()

    if args.check:
        checks = check_environment()
        if args.json_out:
            print("\n[JSON OUTPUT]")
            print(json.dumps(checks, indent=2))

if __name__ == "__main__":
    main()
