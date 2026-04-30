import os
import json
import datetime

from config.settings import PLAN_DIR
from utils.helpers import load_json_file, save_json_file

def save_plan(plan_data):
    plan_id = plan_data.get("plan_id", f"plan_{datetime.datetime.now().strftime('%Y%m%d')}")
    plan_data["plan_id"] = plan_id
    plan_data["generated_at"] = datetime.datetime.now().isoformat()
    
    plan_path = os.path.join(PLAN_DIR, f"{plan_id}.json")
    if save_json_file(plan_path, plan_data):
        return plan_id
    return None

def load_plan(plan_id=None):
    if plan_id:
        plan_path = os.path.join(PLAN_DIR, f"{plan_id}.json")
    else:
        plan_path = os.path.join(PLAN_DIR, "current_plan.json")
    return load_json_file(plan_path)

def save_current_plan(plan_data):
    plan_path = os.path.join(PLAN_DIR, "current_plan.json")
    return save_json_file(plan_path, plan_data)