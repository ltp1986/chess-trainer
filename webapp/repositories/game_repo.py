import os
import json
import uuid
import datetime

from config.settings import LIBRARY_DIR
from utils.helpers import load_json_file, save_json_file

def save_game(game_data):
    game_id = f"game_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    game_data["game_id"] = game_id
    
    if save_json_file(game_path, game_data):
        return game_id
    return None

def load_game(game_id):
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    return load_json_file(game_path)

def delete_game(game_id):
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    if os.path.exists(game_path):
        os.remove(game_path)
        return True
    return False

def list_games():
    games = []
    for filename in os.listdir(LIBRARY_DIR):
        if filename.endswith(".json"):
            game_id = filename[:-5]
            try:
                game = load_game(game_id)
                if game:
                    games.append({
                        "game_id": game_id,
                        "filename": game.get("filename", ""),
                        "date": game.get("date", ""),
                        "white": game.get("white", ""),
                        "black": game.get("black", ""),
                        "result": game.get("result", ""),
                        "total_mistakes": game.get("summary", {}).get("total_mistakes", 0)
                    })
            except:
                pass
    return sorted(games, key=lambda x: x.get("date", ""), reverse=True)