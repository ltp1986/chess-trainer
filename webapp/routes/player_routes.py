import logging

from flask import Blueprint, jsonify, request

from repositories.player_repo import (
    save_player, load_player, delete_player, list_players,
    associate_game_to_player, remove_game_from_player
)
from repositories.game_repo import save_game, load_game
from services.analysis_service import analyze_game_for_library

logger = logging.getLogger(__name__)

player_bp = Blueprint('player', __name__)

@player_bp.route('/api/players', methods=['GET'])
def get_players():
    players = list_players()
    return jsonify({"players": players})

@player_bp.route('/api/player/<player_id>', methods=['GET'])
def get_player(player_id):
    player = load_player(player_id)
    if player:
        return jsonify(player)
    return jsonify({"error": "棋手不存在"}), 404

@player_bp.route('/api/player', methods=['POST'])
def create_player():
    data = request.json
    
    required_fields = ["name"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少必要字段: {field}"}), 400
    
    player_data = {
        "name": data.get("name"),
        "nickname": data.get("nickname", ""),
        "level": data.get("level", "L1"),
        "rating": data.get("rating", 1000),
        "email": data.get("email", ""),
        "total_games": 0,
        "win_rate": 0,
        "game_history": []
    }
    
    player_id = save_player(player_data)
    
    return jsonify({
        "success": True,
        "player_id": player_id,
        "message": "棋手创建成功"
    })

@player_bp.route('/api/player/<player_id>', methods=['PUT'])
def update_player(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    data = request.json
    
    if "name" in data:
        player["name"] = data["name"]
    if "nickname" in data:
        player["nickname"] = data["nickname"]
    if "level" in data:
        player["level"] = data["level"]
    if "rating" in data:
        player["rating"] = data["rating"]
    if "email" in data:
        player["email"] = data["email"]
    
    save_player(player)
    
    return jsonify({
        "success": True,
        "message": "棋手信息更新成功"
    })

@player_bp.route('/api/player/<player_id>', methods=['DELETE'])
def delete_player_endpoint(player_id):
    if delete_player(player_id):
        return jsonify({"success": True, "message": "棋手删除成功"})
    return jsonify({"error": "棋手不存在"}), 404

@player_bp.route('/api/player/<player_id>/add_game', methods=['POST'])
def add_game_to_player(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    data = request.json
    game_id = data.get("game_id")
    
    if not game_id:
        return jsonify({"error": "缺少game_id"}), 400
    
    if game_id not in player.get("game_history", []):
        player["game_history"].append(game_id)
    
    save_player(player)
    
    return jsonify({"success": True, "message": "棋局关联成功"})

@player_bp.route('/api/player/<player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    stats = {
        "player_id": player_id,
        "name": player.get("name"),
        "total_games": player.get("total_games", 0),
        "win_rate": player.get("win_rate", 0),
        "rating": player.get("rating", 0),
        "level": player.get("level", "L1"),
        "game_count": len(player.get("game_history", []))
    }
    
    return jsonify(stats)