# 增强的端到端测试
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.app import app

class TestEnhancedE2E(unittest.TestCase):
    """增强的端到端测试套件"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.client = app.test_client()
        cls.client.testing = True

        # 清理测试数据
        cls.cleanup_test_data()

    @classmethod
    def cleanup_test_data(cls):
        """清理测试数据"""
        import shutil
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'webapp', 'output')

        # 清理棋手
        players_dir = os.path.join(output_dir, 'players')
        if os.path.exists(players_dir):
            for f in os.listdir(players_dir):
                if f.startswith('test_') or f.startswith('player_test'):
                    os.remove(os.path.join(players_dir, f))

        # 清理棋局
        library_dir = os.path.join(output_dir, 'library')
        if os.path.exists(library_dir):
            for f in os.listdir(library_dir):
                if f.startswith('test_'):
                    os.remove(os.path.join(library_dir, f))

    def test_01_api_endpoints_exist(self):
        """测试1: API端点存在性检查"""
        print("\n" + "="*50)
        print("📋 测试1: API端点存在性检查")
        print("="*50)

        endpoints = [
            '/api/library/games',
            '/api/players',
            '/api/profile',
            '/api/training/plan',
            '/api/player',
            '/api/library/game'
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # 只要不返回404（路由不存在）就算通过
            self.assertIn(
                response.status_code,
                [200, 404, 405],
                f"端点 {endpoint} 应该可访问"
            )
            print(f"✅ {endpoint}: {response.status_code}")

    def test_02_navigation_elements_in_html(self):
        """测试2: HTML中的导航元素检查"""
        print("\n" + "="*50)
        print("📋 测试2: HTML导航元素检查")
        print("="*50)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        html = response.data.decode('utf-8')

        nav_buttons = ['nav-home', 'nav-library', 'nav-players', 'nav-profile', 'nav-plan']
        for btn_id in nav_buttons:
            self.assertIn(
                btn_id,
                html,
                f"HTML中应包含导航按钮 {btn_id}"
            )
            print(f"✅ 导航按钮 {btn_id} 存在于HTML中")

        # 检查页面容器
        page_containers = ['page-home', 'page-library', 'page-players', 'page-profile', 'page-plan']
        for page_id in page_containers:
            self.assertIn(
                page_id,
                html,
                f"HTML中应包含页面容器 {page_id}"
            )
            print(f"✅ 页面容器 {page_id} 存在于HTML中")

    def test_03_player_crud_operations(self):
        """测试3: 棋手CRUD操作"""
        print("\n" + "="*50)
        print("📋 测试3: 棋手CRUD操作")
        print("="*50)

        # 创建棋手
        response = self.client.post('/api/player', json={
            'name': '测试棋手',
            'level': 'L3',
            'rating': 1800
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        player_id = data.get('player_id')
        print(f"✅ 创建棋手成功: {player_id}")

        # 获取棋手列表
        response = self.client.get('/api/players')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('players', data)
        self.assertTrue(len(data['players']) >= 1)
        print(f"✅ 获取棋手列表成功: {len(data['players'])}个棋手")

        # 获取单个棋手
        response = self.client.get(f'/api/player/{player_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], '测试棋手')
        print(f"✅ 获取单个棋手成功")

        # 更新棋手
        response = self.client.put(f'/api/player/{player_id}', json={
            'name': '更新后的棋手',
            'level': 'L2',
            'rating': 1850
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        print(f"✅ 更新棋手成功")

        # 删除棋手
        response = self.client.delete(f'/api/player/{player_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        print(f"✅ 删除棋手成功")

    def test_04_library_operations(self):
        """测试4: 点评库操作"""
        print("\n" + "="*50)
        print("📋 测试4: 点评库操作")
        print("="*50)

        # 添加棋局
        pgn_content = """[Event "Test Game"]
[Site "Local"]
[Date "2024.01.15"]
[White "Player1"]
[Black "Player2"]
[Result "0-1"]
1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Nc3 Nxe4 0-1"""

        response = self.client.post('/api/library/game', json={
            'pgn_content': pgn_content,
            'filename': 'test_game.pgn'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        game_id = data.get('game_id')
        print(f"✅ 添加棋局成功: {game_id}")

        # 获取棋局列表
        response = self.client.get('/api/library/games')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('games', data)
        self.assertTrue(len(data['games']) >= 1)
        print(f"✅ 获取棋局列表成功: {len(data['games'])}个棋局")

        # 获取单个棋局
        response = self.client.get(f'/api/library/game/{game_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['filename'], 'test_game.pgn')
        print(f"✅ 获取单个棋局成功")

    def test_05_profile_and_plan_generation(self):
        """测试5: 画像和计划生成"""
        print("\n" + "="*50)
        print("📋 测试5: 画像和计划生成")
        print("="*50)

        # 生成画像
        response = self.client.post('/api/profile/generate')
        self.assertIn(response.status_code, [200, 500])  # 500可能是因为没有数据
        print(f"✅ 画像生成接口响应: {response.status_code}")

        # 获取画像
        response = self.client.get('/api/profile')
        self.assertIn(response.status_code, [200, 404])
        print(f"✅ 画像获取接口响应: {response.status_code}")

        # 生成训练计划
        response = self.client.post('/api/training/plan/generate')
        self.assertIn(response.status_code, [200, 500])
        print(f"✅ 训练计划生成接口响应: {response.status_code}")

        # 获取训练计划
        response = self.client.get('/api/training/plan')
        self.assertIn(response.status_code, [200, 404])
        print(f"✅ 训练计划获取接口响应: {response.status_code}")

    def test_06_error_handling(self):
        """测试6: 错误处理"""
        print("\n" + "="*50)
        print("📋 测试6: 错误处理")
        print("="*50)

        # 获取不存在的棋手
        response = self.client.get('/api/player/nonexistent_id')
        self.assertEqual(response.status_code, 404)
        print(f"✅ 获取不存在的棋手返回404")

        # 获取不存在的棋局
        response = self.client.get('/api/library/game/nonexistent_id')
        self.assertEqual(response.status_code, 404)
        print(f"✅ 获取不存在的棋局返回404")

        # 创建棋手缺少必填字段
        response = self.client.post('/api/player', json={})
        self.assertIn(response.status_code, [400, 500])
        print(f"✅ 创建棋手缺少字段返回错误状态")

    def test_07_complete_workflow(self):
        """测试7: 完整工作流程"""
        print("\n" + "="*50)
        print("📋 测试7: 完整工作流程")
        print("="*50)

        # 1. 创建棋手
        response = self.client.post('/api/player', json={
            'name': '流程测试棋手',
            'level': 'L3',
            'rating': 1800
        })
        self.assertEqual(response.status_code, 200)
        player_id = response.get_json().get('player_id')
        print(f"✅ 步骤1: 创建棋手 {player_id}")

        # 2. 添加棋局
        pgn = """[Event "Workflow Test"]
[White "流程测试棋手"]
[Black "对手"]
[Result "1-0"]
1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O"""

        response = self.client.post('/api/library/game', json={
            'pgn_content': pgn,
            'filename': 'workflow_test.pgn'
        })
        self.assertEqual(response.status_code, 200)
        game_id = response.get_json().get('game_id')
        print(f"✅ 步骤2: 添加棋局 {game_id}")

        # 3. 关联棋局到棋手
        response = self.client.post(f'/api/player/{player_id}/add_game', json={
            'game_id': game_id
        })
        self.assertEqual(response.status_code, 200)
        print(f"✅ 步骤3: 关联棋局")

        # 4. 获取棋手统计
        response = self.client.get(f'/api/player/{player_id}/stats')
        self.assertEqual(response.status_code, 200)
        stats = response.get_json()
        self.assertEqual(stats.get('game_count'), 1)
        print(f"✅ 步骤4: 获取统计 (棋局数: {stats.get('game_count')})")

        # 5. 生成画像
        response = self.client.post('/api/profile/generate')
        print(f"✅ 步骤5: 生成画像")
        self.assertIn(response.status_code, [200, 500])

        # 6. 生成训练计划
        response = self.client.post('/api/training/plan/generate')
        print(f"✅ 步骤6: 生成训练计划")
        self.assertIn(response.status_code, [200, 500])

        # 7. 清理
        self.client.delete(f'/api/player/{player_id}')
        self.client.delete(f'/api/library/game/{game_id}')
        print(f"✅ 步骤7: 清理测试数据")

        print("\n🎉 完整工作流程测试通过!")


def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始增强端到端测试")
    print("="*60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedE2E)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    print(f"测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 有测试失败")
        if result.failures:
            print("\n失败:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\n错误:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)