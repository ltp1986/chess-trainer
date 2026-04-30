import json
import datetime
import logging

from repositories.profile_repo import save_profile, load_profile
from repositories.game_repo import load_game
from services.ai_service import call_doubao_api_with_retry
from mock_data import generate_mock_profile

logger = logging.getLogger(__name__)

def generate_profile(player_id, player_name, use_ai=False):
    if use_ai:
        return generate_enhanced_profile(player_id, player_name)
    
    profile = generate_mock_profile(player_id, player_name)
    save_profile(player_id, profile)
    
    return profile

def generate_enhanced_profile(player_id, player_name):
    logger.info(f"生成AI增强能力画像: player_id={player_id}, player_name={player_name}")
    
    games_data = []
    from repositories.player_repo import load_player
    player = load_player(player_id) if player_id else None
    if player:
        game_history = player.get("game_history", [])
        for game_id in game_history[:5]:
            game = load_game(game_id)
            if game:
                games_data.append(game)
    
    prompt = f"""
你是一位专业的国际象棋教练，擅长分析棋手对局并生成详细的能力画像。

请根据以下棋局分析数据，为棋手【{player_name}】生成专业的能力画像：

【棋手信息】
- 棋手ID: {player_id}
- 棋手姓名: {player_name}
- 对局数量: {len(games_data)}

【棋局分析数据】
{json.dumps(games_data, ensure_ascii=False, indent=2)}

请输出JSON格式的能力画像，包含以下字段：
- strengths: 强项列表，每项包含skill（技能名称）和score（分数0-100）
- weaknesses: 弱项列表，每项包含skill和score
- style: 棋风描述（如：进攻型、稳健型、均衡型、战术型等）
- suggestions: 训练建议列表（最多5条，每条不超过50字）
- overall_rating: 估计等级分（整数，范围1000-2500）
- detailed_analysis: 详细分析报告（中文，不少于200字）
- opening_skill: 开局能力评分（0-100）
- midgame_skill: 中局能力评分（0-100）
- endgame_skill: 残局能力评分（0-100）
- tactical_vision: 战术眼光评分（0-100）
- positional_understanding: 局面理解评分（0-100）

要求：
1. 分析要专业、深入，基于提供的棋局数据
2. 建议要具体可行，有针对性
3. 评分要合理，符合实际水平
4. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api_with_retry(prompt, temperature=0.5, max_tokens=3000)
    
    if result:
        try:
            profile = json.loads(result)
            profile["generated_at"] = datetime.datetime.now().isoformat()
            profile["games_analyzed"] = len(games_data)
            profile["generated_by_ai"] = True
            
            save_profile(player_id, profile)
            
            logger.info(f"AI能力画像生成成功: {player_id}")
            return profile
        except json.JSONDecodeError as e:
            logger.error(f"AI响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地生成")
    profile = generate_local_profile(games_data)
    profile["generated_by_ai"] = False
    
    save_profile(player_id, profile)
    
    return profile

def generate_local_profile(games_data):
    if not games_data:
        return {
            "strengths": [
                {"skill": "残局技巧", "score": 70},
                {"skill": "战术计算", "score": 65}
            ],
            "weaknesses": [
                {"skill": "开局准备", "score": 50},
                {"skill": "时间管理", "score": 55}
            ],
            "style": "均衡型",
            "suggestions": [
                "继续加强战术训练",
                "注意开局准备",
                "提高计算深度"
            ],
            "overall_rating": 1600,
            "generated_at": datetime.datetime.now().isoformat(),
            "games_analyzed": 0
        }
    
    total_mistakes = sum(g.get("summary", {}).get("total_mistakes", 0) for g in games_data)
    avg_mistakes = total_mistakes / len(games_data)
    
    early_mistakes = 0
    mid_mistakes = 0
    late_mistakes = 0
    total_loss = 0
    
    for game in games_data:
        mistakes = game.get("mistakes", [])
        for m in mistakes:
            step = m.get("step", 0)
            loss = m.get("loss", 0)
            total_loss += loss
            if step <= 10:
                early_mistakes += 1
            elif step <= 30:
                mid_mistakes += 1
            else:
                late_mistakes += 1
    
    avg_loss = total_loss / (total_mistakes if total_mistakes > 0 else 1)
    
    strengths = []
    weaknesses = []
    suggestions = []
    
    if avg_mistakes < 2:
        strengths.append({"skill": "战术计算", "score": 85})
    elif avg_mistakes < 4:
        strengths.append({"skill": "战术计算", "score": 70})
    else:
        weaknesses.append({"skill": "战术计算", "score": 50})
        suggestions.append("加强战术计算训练，减少失误")
    
    if early_mistakes <= mid_mistakes and early_mistakes <= late_mistakes:
        strengths.append({"skill": "开局准备", "score": 75})
    else:
        weaknesses.append({"skill": "开局准备", "score": 45})
        suggestions.append("重视开局准备，研究常见开局变化")
    
    if late_mistakes <= early_mistakes and late_mistakes <= mid_mistakes:
        strengths.append({"skill": "残局技巧", "score": 80})
    else:
        weaknesses.append({"skill": "残局技巧", "score": 55})
        suggestions.append("加强残局训练，提高收官能力")
    
    if avg_loss > 200:
        weaknesses.append({"skill": "风险控制", "score": 40})
        suggestions.append("注意风险控制，避免大损失的失误")
    
    if len(suggestions) == 0:
        suggestions = ["继续保持，稳步提升棋力", "增加对局数量以积累经验"]
    
    style = "均衡型"
    if early_mistakes > mid_mistakes * 2:
        style = "进攻型"
    elif late_mistakes > early_mistakes * 2:
        style = "稳健型"
    
    overall_rating = max(1000, min(2000, 1600 - int(avg_mistakes * 50) + len(games_data) * 20))
    
    profile = {
        "strengths": strengths if strengths else [{"skill": "学习态度", "score": 70}],
        "weaknesses": weaknesses if weaknesses else [{"skill": "经验不足", "score": 60}],
        "style": style,
        "suggestions": suggestions[:5],
        "overall_rating": overall_rating,
        "generated_at": datetime.datetime.now().isoformat(),
        "games_analyzed": len(games_data),
        "avg_mistakes_per_game": round(avg_mistakes, 2),
        "avg_loss_per_mistake": round(avg_loss, 2)
    }
    
    return profile