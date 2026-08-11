# -*- coding: utf-8 -*-
import sys
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:5000/api/predict_2year'
stock_name = "씨에스윈드"

print(f"--- 1ST CALL: 2-Year Out-of-Sample Calculation for [{stock_name}] ---")
r1 = requests.post(url, json={'stock_name': stock_name}).json()
print("Response 1:", "cached =", r1.get('cached'), "| Ticker =", r1['data']['ticker'], "| 2yr Hit Ratio =", r1['data']['hit_ratio'], "%")
print("Target Week Daily Predictions Count:", len(r1['data']['target_week_days']))

print("\n--- 2ND CALL: SQLite 2-Year Cache HIT ---")
r2 = requests.post(url, json={'stock_name': stock_name}).json()
print("Response 2:", "cached =", r2.get('cached'), "| Ticker =", r2['data']['ticker'], "| 2yr Hit Ratio =", r2['data']['hit_ratio'], "%")
