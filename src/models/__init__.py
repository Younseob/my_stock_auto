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
