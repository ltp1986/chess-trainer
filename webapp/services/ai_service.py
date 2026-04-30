import json
import time
import requests
import logging

from config.settings import DOUBAO_API_KEY
from services.token_service import TokenMonitor, TokenProtection

logger = logging.getLogger(__name__)

token_protection = TokenProtection()

def call_doubao_api(prompt, temperature=0.7, max_tokens=2048):
    start_time = time.time()
    logger.info(f"开始调用豆包API，prompt长度: {len(prompt)}")
    
    if not DOUBAO_API_KEY:
        logger.warning("豆包API密钥未配置")
        return None
    
    global token_protection
    if token_protection:
        allowed, info = token_protection.should_allow_request()
        if not allowed:
            logger.warning(f"API请求被拦截: {info.get('message')}")
            return None
    
    try:
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
                            "text": f"你是一位专业的国际象棋教练，擅长分析棋局并给出专业建议。\n\n{prompt}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            actual_tokens = data.get("usage", {}).get("total_tokens", max_tokens)
            TokenMonitor().record_api_call(actual_tokens)
            
            response_time = time.time() - start_time
            output = data.get("output", [])
            
            for output_item in output:
                contents = output_item.get("content", [])
                if isinstance(contents, list):
                    for content in contents:
                        if content.get("type") == "output_text":
                            text = content.get("text", "").strip()
                            logger.info(f"豆包API响应成功，token使用: {actual_tokens}，耗时: {response_time:.2f}秒")
                            return text
            
            logger.warning(f"豆包API响应格式异常，尝试从summary提取: {data}")
            for output_item in output:
                summary = output_item.get("summary", [])
                if isinstance(summary, list):
                    for item in summary:
                        if item.get("type") == "summary_text":
                            return item.get("text", "").strip()
            
            logger.error(f"豆包API响应格式错误: {data}")
            return None
        else:
            response_time = time.time() - start_time
            logger.error(f"豆包API调用失败: {response.status_code} - {response.text}，耗时: {response_time:.2f}秒")
            return None
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"调用豆包API异常: {e}，耗时: {response_time:.2f}秒", exc_info=True)
        return None

def call_doubao_api_with_retry(prompt, temperature=0.7, max_tokens=2048, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = call_doubao_api(prompt, temperature, max_tokens)
            if result is not None:
                return result
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"豆包API调用失败，第{attempt+1}次重试，等待{wait_time}秒")
                time.sleep(wait_time)
        except Exception as e:
            logger.error(f"豆包API调用异常 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    logger.warning(f"豆包API调用失败 {max_retries} 次，降级到本地算法")
    return None