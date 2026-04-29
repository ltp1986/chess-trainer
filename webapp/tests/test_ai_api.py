import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestAIAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_profile_generate_enhanced(self):
        """测试AI能力画像增强生成API"""
        response = self.app.post(
            '/api/profile/generate/enhanced',
            data=json.dumps({
                'player_id': 'test_player',
                'player_name': '测试棋手'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('profile', data)
        profile = data['profile']
        self.assertIn('strengths', profile)
        self.assertIn('weaknesses', profile)
        self.assertIn('style', profile)
        self.assertIn('suggestions', profile)
        self.assertIn('overall_rating', profile)
        
    def test_profile_generate_enhanced_no_player(self):
        """测试不带棋手ID的AI能力画像生成"""
        response = self.app.post(
            '/api/profile/generate/enhanced',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('profile', data)
        
    def test_analyze_enhanced(self):
        """测试AI棋局深度分析API"""
        response = self.app.post(
            '/api/analyze/enhanced',
            data=json.dumps({
                'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1',
                'move_number': 1,
                'turn': 'black',
                'context': '开局第一步'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        analysis = data['analysis']
        self.assertIn('evaluation', analysis)
        self.assertIn('position_type', analysis)
        
    def test_analyze_enhanced_invalid_fen(self):
        """测试无效FEN的AI分析"""
        response = self.app.post(
            '/api/analyze/enhanced',
            data=json.dumps({
                'fen': 'invalid_fen_string',
                'move_number': 1,
                'turn': 'black'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        
    def test_exercises_classify(self):
        """测试AI错题分类API"""
        response = self.app.post(
            '/api/exercises/classify',
            data=json.dumps({
                'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 3',
                'actual_move': 'Nf6',
                'best_move': 'd6',
                'loss': 150,
                'move_number': 3
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('classification', data)
        classification = data['classification']
        self.assertIn('category', classification)
        self.assertIn('difficulty', classification)
        
    def test_exercises_batch_classify(self):
        """测试批量AI错题分类API"""
        response = self.app.post(
            '/api/exercises/batch_classify',
            data=json.dumps({
                'exercises': [
                    {
                        'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1',
                        'actual_move': 'e5',
                        'best_move': 'c5',
                        'loss': 50,
                        'move_number': 1
                    },
                    {
                        'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 3',
                        'actual_move': 'Nf6',
                        'best_move': 'd6',
                        'loss': 150,
                        'move_number': 3
                    }
                ]
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('classifications', data)
        self.assertIn('total_count', data)
        self.assertEqual(data['total_count'], 2)
        
    def test_token_status(self):
        """测试Token状态查询API"""
        response = self.app.get('/api/token/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('api_key_configured', data)
        self.assertIn('daily_usage', data)
        self.assertIn('monthly_usage', data)
        self.assertIn('rpm_limit', data)
        self.assertIn('status', data)
        self.assertIn('total_calls', data)
        
    def test_ai_api_fallback(self):
        """测试API调用失败时的降级机制"""
        with patch('app.call_doubao_api') as mock_api:
            mock_api.return_value = None
            
            response = self.app.post(
                '/api/profile/generate/enhanced',
                data=json.dumps({'player_name': '测试棋手'}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode('utf-8'))
            self.assertTrue(data['success'])
            self.assertFalse(data.get('generated_by_ai', False))

class TestIntegrationWithAI(unittest.TestCase):
    """集成测试 - 需要配置有效的API密钥"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_real_ai_api_call(self):
        """测试真实的AI API调用（如果配置了有效密钥）"""
        if not os.environ.get('DOUBAO_API_KEY'):
            self.skipTest("未配置API密钥，跳过真实API测试")
            
        response = self.app.post(
            '/api/exercises/classify',
            data=json.dumps({
                'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1',
                'actual_move': 'e5',
                'best_move': 'c5',
                'loss': 100,
                'move_number': 1
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIn('classification', data)
        
        if data.get('generated_by_ai'):
            classification = data['classification']
            self.assertIn('category', classification)
            self.assertIsNotNone(classification['category'])

if __name__ == '__main__':
    unittest.main()
