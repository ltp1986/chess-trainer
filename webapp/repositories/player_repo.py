import os
import json
import uuid
import datetime

from config.settings import PLAYERS_DIR
from utils.helpers import load_json_file, save_json_file

def save_player(player_data):
    player_id = player_data.get("player_id", f"player_{uuid.uuid4().hex[:8]}")
    player_path = os.path.join(PLAYERS_DIR, f"{player_id}.json")
    
    player_data["player_id"] = player_id
    player_data["updated_at"] = datetime.datetime.now().isoformat()
    
    if "created_at" not in player_data:
        player_data["created_at"] = player_data["updated_at"]
    
    if save_json_file(player_path, player_data):
        return player_id
    return None

def load_player(player_id):
    player_path = os.path.join(PLAYERS_DIR, f"{player_id}.json")
    return load_json_file(player_path)

def delete_player(player_id):
    player_path = os.path.join(PLAYERS_DIR, f"{player_id}.json")
    if os.path.exists(player_path):
        os.remove(player_path)
        return True
    return False

def list_players():
    players = []
    for filename in os.listdir(PLAYERS_DIR):
        if filename.endswith(".json"):
            player_id = filename[:-5]
            try:
                player = load_player(player_id)
                if player:
                    players.append({
                        "player_id": player_id,
                        "name": player.get("name", ""),
                        "nickname": player.get("nickname", ""),
                        "level": player.get("level", "L1"),
                        "rating": player.get("rating", 0),
                        "total_games": player.get("total_games", 0),
                        "win_rate": player.get("win_rate", 0),
                        "created_at": player.get("created_at", "")
                    })
            except:
                pass
    return sorted(players, key=lambda x: x.get("created_at", ""), reverse=True)

def find_player_by_name(name):
    players = list_players()
    for player in players:
        if player.get("name", "").strip() == name.strip():
            return player
    return None

def associate_game_to_player(player_id, game_id):
    player = load_player(player_id)
    if player:
        if "game_history" not in player:
            player["game_history"] = []
        if game_id not in player["game_history"]:
            player["game_history"].append(game_id)
            player["total_games"] = len(player["game_history"])
            save_player(player)
            return True
    return False

def remove_game_from_player(player_id, game_id):
    player = load_player(player_id)
    if player and player.get('game_history'):
        player['game_history'] = [g for g in player['game_history'] if g != game_id]
        player['total_games'] = len(player['game_history'])
        save_player(player)
        return True
    return False