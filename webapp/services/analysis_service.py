import io
import chess
import chess.pgn
import chess.engine
import logging
import datetime

from config.settings import DEPTH, MOVE_TIME, MISTAKE_THRESHOLD
from engine.stockfish import get_engine, restart_engine

logger = logging.getLogger(__name__)

analysis_progress = {}

def update_analysis_progress(file_id, status, current, total, message):
    analysis_progress[file_id] = {
        "status": status,
        "current": current,
        "total": total,
        "message": message,
        "updated_at": datetime.datetime.now().isoformat()
    }

def get_analysis_progress(file_id):
    return analysis_progress.get(file_id)

def analyze_pgn(pgn_path):
    logger.info(f"开始分析PGN文件: {pgn_path}")
    
    file_content = None
    for encoding in ["utf-8", "gbk", "gb2312"]:
        try:
            with open(pgn_path, "r", encoding=encoding) as f:
                file_content = f.read()
                logger.info(f"文件读取成功，编码: {encoding}，文件大小: {len(file_content)} 字符")
                break
        except Exception as e:
            logger.warning(f"使用{encoding}编码读取失败: {str(e)}")
            continue

    if file_content is None:
        logger.error(f"文件读取失败，所有编码均不兼容: {pgn_path}")
        return None, []

    try:
        game = chess.pgn.read_game(io.StringIO(file_content))
        if not game:
            logger.warning(f"无法解析PGN文件: {pgn_path}")
            return None, []

        result = game.headers.get("Result", "*")
        white_player = game.headers.get("White", "?")
        black_player = game.headers.get("Black", "?")
        logger.info(f"棋局信息: {white_player} vs {black_player}, 结果: {result}")

        if result == "1-0":
            loser = chess.BLACK
        elif result == "0-1":
            loser = chess.WHITE
        else:
            loser = None

        board = game.board()
        eng = get_engine()
        moves = list(game.mainline_moves())
        logger.info(f"棋局共有 {len(moves)} 步")
        scores_before, scores_after, boards, bests, legal_moves_list = [], [], [board.copy()], [], []

        for i, mv in enumerate(moves):
            current_player = board.turn
            res_before = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
            score_before = 0
            if "score" in res_before:
                if current_player == chess.WHITE:
                    score_before = res_before["score"].white().score(mate_score=10000)
                else:
                    score_before = res_before["score"].black().score(mate_score=10000)
            pv = res_before.get("pv", [])
            best = pv[0] if pv else None

            scores_before.append(score_before)
            bests.append(best)
            legal_moves_list.append(list(board.legal_moves))

            board.push(mv)
            boards.append(board.copy())

            res_after = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
            score_after = 0
            if "score" in res_after:
                if current_player == chess.WHITE:
                    score_after = res_after["score"].white().score(mate_score=10000)
                else:
                    score_after = res_after["score"].black().score(mate_score=10000)
            scores_after.append(score_after)

            if i % 10 == 0:
                logger.info(f"已分析第 {i+1} 步")

        mistakes = []
        for i in range(len(scores_before)):
            if i >= len(scores_after):
                continue
            current_turn = chess.WHITE if (i % 2 == 0) else chess.BLACK

            if loser is not None and current_turn != loser:
                continue

            delta = scores_after[i] - scores_before[i]
            actual_move = moves[i]

            info = eng.analyse(boards[i], chess.engine.Limit(depth=12, time=0.2))
            pv = info.get("pv", [])
            best_move = pv[0].uci() if pv else None
            
            if best_move == actual_move.uci():
                continue

            if delta < MISTAKE_THRESHOLD:
                mistakes.append({
                    "step": i + 1,
                    "loss": abs(delta),
                    "board_idx": i,
                    "move": actual_move.uci(),
                    "best": best_move,
                    "fen": boards[i].fen(),
                    "turn": "white" if boards[i].turn == chess.WHITE else "black"
                })

        mistakes = sorted(mistakes, key=lambda x: x["step"])
        logger.info(f"分析完成，发现 {len(mistakes)} 个失误")
        return game, mistakes
    except Exception as e:
        logger.error(f"分析PGN文件时出错: {str(e)}", exc_info=True)
        return None, []

def analyze_game_for_library(pgn_content):
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_content))
        board = game.board()
        
        eng = get_engine()
        analysis = []
        mistakes = []
        
        for move_num, move in enumerate(game.mainline_moves()):
            info = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
            
            score = info.get("score")
            eval_score = 0
            if score:
                try:
                    eval_score = score.relative.score(mate_score=10000)
                except:
                    pass
            
            pv_moves = [m.uci() for m in info.get("pv", [])[:5]]
            
            analysis.append({
                "move_number": move_num + 1,
                "move": move.uci(),
                "evaluation": eval_score,
                "pv": pv_moves
            })
            
            if eval_score < MISTAKE_THRESHOLD:
                mistakes.append({
                    "move_number": move_num + 1,
                    "move": move.uci(),
                    "loss": abs(eval_score),
                    "fen": board.fen()
                })
            
            board.push(move)
        
        summary = {
            "total_mistakes": len(mistakes),
            "max_loss": max([m["loss"] for m in mistakes], default=0),
            "worst_move": mistakes[0] if mistakes else None
        }
        
        return {
            "analysis": analysis,
            "mistakes": mistakes,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"分析棋局失败: {e}")
        return None

def generate_local_analysis(fen, move_number, turn):
    try:
        board = chess.Board(fen)
    except ValueError as e:
        logger.error(f"无效的FEN字符串: {e}")
        return {
            "evaluation": "无法评估",
            "score": 0,
            "position_type": "无效局面",
            "key_tactics": [],
            "recommended_moves": [],
            "threats": [],
            "strategic_advice": "FEN格式无效，请检查输入"
        }
    
    is_white = turn == 'white'
    
    try:
        eng = get_engine()
        info = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
        
        score = info.get("score")
        eval_score = 0
        if score:
            try:
                eval_score = score.relative.score(mate_score=10000)
            except:
                pass
        
        pv_moves = [m.uci() for m in info.get("pv", [])[:3]]
        
        if eval_score > 150:
            evaluation = "白方明显优势"
        elif eval_score > 50:
            evaluation = "白方优势"
        elif eval_score > -50:
            evaluation = "均势"
        elif eval_score > -150:
            evaluation = "黑方优势"
        else:
            evaluation = "黑方明显优势"
        
        key_tactics = []
        if eval_score > 200:
            key_tactics.append({
                "name": "优势局面",
                "description": "当前局面占据明显优势，应保持压力"
            })
        
        recommended_moves = []
        for i, mv in enumerate(pv_moves):
            recommended_moves.append({
                "move": mv,
                "reason": f"推荐走法 #{i+1}"
            })
        
        position_type = "中局"
        if move_number <= 10:
            position_type = "开局"
        elif board.piece_count <= 12:
            position_type = "残局"
        
        return {
            "evaluation": evaluation,
            "score": eval_score,
            "key_tactics": key_tactics,
            "recommended_moves": recommended_moves,
            "threats": [],
            "strategic_advice": "继续保持当前策略，寻找战术机会",
            "opening_name": "未知",
            "position_type": position_type,
            "fen": fen,
            "analyzed_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"本地分析失败: {e}")
        return {
            "evaluation": "分析失败",
            "score": 0,
            "key_tactics": [],
            "recommended_moves": [],
            "threats": [],
            "strategic_advice": "无法分析当前局面",
            "opening_name": "未知",
            "position_type": "中局",
            "fen": fen,
            "analyzed_at": datetime.datetime.now().isoformat()
        }