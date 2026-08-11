import sys
import os
import time
from datetime import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify

# src 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db import database as db
from src.models.stock_predictor import (
    get_ticker_by_name,
    fetch_market_data,
    feature_engineering,
    run_walk_forward_backtest
)
from src.models.two_year_predictor import (
    fetch_2year_data,
    analyze_2year_weekly_predictions
)
from src.models.model3_predictor import (
    run_model3,
    get_ticker_by_name as get_ticker_m3
)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
db.init_db()


def sanitize_json(obj):
    """NaN / Infinity 값을 JSON 직렬화 가능한 None으로 재귀 변환"""
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return obj



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    req_data = request.get_json() or {}
    stock_name = req_data.get('stock_name', '').strip() or '삼성전자'
    
    if not stock_name:
        return jsonify({'error': '종목명을 입력해 주세요.'}), 400

    # 1년 워크포워드 SQLite 캐시 확인
    cached_data = db.get_cached_prediction(stock_name)
    if cached_data:
        print(f"[SQLite 1-Year Cache HIT] '{stock_name}'")
        return jsonify({'cached': True, 'data': cached_data})

    print(f"[SQLite 1-Year Cache MISS] '{stock_name}' 계산 중...")
    ticker = get_ticker_by_name(stock_name)
    if not ticker:
        return jsonify({'error': f"종목명 [{stock_name}]에 해당하는 티커를 찾지 못했습니다."}), 404

    try:
        df = fetch_market_data(ticker)
        data = feature_engineering(df)
        
        feature_cols = [c for c in data.columns if c not in ['Target', 'Next_Return', '시가', '고가', '저가', '종가', '거래량', '등락률']]
        X = data[feature_cols].values
        y = data['Target'].values
        returns = data['Next_Return'].values
        dates = data.index

        min_train_size = 60
        predictions, actuals, strat_returns, buy_hold_returns, chart_dates = [], [], [], [], []

        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score

        for i in range(min_train_size, len(data)):
            X_train, y_train = X[:i], y[:i]
            X_test = X[i:i+1]
            
            model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
            model.fit(X_train, y_train)
            pred = model.predict(X_test)[0]
            
            ret = returns[i]
            strat_ret = ret if pred == 1 else 0.0
            
            predictions.append(pred)
            actuals.append(y[i])
            strat_returns.append(strat_ret)
            buy_hold_returns.append(ret)
            chart_dates.append(dates[i].strftime("%Y-%m-%d"))

        predictions, actuals = np.array(predictions), np.array(actuals)
        strat_returns, buy_hold_returns = np.array(strat_returns), np.array(buy_hold_returns)

        cum_strat_series = (np.cumprod(1 + strat_returns) - 1) * 100.0
        cum_buy_hold_series = (np.cumprod(1 + buy_hold_returns) - 1) * 100.0

        peak = np.maximum.accumulate(1 + cum_strat_series / 100.0)
        drawdown = ((1 + cum_strat_series / 100.0) - peak) / peak
        mdd = float(np.min(drawdown) * 100.0)

        hit_ratio = float(accuracy_score(actuals, predictions) * 100.0)
        total_trades = int(sum(predictions == 1))
        win_rate = float((sum(strat_returns > 0) / total_trades * 100.0) if total_trades > 0 else 0.0)

        X_latest = X[-1:]
        latest_model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        latest_model.fit(X, y)
        tomorrow_pred = "상승 🔺" if latest_model.predict(X_latest)[0] == 1 else "하락 🔻"
        tomorrow_prob = float(latest_model.predict_proba(X_latest)[0][1] * 100.0)

        result_payload = {
            'stock_name': stock_name,
            'ticker': ticker,
            'hit_ratio': hit_ratio,
            'cum_strat': float(cum_strat_series[-1]),
            'cum_buy_hold': float(cum_buy_hold_series[-1]),
            'win_rate': win_rate,
            'total_trades': total_trades,
            'mdd': mdd,
            'tomorrow_pred': tomorrow_pred,
            'tomorrow_prob': tomorrow_prob,
            'start_date': chart_dates[0],
            'end_date': chart_dates[-1],
            'chart_dates': chart_dates,
            'cum_strat_series': [round(x, 2) for x in cum_strat_series.tolist()],
            'cum_buy_hold_series': [round(x, 2) for x in cum_buy_hold_series.tolist()]
        }

        db.save_prediction_cache(result_payload)
        return jsonify({'cached': False, 'data': result_payload})

    except Exception as e:
        print(f"Error in /api/predict: {e}")
        return jsonify({'error': f"분석 중 오류가 발생했습니다: {str(e)}"}), 500

@app.route('/api/predict_2year', methods=['POST'])
def predict_2year():
    req_data = request.get_json() or {}
    stock_name = req_data.get('stock_name', '').strip() or '삼성전자'
    
    if not stock_name:
        return jsonify({'error': '종목명을 입력해 주세요.'}), 400

    # 2년 Out-of-Sample SQLite 캐시 확인
    cached_data = db.get_cached_2yr_prediction(stock_name)
    if cached_data:
        print(f"[SQLite 2-Year Cache HIT] '{stock_name}'")
        return jsonify({'cached': True, 'data': cached_data})

    print(f"[SQLite 2-Year Cache MISS] '{stock_name}' 2년 데이터 계산 중...")
    ticker = get_ticker_by_name(stock_name)
    if not ticker:
        return jsonify({'error': f"종목명 [{stock_name}]에 해당하는 티커를 찾지 못했습니다."}), 404

    try:
        df_2yr = fetch_2year_data(ticker)
        data_2yr = feature_engineering(df_2yr)
        analysis_res = analyze_2year_weekly_predictions(data_2yr)

        tw = analysis_res['target_week']
        target_week_days = []
        for d in range(tw['days']):
            p_val = int(tw['preds'][d])
            a_val = int(tw['actuals'][d])
            target_week_days.append({
                'date': tw['dates'][d],
                'close': int(tw['close_prices'][d]),
                'pred_label': "상승 🔺" if p_val == 1 else "하락 🔻",
                'actual_label': "상승 🔺" if a_val == 1 else "하락 🔻",
                'return_pct': float(round(tw['returns'][d] * 100.0, 2)),
                'is_correct': bool(p_val == a_val)
            })

        result_payload = {
            'stock_name': stock_name,
            'ticker': ticker,
            'train_start': analysis_res['train_start'],
            'train_end': analysis_res['train_end'],
            'train_count': analysis_res['train_count'],
            'test_start': analysis_res['test_start'],
            'test_end': analysis_res['test_end'],
            'test_count': analysis_res['test_count'],
            'hit_ratio': float(analysis_res['hit_ratio']),
            'tp': int(analysis_res['cm']['TP']),
            'fp': int(analysis_res['cm']['FP']),
            'tn': int(analysis_res['cm']['TN']),
            'fn': int(analysis_res['cm']['FN']),
            'win_rate': float(analysis_res['win_rate']),
            'total_trades': int(analysis_res['total_trades']),
            'cum_strat': float(analysis_res['cum_strat']),
            'cum_buy_hold': float(analysis_res['cum_buy_hold']),
            'mdd': float(analysis_res['mdd']),
            'target_week_acc': float(tw['accuracy']),
            'target_week_start': tw['start_date'],
            'target_week_end': tw['end_date'],
            'target_week_days': target_week_days
        }

        db.save_2yr_prediction_cache(result_payload)
        return jsonify({'cached': False, 'data': result_payload})

    except Exception as e:
        print(f"Error in /api/predict_2year: {e}")
        return jsonify({'error': f"2년 데이터 분석 중 오류가 발생했습니다: {str(e)}"}), 500


@app.route('/api/predict_model3', methods=['POST'])
def predict_model3():
    """Model 3: 전일 종가 & 코스피 + 수급 데이터 기반 다음날 시가 갭 예측"""
    req_data = request.get_json() or {}
    stock_name = req_data.get('stock_name', '').strip() or '삼성전자'

    if not stock_name:
        return jsonify({'error': '종목명을 입력해 주세요.'}), 400

    # SQLite 캐시 확인
    cached_data = db.get_cached_model3_prediction(stock_name)
    if cached_data:
        print(f"[SQLite Model3 Cache HIT] '{stock_name}'")
        return jsonify({'cached': True, 'data': cached_data})

    print(f"[SQLite Model3 Cache MISS] '{stock_name}' 시가 갭 예측 분석 중...")

    try:
        result = run_model3(stock_name, days=365)
        bt = result['backtest']
        tmr = result['tomorrow']

        result_payload = {
            'stock_name': result['stock_name'],
            'ticker': result['ticker'],
            'data_start': result['data_start'],
            'data_end': result['data_end'],
            'total_days': result['total_days'],
            # 백테스트 성과
            'hit_ratio': bt['hit_ratio'],
            'cum_strat': bt['cum_strat'],
            'cum_bh': bt['cum_bh'],
            'mdd': bt['mdd'],
            'tp': bt['tp'], 'fp': bt['fp'], 'tn': bt['tn'], 'fn': bt['fn'],
            'total_signals': bt['total_signals'],
            # 내일 예측
            'tomorrow_direction': tmr['direction'],
            'tomorrow_prob': tmr['prob'],
            'tomorrow_gap_class': tmr['gap_class'],
            # 차트
            'bt_dates': bt['dates'],
            'bt_cum_strat_series': bt['cum_strat_series'],
            'bt_cum_bh_series': bt['cum_bh_series'],
            'bt_preds': bt['preds'],
            'bt_actuals': bt['actuals'],
            'bt_gap_pcts': bt['gap_pcts'],
            # 피쳐 분석
            'feature_importance': result['feature_importance'],
            'correlation': result['correlation'],
        }

        db.save_model3_prediction_cache(result)
        return jsonify({'cached': False, 'data': sanitize_json(result_payload)})


    except Exception as e:
        import traceback
        print(f"Error in /api/predict_model3: {e}")
        traceback.print_exc()
        return jsonify({'error': f"Model 3 분석 오류: {str(e)}"}), 500


if __name__ == '__main__':
    print("[Model 3 포함] AI 주가 예측 웹 서버 시작 (http://localhost:5000)")
    app.run(host='0.0.0.0', port=5000, debug=False)
