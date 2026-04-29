"""
棋手管理功能测试套件
测试目标：棋手CRUD、统计信息、棋局关联
"""

import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"


def test_player_api():
    """测试棋手管理API"""
    print("\n【测试1】棋手管理API测试")
    
    results = []
    created_player_id = None
    
    # 测试1.1: 获取棋手列表
    print("  --- 测试获取棋手列表 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/players")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert "players" in data, "响应中缺少players字段"
        print("    ✅ 获取棋手列表成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取棋手列表失败: {e}")
        results.append(False)
    
    # 测试1.2: 创建棋手
    print("  --- 测试创建棋手 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/player", json={
            "name": "测试棋手",
            "nickname": "棋圣",
            "level": "L3",
            "rating": 1800,
            "email": "test@example.com"
        })
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") == True, "创建失败"
        created_player_id = data.get("player_id")
        assert created_player_id, "缺少player_id"
        print(f"    ✅ 创建棋手成功，player_id: {created_player_id}")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 创建棋手失败: {e}")
        results.append(False)
    
    # 测试1.3: 获取棋手详情
    if created_player_id:
        print("  --- 测试获取棋手详情 ---")
        try:
            response = requests.get(f"{BASE_URL}/api/player/{created_player_id}")
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("name") == "测试棋手", "姓名错误"
            assert data.get("level") == "L3", "等级错误"
            assert data.get("rating") == 1800, "评级错误"
            print("    ✅ 获取棋手详情成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 获取棋手详情失败: {e}")
            results.append(False)
    
    # 测试1.4: 更新棋手信息
    if created_player_id:
        print("  --- 测试更新棋手信息 ---")
        try:
            response = requests.put(f"{BASE_URL}/api/player/{created_player_id}", json={
                "nickname": "新棋圣",
                "rating": 1850
            })
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("success") == True, "更新失败"
            
            response = requests.get(f"{BASE_URL}/api/player/{created_player_id}")
            updated_data = response.json()
            assert updated_data.get("nickname") == "新棋圣", "昵称更新失败"
            assert updated_data.get("rating") == 1850, "评级更新失败"
            print("    ✅ 更新棋手信息成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 更新棋手信息失败: {e}")
            results.append(False)
    
    # 测试1.5: 获取棋手统计
    if created_player_id:
        print("  --- 测试获取棋手统计 ---")
        try:
            response = requests.get(f"{BASE_URL}/api/player/{created_player_id}/stats")
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert "player_id" in data, "缺少player_id"
            assert "total_games" in data, "缺少total_games"
            assert "win_rate" in data, "缺少win_rate"
            print("    ✅ 获取棋手统计成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 获取棋手统计失败: {e}")
            results.append(False)
    
    # 测试1.6: 添加棋局关联
    if created_player_id:
        print("  --- 测试添加棋局关联 ---")
        try:
            response = requests.post(f"{BASE_URL}/api/player/{created_player_id}/add_game", json={
                "game_id": "test_game_001"
            })
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("success") == True, "关联失败"
            
            response = requests.get(f"{BASE_URL}/api/player/{created_player_id}")
            player_data = response.json()
            assert "test_game_001" in player_data.get("game_history", []), "棋局未关联"
            print("    ✅ 添加棋局关联成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 添加棋局关联失败: {e}")
            results.append(False)
    
    # 测试1.7: 获取不存在的棋手
    print("  --- 测试获取不存在的棋手 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/player/nonexistent_player")
        assert response.status_code == 404, f"期望404，实际{response.status_code}"
        print("    ✅ 获取不存在棋手处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取不存在棋手失败: {e}")
        results.append(False)
    
    # 测试1.8: 删除棋手
    if created_player_id:
        print("  --- 测试删除棋手 ---")
        try:
            response = requests.delete(f"{BASE_URL}/api/player/{created_player_id}")
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("success") == True, "删除失败"
            
            response = requests.get(f"{BASE_URL}/api/player/{created_player_id}")
            assert response.status_code == 404, "棋手未删除"
            print("    ✅ 删除棋手成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 删除棋手失败: {e}")
            results.append(False)
    
    return all(results)


def test_player_flow():
    """测试完整棋手管理流程"""
    print("\n【测试2】完整棋手管理流程")
    
    try:
        # 步骤1: 创建棋手
        print("  --- 步骤1: 创建棋手 ---")
        response = requests.post(f"{BASE_URL}/api/player", json={
            "name": "张三",
            "nickname": "棋王",
            "level": "L2",
            "rating": 1600
        })
        player_id = response.json().get("player_id")
        assert player_id, "创建失败"
        print(f"    ✅ 创建棋手成功: {player_id}")
        
        # 步骤2: 更新信息
        print("  --- 步骤2: 更新信息 ---")
        response = requests.put(f"{BASE_URL}/api/player/{player_id}", json={
            "rating": 1700
        })
        assert response.json().get("success") == True
        print("    ✅ 更新信息成功")
        
        # 步骤3: 关联棋局
        print("  --- 步骤3: 关联棋局 ---")
        response = requests.post(f"{BASE_URL}/api/player/{player_id}/add_game", json={
            "game_id": "game_001"
        })
        assert response.json().get("success") == True
        print("    ✅ 关联棋局成功")
        
        # 步骤4: 查看统计
        print("  --- 步骤4: 查看统计 ---")
        response = requests.get(f"{BASE_URL}/api/player/{player_id}/stats")
        assert response.status_code == 200
        print("    ✅ 查看统计成功")
        
        # 步骤5: 删除棋手
        print("  --- 步骤5: 删除棋手 ---")
        response = requests.delete(f"{BASE_URL}/api/player/{player_id}")
        assert response.json().get("success") == True
        print("    ✅ 删除棋手成功")
        
        print("    ✅ 完整流程测试通过")
        return True
        
    except Exception as e:
        print(f"    ❌ 完整流程测试失败: {e}")
        return False


def main():
    print("=" * 70)
    print("国际象棋学习训练系统 - 棋手管理功能测试套件")
    print("=" * 70)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ 服务运行正常: {BASE_URL}")
    except:
        print("❌ 服务未运行，请先启动webapp/app.py")
        return
    
    test_results = []
    
    test_results.append(("棋手管理API", test_player_api()))
    test_results.append(("完整管理流程", test_player_flow()))
    
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for _, r in test_results if r)
    failed = len(test_results) - passed
    
    for name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 70)
    print(f"总计: {passed}/{len(test_results)} 通过")
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️ {failed} 个测试失败，请检查相关模块")
    print("=" * 70)


if __name__ == "__main__":
    main()