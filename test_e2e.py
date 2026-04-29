"""
端到端闭环测试套件
测试目标：完整的学习训练流程，模拟真实用户操作
"""

import os
import sys
import time
import json
import requests
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

TEST_PGN = """[Event "End-to-End Test Game"]
[Site "Local"]
[Date "2024.01.15"]
[White "TestPlayer"]
[Black "Opponent"]
[Result "0-1"]
[ECO "D00"]
1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Be2 O-O 6. Nf3 Nc6 7. O-O e5 8. d5 Ne7 9. Nd2 c5 10. cxd5 Nxd5 11. Nc4 Nb6 12. Nxb6 axb6 13. Be3 f5 14. exf5 gxf5 15. Bg5 h6 16. Bh4 Bf6 17. Bxf6 Rxf6 18. Qd2 Kh7 19. Rad1 Qe7 20. Qc3 Raf8 21. Rfe1 f4 22. Bf1 e4 23. Nd4 Qh4 24. g3 fxg3 25. hxg3 Qxg3+ 26. Kf1 Qh3+ 27. Ke2 Qg4+ 28. Kd2 Qf4+ 29. Kc2 Qe3 30. Qe1 Qf2+ 31. Kb3 Qxe1 32. Rxe1 Rf2 33. Rd3 Rxa2 34. Rxe4 Rxb2+ 35. Ka4 Ra2+ 36. Kb5 Raa8 37. Nd1 Rb8+ 38. Ka6 Ra8+ 39. Kb7 Rf8 40. Nc3 Rfb8+ 41. Ka7 Rxa1 42. Nxa2 Rxa2+ 43. Kb8 Rb2+ 0-1
"""


def test_complete_workflow():
    """测试完整的学习训练流程"""
    print("\n【测试1】完整学习训练流程")
    
    cleanup_data()
    
    try:
        # 步骤1: 创建棋手
        print("  --- 步骤1: 创建棋手 ---")
        player_response = requests.post(f"{BASE_URL}/api/player", json={
            "name": "测试用户",
            "nickname": "棋士",
            "level": "L2",
            "rating": 1600
        })
        assert player_response.status_code == 200, "创建棋手失败"
        player_data = player_response.json()
        player_id = player_data["player_id"]
        print(f"    ✅ 创建棋手成功: {player_id}")
        
        # 步骤2: 添加棋局到点评库
        print("  --- 步骤2: 添加棋局 ---")
        game_response = requests.post(f"{BASE_URL}/api/library/game", json={
            "pgn_content": TEST_PGN,
            "filename": "test_game.pgn"
        })
        assert game_response.status_code == 200, "添加棋局失败"
        game_data = game_response.json()
        game_id = game_data["game_id"]
        print(f"    ✅ 添加棋局成功: {game_id}")
        
        # 步骤3: 关联棋局到棋手
        print("  --- 步骤3: 关联棋局 ---")
        assoc_response = requests.post(f"{BASE_URL}/api/player/{player_id}/add_game", json={
            "game_id": game_id
        })
        assert assoc_response.status_code == 200, "关联棋局失败"
        print("    ✅ 关联棋局成功")
        
        # 步骤4: 生成能力画像
        print("  --- 步骤4: 生成能力画像 ---")
        profile_response = requests.post(f"{BASE_URL}/api/profile/generate")
        assert profile_response.status_code == 200, "生成画像失败"
        profile_data = profile_response.json()
        assert "profile" in profile_data or profile_data.get("success") is not None, "画像数据异常"
        print("    ✅ 生成能力画像成功")
        
        # 步骤5: 获取能力画像
        print("  --- 步骤5: 获取能力画像 ---")
        get_profile_response = requests.get(f"{BASE_URL}/api/profile")
        assert get_profile_response.status_code == 200, "获取画像失败"
        profile = get_profile_response.json()
        assert "strengths" in profile, "画像缺少强项"
        assert "weaknesses" in profile, "画像缺少弱项"
        assert "style" in profile, "画像缺少风格"
        print(f"    ✅ 获取能力画像成功，风格: {profile.get('style', '未知')}")
        
        # 步骤6: 生成训练计划
        print("  --- 步骤6: 生成训练计划 ---")
        plan_response = requests.post(f"{BASE_URL}/api/training/plan/generate")
        assert plan_response.status_code == 200, "生成训练计划失败"
        plan_data = plan_response.json()
        assert "plan" in plan_data or plan_data.get("success") is not None, "训练计划数据异常"
        print("    ✅ 生成训练计划成功")
        
        # 步骤7: 获取训练计划
        print("  --- 步骤7: 获取训练计划 ---")
        get_plan_response = requests.get(f"{BASE_URL}/api/training/plan")
        assert get_plan_response.status_code == 200, "获取训练计划失败"
        plan = get_plan_response.json()
        assert "plan_id" in plan, "训练计划缺少ID"
        assert "daily_tasks" in plan, "训练计划缺少任务"
        print(f"    ✅ 获取训练计划成功，目标等级: {plan.get('target_level', '未知')}")
        
        # 步骤8: 导出画像
        print("  --- 步骤8: 导出画像 ---")
        export_profile_response = requests.get(f"{BASE_URL}/api/profile/export")
        assert export_profile_response.status_code == 200, "导出画像失败"
        assert "Content-Disposition" in export_profile_response.headers, "缺少下载头"
        print("    ✅ 导出画像成功")
        
        # 步骤9: 导出训练计划
        print("  --- 步骤9: 导出训练计划 ---")
        export_plan_response = requests.get(f"{BASE_URL}/api/training/plan/export")
        assert export_plan_response.status_code == 200, "导出训练计划失败"
        print("    ✅ 导出训练计划成功")
        
        # 步骤10: 获取棋手统计
        print("  --- 步骤10: 获取棋手统计 ---")
        stats_response = requests.get(f"{BASE_URL}/api/player/{player_id}/stats")
        assert stats_response.status_code == 200, "获取统计失败"
        stats = stats_response.json()
        assert stats["game_count"] == 1, "棋局数量错误"
        print(f"    ✅ 获取棋手统计成功，棋局数: {stats['game_count']}")
        
        # 清理测试数据
        cleanup_data()
        
        print("\n    🎉 完整学习训练流程测试通过！")
        return True
        
    except Exception as e:
        print(f"\n    ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        cleanup_data()
        return False


def test_file_import_export():
    """测试文件导入导出功能"""
    print("\n【测试2】文件导入导出流程")
    
    cleanup_data()
    
    try:
        # 步骤1: 导入PGN文件
        print("  --- 步骤1: 导入PGN文件 ---")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            f.write(TEST_PGN)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            import_response = requests.post(f"{BASE_URL}/api/import/pgn", files={'file': f})
        
        os.unlink(temp_path)
        
        assert import_response.status_code == 200, "导入PGN失败"
        import_data = import_response.json()
        assert import_data["success"] == True, "导入未成功"
        game_id = import_data["game_id"]
        print(f"    ✅ 导入PGN文件成功: {game_id}")
        
        # 步骤2: 导入画像JSON
        print("  --- 步骤2: 导入画像JSON ---")
        profile_data = {
            "strengths": [{"skill": "残局技巧", "score": 85}],
            "weaknesses": [{"skill": "开局准备", "score": 50}],
            "style": "进攻型",
            "suggestions": ["加强开局学习"]
        }
        import_profile_response = requests.post(f"{BASE_URL}/api/import/profile", json=profile_data)
        assert import_profile_response.status_code == 200, "导入画像失败"
        print("    ✅ 导入画像JSON成功")
        
        # 步骤3: 验证导入的画像
        print("  --- 步骤3: 验证导入的画像 ---")
        get_profile_response = requests.get(f"{BASE_URL}/api/profile")
        assert get_profile_response.status_code == 200, "获取画像失败"
        profile = get_profile_response.json()
        assert profile["style"] == "进攻型", "画像导入不正确"
        print("    ✅ 验证画像成功")
        
        # 步骤4: 导入训练计划
        print("  --- 步骤4: 导入训练计划 ---")
        plan_data = {
            "plan_id": "test_plan",
            "target_level": "L3",
            "short_term_goal": "测试目标",
            "daily_tasks": [{"name": "测试任务", "duration": "30分钟"}]
        }
        import_plan_response = requests.post(f"{BASE_URL}/api/import/plan", json=plan_data)
        assert import_plan_response.status_code == 200, "导入计划失败"
        print("    ✅ 导入训练计划成功")
        
        # 步骤5: 验证导入的计划
        print("  --- 步骤5: 验证导入的计划 ---")
        get_plan_response = requests.get(f"{BASE_URL}/api/training/plan")
        assert get_plan_response.status_code == 200, "获取计划失败"
        plan = get_plan_response.json()
        assert plan["plan_id"] == "test_plan", "计划导入不正确"
        print("    ✅ 验证计划成功")
        
        cleanup_data()
        
        print("\n    🎉 文件导入导出流程测试通过！")
        return True
        
    except Exception as e:
        print(f"\n    ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        cleanup_data()
        return False


def test_error_handling():
    """测试错误处理机制"""
    print("\n【测试3】错误处理机制")
    
    results = []
    
    # 测试3.1: 导入无效PGN文件
    print("  --- 测试无效PGN文件 ---")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("not a valid pgn")
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            response = requests.post(f"{BASE_URL}/api/import/pgn", files={'file': f})
        
        os.unlink(temp_path)
        
        assert response.status_code == 400, f"期望400，实际{response.status_code}"
        print("    ✅ 无效PGN文件处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 无效PGN测试失败: {e}")
        results.append(False)
    
    # 测试3.2: 获取不存在的棋局
    print("  --- 测试获取不存在的棋局 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/library/game/nonexistent")
        assert response.status_code == 404, f"期望404，实际{response.status_code}"
        print("    ✅ 不存在棋局处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 不存在棋局测试失败: {e}")
        results.append(False)
    
    # 测试3.3: 获取不存在的棋手
    print("  --- 测试获取不存在的棋手 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/player/nonexistent")
        assert response.status_code == 404, f"期望404，实际{response.status_code}"
        print("    ✅ 不存在棋手处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 不存在棋手测试失败: {e}")
        results.append(False)
    
    # 测试3.4: 缺少必填字段
    print("  --- 测试缺少必填字段 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/player", json={})
        assert response.status_code == 400, f"期望400，实际{response.status_code}"
        data = response.json()
        assert "error" in data, "应有错误信息"
        print("    ✅ 缺少字段处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 缺少字段测试失败: {e}")
        results.append(False)
    
    return all(results)


def cleanup_data():
    """清理测试数据"""
    try:
        # 删除所有棋手
        response = requests.get(f"{BASE_URL}/api/players")
        if response.status_code == 200:
            players = response.json().get("players", [])
            for player in players:
                requests.delete(f"{BASE_URL}/api/player/{player['player_id']}")
        
        # 删除所有棋局
        response = requests.get(f"{BASE_URL}/api/library/games")
        if response.status_code == 200:
            games = response.json().get("games", [])
            for game in games:
                requests.delete(f"{BASE_URL}/api/library/game/{game['game_id']}")
        
        # 删除画像和计划文件
        import os
        profile_path = os.path.join(os.path.dirname(__file__), "webapp/output/profiles/current_profile.json")
        plan_path = os.path.join(os.path.dirname(__file__), "webapp/output/plans/current_plan.json")
        
        if os.path.exists(profile_path):
            os.remove(profile_path)
        if os.path.exists(plan_path):
            os.remove(plan_path)
            
    except Exception as e:
        print(f"清理数据时发生错误: {e}")


def test_api_consistency():
    """测试API数据一致性"""
    print("\n【测试4】API数据一致性")
    
    cleanup_data()
    
    try:
        # 创建棋手
        player_response = requests.post(f"{BASE_URL}/api/player", json={
            "name": "一致性测试用户",
            "level": "L2"
        })
        player_id = player_response.json()["player_id"]
        
        # 添加多个棋局
        game_ids = []
        for i in range(3):
            game_response = requests.post(f"{BASE_URL}/api/library/game", json={
                "pgn_content": TEST_PGN,
                "filename": f"test_{i}.pgn"
            })
            game_ids.append(game_response.json()["game_id"])
        
        # 关联所有棋局
        for game_id in game_ids:
            requests.post(f"{BASE_URL}/api/player/{player_id}/add_game", json={"game_id": game_id})
        
        # 验证统计
        stats_response = requests.get(f"{BASE_URL}/api/player/{player_id}/stats")
        stats = stats_response.json()
        assert stats["game_count"] == 3, f"期望3局，实际{stats['game_count']}"
        
        # 验证棋手详情
        player_response = requests.get(f"{BASE_URL}/api/player/{player_id}")
        player = player_response.json()
        assert len(player["game_history"]) == 3, "棋局历史数量错误"
        
        cleanup_data()
        
        print("    ✅ API数据一致性测试通过")
        return True
        
    except Exception as e:
        print(f"    ❌ 数据一致性测试失败: {e}")
        cleanup_data()
        return False


def main():
    print("=" * 70)
    print("国际象棋学习训练系统 - 端到端闭环测试套件")
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
    
    test_results.append(("完整学习训练流程", test_complete_workflow()))
    test_results.append(("文件导入导出流程", test_file_import_export()))
    test_results.append(("错误处理机制", test_error_handling()))
    test_results.append(("API数据一致性", test_api_consistency()))
    
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
        print("🎉 所有端到端测试通过！")
        print("\n📋 测试覆盖的业务流程：")
        print("  • 创建棋手 → 添加棋局 → 关联棋局 → 生成画像 → 生成训练计划")
        print("  • PGN文件导入 → 画像导入 → 训练计划导入")
        print("  • 错误处理和边界情况")
        print("  • 数据一致性验证")
    else:
        print(f"⚠️ {failed} 个测试失败，请检查相关模块")
    print("=" * 70)


if __name__ == "__main__":
    main()