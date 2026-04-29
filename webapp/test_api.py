import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

class TestAPIs(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_exercises_update_method(self):
        """测试更新练习接口只支持POST方法"""
        response = self.app.get('/api/exercises/update/player_cd137a6a')
        self.assertEqual(response.status_code, 405)
    
    def test_exercises_update_success(self):
        """测试成功更新练习状态"""
        response = self.app.post(
            '/api/exercises/update/player_cd137a6a',
            data=json.dumps({'exercise_id': 1, 'status': 'completed'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
    
    def test_training_progress(self):
        """测试获取训练进度"""
        response = self.app.get('/api/training/progress')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('overall_progress', data)
    
    def test_token_status(self):
        """测试获取Token状态"""
        response = self.app.get('/api/token/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('status', data)
    
    def test_profile_generate(self):
        """测试生成能力画像"""
        response = self.app.post(
            '/api/profile/generate',
            data=json.dumps({'player_id': 'test_player', 'player_name': '测试'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data.get('success'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
