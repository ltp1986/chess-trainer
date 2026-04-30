import os
import json
import datetime

DEFAULT_WATCH_DIR = r"D:\Chess_PGN_Receive"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "app_config.json")

DEPTH = 20
MOVE_TIME = 3.0
MISTAKE_THRESHOLD = -100

DIFFICULTY_THRESHOLD = {
    "easy": 100,
    "medium": 150,
    "hard": 250
}

MAX_DEMONSTRATION_MISTAKES = 5

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_SECRET_KEY = os.environ.get("DOUBAO_SECRET_KEY", "")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
LIBRARY_DIR = os.path.join(OUTPUT_DIR, "library")
PROFILE_DIR = os.path.join(OUTPUT_DIR, "profiles")
PLAN_DIR = os.path.join(OUTPUT_DIR, "plans")
PLAYERS_DIR = os.path.join(OUTPUT_DIR, "players")
EXERCISES_DIR = os.path.join(OUTPUT_DIR, "exercises")

STATUS_FILE = os.path.join(OUTPUT_DIR, "processing_status.json")
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "learning_progress.json")
TOKEN_USAGE_FILE = os.path.join(OUTPUT_DIR, "token_usage.json")
TOKEN_ALERTS_FILE = os.path.join(OUTPUT_DIR, "token_alerts.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"watch_dir": DEFAULT_WATCH_DIR}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()
WATCH_DIR = config.get("watch_dir", DEFAULT_WATCH_DIR)

def init_directories():
    directories = [
        WATCH_DIR,
        OUTPUT_DIR,
        LIBRARY_DIR,
        PROFILE_DIR,
        PLAN_DIR,
        PLAYERS_DIR,
        EXERCISES_DIR
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)