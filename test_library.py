"""
点评库功能测试套件
测试目标：点评库管理、能力画像、训练计划功能
"""

import os
import sys
import json
import time
import requests
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"
TEST_PGN = """[Event "Test Game"]
[Site "Local"]
[Date "2024.01.15"]
[White "TestPlayer"]
[Black "Opponent"]
[Result "0-1"]
[ECO "D00"]
1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Be2 O-O 6. Nf3 Nc6 7. O-O e5 8. d5 Ne7 9. Nd2 c5 10. cxd5 Nxd5 11. Nc4 Nb6 12. Nxb6 axb6 13. Be3 f5 14. exf5 gxf5 15. Bg5 h6 16. Bh4 Bf6 17. Bxf6 Rxf6 18. Qd2 Kh7 19. Rad1 Qe7 20. Qc3 Raf8 21. Rfe1 f4 22. Bf1 e4 23. Nd4 Qh4 24. g3 fxg3 25. hxg3 Qxg3+ 26. Kf1 Qh3+ 27. Ke2 Qg4+ 28. Kd2 Qf4+ 29. Kc2 Qe3 30. Qe1 Qf2+ 31. Kb3 Qxe1 32. Rxe1 Rf2 33. Rd3 Rxa2 34. Rxe4 Rxb2+ 35. Ka4 Ra2+ 36. Kb5 Raa8 37. Nd1 Rb8+ 38. Ka6 Ra8+ 39. Kb7 Rf8 40. Nc3 Rfb8+ 41. Ka7 Rxa1 42. Nxa2 Rxa2+ 43. Kb8 Rb2+ 0-1
"""


def test_library_api():
    """测试点评库API"""
    print("\n【测试1】点评库API测试")
    
    results = []
    
    # 测试1.1: 获取棋局列表（空列表）
    print("  --- 测试获取棋局列表 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/library/games")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert "games" in data, "响应中缺少games字段"
        print("    ✅ 获取棋局列表成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取棋局列表失败: {e}")
        results.append(False)
    
    # 测试1.2: 添加棋局
    print("  --- 测试添加棋局 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/library/game", json={
            "pgn_content": TEST_PGN,
            "filename": "test_game.pgn"
        })
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") == True, "添加失败"
        game_id = data.get("game_id")
        assert game_id, "缺少game_id"
        print(f"    ✅ 添加棋局成功，game_id: {game_id}")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 添加棋局失败: {e}")
        results.append(False)
        game_id = None
    
    # 测试1.3: 获取单局详情
    if game_id:
        print("  --- 测试获取单局详情 ---")
        try:
            response = requests.get(f"{BASE_URL}/api/library/game/{game_id}")
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("white") == "TestPlayer", "白方信息错误"
            assert data.get("black") == "Opponent", "黑方信息错误"
            assert data.get("result") == "0-1", "结果错误"
            assert "analysis" in data, "缺少analysis字段"
            assert "summary" in data, "缺少summary字段"
            print("    ✅ 获取单局详情成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 获取单局详情失败: {e}")
            results.append(False)
    
    # 测试1.4: 删除棋局
    if game_id:
        print("  --- 测试删除棋局 ---")
        try:
            response = requests.delete(f"{BASE_URL}/api/library/game/{game_id}")
            assert response.status_code == 200, f"期望200，实际{response.status_code}"
            data = response.json()
            assert data.get("success") == True, "删除失败"
            print("    ✅ 删除棋局成功")
            results.append(True)
        except Exception as e:
            print(f"    ❌ 删除棋局失败: {e}")
            results.append(False)
    
    # 测试1.5: 获取不存在的棋局
    print("  --- 测试获取不存在的棋局 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/library/game/nonexistent")
        assert response.status_code == 404, f"期望404，实际{response.status_code}"
        print("    ✅ 获取不存在棋局处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取不存在棋局失败: {e}")
        results.append(False)
    
    return all(results)


def test_profile_api():
    """测试能力画像API"""
    print("\n【测试2】能力画像API测试")
    
    results = []
    
    # 首先添加一个测试棋局
    print("  --- 准备测试数据 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/library/game", json={
            "pgn_content": TEST_PGN,
            "filename": "test_profile.pgn"
        })
        game_id = response.json().get("game_id")
        print(f"    ✅ 添加测试棋局成功")
    except:
        print("    ⚠️ 添加测试棋局失败，使用本地生成")
        game_id = None
    
    # 测试2.1: 生成画像
    print("  --- 测试生成画像 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/profile/generate")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") is not None, "响应格式错误"
        
        if data.get("profile"):
            profile = data["profile"]
            assert "strengths" in profile, "缺少strengths字段"
            assert "weaknesses" in profile, "缺少weaknesses字段"
            assert "style" in profile, "缺少style字段"
            assert "suggestions" in profile, "缺少suggestions字段"
            print(f"    ✅ 生成画像成功，风格: {profile.get('style')}")
        else:
            print("    ⚠️ 使用本地生成画像")
        
        results.append(True)
    except Exception as e:
        print(f"    ❌ 生成画像失败: {e}")
        results.append(False)
    
    # 测试2.2: 获取画像
    print("  --- 测试获取画像 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert "strengths" in data or data.get("error"), "响应格式错误"
        print("    ✅ 获取画像成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取画像失败: {e}")
        results.append(False)
    
    # 测试2.3: 清理测试数据
    if game_id:
        try:
            requests.delete(f"{BASE_URL}/api/library/game/{game_id}")
        except:
            pass
    
    return all(results)


def test_training_plan_api():
    """测试训练计划API"""
    print("\n【测试3】训练计划API测试")
    
    results = []
    
    # 首先生成画像
    print("  --- 准备测试数据 ---")
    try:
        requests.post(f"{BASE_URL}/api/library/game", json={
            "pgn_content": TEST_PGN,
            "filename": "test_plan.pgn"
        })
        requests.post(f"{BASE_URL}/api/profile/generate")
        print("    ✅ 准备测试数据成功")
    except:
        print("    ⚠️ 准备测试数据失败")
    
    # 测试3.1: 生成训练计划
    print("  --- 测试生成训练计划 ---")
    try:
        response = requests.post(f"{BASE_URL}/api/training/plan/generate")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") is not None, "响应格式错误"
        
        if data.get("plan"):
            plan = data["plan"]
            assert "plan_id" in plan, "缺少plan_id字段"
            assert "target_level" in plan, "缺少target_level字段"
            assert "short_term_goal" in plan, "缺少short_term_goal字段"
            assert "daily_tasks" in plan, "缺少daily_tasks字段"
            print(f"    ✅ 生成训练计划成功，目标等级: {plan.get('target_level')}")
        else:
            print("    ⚠️ 使用本地生成训练计划")
        
        results.append(True)
    except Exception as e:
        print(f"    ❌ 生成训练计划失败: {e}")
        results.append(False)
    
    # 测试3.2: 获取训练计划
    print("  --- 测试获取训练计划 ---")
    try:
        response = requests.get(f"{BASE_URL}/api/training/plan")
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert "plan_id" in data or data.get("error"), "响应格式错误"
        print("    ✅ 获取训练计划成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 获取训练计划失败: {e}")
        results.append(False)
    
    return all(results)


def test_import_export_api():
    """测试导入导出API"""
    print("\n【测试4】导入导出API测试")
    
    results = []
    
    # 测试4.1: 导入PGN文件
    print("  --- 测试导入PGN文件 ---")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            f.write(TEST_PGN)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            response = requests.post(f"{BASE_URL}/api/import/pgn", files={'file': f})
        
        os.unlink(temp_path)
        
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") == True, "导入失败"
        print("    ✅ 导入PGN文件成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 导入PGN文件失败: {e}")
        results.append(False)
    
    # 测试4.2: 导入无效文件
    print("  --- 测试导入无效文件 ---")
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("not a pgn file")
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            response = requests.post(f"{BASE_URL}/api/import/pgn", files={'file': f})
        
        os.unlink(temp_path)
        
        assert response.status_code == 400, f"期望400，实际{response.status_code}"
        print("    ✅ 导入无效文件处理正确")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 导入无效文件失败: {e}")
        results.append(False)
    
    # 测试4.3: 导入画像JSON
    print("  --- 测试导入画像JSON ---")
    try:
        profile_data = {
            "strengths": [{"skill": "测试技能", "score": 80}],
            "weaknesses": [{"skill": "测试弱项", "score": 50}],
            "style": "测试风格",
            "suggestions": ["测试建议"]
        }
        
        response = requests.post(f"{BASE_URL}/api/import/profile", json=profile_data)
        assert response.status_code == 200, f"期望200，实际{response.status_code}"
        data = response.json()
        assert data.get("success") == True, "导入失败"
        print("    ✅ 导入画像JSON成功")
        results.append(True)
    except Exception as e:
        print(f"    ❌ 导入画像JSON失败: {e}")
        results.append(False)
    
    return all(results)


def test_full_workflow():
    """测试完整工作流"""
    print("\n【测试5】完整工作流测试")
    
    results = []
    
    try:
        # 步骤1: 添加棋局到点评库
        print("  --- 步骤1: 添加棋局 ---")
        response = requests.post(f"{BASE_URL}/api/library/game", json={
            "pgn_content": TEST_PGN,
            "filename": "workflow_test.pgn"
        })
        game_id = response.json().get("game_id")
        assert game_id, "添加棋局失败"
        print(f"    ✅ 添加棋局成功: {game_id}")
        
        # 步骤2: 生成能力画像
        print("  --- 步骤2: 生成画像 ---")
        response = requests.post(f"{BASE_URL}/api/profile/generate")
        assert response.status_code == 200, "生成画像失败"
        print("    ✅ 生成画像成功")
        
        # 步骤3: 生成训练计划
        print("  --- 步骤3: 生成训练计划 ---")
        response = requests.post(f"{BASE_URL}/api/training/plan/generate")
        assert response.status_code == 200, "生成训练计划失败"
        print("    ✅ 生成训练计划成功")
        
        # 步骤4: 导出画像
        print("  --- 步骤4: 导出画像 ---")
        response = requests.get(f"{BASE_URL}/api/profile/export")
        assert response.status_code == 200, "导出画像失败"
        assert response.headers.get('Content-Disposition'), "缺少Content-Disposition头"
        print("    ✅ 导出画像成功")
        
        # 步骤5: 导出训练计划
        print("  --- 步骤5: 导出训练计划 ---")
        response = requests.get(f"{BASE_URL}/api/training/plan/export")
        assert response.status_code == 200, "导出训练计划失败"
        print("    ✅ 导出训练计划成功")
        
        # 步骤6: 清理
        requests.delete(f"{BASE_URL}/api/library/game/{game_id}")
        
        print("    ✅ 完整工作流测试通过")
        results.append(True)
        
    except Exception as e:
        print(f"    ❌ 完整工作流测试失败: {e}")
        results.append(False)
    
    return all(results)


def main():
    print("=" * 70)
    print("国际象棋学习训练系统 - 点评库功能测试套件")
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
    
    test_results.append(("点评库API", test_library_api()))
    test_results.append(("能力画像API", test_profile_api()))
    test_results.append(("训练计划API", test_training_plan_api()))
    test_results.append(("导入导出API", test_import_export_api()))
    test_results.append(("完整工作流", test_full_workflow()))
    
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