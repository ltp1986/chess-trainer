import datetime
import logging

from repositories.game_repo import load_game
from repositories.exercise_repo import save_exercises, load_exercises
from engine.stockfish import get_best_move

logger = logging.getLogger(__name__)

def generate_player_exercises(player_id, player_name, game_history):
    exercises = []
    
    if game_history:
        all_mistakes = []
        for game_id in game_history[:5]:
            game = load_game(game_id)
            if game:
                mistakes = game.get("mistakes", [])
                for mistake in mistakes:
                    all_mistakes.append({
                        "game_id": game_id,
                        "filename": game.get("filename", ""),
                        **mistake
                    })
        
        all_mistakes.sort(key=lambda x: -x.get("loss", 0))
        
        for i, mistake in enumerate(all_mistakes[:10], 1):
            best_move = mistake.get("best", "")
            if not best_move and mistake.get("fen"):
                best_move = get_best_move(mistake["fen"]) or ""
            
            exercises.append({
                "id": i,
                "game_id": mistake["game_id"],
                "filename": mistake["filename"],
                "move_number": mistake.get("move_number", 0),
                "loss": mistake.get("loss", 0),
                "fen": mistake.get("fen", ""),
                "actual_move": mistake.get("move", ""),
                "best_move": best_move,
                "status": "pending",
                "attempts": 0,
                "completed": False
            })
    else:
        exercises = generate_mock_exercises(player_id)
    
    exercises_data = {
        "player_id": player_id,
        "player_name": player_name,
        "exercises": exercises,
        "generated_at": datetime.datetime.now().isoformat(),
        "total_exercises": len(exercises)
    }
    
    save_exercises(player_id, exercises_data)
    
    return exercises_data

def generate_mock_exercises(player_id):
    exercises = [
        {
            "id": 1,
            "game_id": "game_mock_001",
            "filename": "mock_game_1.pgn",
            "move_number": 12,
            "loss": 320,
            "fen": "r1bqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            "actual_move": "e5",
            "best_move": "d6",
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "tactical",
            "description": "漏看对手的将军威胁"
        },
        {
            "id": 2,
            "game_id": "game_mock_002",
            "filename": "mock_game_2.pgn",
            "move_number": 18,
            "loss": 285,
            "fen": "r1bq1rk1/ppp2ppp/2n5/2b1p3/4P3/1QN2N2/PPP2PPP/R1B1KB1R w KQ - 0 10",
            "actual_move": "Nc3",
            "best_move": "Bxc6",
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "strategic",
            "description": "兵结构受损"
        },
        {
            "id": 3,
            "game_id": "game_mock_003",
            "filename": "mock_game_3.pgn",
            "move_number": 8,
            "loss": 210,
            "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3",
            "actual_move": "Nf3",
            "best_move": "exd4",
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "opening",
            "description": "开局准备不足"
        },
        {
            "id": 4,
            "game_id": "game_mock_004",
            "filename": "mock_game_4.pgn",
            "move_number": 45,
            "loss": 185,
            "fen": "8/8/8/8/8/8/PPPPPPPP/RNBQKBNR b - - 0 1",
            "actual_move": "Kg7",
            "best_move": "d5",
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "endgame",
            "description": "残局关键着法错误"
        },
        {
            "id": 5,
            "game_id": "game_mock_005",
            "filename": "mock_game_5.pgn",
            "move_number": 22,
            "loss": 160,
            "fen": "r1bqk2r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPP1PPPP/R1BQK2R b KQkq - 0 11",
            "actual_move": "d5",
            "best_move": "c5",
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "tactical",
            "description": "计算深度不足"
        }
    ]
    return exercises