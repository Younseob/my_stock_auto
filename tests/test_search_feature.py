# -*- coding: utf-8 -*-
import sys
import unittest
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

class StockSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_search_typo_error(self):
        """1) 오타/미존재 검색어 ('하이닉시') 입력 시 status: error 반환 검증 (크래시 방지)"""
        res = self.app.get('/api/search_stock?query=하이닉시')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('찾을 수 없습니다', data['message'])
        print("✅ [PASS] 오타 검색어 ('하이닉시') -> status: 'error' 및 안내 메시지 정상 반환")

    def test_search_single_match(self):
        """2) 단일 매칭 ('하이닉스') 입력 시 status: single 및 SK하이닉스 정식 명칭 반환 검증"""
        res = self.app.get('/api/search_stock?query=하이닉스')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'single')
        self.assertEqual(data['item']['name'], 'SK하이닉스')
        self.assertEqual(data['item']['ticker'], '000660')
        print("✅ [PASS] 단일 매칭 ('하이닉스') -> status: 'single' 및 'SK하이닉스' (000660) 정식 종목 대입 반환")

    def test_search_multiple_matches(self):
        """3) 다중 매칭 ('삼성') 입력 시 status: multiple 및 다중 종목 후보 리스트 반환 검증"""
        res = self.app.get('/api/search_stock?query=삼성')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'multiple')
        self.assertGreaterEqual(data['count'], 2)
        names = [item['name'] for item in data['items']]
        self.assertIn('삼성전자', names)
        self.assertIn('삼성SDI', names)
        print(f"✅ [PASS] 다중 매칭 ('삼성') -> status: 'multiple' 및 {data['count']}개 후보 리스트 정상 반환")

if __name__ == '__main__':
    unittest.main()
