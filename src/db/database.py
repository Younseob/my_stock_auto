import os
import sqlite3
import json
from datetime import datetime

# 프로젝트 루트/data 디렉토리 내의 stock_cache.db 참조
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'stock_cache.db')

def init_db():
    """SQLite 데이터베이스 및 캐시 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1년 워크포워드 캐시 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            query_date TEXT NOT NULL,
            hit_ratio REAL,
            cum_strat REAL,
            cum_buy_hold REAL,
            win_rate REAL,
            total_trades INTEGER,
            mdd REAL,
            tomorrow_pred TEXT,
            tomorrow_prob REAL,
            start_date TEXT,
            end_date TEXT,
            chart_dates_json TEXT,
            cum_strat_json TEXT,
            cum_buy_hold_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2년 Out-of-Sample 주차별 분석 캐시 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_2yr_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            query_date TEXT NOT NULL,
            train_start TEXT,
            train_end TEXT,
            train_count INTEGER,
            test_start TEXT,
            test_end TEXT,
            test_count INTEGER,
            hit_ratio REAL,
            tp INTEGER, fp INTEGER, tn INTEGER, fn INTEGER,
            win_rate REAL,
            total_trades INTEGER,
            cum_strat REAL,
            cum_buy_hold REAL,
            mdd REAL,
            target_week_acc REAL,
            target_week_days_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Model 3: 시가 갭 예측 캐시 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_3_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            query_date TEXT NOT NULL,
            data_start TEXT,
            data_end TEXT,
            total_days INTEGER,
            hit_ratio REAL,
            cum_strat REAL,
            cum_bh REAL,
            mdd REAL,
            tp INTEGER, fp INTEGER, tn INTEGER, fn INTEGER,
            total_signals INTEGER,
            tomorrow_direction TEXT,
            tomorrow_prob REAL,
            tomorrow_gap_class TEXT,
            feature_importance_json TEXT,
            correlation_json TEXT,
            bt_dates_json TEXT,
            bt_cum_strat_json TEXT,
            bt_cum_bh_json TEXT,
            bt_preds_json TEXT,
            bt_actuals_json TEXT,
            bt_gap_pcts_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_cached_prediction(stock_name_or_ticker):
    """오늘 날짜 기준 1년 워크포워드 캐시 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT * FROM prediction_cache 
        WHERE (LOWER(stock_name) = LOWER(?) OR ticker = ?) AND query_date = ?
        ORDER BY id DESC LIMIT 1
    ''', (stock_name_or_ticker, stock_name_or_ticker, today_str))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        res = dict(row)
        res['chart_dates'] = json.loads(res['chart_dates_json'])
        res['cum_strat_series'] = json.loads(res['cum_strat_json'])
        res['cum_buy_hold_series'] = json.loads(res['cum_buy_hold_json'])
        return res
    return None

def save_prediction_cache(data):
    """1년 워크포워드 결과 캐시 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        INSERT INTO prediction_cache (
            stock_name, ticker, query_date, hit_ratio, cum_strat, cum_buy_hold,
            win_rate, total_trades, mdd, tomorrow_pred, tomorrow_prob,
            start_date, end_date, chart_dates_json, cum_strat_json, cum_buy_hold_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['stock_name'], data['ticker'], today_str, data['hit_ratio'], data['cum_strat'],
        data['cum_buy_hold'], data['win_rate'], data['total_trades'], data['mdd'],
        data['tomorrow_pred'], data['tomorrow_prob'], data['start_date'], data['end_date'],
        json.dumps(data['chart_dates']), json.dumps(data['cum_strat_series']), json.dumps(data['cum_buy_hold_series'])
    ))
    conn.commit()
    conn.close()

def get_cached_2yr_prediction(stock_name_or_ticker):
    """오늘 날짜 기준 2년 Out-of-Sample 캐시 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT * FROM prediction_2yr_cache 
        WHERE (LOWER(stock_name) = LOWER(?) OR ticker = ?) AND query_date = ?
        ORDER BY id DESC LIMIT 1
    ''', (stock_name_or_ticker, stock_name_or_ticker, today_str))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        res = dict(row)
        res['target_week_days'] = json.loads(res['target_week_days_json'])
        return res
    return None

def save_2yr_prediction_cache(data):
    """2년 Out-of-Sample 결과 캐시 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        INSERT INTO prediction_2yr_cache (
            stock_name, ticker, query_date, train_start, train_end, train_count,
            test_start, test_end, test_count, hit_ratio, tp, fp, tn, fn,
            win_rate, total_trades, cum_strat, cum_buy_hold, mdd,
            target_week_acc, target_week_days_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['stock_name'], data['ticker'], today_str, data['train_start'], data['train_end'],
        data['train_count'], data['test_start'], data['test_end'], data['test_count'],
        data['hit_ratio'], data['tp'], data['fp'], data['tn'], data['fn'],
        data['win_rate'], data['total_trades'], data['cum_strat'], data['cum_buy_hold'],
        data['mdd'], data['target_week_acc'], json.dumps(data['target_week_days'])
    ))
    conn.commit()
    conn.close()

def get_cached_model3_prediction(stock_name_or_ticker):
    """오늘 날짜 기준 Model 3 (시가 갭) 캐시 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
        SELECT * FROM prediction_3_cache
        WHERE (LOWER(stock_name) = LOWER(?) OR ticker = ?) AND query_date = ?
        ORDER BY id DESC LIMIT 1
    ''', (stock_name_or_ticker, stock_name_or_ticker, today_str))

    row = cursor.fetchone()
    conn.close()

    if row:
        res = dict(row)
        res['feature_importance'] = json.loads(res['feature_importance_json'])
        res['correlation'] = json.loads(res['correlation_json'])
        res['bt_dates'] = json.loads(res['bt_dates_json'])
        res['bt_cum_strat_series'] = json.loads(res['bt_cum_strat_json'])
        res['bt_cum_bh_series'] = json.loads(res['bt_cum_bh_json'])
        res['bt_preds'] = json.loads(res['bt_preds_json'])
        res['bt_actuals'] = json.loads(res['bt_actuals_json'])
        res['bt_gap_pcts'] = json.loads(res['bt_gap_pcts_json'])
        return res
    return None


def save_model3_prediction_cache(data):
    """Model 3 시가 갭 예측 결과 캐시 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    bt = data['backtest']
    tmr = data['tomorrow']

    cursor.execute('''
        INSERT INTO prediction_3_cache (
            stock_name, ticker, query_date, data_start, data_end, total_days,
            hit_ratio, cum_strat, cum_bh, mdd, tp, fp, tn, fn, total_signals,
            tomorrow_direction, tomorrow_prob, tomorrow_gap_class,
            feature_importance_json, correlation_json,
            bt_dates_json, bt_cum_strat_json, bt_cum_bh_json,
            bt_preds_json, bt_actuals_json, bt_gap_pcts_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['stock_name'], data['ticker'], today_str,
        data['data_start'], data['data_end'], data['total_days'],
        bt['hit_ratio'], bt['cum_strat'], bt['cum_bh'], bt['mdd'],
        bt['tp'], bt['fp'], bt['tn'], bt['fn'], bt['total_signals'],
        tmr['direction'], tmr['prob'], tmr['gap_class'],
        json.dumps(data['feature_importance'], ensure_ascii=False),
        json.dumps(data['correlation'], ensure_ascii=False),
        json.dumps(bt['dates']),
        json.dumps(bt['cum_strat_series']),
        json.dumps(bt['cum_bh_series']),
        json.dumps(bt['preds']),
        json.dumps(bt['actuals']),
        json.dumps(bt['gap_pcts']),
    ))
    conn.commit()
    conn.close()
