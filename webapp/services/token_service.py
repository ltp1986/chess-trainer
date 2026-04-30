import json
import datetime
import os
import logging

from config.settings import TOKEN_USAGE_FILE, TOKEN_ALERTS_FILE

logger = logging.getLogger(__name__)

class TokenMonitor:
    def __init__(self):
        self.config = {
            "daily_limit": 100000,
            "monthly_limit": 2000000,
            "rpm_limit": 60,
            "daily_warning": 0.8,
            "daily_critical": 0.95,
            "monthly_warning": 0.7,
            "monthly_critical": 0.9
        }
    
    def load_usage(self):
        if os.path.exists(TOKEN_USAGE_FILE):
            try:
                with open(TOKEN_USAGE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_calls": 0,
            "total_tokens": 0,
            "last_updated": datetime.datetime.now().isoformat(),
            "daily": {},
            "rpm": {}
        }
    
    def save_usage(self, usage):
        os.makedirs(os.path.dirname(TOKEN_USAGE_FILE), exist_ok=True)
        with open(TOKEN_USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)
    
    def clean_expired_rpm(self, usage):
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(minutes=5)
        usage["rpm"] = {
            k: v for k, v in usage["rpm"].items()
            if datetime.datetime.strptime(k, "%Y-%m-%d %H:%M") >= cutoff
        }
    
    def get_current_rpm(self, usage):
        now = datetime.datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        return usage["rpm"].get(current_minute, 0)
    
    def record_api_call(self, tokens_used=0, call_type="chat"):
        usage = self.load_usage()
        now = datetime.datetime.now()
        
        usage["total_calls"] += 1
        usage["total_tokens"] += tokens_used
        usage["last_updated"] = now.isoformat()
        
        day_key = now.strftime("%Y-%m-%d")
        if day_key not in usage["daily"]:
            usage["daily"][day_key] = {"calls": 0, "tokens": 0}
        usage["daily"][day_key]["calls"] += 1
        usage["daily"][day_key]["tokens"] += tokens_used
        
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        if minute_key not in usage["rpm"]:
            usage["rpm"] = {}
        usage["rpm"][minute_key] = usage["rpm"].get(minute_key, 0) + 1
        
        self.clean_expired_rpm(usage)
        self.save_usage(usage)
        
        return self.check_thresholds(usage)
    
    def check_thresholds(self, usage):
        day_key = datetime.datetime.now().strftime("%Y-%m-%d")
        day_usage = usage["daily"].get(day_key, {"calls": 0, "tokens": 0})
        
        daily_rate = day_usage["tokens"] / self.config["daily_limit"]
        month_key = datetime.datetime.now().strftime("%Y-%m")
        month_tokens = 0
        for date, d in usage["daily"].items():
            if date.startswith(month_key) and isinstance(d, dict) and "tokens" in d:
                month_tokens += d["tokens"]
        month_rate = month_tokens / self.config["monthly_limit"]
        
        alerts = []
        if daily_rate >= self.config["daily_critical"]:
            alerts.append({
                "level": "critical",
                "type": "daily_limit",
                "message": "🚨 今日API使用量已达到95%上限，即将强制断开",
                "current": day_usage["tokens"],
                "limit": self.config["daily_limit"],
                "remaining": self.config["daily_limit"] - day_usage["tokens"]
            })
        elif daily_rate >= self.config["daily_warning"]:
            alerts.append({
                "level": "warning",
                "type": "daily_limit",
                "message": "⚠️ 今日API使用量已达80%，请注意控制使用",
                "current": day_usage["tokens"],
                "limit": self.config["daily_limit"],
                "remaining": self.config["daily_limit"] - day_usage["tokens"]
            })
        
        if month_rate >= self.config["monthly_critical"]:
            alerts.append({
                "level": "critical",
                "type": "monthly_limit",
                "message": "🚨 本月API使用量已达到90%上限",
                "current": month_tokens,
                "limit": self.config["monthly_limit"]
            })
        elif month_rate >= self.config["monthly_warning"]:
            alerts.append({
                "level": "warning",
                "type": "monthly_limit",
                "message": "⚠️ 本月API使用量已达70%",
                "current": month_tokens,
                "limit": self.config["monthly_limit"]
            })
        
        current_rpm = self.get_current_rpm(usage)
        if current_rpm >= self.config["rpm_limit"] * 0.9:
            alerts.append({
                "level": "warning" if current_rpm < self.config["rpm_limit"] else "critical",
                "type": "rpm_limit",
                "message": f"⚠️ 当前请求速率：{current_rpm}/min",
                "current": current_rpm,
                "limit": self.config["rpm_limit"]
            })
        
        for alert in alerts:
            self.send_alert(alert)
        
        return alerts
    
    def send_alert(self, alert):
        messages = []
        if alert["level"] == "critical":
            messages.append("🚨 【紧急】豆包API使用量告警")
        elif alert["level"] == "warning":
            messages.append("⚠️ 【警告】豆包API使用量预警")
        
        messages.append(f"类型：{alert['type']}")
        messages.append(f"信息：{alert['message']}")
        
        logger.warning("\n".join(messages))
        
        alerts = []
        if os.path.exists(TOKEN_ALERTS_FILE):
            try:
                with open(TOKEN_ALERTS_FILE, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            except:
                pass
        
        alerts.append({
            **alert,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        alerts = alerts[-10:]
        
        os.makedirs(os.path.dirname(TOKEN_ALERTS_FILE), exist_ok=True)
        with open(TOKEN_ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)
    
    def get_usage_stats(self):
        usage = self.load_usage()
        now = datetime.datetime.now()
        day_key = now.strftime("%Y-%m-%d")
        day_usage = usage["daily"].get(day_key, {"calls": 0, "tokens": 0})
        
        month_tokens = 0
        for date, data in usage["daily"].items():
            if date.startswith(now.strftime("%Y-%m")):
                month_tokens += data.get("tokens", 0)
        
        daily_rate = day_usage["tokens"] / self.config["daily_limit"]
        month_rate = month_tokens / self.config["monthly_limit"]
        
        status = "normal"
        if daily_rate >= 0.95:
            status = "critical"
        elif daily_rate >= 0.80:
            status = "warning"
        elif daily_rate >= 0.70:
            status = "notice"
        
        return {
            "status": status,
            "daily_usage": day_usage["tokens"],
            "daily_limit": self.config["daily_limit"],
            "daily_rate": round(daily_rate * 100, 1),
            "monthly_usage": month_tokens,
            "monthly_limit": self.config["monthly_limit"],
            "monthly_rate": round(month_rate * 100, 1),
            "total_calls": usage["total_calls"],
            "total_tokens": usage["total_tokens"],
            "current_rpm": self.get_current_rpm(usage),
            "rpm_limit": self.config["rpm_limit"],
            "last_updated": usage["last_updated"]
        }

class TokenProtection:
    def __init__(self):
        self.protection_config = {
            "warning_threshold": 0.8,
            "critical_threshold": 0.95,
            "rate_limit_delay": 2.0,
            "max_retries": 3,
            "circuit_breaker_timeout": 300
        }
        self.circuit_breaker_active = False
        self.circuit_breaker_endtime = None
    
    def should_allow_request(self):
        if self.circuit_breaker_active:
            if datetime.datetime.now() < self.circuit_breaker_endtime:
                return False, {
                    "blocked": True,
                    "reason": "circuit_breaker",
                    "message": "🚨 熔断保护已启用，请稍后再试",
                    "retry_after": (self.circuit_breaker_endtime - datetime.datetime.now()).seconds
                }
            else:
                self.circuit_breaker_active = False
        
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        if stats["status"] == "critical":
            self.activate_circuit_breaker()
            return False, {
                "blocked": True,
                "reason": "daily_limit",
                "message": "🚨 API配额已用尽，已自动切换到本地模式",
                "switch_to_local": True
            }
        
        if stats["current_rpm"] >= stats["rpm_limit"]:
            return False, {
                "blocked": True,
                "reason": "rate_limit",
                "message": f"请求过于频繁，请等待{self.protection_config['rate_limit_delay']}秒后重试",
                "retry_after": self.protection_config["rate_limit_delay"]
            }
        
        return True, {}
    
    def activate_circuit_breaker(self):
        self.circuit_breaker_active = True
        self.circuit_breaker_endtime = datetime.datetime.now() + datetime.timedelta(
            seconds=self.protection_config["circuit_breaker_timeout"]
        )
        logger.warning("🔥 豆包API熔断保护已激活，切换到本地模式")
    
    def get_protection_status(self):
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        return {
            **stats,
            "circuit_breaker_active": self.circuit_breaker_active,
            "circuit_breaker_resets_at": self.circuit_breaker_endtime.isoformat() if self.circuit_breaker_active else None
        }