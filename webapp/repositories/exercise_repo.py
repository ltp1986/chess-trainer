import os
import json
import datetime

from config.settings import EXERCISES_DIR
from utils.helpers import load_json_file, save_json_file

def save_exercises(player_id, exercises_data):
    exercises_path = os.path.join(EXERCISES_DIR, f"exercises_{player_id}.json")
    return save_json_file(exercises_path, exercises_data)

def load_exercises(player_id):
    exercises_path = os.path.join(EXERCISES_DIR, f"exercises_{player_id}.json")
    return load_json_file(exercises_path)

def update_exercise_progress(player_id, exercise_id, status):
    exercises_data = load_exercises(player_id)
    
    for ex in exercises_data.get("exercises", []):
        if ex["id"] == exercise_id:
            ex["status"] = status
            ex["attempts"] = ex.get("attempts", 0) + 1
            if status == "completed":
                ex["completed"] = True
            break
    
    return save_exercises(player_id, exercises_data)

def get_all_exercises_summary():
    all_exercises = []
    for filename in os.listdir(EXERCISES_DIR):
        if filename.endswith(".json"):
            player_id = filename.replace("exercises_", "").replace(".json", "")
            try:
                data = load_exercises(player_id)
                all_exercises.append({
                    "player_id": player_id,
                    "player_name": data.get("player_name", ""),
                    "total_exercises": data.get("total_exercises", 0),
                    "completed_count": sum(1 for e in data.get("exercises", []) if e.get("completed")),
                    "generated_at": data.get("generated_at", "")
                })
            except:
                pass
    return all_exercises