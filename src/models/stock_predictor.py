import argparse
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from pykrx import stock
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

# Windows 터미널 인코딩 처리
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_ticker_by_name(name):
    """종목명 또는 티커 코드를 받아 6자리 티커 반환"""
    name_clean = name.strip().lower()
    
    # 6자리 티커 코드 직접 입력 시
    if name_clean.isdigit() and len(name_clean) == 6:
        return name_clean

    # 자주 조회되는 주요 종목 맵핑
    known_map = {
        '씨에스윈드': '112610',
        'cswind': '112610',
        '삼성전자': '005930',
        'sk하이닉스': '000660',
        '현대차': '005380',
        'naver': '035420',
        '카카오': '035720',
        'lg에너지솔루션': '373220',
        '한화솔루션': '009830',
        '두산에너빌리티': '034020'
    }
    if name_clean in known_map:
        return known_map[name_clean]
        
    # KOSPI & KOSDAQ 티커 동적 탐색
    today = datetime.now().strftime("%Y%m%d")
    try:
        tickers = stock.get_market_ticker_list(today, market="KOSPI") + stock.get_market_ticker_list(today, market="KOSDAQ")
        for t in tickers:
            if stock.get_market_ticker_name(t).strip().lower() == name_clean:
                return t
    except Exception:
        pass
        
    return None

def fetch_market_data(ticker, days=365):
    """pykrx를 활용한 1년치 일봉 데이터 및 보조 지표 수집"""
    today = datetime.now()
    start_date = (today - timedelta(days=days)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    print(f"[{ticker}] 최근 1년 OHLCV 및 수급/지표 데이터 수집 중 ({start_date} ~ {end_date})...")
    df = stock.get_market_ohlcv_by_date(fromdate=start_date, todate=end_date, ticker=ticker)
    time.sleep(0.5)

    if df.empty:
        raise ValueError(f"티커 [{ticker}]의 데이터를 가져올 수 없습니다.")

    # 펀더멘털 데이터 (PER, PBR 등) 수집시도 (오류 발생 시 기술적 지표로 대체)
    try:
        fund_df = stock.get_market_fundamental_by_date(fromdate=start_date, todate=end_date, ticker=ticker)
        time.sleep(0.5)
        if not fund_df.empty:
            df = df.join(fund_df[['PER', 'PBR']], how='left').fillna(method='ffill').fillna(0)
    except Exception as e:
        print(f"펀더멘털 데이터 수집 건너뜀 (기본 지표 사용): {e}")

    return df

def feature_engineering(df):
    """주가, 거래량, 이동평균, RSI, 모멘텀 지표 생성"""
    data = df.copy()
    
    # 1. 이동평균선 (MA5, MA20, MA60)
    data['MA5'] = data['종가'].rolling(window=5).mean()
    data['MA20'] = data['종가'].rolling(window=20).mean()
    data['MA60'] = data['종가'].rolling(window=60).mean()

    # 2. 이동평균 이격도 (Price to MA ratio)
    data['Disparity_MA5'] = data['종가'] / data['MA5']
    data['Disparity_MA20'] = data['종가'] / data['MA20']

    # 3. RSI (Relative Strength Index 14)
    delta = data['종가'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    data['RSI14'] = 100 - (100 / (1 + rs))

    # 4. 가격 모멘텀 (1일, 3일, 5일 등락률)
    data['Return_1D'] = data['종가'].pct_change(1)
    data['Return_3D'] = data['종가'].pct_change(3)
    data['Return_5D'] = data['종가'].pct_change(5)

    # 5. 거래량 변동률 & 5일 변동성
    data['Vol_Change'] = data['거래량'].pct_change(1)
    data['Vol_MA5'] = data['거래량'] / (data['거래량'].rolling(5).mean() + 1e-9)
    data['Volatility_5D'] = data['Return_1D'].rolling(5).std()

    # 타겟 생성: 내일(D+1) 종가가 오늘 종가보다 높으면 1 (상승), 이하 0 (하락)
    data['Next_Return'] = data['종가'].pct_change(1).shift(-1)
    data['Target'] = (data['Next_Return'] > 0).astype(int)

    # 결측치 제거
    data = data.dropna()
    return data

def run_walk_forward_backtest(data, model_type='rf', min_train_size=60):
    """
    워크포워드(Walk-Forward / Expanding Window) 백테스팅 수행
    시간순 데이터 누출(Data Leakage) 없는 미래 예측 검증
    """
    feature_cols = [c for c in data.columns if c not in ['Target', 'Next_Return', '시가', '고가', '저가', '종가', '거래량', '등락률']]
    
    X = data[feature_cols].values
    y = data['Target'].values
    returns = data['Next_Return'].values
    dates = data.index

    predictions = []
    actuals = []
    strat_returns = []
    buy_hold_returns = []
    test_dates = []

    # 슬라이딩/확장 윈도우 백테스트
    for i in range(min_train_size, len(data)):
        X_train, y_train = X[:i], y[:i]
        X_test = X[i:i+1]
        
        # 모델 선택
        if model_type == 'rf':
            model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        else:
            model = GradientBoostingClassifier(n_estimators=50, learning_rate=0.05, max_depth=3, random_state=42)
            
        model.fit(X_train, y_train)
        pred = model.predict(X_test)[0]
        
        actual = y[i]
        ret = returns[i]
        
        # 매수 전략 (예측이 1일 때 매수 포지션, 0일 때 현금 보유)
        strat_ret = ret if pred == 1 else 0.0
        
        predictions.append(pred)
        actuals.append(actual)
        strat_returns.append(strat_ret)
        buy_hold_returns.append(ret)
        test_dates.append(dates[i])

    # 성과 지표 산출
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    strat_returns = np.array(strat_returns)
    buy_hold_returns = np.array(buy_hold_returns)

    # 누적 수익률 계산
    cum_strat = np.cumprod(1 + strat_returns) - 1
    cum_buy_hold = np.cumprod(1 + buy_hold_returns) - 1

    # MDD (최대 낙폭) 계산
    peak = np.maximum.accumulate(1 + cum_strat)
    drawdown = ((1 + cum_strat) - peak) / peak
    mdd = np.min(drawdown) * 100.0

    hit_ratio = accuracy_score(actuals, predictions) * 100.0
    win_days = sum(strat_returns > 0)
    total_trades = sum(predictions == 1)
    win_rate = (win_days / total_trades * 100.0) if total_trades > 0 else 0.0

    # 내일(D+1) 최종 방향 예측 (가장 최근 데이터 기반)
    X_latest = X[-1:]
    latest_model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
    latest_model.fit(X, y)
    tomorrow_pred = latest_model.predict(X_latest)[0]
    tomorrow_prob = latest_model.predict_proba(X_latest)[0][1] * 100.0

    return {
        'hit_ratio': hit_ratio,
        'cum_strat': cum_strat[-1] * 100.0,
        'cum_buy_hold': cum_buy_hold[-1] * 100.0,
        'win_rate': win_rate,
        'total_trades': total_trades,
        'mdd': mdd,
        'tomorrow_pred': "상승 🔺" if tomorrow_pred == 1 else "하락 🔻",
        'tomorrow_prob': tomorrow_prob,
        'test_count': len(test_dates),
        'start_date': test_dates[0].strftime("%Y-%m-%d"),
        'end_date': test_dates[-1].strftime("%Y-%m-%d")
    }

def main():
    parser = argparse.ArgumentParser(description='주가 방향 예측 및 백테스팅 모델')
    parser.add_argument('--name', type=str, default='씨에스윈드', help='분석 대상 종목명 (기본: 씨에스윈드)')
    args = parser.parse_args()

    stock_name = args.name
    print(f"\n===== [주가 예측 & 백테스트 분석 시스템] =====")
    print(f"분석 대상 종목: {stock_name}")

    ticker = get_ticker_by_name(stock_name)
    if not ticker:
        print(f"❌ 종목명 [{stock_name}]에 해당하는 티커를 찾지 못했습니다.")
        sys.exit(1)

    print(f"종목 코드(Ticker): {ticker}")

    # 데이터 수집 및 가공
    df = fetch_market_data(ticker)
    data = feature_engineering(df)

    # 백테스팅 실행
    print("\n⏳ 워크포워드 백테스트(Walk-Forward Backtest) 실행 중...")
    results = run_walk_forward_backtest(data)

    print("\n" + "="*60)
    print(f"📊 [{stock_name} ({ticker})] 백테스트 분석 결과 리포트")
    print("="*60)
    print(f" • 백테스트 구간: {results['start_date']} ~ {results['end_date']} (총 {results['test_count']} 거래일)")
    print(f" • 예측 적중률 (Hit Ratio): {results['hit_ratio']:.2f}%")
    print(f" • 매수 트레이딩 횟수: {results['total_trades']} 회 (승률: {results['win_rate']:.1f}%)")
    print(f" • 모델 누적 수익률: {results['cum_strat']:+.2f}%")
    print(f" • 단순 보유(Buy & Hold) 수익률: {results['cum_buy_hold']:+.2f}%")
    print(f" • 최대 낙폭 (MDD): {results['mdd']:.2f}%")
    print("-" * 60)
    print(f"🔮 [내일 주가 방향 예측]")
    print(f" • 예측 결과: {results['tomorrow_pred']}")
    print(f" • 상승 확률: {results['tomorrow_prob']:.1f}%")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
