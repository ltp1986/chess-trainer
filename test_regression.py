"""
回归测试套件 - 验证国际象棋习题训练系统的核心功能
测试目标：棋手1.pgn（结果0-1，白方败）
"""

import os
import sys
import json
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WATCH = r"D:\Chess_PGN_Receive"
TEST_PGN = "败局1.pgn"
BASE_URL = "http://localhost:5000"


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "命令超时", -1


def test_pgn_file_exists():
    """测试1：PGN文件是否存在"""
    print("\n【测试1】PGN文件是否存在")
    pgn_path = os.path.join(WATCH, TEST_PGN)
    if os.path.exists(pgn_path):
        print(f"  ✅ PGN文件存在: {pgn_path}")
        return True
    else:
        print(f"  ❌ PGN文件不存在: {pgn_path}")
        return False


def test_pgn_content():
    """测试2：PGN文件内容解析"""
    print("\n【测试2】PGN文件内容解析")
    pgn_path = os.path.join(WATCH, TEST_PGN)
    try:
        with open(pgn_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键字段
        checks = [
            ("[Result \"0-1\"]", "结果字段"),
            ("[White \"棋手\"]", "白方字段"),
            ("[Black \"senserobot_19\"]", "黑方字段"),
        ]
        
        all_passed = True
        for check, desc in checks:
            if check in content:
                print(f"  ✅ {desc}: 正确")
            else:
                print(f"  ❌ {desc}: 缺失或错误")
                all_passed = False
        
        # 检查走法
        lines = content.strip().split('\n')
        moves_line = lines[-1] if lines else ""
        if moves_line and not moves_line.startswith('['):
            moves = moves_line.split()
            print(f"  ✅ 走法数量: {len(moves)}")
        else:
            print(f"  ❌ 走法解析失败")
            all_passed = False
            
        return all_passed
    except Exception as e:
        print(f"  ❌ 读取文件失败: {e}")
        return False


def test_analyze_api():
    """测试3：分析API是否正常工作"""
    print("\n【测试3】分析API是否正常工作")
    import requests
    
    try:
        response = requests.get(f"{BASE_URL}/api/analyze/{TEST_PGN}")
        print(f"  HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ API响应正常")
            print(f"    - 状态: {data.get('status')}")
            print(f"    - 白方: {data.get('white')}")
            print(f"    - 黑方: {data.get('black')}")
            print(f"    - 结果: {data.get('result')}")
            print(f"    - 习题数量: {len(data.get('exercises', []))}")
            
            # 检查习题结构
            exercises = data.get('exercises', [])
            if exercises:
                ex = exercises[0]
                print(f"    - 第1题: 第{ex.get('step')}步, 回合: {ex.get('turn')}")
                print(f"      FEN: {ex.get('fen')[:50]}...")
                print(f"      最佳着法: {ex.get('best_move')}")
                
                # 验证回合是否为败方（白方）
                if ex.get('turn') == 'white':
                    print(f"      ✅ 习题回合正确（白方是败方）")
                else:
                    print(f"      ❌ 习题回合错误（应为白方，实际是{ex.get('turn')}）")
            return True
        else:
            print(f"  ❌ API调用失败: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False


def test_check_move_api():
    """测试4：走棋验证API是否正常工作"""
    print("\n【测试4】走棋验证API是否正常工作")
    import requests
    
    # 先获取习题
    try:
        response = requests.get(f"{BASE_URL}/api/analyze/{TEST_PGN}")
        if response.status_code != 200:
            print("  ❌ 无法获取习题")
            return False
        
        exercises = response.json().get('exercises', [])
        if not exercises:
            print("  ❌ 没有可用的习题")
            return False
        
        ex = exercises[0]
        fen = ex.get('fen')
        best_move = ex.get('best_move')
        
        print(f"  测试习题: 第{ex.get('step')}步")
        print(f"  最佳着法: {best_move}")
        
        # 测试1：走最佳着法
        print("  --- 测试走最佳着法 ---")
        response = requests.post(f"{BASE_URL}/api/check_move", json={
            "fen": fen,
            "move": best_move,
            "expected_best": best_move
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"    响应: valid={result.get('valid')}, correct={result.get('correct')}")
            print(f"    消息: {result.get('message')}")
            if result.get('valid') and result.get('correct'):
                print(f"    ✅ 最佳着法判断正确")
            else:
                print(f"    ❌ 最佳着法判断错误")
        else:
            print(f"    ❌ API调用失败: {response.status_code}")
        
        # 测试2：走错误着法（从合法着法中选一个非最佳的）
        print("  --- 测试走错误着法 ---")
        import chess
        board = chess.Board(fen)
        legal_moves = [m.uci() for m in board.legal_moves]
        
        # 找一个不是最佳着法的合法着法
        wrong_move = None
        for mv in legal_moves:
            if mv != best_move:
                wrong_move = mv
                break
        
        if wrong_move:
            response = requests.post(f"{BASE_URL}/api/check_move", json={
                "fen": fen,
                "move": wrong_move,
                "expected_best": best_move
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"    选择的错误着法: {wrong_move}")
                print(f"    响应: valid={result.get('valid')}, correct={result.get('correct')}")
                print(f"    消息: {result.get('message')}")
                if result.get('valid') and not result.get('correct'):
                    print(f"    ✅ 错误着法判断正确")
                else:
                    print(f"    ❌ 错误着法判断错误")
            else:
                print(f"    ❌ API调用失败: {response.status_code}")
        else:
            print(f"    ⚠️ 没有可用的错误着法（可能只有一个合法着法）")
            
        return True
        
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False


def test_legal_moves_api():
    """测试5：合法着法API是否正常工作"""
    print("\n【测试5】合法着法API是否正常工作")
    import requests
    
    try:
        response = requests.get(f"{BASE_URL}/api/analyze/{TEST_PGN}")
        if response.status_code != 200:
            print("  ❌ 无法获取习题")
            return False
        
        exercises = response.json().get('exercises', [])
        if not exercises:
            print("  ❌ 没有可用的习题")
            return False
        
        ex = exercises[0]
        fen = ex.get('fen')
        
        # 获取合法着法
        response = requests.post(f"{BASE_URL}/api/legal_moves", json={
            "fen": fen,
            "square": "e2"  # 白方王前兵
        })
        
        if response.status_code == 200:
            result = response.json()
            legal_moves = result.get('legal_moves', [])
            print(f"  e2格的合法着法: {legal_moves}")
            if legal_moves:
                print(f"  ✅ 合法着法获取成功")
            else:
                print(f"  ⚠️ 没有合法着法（可能e2格无子或不是该方回合）")
            return True
        else:
            print(f"  ❌ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False


def test_frontend_interaction():
    """测试6：前端走棋交互测试"""
    print("\n【测试6】前端走棋交互测试")
    import requests
    import chess
    
    try:
        response = requests.get(f"{BASE_URL}/api/analyze/{TEST_PGN}")
        if response.status_code != 200:
            print("  ❌ 无法获取习题")
            return False
        
        exercises = response.json().get('exercises', [])
        if not exercises:
            print("  ❌ 没有可用的习题")
            return False
        
        ex = exercises[0]
        fen = ex.get('fen')
        best_move = ex.get('best_move')
        turn = ex.get('turn')
        
        print(f"  当前习题: 第{ex.get('step')}步")
        print(f"  局面FEN: {fen[:50]}...")
        print(f"  当前回合: {turn}")
        print(f"  最佳着法: {best_move}")
        
        # 验证最佳着法是否合法
        board = chess.Board(fen)
        if best_move:
            best_move_obj = chess.Move.from_uci(best_move)
            is_legal = best_move_obj in board.legal_moves
            print(f"  最佳着法{best_move}是否合法: {'✅ 是' if is_legal else '❌ 否'}")
            
            if is_legal:
                # 检查走子方是否正确
                expected_color = chess.WHITE if turn == 'white' else chess.BLACK
                actual_color = board.turn
                color_match = expected_color == actual_color
                print(f"  回合颜色是否匹配: {'✅ 匹配' if color_match else '❌ 不匹配'}")
                
                if color_match:
                    print(f"  ✅ 前端可以正确走棋")
                    return True
                else:
                    print(f"  ❌ 回合颜色不匹配，前端无法正确走棋")
                    return False
            else:
                print(f"  ❌ 最佳着法不合法，前端无法走棋")
                return False
        else:
            print(f"  ⚠️ 没有最佳着法")
            return True
            
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return False


def main():
    print("=" * 70)
    print("国际象棋习题训练系统 - 回归测试套件")
    print("=" * 70)
    print(f"测试文件: {TEST_PGN}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 检查服务是否运行
    import requests
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ 服务运行正常: {BASE_URL}")
    except:
        print("❌ 服务未运行，请先启动webapp/app.py")
        return
    
    results = []
    
    # 运行所有测试
    results.append(("PGN文件存在", test_pgn_file_exists()))
    results.append(("PGN内容解析", test_pgn_content()))
    results.append(("分析API", test_analyze_api()))
    results.append(("走棋验证API", test_check_move_api()))
    results.append(("合法着法API", test_legal_moves_api()))
    results.append(("前端走棋交互", test_frontend_interaction()))
    
    # 输出总结
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 70)
    print(f"总计: {passed}/{len(results)} 通过")
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️ {failed} 个测试失败，请检查相关模块")
    print("=" * 70)


if __name__ == "__main__":
    main()
