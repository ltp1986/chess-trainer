import os
import json
import logging

from flask import Blueprint, jsonify, request

from services.token_service import TokenMonitor, TokenProtection
from config.settings import DOUBAO_API_KEY, TOKEN_ALERTS_FILE

logger = logging.getLogger(__name__)

token_bp = Blueprint('token', __name__)

token_protection = TokenProtection()

@token_bp.route('/api/token/status', methods=['GET'])
def get_token_status():
    try:
        global token_protection
        if token_protection:
            status = token_protection.get_protection_status()
        else:
            monitor = TokenMonitor()
            status = monitor.get_usage_stats()
            status["circuit_breaker_active"] = False
            status["circuit_breaker_resets_at"] = None
        
        status["api_key_configured"] = bool(DOUBAO_API_KEY)
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取Token状态失败: {e}")
        return jsonify({"error": "获取Token状态失败"}), 500

@token_bp.route('/api/token/usage', methods=['GET'])
def get_token_usage():
    try:
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        usage_history = []
        usage = monitor.load_usage()
        for date, data in usage["daily"].items():
            usage_history.append({
                "date": date,
                "calls": data.get("calls", 0),
                "tokens": data.get("tokens", 0)
            })
        
        stats["usage_history"] = sorted(usage_history, key=lambda x: x["date"])
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取Token使用统计失败: {e}")
        return jsonify({"error": "获取Token使用统计失败"}), 500

@token_bp.route('/api/token/alerts', methods=['GET'])
def get_token_alerts():
    try:
        if os.path.exists(TOKEN_ALERTS_FILE):
            with open(TOKEN_ALERTS_FILE, "r", encoding="utf-8") as f:
                alerts = json.load(f)
        else:
            alerts = []
        
        return jsonify({"alerts": alerts})
    except Exception as e:
        logger.error(f"获取Token告警失败: {e}")
        return jsonify({"error": "获取Token告警失败"}), 500

@token_bp.route('/api/token/config', methods=['POST'])
def update_token_config():
    try:
        data = request.json
        monitor = TokenMonitor()
        
        if "daily_limit" in data:
            monitor.config["daily_limit"] = data["daily_limit"]
        if "monthly_limit" in data:
            monitor.config["monthly_limit"] = data["monthly_limit"]
        if "rpm_limit" in data:
            monitor.config["rpm_limit"] = data["rpm_limit"]
        if "daily_warning" in data:
            monitor.config["daily_warning"] = data["daily_warning"]
        if "daily_critical" in data:
            monitor.config["daily_critical"] = data["daily_critical"]
        if "monthly_warning" in data:
            monitor.config["monthly_warning"] = data["monthly_warning"]
        if "monthly_critical" in data:
            monitor.config["monthly_critical"] = data["monthly_critical"]
        
        return jsonify({
            "success": True,
            "message": "Token监控配置更新成功",
            "config": monitor.config
        })
    except Exception as e:
        logger.error(f"更新Token配置失败: {e}")
        return jsonify({"error": "更新Token配置失败"}), 500

@token_bp.route('/api/token/reset-circuit', methods=['POST'])
def reset_circuit_breaker():
    try:
        global token_protection
        if token_protection:
            token_protection.circuit_breaker_active = False
            token_protection.circuit_breaker_endtime = None
            logger.info("熔断器已手动重置")
        
        return jsonify({
            "success": True,
            "message": "熔断器已重置"
        })
    except Exception as e:
        logger.error(f"重置熔断器失败: {e}")
        return jsonify({"error": "重置熔断器失败"}), 500