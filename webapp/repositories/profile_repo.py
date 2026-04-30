import os
import json
import datetime

from config.settings import PROFILE_DIR
from utils.helpers import load_json_file, save_json_file

def save_profile(player_id, profile_data):
    profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
    profile_data["player_id"] = player_id
    profile_data["updated_at"] = datetime.datetime.now().isoformat()
    return save_json_file(profile_path, profile_data)

def load_profile(player_id=None):
    if player_id:
        profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
    else:
        profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    return load_json_file(profile_path)

def save_current_profile(profile_data):
    profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    return save_json_file(profile_path, profile_data)