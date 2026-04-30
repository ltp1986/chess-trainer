import io
import logging
import chess.pgn

from flask import Blueprint, jsonify, request

from repositories.game_repo import save_game, load_game, delete_game, list_games
from repositories.player_repo import associate_game_to_player, remove_game_from_player
from services.analysis_service import analyze_game_for_library

logger = logging.getLogger(__name__)

game_bp = Blueprint('game', __name__)

@game_bp.route('/api/games', methods=['GET'])
def get_games():
    games = list_games()
    return jsonify({"games": games})

@game_bp.route('/api/game/<game_id>', methods=['GET'])
def get_game(game_id):
    game = load_game(game_id)
    if game:
        return jsonify(game)
    return jsonify({"error": "棋局不存在"}), 404

@game_bp.route('/api/game', methods=['POST'])
def add_game():
    data = request.json
    pgn_content = data.get('pgn_content')
    filename = data.get('filename', '')
    white_player_id = data.get('white_player_id', '')
    black_player_id = data.get('black_player_id', '')
    
    if not pgn_content:
        return jsonify({"error": "缺少PGN内容"}), 400
    
    analysis_result = analyze_game_for_library(pgn_content)
    if not analysis_result:
        return jsonify({"error": "分析失败"}), 500
    
    game = chess.pgn.read_game(io.StringIO(pgn_content))
    
    game_data = {
        "filename": filename,
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "white": game.headers.get("White", ""),
        "black": game.headers.get("Black", ""),
        "result": game.headers.get("Result", "*"),
        "pgn_content": pgn_content,
        "white_player_id": white_player_id,
        "black_player_id": black_player_id,
        **analysis_result
    }
    
    game_id = save_game(game_data)
    
    if white_player_id:
        associate_game_to_player(white_player_id, game_id)
    
    if black_player_id:
        associate_game_to_player(black_player_id, game_id)
    
    return jsonify({
        "success": True,
        "game_id": game_id,
        "message": "棋局添加成功",
        "associated_players": {
            "white": white_player_id if white_player_id else None,
            "black": black_player_id if black_player_id else None
        }
    })

@game_bp.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game_endpoint(game_id):
    if delete_game(game_id):
        return jsonify({"success": True, "message": "删除成功"})
    return jsonify({"error": "棋局不存在"}), 404

@game_bp.route('/api/game/<game_id>/associate', methods=['POST'])
def associate_game_players(game_id):
    data = request.json
    white_player_id = data.get('white_player_id', '')
    black_player_id = data.get('black_player_id', '')
    
    game = load_game(game_id)
    if not game:
        return jsonify({"error": "棋局不存在"}), 404
    
    old_white_id = game.get('white_player_id', '')
    old_black_id = game.get('black_player_id', '')
    
    if old_white_id and old_white_id != white_player_id:
        remove_game_from_player(old_white_id, game_id)
    
    if old_black_id and old_black_id != black_player_id:
        remove_game_from_player(old_black_id, game_id)
    
    game['white_player_id'] = white_player_id
    game['black_player_id'] = black_player_id
    save_game(game)
    
    if white_player_id:
        associate_game_to_player(white_player_id, game_id)
    
    if black_player_id:
        associate_game_to_player(black_player_id, game_id)
    
    return jsonify({
        "success": True,
        "message": "棋手关联更新成功",
        "associated_players": {
            "white": white_player_id if white_player_id else None,
            "black": black_player_id if black_player_id else None
        }
    })

@game_bp.route('/api/import/pgn', methods=['POST'])
def import_pgn():
    if 'file' not in request.files:
        return jsonify({"error": "缺少文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名不能为空"}), 400
    
    if file.filename.endswith('.pgn'):
        try:
            pgn_content = file.read().decode('utf-8')
            analysis_result = analyze_game_for_library(pgn_content)
            if not analysis_result:
                return jsonify({"error": "分析失败"}), 500
            
            game = chess.pgn.read_game(io.StringIO(pgn_content))
            
            white_player = game.headers.get("White", "")
            black_player = game.headers.get("Black", "")
            
            white_player_id = request.form.get('white_player_id', '')
            black_player_id = request.form.get('black_player_id', '')
            
            game_data = {
                "filename": file.filename,
                "date": datetime.datetime.now().strftime('%Y-%m-%d'),
                "white": white_player,
                "black": black_player,
                "result": game.headers.get("Result", "*"),
                "pgn_content": pgn_content,
                "white_player_id": white_player_id,
                "black_player_id": black_player_id,
                **analysis_result
            }
            
            game_id = save_game(game_data)
            
            if white_player_id:
                associate_game_to_player(white_player_id, game_id)
            
            if black_player_id:
                associate_game_to_player(black_player_id, game_id)
            
            return jsonify({
                "success": True,
                "game_id": game_id,
                "message": "PGN导入成功",
                "game_info": {
                    "white": white_player,
                    "black": black_player,
                    "result": game.headers.get("Result", "*")
                },
                "associated_players": {
                    "white": white_player_id if white_player_id else None,
                    "black": black_player_id if black_player_id else None
                }
            })
        except Exception as e:
            return jsonify({"error": f"导入失败: {str(e)}"}), 500
    else:
        return jsonify({"error": "文件格式不正确，仅支持PGN文件"}), 400

import datetime