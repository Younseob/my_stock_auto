import sys
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:5000/api/predict'

print("--- 1ST CALL (MISS -> Calculate & Save to SQLite) ---")
r1 = requests.post(url, json={'stock_name': '씨에스윈드'}).json()
print("Response 1:", "cached =", r1.get('cached'), "| Ticker =", r1['data']['ticker'], "| Tomorrow Pred =", r1['data']['tomorrow_pred'], "| HitRatio =", r1['data']['hit_ratio'])

print("\n--- 2ND CALL (HIT -> Read directly from SQLite Cache) ---")
r2 = requests.post(url, json={'stock_name': '씨에스윈드'}).json()
print("Response 2:", "cached =", r2.get('cached'), "| Ticker =", r2['data']['ticker'], "| Tomorrow Pred =", r2['data']['tomorrow_pred'], "| HitRatio =", r2['data']['hit_ratio'])
