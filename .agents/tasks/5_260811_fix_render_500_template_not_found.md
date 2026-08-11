# Task: 5_260811_fix_render_500_template_not_found.md - Render 500 TemplateNotFound 에러 긴급 복구

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/5_260811_fix_render_500_template_not_found.md
> 생성일: 2026-08-11

## 목표
Render 배포 환경에서 `https://my-stock-auto.onrender.com/` 접속 시 발생한 **500 Internal Server Error (`jinja2.exceptions.TemplateNotFound: index.html`)**를 긴급 수정한다.

---

## 장애 원인 분석
- `app.py` 상단에 `BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))` 로 설정되어 있어, 루트에 위치한 `app.py` 관점에서 `templates/` 경로가 프로젝트 외부 상위 폴더(`../..`)를 참조함.
- 이로 인해 Render 서버가 `templates/index.html`을 찾지 못하고 500 Internal Server Error 발생.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### `app.py` / `src/web/app.py` BASE_DIR 경로 정상화
- `app.py` 상단의 `BASE_DIR` 경로 계산을 프로젝트 루트 기준으로 수정:
  ```python
  BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  template_dir = os.path.join(BASE_DIR, 'templates')
  app = Flask(__name__, template_folder=template_dir)
  ```

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] `py -c "import app; print('Template path verified!')"` 실행 시 성공
- [ ] `Flask` 개발 서버/테스트 클라이언트로 `GET /` 호출 시 `200 OK` 및 `index.html` 정상 반환 확인

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -c "import app; print('Render 500 error fix verified!')"
```
