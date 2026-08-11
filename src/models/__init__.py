"""
Predictor Models Package
"""
try:
    from .stock_predictor import predict_stock
except ImportError:
    pass

try:
    from .two_year_predictor import predict_two_year
except ImportError:
    pass

try:
    from .model3_predictor import predict_model3
except ImportError:
    pass

try:
    from .pattern_predictor import PatternPredictor
except ImportError:
    pass

# Mode 식별자 정의 (Mode 1 ~ Mode 4)
MODES = {
    "MODE_1": {
        "id": "1yr",
        "name": "Mode 1: 1년 워크포워드 백테스트",
        "badge": "Mode 1",
        "description": "기본 1년 워크포워드 백테스트",
        "endpoint": "/api/predict",
        "func": "predict_stock"
    },
    "MODE_2": {
        "id": "2yr",
        "name": "Mode 2: 2년 기간 주간 예측 분석",
        "badge": "Mode 2",
        "description": "2년 기간 주간 예측 분석",
        "endpoint": "/api/predict_2year",
        "func": "predict_two_year"
    },
    "MODE_3": {
        "id": "m3",
        "name": "Mode 3: 시가 갭상승 & 기술지표 고도화 예측",
        "badge": "Mode 3",
        "description": "시가 갭상승 & 기술지표 고도화 예측",
        "endpoint": "/api/predict_model3",
        "func": "predict_model3"
    },
    "MODE_4": {
        "id": "m4",
        "name": "Mode 4: 차트 패턴 유사도 매칭 예측",
        "badge": "Mode 4",
        "description": "차트 패턴 유사도 매칭 예측",
        "endpoint": "/api/predict_pattern",
        "func": "PatternPredictor"
    }
}
