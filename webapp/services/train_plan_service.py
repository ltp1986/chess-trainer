import json
import datetime
import logging

from repositories.plan_repo import save_plan, load_plan, save_current_plan
from repositories.profile_repo import load_profile
from services.ai_service import call_doubao_api_with_retry
from mock_data import generate_mock_training_plan

logger = logging.getLogger(__name__)

def generate_training_plan(player_id=None, player_name=None, use_ai=False):
    if player_id:
        profile = load_profile(player_id)
    else:
        profile = load_profile()
    
    if not profile:
        profile = {
            "strengths": [{"skill": "残局技巧", "score": 70}, {"skill": "战术计算", "score": 65}],
            "weaknesses": [{"skill": "开局准备", "score": 50}, {"skill": "时间管理", "score": 55}],
            "style": "均衡型",
            "overall_rating": 1600
        }
    
    if use_ai:
        return generate_ai_training_plan(profile)
    
    plan = generate_local_plan(profile)
    save_current_plan(plan)
    
    return plan

def generate_ai_training_plan(profile):
    prompt = f"""根据以下能力画像生成训练计划：

能力画像：
{json.dumps(profile, ensure_ascii=False, indent=2)}

请输出JSON格式，包含以下字段：
- plan_id: 计划ID
- target_level: 目标等级
- short_term_goal: 短期目标（1个月）
- long_term_goal: 长期目标（3个月）
- daily_tasks: 每日任务列表，每个包含name、duration、frequency
- weekly_focus: 每周重点
- recommendations: 推荐资源列表，每个包含resource和type
- estimated_time: 预计完成时间

请用中文输出。
"""
    
    result = call_doubao_api_with_retry(prompt, temperature=0.5)
    
    if result:
        try:
            plan = json.loads(result)
            plan["plan_id"] = f"plan_{datetime.datetime.now().strftime('%Y%m%d')}"
            plan["generated_at"] = datetime.datetime.now().isoformat()
            
            save_current_plan(plan)
            
            return plan
        except:
            pass
    
    plan = generate_local_plan(profile)
    save_current_plan(plan)
    
    return plan

def generate_local_plan(profile):
    weaknesses = profile.get("weaknesses", [])
    weak_skills = [w["skill"] for w in weaknesses if w["score"] < 60]
    strengths = profile.get("strengths", [])
    strong_skills = [s["skill"] for s in strengths if s["score"] > 70]
    
    daily_tasks = []
    weekly_tasks = []
    focus_areas = []
    
    if "战术计算" in weak_skills:
        daily_tasks.append({"name": "战术谜题训练", "duration": "30分钟", "frequency": "每天", "description": "完成10道战术谜题，重点练习组合战术", "completed": False})
        weekly_tasks.append({"name": "战术专项练习", "duration": "2小时", "frequency": "每周", "description": "进行战术专题训练，重点解决计算深度问题"})
        focus_areas.append("战术计算")
    else:
        daily_tasks.append({"name": "战术维持训练", "duration": "15分钟", "frequency": "每天", "description": "保持战术敏感度，完成5道谜题", "completed": False})
    
    if "开局准备" in weak_skills:
        daily_tasks.append({"name": "开局学习", "duration": "20分钟", "frequency": "每天", "description": "学习并记忆1-2个开局变例", "completed": False})
        weekly_tasks.append({"name": "开局复盘", "duration": "1小时", "frequency": "每周", "description": "分析自己的开局走法，找出改进点"})
        focus_areas.append("开局准备")
    
    if "残局技巧" in weak_skills:
        daily_tasks.append({"name": "残局练习", "duration": "15分钟", "frequency": "每天", "description": "练习基础残局（王兵残局、车兵残局等）", "completed": False})
        weekly_tasks.append({"name": "残局专题", "duration": "1小时", "frequency": "每周", "description": "深入学习特定残局类型"})
        focus_areas.append("残局技巧")
    
    if "风险控制" in weak_skills:
        daily_tasks.append({"name": "局面评估练习", "duration": "10分钟", "frequency": "每天", "description": "分析3个复杂局面，评估风险", "completed": False})
        focus_areas.append("风险控制")
    
    daily_tasks.append({"name": "错题回顾", "duration": "15分钟", "frequency": "每天", "description": "复习错题集中的2-3道题目", "completed": False})
    daily_tasks.append({"name": "快速对局", "duration": "30分钟", "frequency": "每天", "description": "进行15分钟快棋练习", "completed": False})
    
    weekly_tasks.append({"name": "深度复盘", "duration": "2小时", "frequency": "每周", "description": "详细分析本周最差的一局棋"})
    weekly_tasks.append({"name": "模拟比赛", "duration": "3小时", "frequency": "每周", "description": "进行一轮模拟比赛"})
    
    target_rating = profile.get("overall_rating", 1600)
    if target_rating < 1400:
        target_level = "L1"
        estimated_time = "2个月"
    elif target_rating < 1600:
        target_level = "L2"
        estimated_time = "3个月"
    elif target_rating < 1800:
        target_level = "L3"
        estimated_time = "4个月"
    else:
        target_level = "L4"
        estimated_time = "5个月"
    
    recommendations = []
    if "战术计算" in weak_skills or "战术计算" in strong_skills:
        recommendations.append({"resource": "《国际象棋战术大全》", "type": "书籍", "priority": "high"})
        recommendations.append({"resource": "CT-ART 4.0", "type": "软件", "priority": "high"})
    
    if "开局准备" in weak_skills:
        recommendations.append({"resource": "《开局百科全书》", "type": "书籍", "priority": "medium"})
    
    if "残局技巧" in weak_skills or "残局技巧" in strong_skills:
        recommendations.append({"resource": "《残局基础》", "type": "书籍", "priority": "high"})
    
    recommendations.extend([
        {"resource": "Lichess战术训练", "type": "在线", "priority": "high"},
        {"resource": "Chess.com练习", "type": "在线", "priority": "medium"},
        {"resource": "观看GM对局视频", "type": "视频", "priority": "low"}
    ])
    
    return {
        "plan_id": f"plan_{datetime.datetime.now().strftime('%Y%m%d')}",
        "target_level": target_level,
        "target_rating": target_rating + 200,
        "short_term_goal": f"在1个月内将等级分提升至 {target_rating + 50}，减少{', '.join(focus_areas) if focus_areas else '战术'}失误",
        "long_term_goal": f"在{estimated_time}内达到 {target_rating + 200} 等级分，成为{target_level}级棋手",
        "daily_tasks": daily_tasks,
        "weekly_tasks": weekly_tasks,
        "weekly_focus": f"本周重点：{'、'.join(focus_areas) if focus_areas else '综合训练'}",
        "focus_areas": focus_areas,
        "recommendations": recommendations,
        "estimated_time": estimated_time,
        "generated_at": datetime.datetime.now().isoformat(),
        "progress": 0,
        "completed_tasks": 0,
        "total_tasks": len(daily_tasks) * 30 + len(weekly_tasks) * 4
    }