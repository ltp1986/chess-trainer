import json
import os
from datetime import datetime, timedelta

OUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def generate_mock_profile(player_id="player_cd137a6a", player_name="刘洪硕"):
    today = datetime.now().isoformat()
    profile = {
        "player_id": player_id,
        "player_name": player_name,
        "generated_at": today,
        "games_analyzed": 5,
        "overall_rating": 1620,
        "style": "进攻型",
        "detailed_analysis": {
            "opening": {
                "score": 52,
                "avg_mistakes": 1.2,
                "common_openings": ["意大利开局", "西班牙开局"],
                "suggestions": ["加强西西里防御应对", "丰富开局武器库"]
            },
            "tactics": {
                "score": 68,
                "total_tactical_mistakes": 8,
                "avg_loss": 185,
                "tactical_patterns": ["双攻", "牵制", "消除保护"]
            },
            "strategy": {
                "score": 48,
                "positional_errors": 12,
                "suggestions": ["改善兵结构评估", "加强计划制定"]
            },
            "endgame": {
                "score": 72,
                "endgame_mistakes": 3,
                "mastered_endgames": ["王兵残局", "车兵残局"]
            }
        },
        "strengths": [
            {"skill": "残局技巧", "score": 72, "evidence": "残局阶段失误率仅15%"},
            {"skill": "战术识别", "score": 68, "evidence": "成功发现80%的战术机会"}
        ],
        "weaknesses": [
            {"skill": "开局准备", "score": 52, "evidence": "前10步平均损失85cp"},
            {"skill": "局面判断", "score": 48, "evidence": "中局计划连贯性不足"}
        ],
        "trend_analysis": {
            "rating_trend": "上升",
            "improvement_rate": "+15分/周",
            "focus_areas": ["开局", "战略计划"]
        },
        "suggestions": [
            "建议重点加强西西里防御的学习",
            "每天进行30分钟战术训练，重点练习双攻和牵制",
            "增加慢棋对局数量，提高局面判断能力",
            "学习《卡尔波夫的残局技巧》提升残局水平"
        ],
        "initial_scores": {
            "tactical_calculation": 60,
            "opening_preparation": 47,
            "endgame_skills": 69
        }
    }
    return profile

def generate_mock_mistakes(player_id="player_cd137a6a"):
    mistakes = {
        "player_id": player_id,
        "total_mistakes": 32,
        "mistake_distribution": {
            "tactical": {"count": 15, "percentage": 46.9, "avg_loss": 210},
            "strategic": {"count": 8, "percentage": 25.0, "avg_loss": 145},
            "opening": {"count": 5, "percentage": 15.6, "avg_loss": 95},
            "endgame": {"count": 4, "percentage": 12.5, "avg_loss": 180}
        },
        "tactical_breakdown": {
            "missed_threats": 6,
            "miscalculations": 5,
            "missed_opportunities": 4
        },
        "opening_breakdown": {
            "italian_opening": {"mistakes": 2, "avg_loss": 85},
            "spanish_opening": {"mistakes": 1, "avg_loss": 120},
            "sicilian_defense": {"mistakes": 2, "avg_loss": 80}
        },
        "frequency_by_move": {
            "1-10": {"count": 8, "percentage": 25},
            "11-25": {"count": 14, "percentage": 43.8},
            "26-40": {"count": 7, "percentage": 21.9},
            "41+": {"count": 3, "percentage": 9.3}
        },
        "top_mistakes": [
            {
                "fen": "r1bqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                "loss": 320,
                "category": "tactical",
                "description": "漏看对手的将军威胁"
            },
            {
                "fen": "r1bq1rk1/ppp2ppp/2n5/2b1p3/4P3/1QN2N2/PPP2PPP/R1B1KB1R w KQ - 0 10",
                "loss": 285,
                "category": "strategic",
                "description": "兵结构受损"
            }
        ]
    }
    return mistakes

def generate_mock_training_plan(player_id="player_cd137a6a", player_name="刘洪硕"):
    today = datetime.now().isoformat()
    plan = {
        "plan_id": f"plan_{datetime.now().strftime('%Y%m%d')}_{player_id.split('_')[1]}",
        "player_id": player_id,
        "player_name": player_name,
        "generated_at": today,
        "target_level": "L3",
        "target_rating": 1800,
        "estimated_time": "3个月",
        "short_term_goal": "1个月内将战术失误减少30%，开局准备更加扎实",
        "long_term_goal": "3个月内达到1800等级分，成为L3级棋手",
        "focus_areas": ["战术计算", "开局准备", "局面判断"],
        "daily_tasks": [
            {
                "task_id": "task_tactics",
                "name": "战术专项训练",
                "type": "daily",
                "duration": "30分钟",
                "frequency": "每天",
                "target": "完成15道战术谜题，正确率≥70%",
                "priority": "high",
                "description": "针对46.9%的战术失误，重点练习双攻、牵制等模式",
                "difficulty": "medium",
                "completion_history": [
                    {"date": "2026-04-25", "completed": True, "score": 75, "notes": "完成15题，正确率75%"},
                    {"date": "2026-04-26", "completed": True, "score": 68, "notes": "完成15题，正确率68%"},
                    {"date": "2026-04-27", "completed": False, "notes": "未完成"}
                ],
                "streak": 2,
                "total_completed": 12,
                "avg_score": 72,
                "improvement_trend": "up",
                "adjustment_count": 0,
                "status": "pending"
            },
            {
                "task_id": "task_opening",
                "name": "开局学习",
                "type": "daily",
                "duration": "20分钟",
                "frequency": "每天",
                "target": "掌握西西里防御 Najdorf变例前15步",
                "priority": "high",
                "description": "学习西西里防御和西班牙开局的关键变化",
                "difficulty": "medium",
                "completion_history": [
                    {"date": "2026-04-25", "completed": True, "score": 80, "notes": "完成学习"},
                    {"date": "2026-04-26", "completed": True, "score": 75, "notes": "完成学习"},
                    {"date": "2026-04-27", "completed": True, "score": 82, "notes": "完成学习"}
                ],
                "streak": 3,
                "total_completed": 14,
                "avg_score": 79,
                "improvement_trend": "up",
                "adjustment_count": 0,
                "status": "pending"
            },
            {
                "task_id": "task_review",
                "name": "错题回顾",
                "type": "daily",
                "duration": "15分钟",
                "frequency": "每天",
                "target": "完成所有标记错题",
                "priority": "medium",
                "description": "复习当日错题，分析失误原因",
                "difficulty": "easy",
                "completion_history": [],
                "streak": 0,
                "total_completed": 8,
                "avg_score": 0,
                "improvement_trend": "up",
                "adjustment_count": 0,
                "status": "pending"
            },
            {
                "task_id": "task_quick",
                "name": "快速对局",
                "type": "daily",
                "duration": "30分钟",
                "frequency": "每天",
                "target": "保持50%胜率",
                "priority": "medium",
                "description": "进行15分钟快棋练习",
                "difficulty": "medium",
                "completion_history": [],
                "streak": 0,
                "total_completed": 10,
                "avg_score": 55,
                "improvement_trend": "up",
                "adjustment_count": 0,
                "status": "pending"
            }
        ],
        "weekly_tasks": [
            {
                "task_id": "task_review_deep",
                "name": "深度复盘",
                "duration": "2小时",
                "frequency": "每周",
                "description": "详细分析本周最差的一局棋"
            },
            {
                "task_id": "task_opening_sim",
                "name": "开局模拟",
                "duration": "1小时",
                "frequency": "每周",
                "description": "与电脑进行开局对练"
            }
        ],
        "weekly_focus": "战术计算、开局准备",
        "recommendations": [
            {"resource": "CT-ART 4.0", "type": "软件", "priority": "high", "reason": "针对战术薄弱"},
            {"resource": "《西西里防御大全》", "type": "书籍", "priority": "high", "reason": "开局准备不足"},
            {"resource": "Lichess战术训练", "type": "在线", "priority": "medium"},
            {"resource": "《卡尔波夫的残局技巧》", "type": "书籍", "priority": "medium", "reason": "巩固残局优势"}
        ],
        "progress": 0,
        "completed_tasks": 0,
        "total_tasks": 120
    }
    return plan

def generate_mock_progress(player_id="player_cd137a6a"):
    today = datetime.now()
    plan_id = f"plan_{today.strftime('%Y%m%d')}_{player_id.split('_')[1]}"
    
    progress = {
        "player_id": player_id,
        "plan_id": plan_id,
        "overall_progress": 35,
        "time_progress": 14,
        "task_progress": 45,
        "daily_progress": {
            "completion_rate": 78,
            "streak": 5,
            "best_streak": 12
        },
        "weekly_progress": {
            "week_number": 2,
            "target_level": "L3",
            "current_rating": 1640,
            "rating_gain": 20
        },
        "skill_progress": {
            "tactical_calculation": {"current": 68, "target": 80, "improvement": 8},
            "opening_preparation": {"current": 52, "target": 70, "improvement": 5},
            "endgame_skills": {"current": 72, "target": 80, "improvement": 3}
        },
        "mistake_reduction": {
            "tactical_mistakes": {"avg_per_game": 3.2, "reduction": 28},
            "opening_mistakes": {"avg_per_game": 0.8, "reduction": 33},
            "endgame_mistakes": {"avg_per_game": 0.5, "reduction": 20}
        },
        "activity_timeline": [
            {"date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "tasks_completed": 4, "study_time": 95},
            {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "tasks_completed": 5, "study_time": 110},
            {"date": today.strftime("%Y-%m-%d"), "tasks_completed": 3, "study_time": 85}
        ],
        "updated_at": today.isoformat()
    }
    return progress

def generate_mock_achievements(player_id="player_cd137a6a"):
    achievements = {
        "player_id": player_id,
        "achievements": [
            {
                "id": "ach_001",
                "name": "初学者",
                "description": "完成第一次训练",
                "icon": "🌱",
                "unlocked": True,
                "unlocked_at": "2026-04-20"
            },
            {
                "id": "ach_002",
                "name": "坚持不懈",
                "description": "连续打卡7天",
                "icon": "🔥",
                "unlocked": True,
                "unlocked_at": "2026-04-27"
            },
            {
                "id": "ach_003",
                "name": "战术大师",
                "description": "战术训练正确率达到90%",
                "icon": "⚡",
                "unlocked": False,
                "progress": 72
            },
            {
                "id": "ach_004",
                "name": "等级飞跃",
                "description": "等级分提升100分",
                "icon": "🚀",
                "unlocked": False,
                "progress": 20
            },
            {
                "id": "ach_005",
                "name": "残局专家",
                "description": "残局训练正确率达到85%",
                "icon": "👑",
                "unlocked": False,
                "progress": 68
            }
        ],
        "points": 1560,
        "level": 5,
        "next_level_points": 2000
    }
    return achievements

def generate_mock_reminders(player_id="player_cd137a6a"):
    today = datetime.now().strftime("%Y-%m-%d")
    reminders = {
        "reminders": [
            {
                "type": "daily_reminder",
                "level": "info",
                "message": "今日训练任务尚未完成，请及时完成",
                "tasks": ["战术专项训练", "开局学习", "错题回顾"]
            },
            {
                "type": "skill_warning",
                "level": "warning",
                "message": "开局准备提升缓慢，建议调整训练方式",
                "suggestion": "建议增加开局模拟对练，每天进行20分钟开局复盘"
            }
        ],
        "daily_summary": {
            "date": today,
            "tasks_completed": 3,
            "tasks_total": 5,
            "study_time": 85,
            "avg_score": 72,
            "rating_change": "+5",
            "message": "今日表现良好！战术训练正确率提升5%，继续保持！"
        },
        "weekly_summary": {
            "week": 2,
            "tasks_completed": 28,
            "tasks_total": 35,
            "rating_change": "+20",
            "best_skill": "战术计算",
            "weak_skill": "开局准备",
            "recommendation": "下周重点加强开局准备训练"
        }
    }
    return reminders

def save_mock_data():
    profile = generate_mock_profile()
    mistakes = generate_mock_mistakes()
    plan = generate_mock_training_plan()
    progress = generate_mock_progress()
    achievements = generate_mock_achievements()
    
    with open(os.path.join(OUT_DIR, "profiles", f"profile_{profile['player_id']}.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUT_DIR, "mistakes", f"mistakes_{mistakes['player_id']}.json"), "w", encoding="utf-8") as f:
        json.dump(mistakes, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUT_DIR, "plans", f"{plan['plan_id']}.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUT_DIR, "progress", f"progress_{progress['player_id']}.json"), "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(OUT_DIR, "achievements", f"achievements_{achievements['player_id']}.json"), "w", encoding="utf-8") as f:
        json.dump(achievements, f, ensure_ascii=False, indent=2)
    
    print("模拟数据已生成")

if __name__ == "__main__":
    save_mock_data()