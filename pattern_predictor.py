import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pykrx import stock
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Windows 터미널 한글/인코딩 호환 처리
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Constants
TICKER = '005930'  # 삼성전자
WINDOW_SIZE = 5
NUM_TOP_PATTERNS = 3

def fetch_data(ticker, months=12):
    """pykrx를 사용하여 최근 months 개월 치 일봉 데이터(OHLCV) 수집"""
    today = datetime.now()
    start_date = (today - timedelta(days=365)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")
    
    print(f"[{ticker}] 데이터 수집 시작 ({start_date} ~ {end_date})...")
    df = stock.get_market_ohlcv_by_date(fromdate=start_date, todate=end_date, ticker=ticker)
    time.sleep(1)  # pykrx 서버 부하 방지를 위한 sleep
    return df

def normalize_series(series):
    """시작가/시작점 대비 비율 또는 Min-Max Scaling으로 정규화 (0 ~ 1)"""
    scaler = MinMaxScaler()
    return scaler.fit_transform(series.values.reshape(-1, 1)).flatten()

def find_similar_patterns(df, window_size=WINDOW_SIZE, top_n=NUM_TOP_PATTERNS):
    """
    최근 window_size 일 간의 종가 패턴('현재 패턴')과
    과거 window_size 일 간의 슬라이딩 윈도우 패턴들을 비교하여 코사인 유사도 Top N 추출
    """
    close_prices = df['종가'].values
    dates = df.index
    
    if len(close_prices) < window_size * 2 + 1:
        raise ValueError("데이터 길이가 패턴 매칭을 수행하기에 너무 적습니다.")

    # 현재 패턴 (가장 최근 window_size 영업일)
    current_raw = close_prices[-window_size:]
    current_norm = normalize_series(pd.Series(current_raw))

    results = []

    # 과거 패턴 탐색 (현재 패턴과 중복되지 않는 과거 구간)
    # i는 과거 패턴의 시작 인덱스. 과거 패턴의 다음날(i + window_size)이 존재해야 함.
    max_history_start = len(close_prices) - window_size - 1

    for i in range(0, max_history_start):
        past_raw = close_prices[i : i + window_size]
        past_norm = normalize_series(pd.Series(past_raw))

        # 코사인 유사도 계산
        sim = cosine_similarity(current_norm.reshape(1, -1), past_norm.reshape(1, -1))[0][0]

        # 과거 패턴 종료 다음날(D+1) 수익률 계산
        d_day_close = past_raw[-1]  # 과거 5일차 종가
        d_plus_1_close = close_prices[i + window_size]  # D+1 종가
        next_day_return = ((d_plus_1_close - d_day_close) / d_day_close) * 100.0

        results.append({
            'start_date': dates[i].strftime('%Y-%m-%d'),
            'end_date': dates[i + window_size - 1].strftime('%Y-%m-%d'),
            'd_plus_1_date': dates[i + window_size].strftime('%Y-%m-%d'),
            'similarity': sim,
            'd_plus_1_return': next_day_return,
            'past_end_close': d_day_close,
            'd_plus_1_close': d_plus_1_close
        })

    # 코사인 유사도 기준 내림차순 정렬
    results_df = pd.DataFrame(results)
    top_matches = results_df.sort_values(by='similarity', ascending=False).head(top_n)
    return current_raw, dates[-window_size:], top_matches

def main():
    df = fetch_data(TICKER)
    current_raw, current_dates, top_matches = find_similar_patterns(df)

    print("\n" + "="*60)
    print(f"[패턴 매칭 분석 결과] - 대상: {TICKER} (삼성전자)")
    print("="*60)
    print(f"현재 패턴 기간: {current_dates[0].strftime('%Y-%m-%d')} ~ {current_dates[-1].strftime('%Y-%m-%d')} (5영업일)")
    print(f"현재 패턴 종가 흐름: {[int(x) for x in current_raw]}")
    print("-" * 60)

    print(f"\n[과거 유사 패턴 Top {NUM_TOP_PATTERNS}]")
    returns = []
    for idx, row in top_matches.reset_index(drop=True).iterrows():
        returns.append(row['d_plus_1_return'])
        direction = "[상승]" if row['d_plus_1_return'] > 0 else ("[하락]" if row['d_plus_1_return'] < 0 else "[보합]")
        print(f" [{idx+1}위] 과거 구간: {row['start_date']} ~ {row['end_date']} | 유사도: {row['similarity']*100:.2f}%")
        print(f"      -> 다음날({row['d_plus_1_date']}) 종가: {int(row['d_plus_1_close']):,}원 ({direction} {row['d_plus_1_return']:+.2f}%)")

    avg_return = np.mean(returns)
    up_count = sum(r > 0 for r in returns)
    up_prob = (up_count / len(returns)) * 100.0

    print("\n" + "="*60)
    print("[내일 주가 예측 종합 Summary]")
    print(f" * 예상 등락 방향: {'[상승]' if avg_return > 0 else '[하락]'}")
    print(f" * 내일 상승 확률: {up_prob:.1f}% ({up_count}/{len(returns)}개 구간 상승)")
    print(f" * 평균 예상 변동폭 (D+1): {avg_return:+.2f}%")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
