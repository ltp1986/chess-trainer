import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")

print("=== 豆包API密钥配置测试 ===")
print(f"API Key配置状态: {'已配置' if DOUBAO_API_KEY else '未配置'}")
print(f"API Key长度: {len(DOUBAO_API_KEY) if DOUBAO_API_KEY else 0} 字符")

if DOUBAO_API_KEY:
    print("\n✅ 密钥配置成功！")
    print("下一步：开始实现AI模块功能")
else:
    print("\n❌ 密钥未配置，请检查.env文件")
