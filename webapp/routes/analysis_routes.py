import os
import logging

from flask import Blueprint, jsonify, request
from urllib.parse import unquote

from config.settings import WATCH_DIR, STATUS_FILE, DIFFICULTY_THRESHOLD, MAX_DEMONSTRATION_MISTAKES
from services.analysis_service import analyze_pgn, update_analysis_progress, get_analysis_progress
from services.tactics_service import generate_mistake_explanation, get_tactic_explanation
from utils.helpers import format_pgn, load_json_file

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

@analysis_bp.route('/js/<path:filename>')
def serve_js(filename):
    from flask import send_from_directory
    return send_from_directory('js', filename)

@analysis_bp.route('/api/pgn_files')
def get_pgn_files():
    logger.info("获取PGN文件列表")
    if not os.path.exists(WATCH_DIR):
        logger.warning(f"PGN目录不存在: {WATCH_DIR}")
        return jsonify({"files": [], "watch_dir": WATCH_DIR})
    files = [f for f in os.listdir(WATCH_DIR) if f.endswith('.pgn')]
    logger.info(f"找到 {len(files)} 个PGN文件: {files}")
    return jsonify({"files": files, "watch_dir": WATCH_DIR})

@analysis_bp.route('/api/config/watch_dir', methods=['GET'])
def get_watch_dir():
    logger.info(f"获取当前PGN目录: {WATCH_DIR}")
    return jsonify({"watch_dir": WATCH_DIR})

@analysis_bp.route('/api/config/watch_dir', methods=['POST'])
def set_watch_dir():
    global WATCH_DIR
    data = request.json
    new_dir = data.get('watch_dir', '')
    
    if not new_dir:
        return jsonify({"error": "目录路径不能为空"}), 400
    
    if not os.path.isdir(new_dir):
        return jsonify({"error": "指定的路径不是有效的目录"}), 400
    
    from config.settings import save_config, load_config
    config = load_config()
    config['watch_dir'] = new_dir
    save_config(config)
    WATCH_DIR = new_dir
    
    logger.info(f"PGN目录已更新为: {WATCH_DIR}")
    return jsonify({"success": True, "watch_dir": WATCH_DIR, "message": "PGN目录设置成功"})

@analysis_bp.route('/api/analysis/progress/<file_id>', methods=['GET'])
def api_get_analysis_progress(file_id):
    progress = get_analysis_progress(file_id)
    
    if not progress:
        return jsonify({
            "status": "not_found",
            "message": "未找到分析任务"
        })
    
    total = progress["total"] if progress["total"] > 0 else 1
    progress_percent = round(progress["current"] / total * 100, 2)
    
    return jsonify({
        "status": progress["status"],
        "progress": progress_percent,
        "current_step": progress["current"],
        "total_steps": progress["total"],
        "message": progress["message"],
        "updated_at": progress["updated_at"]
    })

@analysis_bp.route('/api/analysis/cancel/<file_id>', methods=['POST'])
def api_cancel_analysis(file_id):
    if file_id in analysis_progress:
        analysis_progress[file_id]["status"] = "cancelled"
        analysis_progress[file_id]["message"] = "分析已取消"
        return jsonify({"success": True, "message": "分析已取消"})
    return jsonify({"success": False, "message": "未找到分析任务"})

@analysis_bp.route('/api/analyze/<filename>')
def analyze_file(filename):
    filename = unquote(filename)
    filename = filename.split(':')[0]
    logger.info(f"清理后的文件名: {filename}")
    
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in DIFFICULTY_THRESHOLD:
        difficulty = 'medium'
    
    pgn_path = os.path.join(WATCH_DIR, filename)
    
    if not os.path.exists(pgn_path):
        logger.error(f"文件不存在: {pgn_path}")
        return jsonify({"error": f"文件不存在: {filename}"}), 404
    if os.path.getsize(pgn_path) == 0:
        logger.error(f"文件为空: {pgn_path}")
        return jsonify({"error": "PGN文件为空，无法解析"}), 400

    status = load_json_file(STATUS_FILE)
    file_status = status.get(filename, {})
    status_value = file_status.get("status")
    
    if status_value == "processing":
        logger.info(f"文件 {filename} 正在处理中")
        return jsonify({
            "status": "processing",
            "message": "文件正在处理中，请稍后再试"
        })

    update_analysis_progress(filename, "processing", 0, 100, "开始分析...")
    
    try:
        game, mistakes = analyze_pgn(pgn_path)
        
        if not game:
            logger.error(f"解析PGN文件失败: {filename}")
            return jsonify({"error": "PGN文件解析失败，请检查文件格式是否正确"}), 400

        min_loss = DIFFICULTY_THRESHOLD[difficulty]
        filtered_mistakes = [m for m in mistakes if m["loss"] >= min_loss]

        mistakes_for_frontend = []
        for m in filtered_mistakes:
            cause, idea = generate_mistake_explanation(m["fen"], m["move"], m["best"], m["loss"])
            tactic_exp = get_tactic_explanation(m["fen"], m["move"], m["best"], m["loss"])
            mistakes_for_frontend.append({
                "step": m["step"],
                "loss": m["loss"],
                "fen": m["fen"],
                "turn": m["turn"],
                "actual_move": m["move"],
                "best_move": m["best"],
                "cause": cause,
                "idea": idea,
                "tactic_exp": tactic_exp
            })

        exercises = []
        for i, e in enumerate(filtered_mistakes, 1):
            exercises.append({
                "id": i,
                "step": e["step"],
                "fen": e["fen"],
                "turn": e["turn"],
                "best_move": e["best"],
                "loss": e["loss"],
                "actual_move": e["move"],
                "description": f"第{e['step']}步 - 找出最佳着法"
            })

        logger.info(f"生成 {len(exercises)} 个习题（难度: {difficulty}，筛选阈值: {min_loss}cp）")
        return jsonify({
            "status": "completed",
            "filename": filename,
            "white": game.headers.get("White", "?"),
            "black": game.headers.get("Black", "?"),
            "result": game.headers.get("Result", "*"),
            "difficulty": difficulty,
            "total_mistakes": len(mistakes),
            "filtered_mistakes": len(filtered_mistakes),
            "mistakes": mistakes_for_frontend,
            "exercises": exercises
        })
    except Exception as e:
        logger.error(f"分析PGN文件时出错: {str(e)}", exc_info=True)
        return jsonify({"error": f"分析失败: {str(e)}"}), 500

@analysis_bp.route('/api/check_move', methods=['POST'])
def check_move():
    from engine.stockfish import get_engine, restart_engine
    
    data = request.json
    fen = data.get('fen')
    user_move = data.get('move')
    expected_best = data.get('expected_best')
    logger.info('检查用户着法', extra={'user_move': user_move, 'expected_best': expected_best})

    if not fen or not user_move:
        logger.warning('缺少参数', extra={'fen': fen, 'user_move': user_move})
        return jsonify({"error": "缺少参数"}), 400

    import chess
    board = chess.Board(fen)

    try:
        move = chess.Move.from_uci(user_move)
        if move not in board.legal_moves:
            logger.warning('非法着法', extra={'user_move': user_move, 'legal_moves': [m.uci() for m in board.legal_moves], 'turn': 'white' if board.turn == chess.WHITE else 'black'})
            return jsonify({
                "valid": False,
                "correct": False,
                "message": "非法着法！"
            })
    except Exception as e:
        logger.error('着法格式错误', extra={'user_move': user_move, 'error': str(e), 'turn': 'white' if board.turn == chess.WHITE else 'black'})
        return jsonify({
            "valid": False,
            "correct": False,
            "message": "着法格式错误"
        })

    try:
        eng = get_engine()
    except:
        eng = restart_engine()

    current_player = board.turn
    
    from config.settings import DEPTH, MOVE_TIME, MISTAKE_THRESHOLD
    res_before = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
    score_before = 0
    if "score" in res_before:
        if current_player == chess.WHITE:
            score_before = res_before["score"].white().score(mate_score=10000)
        else:
            score_before = res_before["score"].black().score(mate_score=10000)

    board.push(move)
    res_after = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
    score_after = 0
    if "score" in res_after:
        if current_player == chess.WHITE:
            score_after = res_after["score"].white().score(mate_score=10000)
        else:
            score_after = res_after["score"].black().score(mate_score=10000)

    delta = score_after - score_before
    is_mistake = delta < MISTAKE_THRESHOLD

    best_move = expected_best
    if not best_move:
        pv = res_before.get("pv", [])
        if pv:
            best_move = pv[0].uci()

    is_correct = (user_move == best_move)

    if is_correct:
        message = "✅ 正确！这就是最佳着法。"
        feedback_type = "success"
    else:
        if is_mistake:
            message = f"❌ 失误！这步棋导致局面失分约{abs(delta):.0f}分。"
        else:
            message = f"⚠️ 不够精确。虽然不是明显失误，但还有更好的选择。"
        feedback_type = "error" if is_mistake else "warning"

    result = {
        "valid": True,
        "correct": is_correct,
        "message": message,
        "feedback_type": feedback_type,
        "user_move": user_move,
        "best_move": best_move,
        "delta": delta,
        "is_mistake": is_mistake,
        "score_before": score_before,
        "score_after": score_after
    }
    logger.debug('着法验证结果', extra=result)
    return jsonify(result)

@analysis_bp.route('/api/legal_moves', methods=['POST'])
def get_legal_moves():
    data = request.json
    fen = data.get('fen')
    square = data.get('square')

    if not fen or not square:
        return jsonify({"error": "缺少参数"}), 400

    try:
        import chess
        board = chess.Board(fen)
        from_sq = chess.parse_square(square)
        legal_targets = []
        for move in board.legal_moves:
            if move.from_square == from_sq:
                legal_targets.append(chess.square_name(move.to_square))

        return jsonify({
            "square": square,
            "legal_moves": legal_targets
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@analysis_bp.route('/api/hint', methods=['POST'])
def get_hint():
    from engine.stockfish import get_engine, restart_engine
    
    data = request.json
    fen = data.get('fen')

    if not fen:
        return jsonify({"error": "缺少FEN"}), 400

    try:
        import chess
        board = chess.Board(fen)
        eng = get_engine()
    except:
        eng = restart_engine()
        board = chess.Board(fen)

    from config.settings import DEPTH, MOVE_TIME
    res = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
    pv = res.get("pv", [])

    if pv:
        best_move = pv[0]
        from_sq = chess.square_name(best_move.from_square)
        hint = f"考虑从 {from_sq} 出发的着法..."
        return jsonify({
            "hint": hint,
            "from_square": from_sq,
            "piece_type": chess.piece_name(board.piece_at(best_move.from_square).piece_type) if board.piece_at(best_move.from_square) else "未知"
        })

    return jsonify({"hint": "暂无提示"})

@analysis_bp.route('/api/best_move', methods=['POST'])
def get_best_move():
    from engine.stockfish import get_engine, restart_engine
    
    data = request.json
    fen = data.get('fen')

    if not fen:
        return jsonify({"error": "缺少FEN"}), 400

    try:
        import chess
        board = chess.Board(fen)
        eng = get_engine()
    except:
        eng = restart_engine()
        board = chess.Board(fen)

    from config.settings import DEPTH, MOVE_TIME
    res = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
    pv = res.get("pv", [])

    if pv:
        best_move = pv[0]
        return jsonify({
            "best_move": best_move.uci(),
            "from_square": chess.square_name(best_move.from_square),
            "to_square": chess.square_name(best_move.to_square)
        })

    return jsonify({"best_move": None})

@analysis_bp.route('/api/report/<filename>')
def get_report(filename):
    filename = unquote(filename)
    filename = filename.split(':')[0]
    logger.info(f"获取复盘数据: {filename}")
    
    pgn_path = os.path.join(WATCH_DIR, filename)
    
    if not os.path.exists(pgn_path):
        logger.error(f"文件不存在: {pgn_path}")
        return jsonify({"error": f"文件不存在: {filename}"}), 404
    if os.path.getsize(pgn_path) == 0:
        logger.error(f"文件为空: {pgn_path}")
        return jsonify({"error": "PGN文件为空，无法解析"}), 400

    game, mistakes = analyze_pgn(pgn_path)
    if not game:
        logger.error(f"解析PGN文件失败: {filename}")
        return jsonify({"error": "PGN文件解析失败"}), 400

    import chess
    board = game.board()
    all_moves = list(game.mainline_moves())
    
    mistakes_with_details = []
    for m in mistakes:
        cause, idea = generate_mistake_explanation(m["fen"], m["move"], m["best"], m["loss"])
        tactic_exp = get_tactic_explanation(m["fen"], m["move"], m["best"], m["loss"])
        mistakes_with_details.append({
            "step": m["step"],
            "loss": m["loss"],
            "fen": m["fen"],
            "turn": m["turn"],
            "actual_move": m["move"],
            "best_move": m["best"],
            "cause": cause,
            "idea": idea,
            "tactic_exp": tactic_exp
        })

    mistakes_sorted = sorted(mistakes_with_details, key=lambda x: -x["loss"])
    
    demonstration_mistakes = mistakes_sorted[:MAX_DEMONSTRATION_MISTAKES]
    remaining_mistakes = []
    for i, m in enumerate(mistakes_sorted[MAX_DEMONSTRATION_MISTAKES:], 1):
        remaining_mistakes.append({
            "id": MAX_DEMONSTRATION_MISTAKES + i,
            "step": m["step"],
            "loss": m["loss"],
            "cause": m["cause"],
            "idea": m["idea"]
        })

    for i, m in enumerate(demonstration_mistakes, 1):
        m["id"] = i

    result = {
        "status": "completed",
        "filename": filename,
        "white": game.headers.get("White", "?"),
        "black": game.headers.get("Black", "?"),
        "result": game.headers.get("Result", "*"),
        "full_pgn": format_pgn(all_moves),
        "total_mistakes": len(mistakes),
        "demonstration_mistakes": demonstration_mistakes,
        "remaining_mistakes": remaining_mistakes
    }

    logger.info(f"返回复盘数据: {len(demonstration_mistakes)} 条演示, {len(remaining_mistakes)} 条文字描述")
    return jsonify(result)