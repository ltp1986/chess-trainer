import os
import sys
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_ai_api():
    print("=== 测试豆包API连接 ===")
    
    DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
    if not DOUBAO_API_KEY:
        print("❌ API密钥未配置")
        return False
    
    print(f"✅ API密钥已配置: {DOUBAO_API_KEY[:10]}...")
    
    import requests
    
    url = "https://ark.cn-beijing.volces.com/api/v3/responses"
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "doubao-seed-2-0-pro-260215",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "你好，请回复'测试成功'。"
                    }
                ]
            }
        ]
    }
    
    try:
        print("🔄 正在调用豆包API...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            output = data.get("output", [])
            
            for output_item in output:
                contents = output_item.get("content", [])
                if isinstance(contents, list):
                    for content in contents:
                        if content.get("type") == "output_text":
                            result = content.get("text")
                            print(f"✅ API调用成功!")
                            print(f"📝 响应内容: {result}")
                            return True
            
            print(f"❌ 响应格式错误: {data}")
        else:
            print(f"❌ API调用失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 调用异常: {e}")
        return False
    
    return False

def test_enhanced_profile():
    print("\n=== 测试AI能力画像生成 ===")
    
    try:
        import requests
        
        data = {
            "player_id": "test_player",
            "player_name": "测试棋手"
        }
        
        response = requests.post("http://localhost:5000/api/profile/generate/enhanced", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI能力画像生成成功!")
            print(f"   生成方式: {'AI' if result.get('generated_by_ai') else '本地'}")
            print(f"   棋风: {result['profile'].get('style', '未知')}")
            print(f"   等级分: {result['profile'].get('overall_rating', 0)}")
            if 'detailed_analysis' in result['profile']:
                print(f"   详细分析: {result['profile']['detailed_analysis'][:100]}...")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_analyze_enhanced():
    print("\n=== 测试AI棋局深度分析 ===")
    
    try:
        import requests
        
        data = {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            "move_number": 1,
            "turn": "black",
            "context": "开局第一步"
        }
        
        response = requests.post("http://localhost:5000/api/analyze/enhanced", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI棋局分析成功!")
            print(f"   生成方式: {'AI' if result.get('generated_by_ai') else '本地'}")
            print(f"   评估: {result['analysis'].get('evaluation', '未知')}")
            print(f"   局面类型: {result['analysis'].get('position_type', '未知')}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_classify_exercise():
    print("\n=== 测试AI错题分类 ===")
    
    try:
        import requests
        
        data = {
            "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 3",
            "actual_move": "Nf6",
            "best_move": "d6",
            "loss": 150,
            "move_number": 3
        }
        
        response = requests.post("http://localhost:5000/api/exercises/classify", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI错题分类成功!")
            print(f"   生成方式: {'AI' if result.get('generated_by_ai') else '本地'}")
            print(f"   分类: {result['classification'].get('category', '未知')}")
            print(f"   子类型: {result['classification'].get('sub_category', '未知')}")
            print(f"   难度: {result['classification'].get('difficulty', 0)}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试AI模块...")
    print("="*50)
    
    success_count = 0
    total_count = 4
    
    if test_ai_api():
        success_count += 1
    
    print("\n" + "="*50)
    print("启动Flask服务进行API测试...")
    
    import subprocess
    import threading
    
    def start_server():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(["python", "app.py"], check=True)
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    
    try:
        server_thread.start()
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        if test_enhanced_profile():
            success_count += 1
        
        if test_analyze_enhanced():
            success_count += 1
        
        if test_classify_exercise():
            success_count += 1
            
    except Exception as e:
        print(f"⚠️ 服务启动失败，跳过API测试: {e}")
    
    print("\n" + "="*50)
    print(f"测试完成: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过!")
    else:
        print(f"⚠️ {total_count - success_count} 个测试未通过")
