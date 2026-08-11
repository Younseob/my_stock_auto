import unittest
import sys
import os

# root 경로 추가
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app


class WebServerLiveTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_index_route(self):
        """1) GET /: 메인 웹 화면 HTTP 200 OK 및 <!DOCTYPE html> 렌더링 검증"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn('<!doctype html>', content.lower())
        self.assertIn('Mode별 분석 가이드', content)
        self.assertIn('tab-m4', content)
        self.assertIn('mode4ResultCard', content)
        self.assertIn('m4TopMatchesTable', content)
        self.assertIn('runMode4Prediction', content)

    def test_search_stock_api(self):
        """2) GET /api/search_stock?query=삼성전자: 종목 부분 검색 API HTTP 200 OK 검증"""
        response = self.client.get('/api/search_stock?query=삼성전자')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn('status', data)
        self.assertIn('items', data)

    def test_get_modes_api(self):
        """3) GET /api/modes: Mode 1~4 메타데이터 API HTTP 200 OK 검증"""
        response = self.client.get('/api/modes')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('modes', data)

    def test_predict_pattern_api(self):
        """4) POST /api/predict_pattern: Mode 4 차트 패턴 매칭 비동기 API 검증"""
        # 종목명 미입력 시 400 Bad Request 검증
        response = self.client.post('/api/predict_pattern', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
