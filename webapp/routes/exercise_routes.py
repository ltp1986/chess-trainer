import json
import logging

from flask import Blueprint, jsonify, request

from repositories.player_repo import load_player
from repositories.exercise_repo import (
    load_exercises, save_exercises, update_exercise_progress, get_all_exercises_summary
)
from services.exercise_service import generate_player_exercises
from services.tactics_service import generate_local_classification
from services.ai_service import call_doubao_api_with_retry

logger = logging.getLogger(__name__)

exercise_bp = Blueprint('exercise', __name__)

@exercise_bp.route('/api/exercises/player/<player_id>', methods=['GET'])
def get_player_exercises(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    exercises = load_exercises(player_id)
    
    if exercises:
        return jsonify(exercises)
    
    return jsonify({"exercises": [], "player_id": player_id, "player_name": player.get("name")})

@exercise_bp.route('/api/exercises/generate/<player_id>', methods=['GET', 'POST'])
def generate_exercises(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    game_history = player.get("game_history", [])
    player_name = player.get("name", "")
    
    exercises_data = generate_player_exercises(player_id, player_name, game_history)
    
    return jsonify({
        "success": True,
        "message": f"生成了 {len(exercises_data['exercises'])} 道错题练习",
        "exercises": exercises_data
    })

@exercise_bp.route('/api/exercises/update/<player_id>', methods=['POST'])
def update_exercises(player_id):
    data = request.json
    exercise_id = data.get('exercise_id')
    status = data.get('status')
    
    if update_exercise_progress(player_id, exercise_id, status):
        exercises_data = load_exercises(player_id)
        return jsonify({"success": True, "exercises": exercises_data})
    
    return jsonify({"error": "更新失败"}), 500

@exercise_bp.route('/api/exercises', methods=['GET'])
def get_all_exercises():
    all_exercises = get_all_exercises_summary()
    return jsonify({"exercises": all_exercises})

@exercise_bp.route('/api/exercises/classify', methods=['POST'])
def classify_exercise():
    data = request.json or {}
    fen = data.get('fen')
    actual_move = data.get('actual_move')
    best_move = data.get('best_move')
    loss = data.get('loss', 0)
    move_number = data.get('move_number', 0)
    
    if not fen:
        return jsonify({"error": "缺少FEN参数"}), 400
    
    logger.info(f"AI错题分类: move_number={move_number}, loss={loss}")
    
    prompt = f"""
你是一位专业的国际象棋教练，擅长分析错误走法并进行分类。

请分析以下错题并进行智能分类：

【FEN】{fen}
【实际走法】{actual_move}
【最佳走法】{best_move}
【分值损失】{loss}
【步数】{move_number}

请输出JSON格式的分类结果，包含以下字段：
- category: 错误类型（开局错误/中局错误/残局错误/战术错误/战略错误/计算错误）
- sub_category: 子类型（如：双攻、牵制、通路兵、王安全、兵结构等）
- difficulty: 难度等级（1-5，1最简单，5最难）
- description: 错误原因描述（不超过100字）
- suggestion: 改进建议（不超过100字）
- common_mistake: 是否为常见错误（true/false）

要求：
1. 分类要准确、专业
2. 描述和建议要具体
3. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api_with_retry(prompt, temperature=0.3, max_tokens=1000)
    
    if result:
        try:
            classification = json.loads(result)
            classification["classified_at"] = datetime.datetime.now().isoformat()
            classification["generated_by_ai"] = True
            
            logger.info("AI错题分类成功")
            return jsonify({
                "success": True,
                "classification": classification,
                "generated_by_ai": True
            })
        except json.JSONDecodeError as e:
            logger.error(f"AI分类响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地分类")
    classification = generate_local_classification(fen, actual_move, best_move, loss, move_number)
    classification["generated_by_ai"] = False
    
    return jsonify({
        "success": True,
        "classification": classification,
        "generated_by_ai": False
    })

@exercise_bp.route('/api/exercises/batch_classify', methods=['POST'])
def batch_classify_exercises():
    data = request.json or {}
    exercises = data.get('exercises', [])
    
    if not exercises:
        return jsonify({"error": "缺少练习数据"}), 400
    
    logger.info(f"批量分类练习: {len(exercises)} 条")
    
    results = []
    for ex in exercises:
        result = classify_exercise_internal(ex)
        results.append(result)
    
    return jsonify({
        "success": True,
        "classifications": results,
        "total_count": len(results)
    })

def classify_exercise_internal(exercise):
    fen = exercise.get('fen')
    actual_move = exercise.get('actual_move')
    best_move = exercise.get('best_move')
    loss = exercise.get('loss', 0)
    move_number = exercise.get('move_number', 0)
    
    prompt = f"""
分析以下错题：

【FEN】{fen}
【实际走法】{actual_move}
【最佳走法】{best_move}
【分值损失】{loss}
【步数】{move_number}

请输出JSON格式：
{{"category": "错误类型", "sub_category": "子类型", "difficulty": 1-5, "description": "描述", "suggestion": "建议"}}
"""
    
    result = call_doubao_api_with_retry(prompt, temperature=0.3, max_tokens=500)
    
    if result:
        try:
            return json.loads(result)
        except:
            pass
    
    return generate_local_classification(fen, actual_move, best_move, loss, move_number)

import datetime