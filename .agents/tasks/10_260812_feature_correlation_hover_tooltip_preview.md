# Task: 10_260812_feature_correlation_hover_tooltip_preview.md - 상관관계 피쳐 항목 마우스 호버(Hover) 미리보기 툴팁 구현

> Orchestrator → Coder(Cline) 구현 명세 전달 파일
> 경로: .agents/tasks/10_260812_feature_correlation_hover_tooltip_preview.md
> 생성일: 2026-08-12

## 목표
상관관계 분석 결과 카드 내의 피쳐 지표 항목에 마우스 커서를 올리면(Hover), 해당 지표가 뜻하는 상세 의미와 주가 영향 해석이 직관적인 **커스텀 풍선 도움말 / 미리보기 툴팁(Hover Preview Tooltip)**으로 즉시 노출되도록 웹 UI(`templates/index.html`)를 수정한다.

---

## 구현 명세 (`Coder-Cline` 워크스페이스 기준)

### 1. CSS Hover Tooltip 스타일 정의 (`templates/index.html`)
- 커스텀 Glassmorphism 미리보기 툴팁 스타일 추가 (`.tooltip-container`, `.tooltip-box`):
  - 마우스 커서 호버 시 smooth fade-in 툴팁 박스 노출.
  - 다크 템플릿 분위기에 맞춘 은은한 글로우 및 높은 가독성의 폰트 적용.

### 2. JavaScript 렌더링 시 Hover Tooltip 바인딩 (`templates/index.html`)
- 상관관계 10개 피쳐 항목 출력 시:
  ```html
  <div class="correlation-item tooltip-container">
      <span class="feature-label">최근 3일 누적 수익률 (ret_3d)</span>
      <span class="feature-val">-0.2012</span>
      <!-- Hover 시 노출되는 미리보기 박스 -->
      <div class="tooltip-box">
          <strong>💡 최근 3일 누적 수익률 (ret_3d)</strong><br>
          최근 3일간의 누적 주가 변동률입니다. 음수(-0.2012) 상관관계는 최근 3일간 급등했을 시 차익실현 매물로 인해 내일 주가가 하락할 가능성이 높음을 의미합니다.
      </div>
  </div>
  ```

---

## 검증 조건 (`Tester-Cline` 수행)
- [ ] 웹 화면 상관관계 피쳐 지표 항목에 마우스 호버 시 상세 설명 툴팁 박스 즉시 노출
- [ ] 마우스 커서 이동 시 자연스러운 fade-in/out 미리보기 동작 확인
- [ ] `py -m unittest tests/test_web_server_live.py` 100% PASS 검증

---

## Coder 실행 명령어

```bash
# Coder-Cline 워크스페이스에서 실행
py -m unittest tests/test_web_server_live.py
```
