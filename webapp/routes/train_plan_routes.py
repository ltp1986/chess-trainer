import logging

from flask import Blueprint, jsonify, request, Response

from repositories.plan_repo import load_plan, save_plan, save_current_plan
from services.train_plan_service import generate_training_plan
from mock_data import (
    generate_mock_training_plan,
    generate_mock_progress,
    generate_mock_achievements,
    generate_mock_reminders,
    generate_mock_mistakes
)

logger = logging.getLogger(__name__)

train_plan_bp = Blueprint('train_plan', __name__)

@train_plan_bp.route('/api/training/plan', methods=['GET'])
def get_training_plan():
    plan = load_plan()
    if plan:
        return jsonify(plan)
    return jsonify({"error": "训练计划不存在"}), 404

@train_plan_bp.route('/api/training/plan/generate', methods=['POST'])
def generate_training_plan_endpoint():
    data = request.json or {}
    player_id = data.get('player_id', 'player_cd137a6a')
    player_name = data.get('player_name', '刘洪硕')
    
    plan = generate_training_plan(player_id, player_name)
    
    return jsonify({
        "success": True,
        "message": "训练计划生成成功",
        "plan": plan
    })

@train_plan_bp.route('/api/training/plan/export', methods=['GET'])
def export_training_plan():
    plan = load_plan()
    if plan:
        import json
        data = json.dumps(plan, ensure_ascii=False)
        response = Response(data, status=200, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=training_plan.json'
        return response
    return jsonify({"error": "训练计划不存在"}), 404

@train_plan_bp.route('/api/training/task/complete', methods=['POST'])
def complete_task():
    try:
        data = request.json
        player_id = data.get("player_id", "player_cd137a6a")
        task_id = data.get("task_id")
        completed = data.get("completed", True)
        score = data.get("score", 0)
        duration_minutes = data.get("duration_minutes", 0)
        notes = data.get("notes", "")
        
        plan = generate_mock_training_plan(player_id)
        
        for task in plan["daily_tasks"]:
            if task["task_id"] == task_id:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                task["completion_history"].append({
                    "date": today,
                    "completed": completed,
                    "score": score,
                    "notes": notes
                })
                task["total_completed"] += 1
                if completed:
                    task["streak"] += 1
                    if task["avg_score"] == 0:
                        task["avg_score"] = score
                    else:
                        task["avg_score"] = round((task["avg_score"] * (task["total_completed"] - 1) + score) / task["total_completed"])
                else:
                    task["streak"] = 0
        
        points_earned = 10
        if score >= 80:
            points_earned += 20
        
        return jsonify({
            "success": True,
            "message": "任务完成记录成功",
            "update": {
                "streak": plan["daily_tasks"][0]["streak"],
                "total_completed": plan["daily_tasks"][0]["total_completed"],
                "avg_score": plan["daily_tasks"][0]["avg_score"],
                "points_earned": points_earned
            },
            "reminders": []
        })
    except Exception as e:
        logger.error(f"完成任务失败: {e}")
        return jsonify({"error": "完成任务失败"}), 500

@train_plan_bp.route('/api/training/progress', methods=['GET'])
def get_training_progress():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        progress = generate_mock_progress(player_id)
        return jsonify(progress)
    except Exception as e:
        logger.error(f"获取训练进度失败: {e}")
        return jsonify({"error": "获取训练进度失败"}), 500

@train_plan_bp.route('/api/training/progress/<player_id>', methods=['GET'])
def get_player_progress(player_id):
    try:
        progress = generate_mock_progress(player_id)
        return jsonify(progress)
    except Exception as e:
        logger.error(f"获取选手训练进度失败: {e}")
        return jsonify({"error": "获取选手训练进度失败"}), 500

@train_plan_bp.route('/api/training/reminders', methods=['GET'])
def get_reminders():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders)
    except Exception as e:
        logger.error(f"获取训练提醒失败: {e}")
        return jsonify({"error": "获取训练提醒失败"}), 500

@train_plan_bp.route('/api/training/reminders/<player_id>', methods=['GET'])
def get_player_reminders(player_id):
    try:
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders)
    except Exception as e:
        logger.error(f"获取选手训练提醒失败: {e}")
        return jsonify({"error": "获取选手训练提醒失败"}), 500

@train_plan_bp.route('/api/training/summary/daily', methods=['GET'])
def get_daily_summary():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders["daily_summary"])
    except Exception as e:
        logger.error(f"获取每日总结失败: {e}")
        return jsonify({"error": "获取每日总结失败"}), 500

@train_plan_bp.route('/api/training/summary/weekly', methods=['GET'])
def get_weekly_summary():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders["weekly_summary"])
    except Exception as e:
        logger.error(f"获取每周总结失败: {e}")
        return jsonify({"error": "获取每周总结失败"}), 500

@train_plan_bp.route('/api/training/achievements', methods=['GET'])
def get_achievements():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        achievements = generate_mock_achievements(player_id)
        return jsonify(achievements)
    except Exception as e:
        logger.error(f"获取成就失败: {e}")
        return jsonify({"error": "获取成就失败"}), 500

@train_plan_bp.route('/api/training/achievements/<player_id>', methods=['GET'])
def get_player_achievements(player_id):
    try:
        achievements = generate_mock_achievements(player_id)
        return jsonify(achievements)
    except Exception as e:
        logger.error(f"获取选手成就失败: {e}")
        return jsonify({"error": "获取选手成就失败"}), 500

@train_plan_bp.route('/api/training/adjust', methods=['POST'])
def adjust_training_plan():
    try:
        data = request.json
        player_id = data.get("player_id", "player_cd137a6a")
        
        plan = generate_mock_training_plan(player_id)
        progress = generate_mock_progress(player_id)
        
        adjustments = []
        
        for task in plan["daily_tasks"]:
            avg_score = task.get("avg_score", 0)
            if avg_score > 85:
                task["difficulty"] = "hard"
                adjustments.append({
                    "type": "increase_difficulty",
                    "task": task["name"],
                    "change": "难度提升为困难"
                })
            elif avg_score < 50:
                task["difficulty"] = "easy"
                adjustments.append({
                    "type": "decrease_difficulty",
                    "task": task["name"],
                    "change": "难度降低为简单"
                })
        
        return jsonify({
            "success": True,
            "message": "训练计划调整完成",
            "adjustments": adjustments,
            "plan": plan
        })
    except Exception as e:
        logger.error(f"调整训练计划失败: {e}")
        return jsonify({"error": "调整训练计划失败"}), 500

@train_plan_bp.route('/api/mistakes/analysis/<player_id>', methods=['GET'])
def get_mistakes_analysis(player_id):
    try:
        mistakes = generate_mock_mistakes(player_id)
        return jsonify(mistakes)
    except Exception as e:
        logger.error(f"获取错题分析失败: {e}")
        return jsonify({"error": "获取错题分析失败"}), 500

@train_plan_bp.route('/api/import/plan', methods=['POST'])
def import_plan():
    data = request.json
    if not data:
        return jsonify({"error": "缺少数据"}), 400
    
    save_current_plan(data)
    
    return jsonify({"success": True, "message": "训练计划导入成功"})

import datetime