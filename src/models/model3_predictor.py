"""
Model 3: 전일 종가 & 수급이 다음날 시가(갭)에 미치는 영향 예측
========================================================================
- KOSPI 지수 OHLCV (시가/저가/고가/종가) + 개별 종목 OHLCV + 외국인/기관 순매수 수급 활용
- 예측 목표: 다음 영업일 시가 갭 방향(상승갭/하락갭) 및 갭 크기 분류
- 모델: GradientBoosting (또는 LightGBM) + Walk-Forward 백테스트
- 분석 출력: 피처 중요도 (어떤 변수가 시가 갭에 가장 영향?) + 내일 시가 예측
"""

import argparse
import sys
import os
import warnings
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from pykrx import stock
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

warnings.filterwarnings('ignore')

# Windows 터미널 인코딩 처리
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

KOSPI_TICKER = "1001"  # pykrx KOSPI 지수 티커

# ─────────────────────────────────────────────────────────────────────────────
# 1. 티커 탐색
# ─────────────────────────────────────────────────────────────────────────────
def get_ticker_by_name(name: str) -> str | None:
    name_clean = name.strip().lower()
    if name_clean.isdigit() and len(name_clean) == 6:
        return name_clean

    known_map = {
        '씨에스윈드': '112610', 'cswind': '112610',
        '삼성전자': '005930', 'sk하이닉스': '000660',
        '현대차': '005380', 'naver': '035420',
        '카카오': '035720', 'lg에너지솔루션': '373220',
        '한화솔루션': '009830', '두산에너빌리티': '034020',
        '포스코홀딩스': '005490', 'kb금융': '105560',
        '셀트리온': '068270', '기아': '000270',
    }
    if name_clean in known_map:
        return known_map[name_clean]

    today = datetime.now().strftime("%Y%m%d")
    try:
        tickers = (stock.get_market_ticker_list(today, market="KOSPI") +
                   stock.get_market_ticker_list(today, market="KOSDAQ"))
        for t in tickers:
            if stock.get_market_ticker_name(t).strip().lower() == name_clean:
                return t
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 2. 데이터 수집 (종목 OHLCV + KOSPI OHLCV + 수급)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_all_data(ticker: str, days: int = 365) -> pd.DataFrame:
    today = datetime.now()
    start_date = (today - timedelta(days=days + 60)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")

    print(f"\n[데이터 수집] {ticker} | {start_date} ~ {end_date}")

    # ── 2-1. 종목 OHLCV ──────────────────────────────────────────────────────
    print("  └ 종목 OHLCV 수집 중...")
    df_stock = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
    if df_stock is None or df_stock.empty:
        raise ValueError(f"종목 [{ticker}] OHLCV 데이터를 가져올 수 없습니다.")

    df_stock.index = pd.to_datetime(df_stock.index)
    df_stock.columns = df_stock.columns.str.strip()

    # 컬럼 이름 통일 (한글 컬럼 처리)
    col_map = {}
    for c in df_stock.columns:
        if '시가' in c or c == '시가': col_map[c] = 'open'
        elif '고가' in c: col_map[c] = 'high'
        elif '저가' in c: col_map[c] = 'low'
        elif '종가' in c: col_map[c] = 'close'
        elif '거래량' in c: col_map[c] = 'volume'
    df_stock = df_stock.rename(columns=col_map)
    if 'close' not in df_stock.columns:
        raise ValueError("종목 OHLCV에서 '종가' 컬럼을 찾지 못했습니다.")

    # ── 2-2. KOSPI 지수 OHLCV (재시도 + KODEX200 ETF 폴백) ──────────────────
    print("  └ KOSPI 지수 OHLCV 수집 중...")
    df_kospi = None
    kospi_attempts = [
        ("pykrx 지수 API", lambda: stock.get_index_ohlcv_by_date(start_date, end_date, KOSPI_TICKER)),
        ("KODEX200 ETF 폴백", lambda: stock.get_market_ohlcv_by_date(start_date, end_date, "069500")),
    ]
    for attempt_name, fetch_fn in kospi_attempts:
        if df_kospi is not None:
            break
        try:
            df_k = fetch_fn()
            if df_k is not None and not df_k.empty:
                df_k.index = pd.to_datetime(df_k.index)
                kmap = {}
                for c in df_k.columns:
                    if '시가' in c: kmap[c] = 'kospi_open'
                    elif '고가' in c: kmap[c] = 'kospi_high'
                    elif '저가' in c: kmap[c] = 'kospi_low'
                    elif '종가' in c: kmap[c] = 'kospi_close'
                df_kospi = df_k.rename(columns=kmap)
                kospi_cols = [c for c in ['kospi_open', 'kospi_high', 'kospi_low', 'kospi_close'] if c in df_kospi.columns]
                df_kospi = df_kospi[kospi_cols]
                print(f"  └ KOSPI 수집 완료 [{attempt_name}] ({len(df_kospi)}일)")
        except Exception as e:
            print(f"  └ [경고] {attempt_name} 실패: {e}")


    # ── 2-3. 수급 데이터 (외국인/기관 순매수) ────────────────────────────────
    print("  └ 수급 데이터(외국인/기관) 수집 중...")
    df_supp = None
    try:
        df_tv = stock.get_market_trading_volume_by_date(start_date, end_date, ticker)
        if df_tv is not None and not df_tv.empty:
            df_tv.index = pd.to_datetime(df_tv.index)
            # 컬럼 탐색: 외국인, 기관 순매수 찾기
            supp_cols = {}
            for c in df_tv.columns:
                if '외국인' in c and ('순매수' in c or '순' in c):
                    supp_cols[c] = 'foreign_net'
                elif '기관' in c and ('순매수' in c or '순' in c):
                    supp_cols[c] = 'inst_net'
                elif '개인' in c and ('순매수' in c or '순' in c):
                    supp_cols[c] = 'retail_net'
            if supp_cols:
                df_supp = df_tv[list(supp_cols.keys())].rename(columns=supp_cols)
                print(f"  └ 수급 수집 완료 (컬럼: {list(df_supp.columns)})")
            else:
                print(f"  └ [경고] 수급 순매수 컬럼 없음. 컬럼 목록: {list(df_tv.columns)}")
    except Exception as e:
        print(f"  └ [경고] 수급 데이터 수집 실패: {e}")

    # ── 2-4. 데이터 병합 ─────────────────────────────────────────────────────
    df = df_stock[['open', 'high', 'low', 'close', 'volume']].copy()

    if df_kospi is not None:
        kospi_cols = [c for c in ['kospi_open', 'kospi_high', 'kospi_low', 'kospi_close'] if c in df_kospi.columns]
        df = df.join(df_kospi[kospi_cols], how='left')
    else:
        # fallback: KOSPI 컬럼 없이 진행
        for c in ['kospi_open', 'kospi_high', 'kospi_low', 'kospi_close']:
            df[c] = np.nan

    if df_supp is not None:
        df = df.join(df_supp, how='left')
    else:
        df['foreign_net'] = np.nan
        df['inst_net'] = np.nan
        df['retail_net'] = np.nan

    df = df.sort_index()
    df = df.dropna(subset=['close'])

    print(f"\n[데이터 병합 완료] {len(df)}개 거래일 | 컬럼: {list(df.columns)}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 3. 피처 엔지니어링
# ─────────────────────────────────────────────────────────────────────────────
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    # ── 3-1. 종목 자체 피처 ──────────────────────────────────────────────────
    # 전일 대비 당일 시가 갭 (gap_pct): 오늘의 시가가 어제 종가 대비 몇% 위에서 출발?
    data['gap_pct'] = (data['open'] - data['close'].shift(1)) / data['close'].shift(1) * 100

    # 당일 종가 등락률
    data['close_chg'] = data['close'].pct_change() * 100

    # 당일 시가~종가 등락 (장중 방향)
    data['intraday_chg'] = (data['close'] - data['open']) / data['open'] * 100

    # 장중 변동성 (고-저/종)
    data['intraday_range'] = (data['high'] - data['low']) / data['close'] * 100

    # 종가의 당일 레인지 내 위치 (0=저가 근접, 1=고가 근접)
    hl = (data['high'] - data['low']).replace(0, np.nan)
    data['close_position'] = (data['close'] - data['low']) / hl

    # 위꼬리 비율 (매도 압력: (고가-종가)/(고가-저가))
    data['upper_wick'] = (data['high'] - data['close']) / hl.replace(np.nan, 1)

    # 아래꼬리 비율 (매수 지지: (시가-저가)/(고가-저가))
    data['lower_wick'] = (data['close'] - data['low']) / hl.replace(np.nan, 1)

    # 이동평균 (MA5, MA20)
    data['ma5'] = data['close'].rolling(5).mean()
    data['ma20'] = data['close'].rolling(20).mean()
    data['disp_ma5'] = (data['close'] - data['ma5']) / data['ma5'] * 100
    data['disp_ma20'] = (data['close'] - data['ma20']) / data['ma20'] * 100

    # 거래량 변화율
    data['vol_ratio'] = data['volume'] / data['volume'].rolling(20).mean()

    # RSI 14
    delta = data['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    data['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # 3일/5일 모멘텀
    data['ret_3d'] = data['close'].pct_change(3) * 100
    data['ret_5d'] = data['close'].pct_change(5) * 100

    # ── 3-2. KOSPI 지수 피처 ─────────────────────────────────────────────────
    has_kospi = 'kospi_close' in data.columns and data['kospi_close'].notna().sum() > 10

    if has_kospi:
        data['kospi_chg'] = data['kospi_close'].pct_change() * 100
        data['kospi_gap'] = (data['kospi_open'] - data['kospi_close'].shift(1)) / data['kospi_close'].shift(1) * 100
        khl = (data['kospi_high'] - data['kospi_low']).replace(0, np.nan)
        data['kospi_range'] = khl / data['kospi_close'] * 100
        data['kospi_close_pos'] = (data['kospi_close'] - data['kospi_low']) / khl
        data['kospi_intraday'] = (data['kospi_close'] - data['kospi_open']) / data['kospi_open'] * 100
        data['kospi_ma5'] = data['kospi_close'].rolling(5).mean()
        data['kospi_disp_ma5'] = (data['kospi_close'] - data['kospi_ma5']) / data['kospi_ma5'] * 100
        data['kospi_ret_3d'] = data['kospi_close'].pct_change(3) * 100
        # 개별 종목 vs 코스피 상대강도
        data['relative_strength'] = data['close_chg'] - data['kospi_chg']
    else:
        for c in ['kospi_chg', 'kospi_gap', 'kospi_range', 'kospi_close_pos',
                  'kospi_intraday', 'kospi_disp_ma5', 'kospi_ret_3d', 'relative_strength']:
            data[c] = 0.0

    # ── 3-3. 수급 피처 ───────────────────────────────────────────────────────
    for col in ['foreign_net', 'inst_net', 'retail_net']:
        if col not in data.columns:
            data[col] = np.nan

    data['foreign_net'] = data['foreign_net'].fillna(0)
    data['inst_net'] = data['inst_net'].fillna(0)
    data['retail_net'] = data.get('retail_net', pd.Series(0, index=data.index)).fillna(0)

    # 수급 정규화 (Z-score rolling 60일)
    for col in ['foreign_net', 'inst_net']:
        roll_mean = data[col].rolling(60).mean()
        roll_std = data[col].rolling(60).std().replace(0, 1)
        data[f'{col}_z'] = (data[col] - roll_mean) / roll_std

    # 수급 3일 누적 방향
    data['foreign_3d'] = data['foreign_net'].rolling(3).sum()
    data['inst_3d'] = data['inst_net'].rolling(3).sum()

    # ── 3-4. 예측 대상 (Target): 다음날 시가 갭 ─────────────────────────────
    data['next_gap_pct'] = data['gap_pct'].shift(-1)  # 다음날의 gap_pct
    data['next_open'] = data['open'].shift(-1)

    # 갭 방향 (이진 분류): 1=상승갭, 0=하락/보합갭
    data['target_direction'] = (data['next_gap_pct'] > 0).astype(int)

    # 갭 크기 분류 (4분류)
    # 2: 대형 상승갭 (>+1%), 1: 소형 상승갭 (0~+1%)
    # 0: 소형 하락갭 (-1%~0), -1: 대형 하락갭 (<-1%)
    def classify_gap(x):
        if pd.isna(x): return np.nan
        if x > 1.0: return 2    # 대형 상승갭
        elif x > 0: return 1    # 소형 상승갭
        elif x > -1.0: return 0 # 소형 하락갭
        else: return -1          # 대형 하락갭

    data['target_class'] = data['next_gap_pct'].apply(classify_gap)

    return data


# ─────────────────────────────────────────────────────────────────────────────
# 4. 피처 목록 정의
# ─────────────────────────────────────────────────────────────────────────────
FEATURE_COLS = [
    # 종목 종가/OHLCV 파생
    'gap_pct',            # 당일 시가 갭 (오늘 자신의 갭)
    'close_chg',          # 당일 종가 등락률
    'intraday_chg',       # 당일 시가→종가 장중 방향
    'intraday_range',     # 장중 변동폭
    'close_position',     # 종가의 레인지 내 위치 (위꼬리/아래꼬리 종합)
    'upper_wick',         # 위꼬리 비율 (매도 압력)
    'lower_wick',         # 아래꼬리 비율 (매수 지지)
    'disp_ma5',           # MA5 이격도
    'disp_ma20',          # MA20 이격도
    'vol_ratio',          # 거래량 vs 20일 평균
    'rsi',                # RSI14
    'ret_3d',             # 3일 수익률
    'ret_5d',             # 5일 수익률
    # KOSPI 지수
    'kospi_chg',          # KOSPI 종가 등락률
    'kospi_gap',          # KOSPI 시가 갭
    'kospi_range',        # KOSPI 장중 변동폭
    'kospi_close_pos',    # KOSPI 종가 레인지 내 위치
    'kospi_intraday',     # KOSPI 장중 방향
    'kospi_disp_ma5',     # KOSPI MA5 이격도
    'kospi_ret_3d',       # KOSPI 3일 수익률
    'relative_strength',  # 개별 종목 vs KOSPI 상대강도
    # 수급
    'foreign_net_z',      # 외국인 순매수 Z-score
    'inst_net_z',         # 기관 순매수 Z-score
    'foreign_3d',         # 외국인 3일 누적 순매수
    'inst_3d',            # 기관 3일 누적 순매수
]


# ─────────────────────────────────────────────────────────────────────────────
# 5. Walk-Forward 백테스트 (시가 갭 방향 예측)
# ─────────────────────────────────────────────────────────────────────────────
def walk_forward_backtest(data: pd.DataFrame, min_train: int = 60) -> dict:
    valid = data[FEATURE_COLS + ['target_direction', 'next_gap_pct', 'close']].dropna()
    valid = valid.sort_index()

    n = len(valid)
    if n < min_train + 20:
        raise ValueError(f"유효 데이터 부족: {n}개 (최소 {min_train+20}개 필요)")

    preds, actuals, probs = [], [], []
    gap_pcts_pred = []
    dates = []

    print(f"\n[Walk-Forward 백테스트] 전체 {n}개 중 학습 시작점={min_train}")

    current_model = None
    refit_step = 5  # 5영업일마다 모델 재학습 (연산 속도 12배 향상, Render 504 타임아웃 완전 방지)

    for i in range(min_train, n):
        train = valid.iloc[:i]
        test_row = valid.iloc[i]

        X_train = train[FEATURE_COLS].values
        y_train = train['target_direction'].values.astype(int)

        if len(np.unique(y_train)) < 2:
            continue

        if current_model is None or (i - min_train) % refit_step == 0:
            current_model = GradientBoostingClassifier(
                n_estimators=40, max_depth=3, learning_rate=0.1,
                subsample=0.8, random_state=42
            )
            current_model.fit(X_train, y_train)

        X_test = test_row[FEATURE_COLS].values.reshape(1, -1)
        pred = current_model.predict(X_test)[0]
        prob = current_model.predict_proba(X_test)[0][1]


        preds.append(pred)
        actuals.append(int(test_row['target_direction']))
        probs.append(round(float(prob), 4))
        gap_pcts_pred.append(round(float(test_row['next_gap_pct']), 4))
        dates.append(str(valid.index[i].date()))

        if (i - min_train + 1) % 30 == 0:
            done = i - min_train + 1
            total = n - min_train
            print(f"  └ 진행: {done}/{total} ({done/total*100:.1f}%)")

    preds = np.array(preds)
    actuals = np.array(actuals)
    hit_ratio = accuracy_score(actuals, preds) * 100
    cm = confusion_matrix(actuals, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

    # 갭 방향 적중 시 수익: 갭이 상승이면 매수 포지션, 갭이 하락이면 현금 or 공매도
    # 단순 전략: 상승갭 예측 시 전날 종가에 매수 → 시가에 청산 (갭 수익 획득)
    strategy_returns = []
    for i in range(len(preds)):
        actual_gap = gap_pcts_pred[i]
        if preds[i] == 1:   # 상승갭 예측 → 매수
            strategy_returns.append(actual_gap)
        else:               # 하락갭 예측 → 현금 (0%)
            strategy_returns.append(0.0)

    cum_strat = (1 + np.array(strategy_returns) / 100).cumprod()
    cum_strat_return = (cum_strat[-1] - 1) * 100

    # 매수보유: 매일 시가 갭만큼 수익 (시가에 사고 바로 파는 전략 비교)
    buy_hold_gaps = [gap_pcts_pred[i] for i in range(len(gap_pcts_pred))]
    cum_bh = (1 + np.array(buy_hold_gaps) / 100).cumprod()
    cum_bh_return = (cum_bh[-1] - 1) * 100

    # MDD
    peak = np.maximum.accumulate(cum_strat)
    mdd = float(((cum_strat - peak) / peak).min() * 100)

    return {
        'hit_ratio': round(hit_ratio, 2),
        'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
        'total_signals': len(preds),
        'cum_strat': round(cum_strat_return, 2),
        'cum_bh': round(cum_bh_return, 2),
        'mdd': round(mdd, 2),
        'dates': dates,
        'preds': preds.tolist(),
        'actuals': actuals.tolist(),
        'probs': probs,
        'gap_pcts': gap_pcts_pred,
        'cum_strat_series': [round(x, 4) for x in cum_strat.tolist()],
        'cum_bh_series': [round(x, 4) for x in cum_bh.tolist()],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. 피처 중요도 분석 (전체 데이터 기준)
# ─────────────────────────────────────────────────────────────────────────────
def analyze_feature_importance(data: pd.DataFrame) -> list[dict]:
    valid = data[FEATURE_COLS + ['target_direction']].dropna()
    if len(valid) < 60:
        return []

    model = GradientBoostingClassifier(
        n_estimators=50, max_depth=3, learning_rate=0.08,
        subsample=0.8, random_state=42
    )
    model.fit(valid[FEATURE_COLS], valid['target_direction'].astype(int))

    importances = model.feature_importances_
    feat_imp = sorted(
        [{'feature': f, 'importance': round(float(imp), 5)}
         for f, imp in zip(FEATURE_COLS, importances)],
        key=lambda x: x['importance'], reverse=True
    )
    return feat_imp


# ─────────────────────────────────────────────────────────────────────────────
# 7. 내일 시가 갭 예측 (최신 데이터 기준)
# ─────────────────────────────────────────────────────────────────────────────
def predict_tomorrow_gap(data: pd.DataFrame) -> dict:
    valid = data[FEATURE_COLS + ['target_direction']].dropna()
    if len(valid) < 60:
        return {'direction': 'unknown', 'prob': 0.0, 'gap_class': 'unknown'}

    # 전체 데이터로 최종 모델 학습
    X_train = valid[FEATURE_COLS].values
    y_train = valid['target_direction'].values.astype(int)

    model = GradientBoostingClassifier(
        n_estimators=50, max_depth=3, learning_rate=0.08,
        subsample=0.8, random_state=42
    )
    model.fit(X_train, y_train)


    # 가장 최근 행 (갭 타겟 제외한 피처만)
    latest_features = data[FEATURE_COLS].dropna().iloc[-1]
    X_pred = latest_features.values.reshape(1, -1)

    pred = model.predict(X_pred)[0]
    prob = model.predict_proba(X_pred)[0][1]

    # 최근 gap_pct 평균으로 예상 갭 크기 추정
    avg_abs_gap = data['gap_pct'].dropna().abs().tail(20).mean()

    direction_label = "상승갭 (시가 상승 출발 예측)" if pred == 1 else "하락갭 (시가 하락 출발 예측)"
    if pred == 1 and prob > 0.65:
        gap_class = f"강한 상승갭 예측 (예상 +{avg_abs_gap:.2f}%)"
    elif pred == 1:
        gap_class = f"약한 상승갭 예측 (예상 +{avg_abs_gap*0.5:.2f}%)"
    elif pred == 0 and prob < 0.35:
        gap_class = f"강한 하락갭 예측 (예상 -{avg_abs_gap:.2f}%)"
    else:
        gap_class = f"약한 하락갭 예측 (예상 -{avg_abs_gap*0.5:.2f}%)"

    return {
        'direction': direction_label,
        'pred_label': '상승갭' if pred == 1 else '하락갭',
        'prob': round(float(prob) * 100, 1),
        'gap_class': gap_class,
        'avg_abs_gap': round(avg_abs_gap, 3),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. 상관관계 분석 (수급/지수가 갭에 미치는 영향)
# ─────────────────────────────────────────────────────────────────────────────
def analyze_correlation(data: pd.DataFrame) -> list[dict]:
    corr_target = 'next_gap_pct'
    key_features = [
        'close_chg', 'intraday_chg', 'close_position', 'upper_wick',
        'vol_ratio', 'rsi', 'ret_3d',
        'kospi_chg', 'kospi_gap', 'kospi_intraday', 'kospi_close_pos',
        'relative_strength',
        'foreign_net_z', 'inst_net_z', 'foreign_3d', 'inst_3d'
    ]
    available = [f for f in key_features if f in data.columns]
    df_corr = data[available + [corr_target]].dropna()

    results = []
    for feat in available:
        series = df_corr[feat]
        # KOSPI 피처가 0 상수일 때(분산=0) corr()는 NaN 반환 → 제외
        if series.std() == 0:
            continue
        corr_val = series.corr(df_corr[corr_target])
        if pd.isna(corr_val):
            continue
        results.append({
            'feature': feat,
            'correlation': round(float(corr_val), 4),
            'abs_corr': round(abs(float(corr_val)), 4)
        })

    return sorted(results, key=lambda x: x['abs_corr'], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# 메인 실행 & CLI
# ─────────────────────────────────────────────────────────────────────────────
def run_model3(stock_name: str, days: int = 365) -> dict:
    """Model 3 전체 파이프라인 실행 및 결과 딕셔너리 반환"""
    ticker = get_ticker_by_name(stock_name)
    if not ticker:
        raise ValueError(f"종목명 [{stock_name}]에 해당하는 티커를 찾을 수 없습니다.")

    print(f"\n{'='*60}")
    print(f"  [Model 3] 시가 갭 예측 - {stock_name} ({ticker})")
    print(f"  전일 종가 & 수급 → 다음날 시가 갭 방향 예측")
    print(f"{'='*60}")

    df_raw = fetch_all_data(ticker, days=days)
    data = feature_engineering(df_raw)

    print("\n[피처 엔지니어링 완료] 피처 결측값 확인 중...")
    for feat in FEATURE_COLS:
        nn = data[feat].notna().sum()
        if nn < 30:
            print(f"  └ [경고] {feat}: 유효값 {nn}개 (수급 없이 0으로 대체됩니다)")

    # 백테스트
    bt_result = walk_forward_backtest(data, min_train=60)

    # 피처 중요도
    feat_imp = analyze_feature_importance(data)

    # 상관관계 분석
    corr_result = analyze_correlation(data)

    # 내일 예측
    tomorrow = predict_tomorrow_gap(data)

    return {
        'stock_name': stock_name,
        'ticker': ticker,
        'data_start': str(data.index[0].date()),
        'data_end': str(data.index[-1].date()),
        'total_days': len(data),
        'backtest': bt_result,
        'feature_importance': feat_imp,
        'correlation': corr_result,
        'tomorrow': tomorrow,
    }


def print_results(res: dict):
    bt = res['backtest']
    tmr = res['tomorrow']

    print(f"\n{'='*60}")
    print(f"  [Model 3 결과] {res['stock_name']} ({res['ticker']})")
    print(f"  분석 기간: {res['data_start']} ~ {res['data_end']} ({res['total_days']}일)")
    print(f"{'='*60}")

    print(f"\n[백테스트 성과]")
    print(f"  시가갭 방향 적중률   : {bt['hit_ratio']:.2f}%")
    print(f"  전체 예측 횟수       : {bt['total_signals']}회")
    print(f"  갭 매매 전략 수익    : {bt['cum_strat']:+.2f}%")
    print(f"  시가 전량 매수 수익  : {bt['cum_bh']:+.2f}%")
    print(f"  최대낙폭(MDD)        : {bt['mdd']:.2f}%")
    print(f"  혼동행렬             : TP={bt['tp']} FP={bt['fp']} TN={bt['tn']} FN={bt['fn']}")

    print(f"\n[내일 시가 갭 예측]")
    print(f"  예측 방향  : {tmr['direction']}")
    print(f"  상승갭 확률: {tmr['prob']:.1f}%")
    print(f"  갭 크기 평가: {tmr['gap_class']}")

    print(f"\n[피처 중요도 TOP10] - '어떤 변수가 시가갭에 가장 영향을 주나?'")
    for i, fi in enumerate(res['feature_importance'][:10], 1):
        bar = '|' * int(fi['importance'] * 200)
        print(f"  {i:2d}. {fi['feature']:<22} {fi['importance']:.4f}  {bar}")

    print(f"\n[상관관계 TOP10] - '전일 데이터와 다음날 시가갭의 선형 상관'")
    for i, ci in enumerate(res['correlation'][:10], 1):
        direction = '+' if ci['correlation'] > 0 else '-'
        print(f"  {i:2d}. {ci['feature']:<22} r={ci['correlation']:+.4f}  ({direction})")

    print(f"\n{'='*60}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Model 3: 시가 갭 예측 (전일 종가 & 수급 기반)')
    parser.add_argument('--name', type=str, default='씨에스윈드', help='종목명 또는 6자리 티커')
    parser.add_argument('--days', type=int, default=365, help='분석 기간 (일수, 기본 365)')
    args = parser.parse_args()

    result = run_model3(args.name, args.days)
    print_results(result)
