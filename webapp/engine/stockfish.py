import chess
import chess.engine
import logging

from config.settings import DEPTH, MOVE_TIME

logger = logging.getLogger(__name__)

engine = None

def find_engine():
    for p in ["stockfish.exe", "stockfish-windows-x86-64-avx2.exe", r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"]:
        if os.path.exists(p):
            return p
    logger.error("未找到Stockfish引擎")
    raise Exception("未找到Stockfish引擎")

def get_engine():
    global engine
    if engine is None:
        engine_path = find_engine()
        logger.info(f"初始化Stockfish引擎: {engine_path}")
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        engine.configure({"Threads": 4, "Hash": 512})
        logger.info("Stockfish引擎初始化成功")
    return engine

def restart_engine():
    global engine
    logger.warning("尝试重启Stockfish引擎")
    if engine is not None:
        try:
            engine.quit()
        except:
            pass
        engine = None
    return get_engine()

def analyze_position(fen, depth=DEPTH, time=MOVE_TIME):
    try:
        board = chess.Board(fen)
        eng = get_engine()
        info = eng.analyse(board, chess.engine.Limit(depth=depth, time=time))
        return info
    except Exception as e:
        logger.error(f"分析位置失败: {e}")
        return None

def get_best_move(fen, depth=DEPTH, time=MOVE_TIME):
    try:
        board = chess.Board(fen)
        eng = get_engine()
        info = eng.analyse(board, chess.engine.Limit(depth=depth, time=time))
        pv = info.get("pv", [])
        if pv:
            return pv[0].uci()
        return None
    except Exception as e:
        logger.error(f"获取最佳走法失败: {e}")
        return None

def evaluate_position(fen, depth=DEPTH, time=MOVE_TIME):
    try:
        board = chess.Board(fen)
        eng = get_engine()
        info = eng.analyse(board, chess.engine.Limit(depth=depth, time=time))
        score = info.get("score")
        if score:
            return score.relative.score(mate_score=10000)
        return 0
    except Exception as e:
        logger.error(f"评估位置失败: {e}")
        return 0

def get_legal_moves(fen):
    try:
        board = chess.Board(fen)
        return [move.uci() for move in board.legal_moves]
    except Exception as e:
        logger.error(f"获取合法走法失败: {e}")
        return []

def check_move_valid(fen, move_uci):
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        return move in board.legal_moves
    except Exception as e:
        logger.error(f"验证走法失败: {e}")
        return False

import os