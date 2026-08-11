import argparse
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from pykrx import stock
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Windows 터미널 인코딩 처리
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_ticker_by_name(name):
    """종목명 또는 6자리 티커 반환"""
    name_clean = name.strip().lower()
    if name_clean.isdigit() and len(name_clean) == 6:
        return name_clean

    known_map = {
        '씨에스윈드': '112610',
        'cswind': '112610',
        '삼성전자': '005930',
        'sk하이닉스': '000660',
        '현대차': '005380',
        'naver': '035420'
    }
    if name_clean in known_map:
        return known_map[name_clean]
        
    today = datetime.now().strftime("%Y%m%d")
    try:
        tickers = stock.get_market_ticker_list(today, market="KOSPI") + stock.get_market_ticker_list(today, market="KOSDAQ")
        for t in tickers:
            if stock.get_market_ticker_name(t).strip().lower() == name_clean:
                return t
    except Exception:
        pass
    return None

def fetch_2year_data(ticker):
    """2년치(730일) 일봉 데이터 수집"""
    today = datetime.now()
    start_date = (today - timedelta(days=730)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    print(f"[{ticker}] 최근 2년치 데이터 수집 중 ({start_date} ~ {end_date})...")
    df = stock.get_market_ohlcv_by_date(fromdate=start_date, todate=end_date, ticker=ticker)
    time.sleep(1)
    
    if df.empty or len(df) < 300:
        raise ValueError("분석에 필요한 2년치 데이터를 가져오지 못했습니다.")
        
    return df

def feature_engineering(df):
    """이동평균, 이격도, RSI, 거래량 변동률 등 지표 생성"""
    data = df.copy()
    
    data['MA5'] = data['종가'].rolling(window=5).mean()
    data['MA20'] = data['종가'].rolling(window=20).mean()
    data['MA60'] = data['종가'].rolling(window=60).mean()

    data['Disparity_MA5'] = data['종가'] / data['MA5']
    data['Disparity_MA20'] = data['종가'] / data['MA20']

    delta = data['종가'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    data['RSI14'] = 100 - (100 / (1 + rs))

    data['Return_1D'] = data['종가'].pct_change(1)
    data['Return_3D'] = data['종가'].pct_change(3)
    data['Return_5D'] = data['종가'].pct_change(5)

    data['Vol_Change'] = data['거래량'].pct_change(1)
    data['Vol_MA5'] = data['거래량'] / (data['거래량'].rolling(5).mean() + 1e-9)
    data['Volatility_5D'] = data['Return_1D'].rolling(5).std()

    # 타겟: D+1 상승 1, 하락/보합 0
    data['Next_Return'] = data['종가'].pct_change(1).shift(-1)
    data['Target'] = (data['Next_Return'] > 0).astype(int)

    return data.dropna()

def analyze_2year_weekly_predictions(data, target_week_idx=-1):
    """
    1. 데이터 분할:
       - 학습 데이터 (Year -2 ~ Year -1): 전반부 ~50%
       - 검증 데이터 (Recent 1 Year): 후반부 ~50%
    2. 학습 데이터로 머신러닝 모델 훈련
    3. 최근 1년 분량 주차(Weekly, 5영업일 단위)별 예측 정확도 및 특정 주 성능 분석
    """
    total_len = len(data)
    split_idx = total_len // 2  # 절반 기준 (약 1년 전 시점)

    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]

    feature_cols = [c for c in data.columns if c not in ['Target', 'Next_Return', '시가', '고가', '저가', '종가', '거래량', '등락률']]
    
    X_train = train_data[feature_cols].values
    y_train = train_data['Target'].values

    X_test = test_data[feature_cols].values
    y_test = test_data['Target'].values
    returns_test = test_data['Next_Return'].values
    test_dates = test_data.index

    # 모델 학습 (Year -2 ~ Year -1 데이터 기준)
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # 최근 1년 아웃오브샘플(Out-of-Sample) 데이터 예측
    predictions = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    # Overall Metrics
    hit_ratio = accuracy_score(y_test, predictions) * 100.0
    cm = confusion_matrix(y_test, predictions) # [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm.ravel()

    # Strategy Returns vs Buy & Hold
    strat_returns = np.where(predictions == 1, returns_test, 0.0)
    cum_strat = (np.cumprod(1 + strat_returns) - 1) * 100.0
    cum_buy_hold = (np.cumprod(1 + returns_test) - 1) * 100.0

    peak = np.maximum.accumulate(1 + cum_strat / 100.0)
    drawdown = ((1 + cum_strat / 100.0) - peak) / peak
    mdd = float(np.min(drawdown) * 100.0)

    total_trades = sum(predictions == 1)
    win_rate = (sum(strat_returns > 0) / total_trades * 100.0) if total_trades > 0 else 0.0

    # 주차(Weekly, 5영업일 단위)별 분석
    num_days = len(test_data)
    weeks = []
    for w in range(0, num_days, 5):
        w_end = min(w + 5, num_days)
        if w_end - w < 3: # 최소 3일 이상 주차만 포함
            continue
        
        w_y_test = y_test[w:w_end]
        w_preds = predictions[w:w_end]
        w_acc = accuracy_score(w_y_test, w_preds) * 100.0
        
        weeks.append({
            'week_num': len(weeks) + 1,
            'start_date': test_dates[w].strftime("%Y-%m-%d"),
            'end_date': test_dates[w_end-1].strftime("%Y-%m-%d"),
            'days': w_end - w,
            'accuracy': w_acc,
            'preds': w_preds,
            'actuals': w_y_test,
            'dates': [d.strftime("%Y-%m-%d") for d in test_dates[w:w_end]],
            'close_prices': test_data['종가'].values[w:w_end],
            'returns': returns_test[w:w_end]
        })

    # 특정 주 (지정 주차, 기본: 가장 최근 1주일)
    target_week = weeks[target_week_idx]

    return {
        'train_start': train_data.index[0].strftime("%Y-%m-%d"),
        'train_end': train_data.index[-1].strftime("%Y-%m-%d"),
        'train_count': len(train_data),
        'test_start': test_data.index[0].strftime("%Y-%m-%d"),
        'test_end': test_data.index[-1].strftime("%Y-%m-%d"),
        'test_count': len(test_data),
        'hit_ratio': hit_ratio,
        'cm': {'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn},
        'cum_strat': cum_strat[-1],
        'cum_buy_hold': cum_buy_hold[-1],
        'win_rate': win_rate,
        'total_trades': total_trades,
        'mdd': mdd,
        'weeks_count': len(weeks),
        'weeks_avg_acc': np.mean([w['accuracy'] for w in weeks]),
        'target_week': target_week
    }

def main():
    parser = argparse.ArgumentParser(description='2년 데이터 기반 최근 1년 특정 주 주가 예측 정확도 분석')
    parser.add_argument('--name', type=str, default='씨에스윈드', help='대상 종목명 (기본: 씨에스윈드)')
    args = parser.parse_args()

    stock_name = args.name
    print(f"\n============================================================")
    print(f"📊 [2년치 데이터 기반 학습 & 최근 1년 주차별 예측 분석]")
    print(f"============================================================")
    print(f"대상 종목: {stock_name}")

    ticker = get_ticker_by_name(stock_name)
    if not ticker:
        print(f"❌ 종목명 [{stock_name}] 티커를 찾지 못했습니다.")
        sys.exit(1)

    print(f"종목 코드(Ticker): {ticker}")

    df = fetch_2year_data(ticker)
    data = feature_engineering(df)

    res = analyze_2year_weekly_predictions(data)

    print("\n" + "="*60)
    print("📌 [1. 데이터 분할 & 학습/검증 데이터셋 정보]")
    print("="*60)
    print(f" • 학습 데이터 (Year -2 ~ Year -1) : {res['train_start']} ~ {res['train_end']} ({res['train_count']} 영업일)")
    print(f" • 검증 데이터 (최근 1년 Out-of-Sample): {res['test_start']} ~ {res['test_end']} ({res['test_count']} 영업일)")
    print("-" * 60)

    print("\n" + "="*60)
    print("📈 [2. 최근 1년 전체 예측 정확도 (Out-of-Sample Performance)]")
    print("="*60)
    print(f" • 전체 적중률 (Hit Ratio): {res['hit_ratio']:.2f}%")
    print(f" • 오차 행렬 (Confusion Matrix):")
    print(f"    - True Positive (상승 예측 적중) : {res['cm']['TP']} 회")
    print(f"    - False Positive (상승 예측 틀림) : {res['cm']['FP']} 회")
    print(f"    - True Negative (하락 예측 적중) : {res['cm']['TN']} 회")
    print(f"    - False Negative (하락 예측 틀림) : {res['cm']['FN']} 회")
    print(f" • 모델 매수 승률 (Win Rate): {res['win_rate']:.1f}% ({res['total_trades']}회 매수)")
    print(f" • 전략 누적 수익률: {res['cum_strat']:+.2f}% vs 단순보유: {res['cum_buy_hold']:+.2f}%")
    print(f" • 최대 낙폭 (MDD): {res['mdd']:.2f}%")

    tw = res['target_week']
    print("\n" + "="*60)
    print(f"🔍 [3. 최근 1년 중 특정 주차(최근 주: {tw['start_date']} ~ {tw['end_date']}) 심층 분석]")
    print("="*60)
    print(f" • 해당 주차 적중률 (Hit Ratio): {tw['accuracy']:.1f}% ({sum(np.array(tw['preds']) == np.array(tw['actuals']))}/{tw['days']} 영업일 적중)")
    print(" • 일별 상세 예측 내역:")
    for d_idx in range(tw['days']):
        date_str = tw['dates'][d_idx]
        close_p = int(tw['close_prices'][d_idx])
        pred_label = "상승 🔺" if tw['preds'][d_idx] == 1 else "하락 🔻"
        actual_label = "상승 🔺" if tw['actuals'][d_idx] == 1 else "하락 🔻"
        is_correct = "✅ 적중" if tw['preds'][d_idx] == tw['actuals'][d_idx] else "❌ 오답"
        ret_val = tw['returns'][d_idx] * 100.0
        
        print(f"   [{date_str}] 종가: {close_p:,}원 | 예측: {pred_label} | 실제: {actual_label} ({ret_val:+.2f}%) ➔ {is_correct}")

    print("="*60 + "\n")

if __name__ == "__main__":
    main()
