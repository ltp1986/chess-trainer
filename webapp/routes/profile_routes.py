import logging

from flask import Blueprint, jsonify, request, Response

from repositories.profile_repo import load_profile, save_profile, save_current_profile
from services.profile_service import generate_profile
from services.ai_service import call_doubao_api_with_retry
from services.analysis_service import generate_local_analysis

logger = logging.getLogger(__name__)

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile_endpoint():
    player_id = request.args.get('player_id')
    profile = load_profile(player_id)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "画像不存在"}), 404

@profile_bp.route('/api/profile/generate', methods=['POST'])
def generate_profile_endpoint():
    data = request.json or {}
    player_id = data.get('player_id', 'player_cd137a6a')
    player_name = data.get('player_name', '刘洪硕')
    use_ai = data.get('use_ai', False)
    
    profile = generate_profile(player_id, player_name, use_ai)
    
    return jsonify({
        "success": True,
        "message": "能力画像生成成功",
        "profile": profile
    })

@profile_bp.route('/api/profile/generate/enhanced', methods=['POST'])
def generate_enhanced_profile_endpoint():
    data = request.json or {}
    player_id = data.get('player_id', 'player_cd137a6a')
    player_name = data.get('player_name', '刘洪硕')
    
    profile = generate_profile(player_id, player_name, use_ai=True)
    
    return jsonify({
        "success": True,
        "message": "AI增强能力画像生成成功",
        "profile": profile,
        "generated_by_ai": profile.get("generated_by_ai", False)
    })

@profile_bp.route('/api/profile/export', methods=['GET'])
def export_profile():
    profile = load_profile()
    if profile:
        import json
        data = json.dumps(profile, ensure_ascii=False)
        response = Response(data, status=200, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=profile.json'
        return response
    return jsonify({"error": "画像不存在"}), 404

@profile_bp.route('/api/analyze/enhanced', methods=['POST'])
def analyze_position_enhanced():
    data = request.json or {}
    fen = data.get('fen')
    move_number = data.get('move_number', 0)
    turn = data.get('turn', 'white')
    context = data.get('context', '')
    
    if not fen:
        return jsonify({"error": "缺少FEN参数"}), 400
    
    logger.info(f"AI深度分析棋局: move_number={move_number}, turn={turn}")
    
    prompt = f"""
你是一位专业的国际象棋特级大师，擅长深度分析棋局。请分析以下局面：

【FEN】{fen}
【当前回合】{turn}
【已走步数】{move_number}
【附加信息】{context}

请输出JSON格式的分析结果，包含以下字段：
- evaluation: 局面评估（如"白方优势"、"黑方优势"、"均势"）
- score: 分数评估（用cp表示，正数表示白方优势，负数表示黑方优势）
- key_tactics: 关键战术机会列表（每项包含name和description）
- recommended_moves: 推荐走法列表（每项包含move和reason）
- threats: 潜在威胁列表（每项包含description）
- strategic_advice: 战略建议（字符串，不超过500字）
- opening_name: 开局名称（如果能识别）
- position_type: 局面类型（开局/中局/残局）

要求：
1. 分析要专业、深入
2. 推荐走法要有具体理由
3. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api_with_retry(prompt, temperature=0.4, max_tokens=2000)
    
    if result:
        try:
            import json
            analysis = json.loads(result)
            analysis["fen"] = fen
            analysis["analyzed_at"] = datetime.datetime.now().isoformat()
            analysis["generated_by_ai"] = True
            
            logger.info("AI棋局分析成功")
            return jsonify({
                "success": True,
                "analysis": analysis,
                "generated_by_ai": True
            })
        except json.JSONDecodeError as e:
            logger.error(f"AI分析响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地分析")
    analysis = generate_local_analysis(fen, move_number, turn)
    analysis["generated_by_ai"] = False
    
    return jsonify({
        "success": True,
        "analysis": analysis,
        "generated_by_ai": False
    })

@profile_bp.route('/api/import/profile', methods=['POST'])
def import_profile():
    data = request.json
    if not data:
        return jsonify({"error": "缺少数据"}), 400
    
    save_current_profile(data)
    
    return jsonify({"success": True, "message": "画像导入成功"})

import datetime