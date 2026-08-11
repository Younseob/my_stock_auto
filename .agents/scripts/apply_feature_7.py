import os
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def apply_feature_7():
    print("🚀 Mode 1~4 상세 설명 및 상관관계 지표 도움말 UI 반영 중...")
    
    html_path = os.path.join("templates", "index.html")
    if not os.path.exists(html_path):
        print(f"❌ Error: {html_path} 경로를 찾을 수 없습니다.")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Mode 1~4 안내 카드 HTML 준비
    mode_guide_html = '''
        <!-- Mode 1~4 초보자용 직관적 가이드 카드 -->
        <div class="card mb-4" style="background: rgba(30, 41, 59, 0.6); border: 1px solid var(--card-border); border-radius: 12px; padding: 1.2rem;">
            <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.8rem; color: #a5b4fc; display: flex; align-items: center; gap: 8px;">
                <span>💡 AI 예측 모드(Mode 1 ~ Mode 4) 완벽 가이드</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; font-size: 0.88rem; line-height: 1.5;">
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #6366f1;">
                    <strong style="color: #c7d2fe;">Mode 1 (1년 백테스팅기)</strong><br>
                    <span style="color: var(--text-muted);">최근 1년간의 일별 데이터로 AI의 매매 전략을 백테스트하고 내일의 주가 방향을 예측합니다.</span>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #10b981;">
                    <strong style="color: #a7f3d0;">Mode 2 (2년 주간분석기)</strong><br>
                    <span style="color: var(--text-muted);">최근 2년간의 주간 단위 추세를 분석하여 중장기적인 승률과 이번 주 주가 흐름을 제시합니다.</span>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #f59e0b;">
                    <strong style="color: #fde68a;">Mode 3 (시가 갭상승 & 수급)</strong><br>
                    <span style="color: var(--text-muted);">코스피, 외국인/기관 수급, 거래량을 기계학습으로 종합 분석하여 내일 시가 갭상승 가능성을 예측합니다.</span>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #ec4899;">
                    <strong style="color: #fbcfe8;">Mode 4 (차트 패턴 매칭)</strong><br>
                    <span style="color: var(--text-muted);">과거 10년 차트 중 현재 주가 흐름과 가장 똑같은 top 5 유사 과거 패턴을 찾아 미래를 추정합니다.</span>
                </div>
            </div>
        </div>
'''

    # 2. 상관관계 & 피쳐 지표 상세 설명 도움말 HTML 준비
    help_catalog_html = '''
        <!-- 상관관계 & 주요 지표 상세 도움말 카드 -->
        <div class="card mt-4" style="background: rgba(30, 41, 59, 0.6); border: 1px solid var(--card-border); border-radius: 12px; padding: 1.2rem;">
            <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.8rem; color: #a5b4fc; display: flex; align-items: center; gap: 8px;">
                <span>🔍 상관관계 & 주요 피쳐 지표 상세 설명</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; font-size: 0.85rem; line-height: 1.5; color: var(--text-muted);">
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• 외국인/기관 순매수 (Net Buying):</b><br>
                    주가 상승을 이끄는 메이저 주포 세력의 수급 유입 강도입니다. (양수(+) 값이 클수록 강력한 상승 동력)
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• RSI (상대강도지수):</b><br>
                    주가의 과매수/과매도 심리를 나타냅니다. (70 이상: 과매수 경계, 30 이하: 과매도 반등 기회)
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• MACD (이동평균수렴조음):</b><br>
                    단기/장기 이동평균선의 교차를 통해 추세 전환점(골든크로스/데드크로스)을 나타내는 지표입니다.
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• 시가 갭비율 (Open Gap Pct):</b><br>
                    전일 종가 대비 당일 시가 형성 폭으로, 밤사이 발생한 모멘텀과 시가 수급 강도를 의미합니다.
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• 코스피 변동률 (KOSPI Return):</b><br>
                    전체 주식 시장의 대세 상승/하락 분위기가 해당 종목에 미치는 지수 커플링 동조화 영향력입니다.
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 6px;">
                    <b style="color: #f8fafc;">• 볼린저 밴드 (Bollinger Bands):</b><br>
                    주가의 표준편차 변동성 범위를 나타내며, 상한/하한 이탈 시 변동성 확장 또는 반전을 예고합니다.
                </div>
            </div>
        </div>
'''

    if "💡 AI 예측 모드(Mode 1 ~ Mode 4) 완벽 가이드" not in content:
        # 헤더 직후에 삽입
        content = content.replace("</header>", "</header>\n" + mode_guide_html)
        print("  [✅] Mode 1~4 초보자용 가이드 카드 추가 완료")

    if "🔍 상관관계 & 주요 피쳐 지표 상세 설명" not in content:
        # container 닫히기 직전에 삽입
        content = content.replace("</div>\n</body>", help_catalog_html + "\n</div>\n</body>")
        print("  [✅] 상관관계 & 주요 피쳐 지표 상세 설명 카드 추가 완료")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("🎉 templates/index.html UI 업데이트 완료!")

if __name__ == "__main__":
    apply_feature_7()
