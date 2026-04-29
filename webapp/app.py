import os
import sys
import json
import datetime
import chess
import chess.pgn
import chess.engine
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from urllib.parse import unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from mock_data import (
    generate_mock_profile,
    generate_mock_mistakes,
    generate_mock_training_plan,
    generate_mock_progress,
    generate_mock_achievements,
    generate_mock_reminders
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('chess_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

app.logger.setLevel(logging.INFO)
for handler in logging.getLogger().handlers:
    app.logger.addHandler(handler)

@app.before_request
def log_request():
    if request.path.startswith('/api/'):
        try:
            json_data = request.get_json(silent=True)
            logger.info(f"收到API请求: {request.method} {request.path}", extra={
                'method': request.method,
                'path': request.path,
                'args': request.args.to_dict(),
                'json': json_data
            })
        except Exception as e:
            logger.info(f"收到API请求: {request.method} {request.path}")

@app.after_request
def log_response(response):
    if request.path.startswith('/api/'):
        logger.info(f"API响应: {request.method} {request.path} -> {response.status_code}")
    return response

DEFAULT_WATCH_DIR = r"D:\Chess_PGN_Receive"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "app_config.json")

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
WATCH = config.get("watch_dir", DEFAULT_WATCH_DIR)
OUT = os.path.join(os.path.dirname(__file__), "output")
STATUS_FILE = os.path.join(OUT, "processing_status.json")
PROGRESS_FILE = os.path.join(OUT, "learning_progress.json")
DEPTH = 20
MOVE_TIME = 3.0
MISTAKE = -100

DIFFICULTY_THRESHOLD = {
    "easy": 100,
    "medium": 150,
    "hard": 250
}

MAX_DEMONSTRATION_MISTAKES = 5

engine = None

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

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def find_engine():
    for p in ["stockfish.exe", "stockfish-windows-x86-64-avx2.exe", r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"]:
        if os.path.exists(p):
            return p
    logger.error("未找到Stockfish引擎")
    raise Exception("未找到Stockfish引擎")

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_progress(data):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"保存进度失败: {str(e)}")
        return False

def analyze_pgn(pgn_path):
    logger.info(f"开始分析PGN文件: {pgn_path}")
    
    # 修复：兼容Windows多种编码读取PGN
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
        import io
        game = chess.pgn.read_game(io.StringIO(file_content))
        if not game:
            logger.warning(f"无法解析PGN文件: {pgn_path}")
            return None, []

        result = game.headers.get("Result", "*")
        white_player = game.headers.get("White", "?")
        black_player = game.headers.get("Black", "?")
        logger.info(f"棋局信息: {white_player} vs {black_player}, 结果: {result}")

        # 正确识别败方
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

            # 安全获取pv键，避免KeyError
            info = eng.analyse(boards[i], chess.engine.Limit(depth=12, time=0.2))
            pv = info.get("pv", [])
            best_move = pv[0].uci() if pv else None
            
            # 如果玩家走的就是最佳着法，跳过（不是失误）
            if best_move == actual_move.uci():
                continue

            if delta < MISTAKE:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/api/pgn_files')
def get_pgn_files():
    logger.info("获取PGN文件列表")
    if not os.path.exists(WATCH):
        logger.warning(f"PGN目录不存在: {WATCH}")
        return jsonify({"files": [], "watch_dir": WATCH})
    files = [f for f in os.listdir(WATCH) if f.endswith('.pgn')]
    logger.info(f"找到 {len(files)} 个PGN文件: {files}")
    return jsonify({"files": files, "watch_dir": WATCH})

@app.route('/api/config/watch_dir', methods=['GET'])
def get_watch_dir():
    logger.info(f"获取当前PGN目录: {WATCH}")
    return jsonify({"watch_dir": WATCH})

@app.route('/api/config/watch_dir', methods=['POST'])
def set_watch_dir():
    global WATCH
    data = request.json
    new_dir = data.get('watch_dir', '')
    
    if not new_dir:
        return jsonify({"error": "目录路径不能为空"}), 400
    
    if not os.path.isdir(new_dir):
        return jsonify({"error": "指定的路径不是有效的目录"}), 400
    
    config = load_config()
    config['watch_dir'] = new_dir
    save_config(config)
    WATCH = new_dir
    
    logger.info(f"PGN目录已更新为: {WATCH}")
    return jsonify({"success": True, "watch_dir": WATCH, "message": "PGN目录设置成功"})

@app.route('/api/analysis/progress/<file_id>', methods=['GET'])
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

@app.route('/api/analysis/cancel/<file_id>', methods=['POST'])
def api_cancel_analysis(file_id):
    if file_id in analysis_progress:
        analysis_progress[file_id]["status"] = "cancelled"
        analysis_progress[file_id]["message"] = "分析已取消"
        return jsonify({"success": True, "message": "分析已取消"})
    return jsonify({"success": False, "message": "未找到分析任务"})

@app.route('/api/analyze/<filename>')
def analyze_file(filename):
    # 修复1：URL解码中文文件名，解决%E8%B4%A5乱码找不到文件的问题
    filename = unquote(filename)
    # 修复2：清理文件名末尾多余的:1等异常字符（解决你截图里URL带:1的问题）
    filename = filename.split(':')[0]
    logger.info(f"清理后的文件名: {filename}")
    
    # 获取难度参数
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in DIFFICULTY_THRESHOLD:
        difficulty = 'medium'
    
    pgn_path = os.path.join(WATCH, filename)
    
    # 前置文件校验，返回明确错误
    if not os.path.exists(pgn_path):
        logger.error(f"文件不存在: {pgn_path}")
        return jsonify({"error": f"文件不存在: {filename}"}), 404
    if os.path.getsize(pgn_path) == 0:
        logger.error(f"文件为空: {pgn_path}")
        return jsonify({"error": "PGN文件为空，无法解析"}), 400

    status = load_status()
    file_status = status.get(filename, {})
    status_value = file_status.get("status")
    
    if status_value == "processing":
        logger.info(f"文件 {filename} 正在处理中")
        return jsonify({
            "status": "processing",
            "message": "文件正在处理中，请稍后再试"
        })

    # 初始化进度
    update_analysis_progress(filename, "processing", 0, 100, "开始分析...")
    
    try:
        game, mistakes = analyze_pgn_with_progress(pgn_path, filename)
        
        if not game:
            logger.error(f"解析PGN文件失败: {filename}")
            return jsonify({"error": "PGN文件解析失败，请检查文件格式是否正确"}), 400

        # 根据难度筛选习题
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

@app.route('/api/check_move', methods=['POST'])
def check_move():
    data = request.json
    fen = data.get('fen')
    user_move = data.get('move')
    expected_best = data.get('expected_best')

    logger.info('检查用户着法', extra={'user_move': user_move, 'expected_best': expected_best})

    if not fen or not user_move:
        logger.warning('缺少参数', extra={'fen': fen, 'user_move': user_move})
        return jsonify({"error": "缺少参数"}), 400

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
    is_mistake = delta < MISTAKE

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

@app.route('/api/legal_moves', methods=['POST'])
def get_legal_moves():
    data = request.json
    fen = data.get('fen')
    square = data.get('square')

    if not fen or not square:
        return jsonify({"error": "缺少参数"}), 400

    try:
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

@app.route('/api/hint', methods=['POST'])
def get_hint():
    data = request.json
    fen = data.get('fen')

    if not fen:
        return jsonify({"error": "缺少FEN"}), 400

    try:
        board = chess.Board(fen)
        eng = get_engine()
    except:
        eng = restart_engine()
        board = chess.Board(fen)

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

@app.route('/api/best_move', methods=['POST'])
def get_best_move():
    data = request.json
    fen = data.get('fen')

    if not fen:
        return jsonify({"error": "缺少FEN"}), 400

    try:
        board = chess.Board(fen)
        eng = get_engine()
    except:
        eng = restart_engine()
        board = chess.Board(fen)

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

def explain_loss(loss):
    if loss > 500:
        return "严重失误，重大子力损失", "立即评估局面，寻找止损方案"
    elif loss > 300:
        return "送子丢子，漏看战术", "必须保护子力，避开攻击线"
    elif loss > 150:
        return "关键格失守，被突破", "守住要点，加固防线"
    else:
        return "局面判断偏差", "改善子力位置，稳健防守"

def generate_mistake_explanation(fen, actual_move, best_move, loss):
    """生成更准确的错误解释，结合战术分析"""
    if not fen or not actual_move:
        return explain_loss(loss)
    
    try:
        board = chess.Board(fen)
        analysis = analyze_tactic_situation(fen, actual_move, best_move)
        
        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100}
        piece_names = {'P': '兵', 'N': '马', 'B': '象', 'R': '车', 'Q': '后', 'K': '王'}
        
        cause = ""
        idea = ""
        
        temp_board = board.copy()
        move_obj = chess.Move.from_uci(actual_move)
        
        if move_obj in temp_board.legal_moves:
            moved_piece = board.piece_at(move_obj.from_square)
            moved_piece_type = moved_piece.symbol().upper() if moved_piece else ''
            moved_piece_name = piece_names.get(moved_piece_type, '子')
            
            moved_to = chess.square_name(move_obj.to_square)
            moved_from = chess.square_name(move_obj.from_square)
            
            before_capture = board.piece_at(move_obj.to_square)
            temp_board.push(move_obj)
            
            if temp_board.is_capture(move_obj):
                captured = temp_board.piece_at(move_obj.to_square)
                
                if captured and moved_piece:
                    captured_value = piece_values.get(captured.symbol().upper(), 0)
                    moved_value = piece_values.get(moved_piece.symbol().upper(), 0)
                    
                    attackers_after = temp_board.attackers(not board.turn, move_obj.to_square)
                    defenders_after = temp_board.attackers(board.turn, move_obj.to_square)
                    is_attacked_after = len(attackers_after) > len(defenders_after)
                    
                    if moved_value < captured_value:
                        if is_attacked_after:
                            cause = f"用{moved_piece_name}换{piece_names.get(captured.symbol().upper(), '子')}赚分，但新位置{moved_to}被攻击"
                            idea = "评估是否值得冒险，准备后续应对"
                        else:
                            cause = f"用{moved_piece_name}换{piece_names.get(captured.symbol().upper(), '子')}，赚分"
                            idea = "继续保持优势，扩大战果"
                    elif moved_value > captured_value:
                        if captured_value == 9:
                            cause = f"牺牲{moved_piece_name}换后，需要精确计算后续战术"
                            idea = "确认后续战术是否成立"
                        else:
                            cause = f"用{moved_piece_name}换{piece_names.get(captured.symbol().upper(), '子')}，亏分"
                            idea = "避免得不偿失的交换"
                    else:
                        if before_capture:
                            before_attacked = board.attackers(board.turn, move_obj.to_square)
                            before_defended = board.attackers(not board.turn, move_obj.to_square)
                            was_attacked_before = len(before_attacked) > len(before_defended)
                            
                            if was_attacked_before:
                                cause = f"被迫用{moved_piece_name}兑{piece_names.get(captured.symbol().upper(), '子')}"
                                idea = "这是必要的防御，局面保持平衡"
                            elif is_attacked_after:
                                cause = f"主动用{moved_piece_name}兑{piece_names.get(captured.symbol().upper(), '子')}，但新位置{moved_to}被攻击"
                                idea = "评估是否需要立即保护或寻找反击"
                            else:
                                cause = f"同等子力交换"
                                idea = "局面保持平衡，寻找其他机会"
            
                if not cause:
                    attackers_after = temp_board.attackers(not board.turn, move_obj.to_square)
                    defenders_after = temp_board.attackers(board.turn, move_obj.to_square)
                    
                    if len(attackers_after) > len(defenders_after):
                        cause = f"{moved_piece_name}从{moved_from}走到{moved_to}后被攻击"
                        idea = "保护被攻击的棋子或寻找反击机会"
        
        if not cause:
            if loss > 300:
                cause = "严重战术失误，子力损失"
                idea = "重新评估局面，寻找最佳应对"
            elif loss > 150:
                cause = "局面优势丧失，需要改进"
                idea = "加固防线，寻找反击机会"
            elif loss > 100:
                cause = "明显的局面判断偏差"
                idea = "改善子力协调，保持局面平衡"
            else:
                cause = "细微的局面判断偏差"
                idea = "注意局面细节，精确计算"
        
        return cause.strip(), idea.strip()
    
    except Exception as e:
        logger.error(f"生成错误解释失败: {e}")
        return explain_loss(loss)

def analyze_tactic_situation(board_fen, actual_move, best_move):
    """详细分析战术局面"""
    analysis = {
        'captured_piece': None,
        'attacked_pieces': [],
        'defended_pieces': [],
        'threats': [],
        'material_loss': 0,
        'strategic_impact': '',
        'concrete_example': '',
        'capture_moves': [],
        'forks': [],
        'pins': []
    }
    
    piece_values = {'P': 100, 'N': 300, 'B': 300, 'R': 500, 'Q': 900, 'K': 10000}
    piece_names = {'P': '兵', 'N': '马', 'B': '象', 'R': '车', 'Q': '后', 'K': '王'}
    
    try:
        board = chess.Board(board_fen)
        current_player = board.turn
        opponent = not current_player
        actual_move_obj = chess.Move.from_uci(actual_move)
        
        if actual_move_obj in board.legal_moves:
            temp_board = board.copy()
            temp_board.push(actual_move_obj)
            
            if temp_board.is_check():
                analysis['threats'].append('将军')
            
            if temp_board.is_capture(actual_move_obj):
                captured = temp_board.piece_at(actual_move_obj.to_square)
                if captured:
                    analysis['captured_piece'] = {
                        'symbol': captured.symbol(),
                        'name': piece_names.get(captured.symbol().upper(), '未知'),
                        'value': piece_values.get(captured.symbol().upper(), 0),
                        'square': chess.square_name(actual_move_obj.to_square)
                    }
            
            for square in chess.SQUARES:
                piece = temp_board.piece_at(square)
                if piece and piece.color == current_player:
                    attackers = temp_board.attackers(not piece.color, square)
                    defenders = temp_board.attackers(piece.color, square)
                    
                    attack_details = []
                    for att_sq in attackers:
                        att_piece = temp_board.piece_at(att_sq)
                        if att_piece:
                            attack_details.append({
                                'name': piece_names.get(att_piece.symbol().upper(), '未知'),
                                'from_square': chess.square_name(att_sq),
                                'move': f"{chess.square_name(att_sq)}{chess.square_name(square)}"
                            })
                    
                    if len(attackers) > len(defenders):
                        analysis['attacked_pieces'].append({
                            'piece': piece.symbol(),
                            'name': piece_names.get(piece.symbol().upper(), '未知'),
                            'square': chess.square_name(square),
                            'attackers': len(attackers),
                            'attack_details': attack_details,
                            'defenders': len(defenders)
                        })
                        
                        for attack in attack_details:
                            analysis['capture_moves'].append({
                                'captured_piece': piece_names.get(piece.symbol().upper(), '未知'),
                                'captured_square': chess.square_name(square),
                                'capturer': attack['name'],
                                'capturer_from': attack['from_square'],
                                'move': attack['move']
                            })
        
        if best_move:
            best_move_obj = chess.Move.from_uci(best_move)
            if best_move_obj in board.legal_moves:
                best_board = board.copy()
                best_board.push(best_move_obj)
                
                attacked_squares_before = set()
                for ap in analysis['attacked_pieces']:
                    attacked_squares_before.add(ap['square'])
                
                for square in chess.SQUARES:
                    piece = best_board.piece_at(square)
                    if piece and piece.color == current_player:
                        attackers = best_board.attackers(not piece.color, square)
                        defenders = best_board.attackers(piece.color, square)
                        square_name = chess.square_name(square)
                        
                        if square_name in attacked_squares_before and len(defenders) >= len(attackers):
                            analysis['defended_pieces'].append({
                                'piece': piece.symbol(),
                                'name': piece_names.get(piece.symbol().upper(), '未知'),
                                'square': square_name
                            })
    
    except Exception as e:
        logger.error(f"分析战术局面出错: {e}")
    
    return analysis

def get_tactic_explanation(board_fen, actual_move, best_move, loss):
    try:
        analysis = analyze_tactic_situation(board_fen, actual_move, best_move)
        parts = []
        
        if analysis['captured_piece']:
            cap = analysis['captured_piece']
            parts.append(f"⚠️ **立即丢子**: 你走{actual_move}后，{cap['name']}在{cap['square']}被对方直接吃掉")
        
        if analysis['capture_moves']:
            for capture in analysis['capture_moves']:
                parts.append(f"❌ **吃子威胁**: 对方{capture['capturer']}从{capture['capturer_from']}走{capture['move']}吃掉你在{capture['captured_square']}的{capture['captured_piece']}")
        
        if analysis['attacked_pieces']:
            for ap in analysis['attacked_pieces']:
                parts.append(f"🔴 **受攻子力**: {ap['name']}在{ap['square']}")
                if 'attack_details' in ap and ap['attack_details']:
                    for attack in ap['attack_details']:
                        parts.append(f"   → 被{attack['name']}从{attack['from_square']}攻击，对方可走{attack['move']}吃")
        
        if analysis['threats']:
            parts.append(f"⚔️ **即时威胁**: {', '.join(analysis['threats'])}")
        
        if analysis['defended_pieces'] and best_move:
            defended_names = ", ".join([f"{dp['name']}({dp['square']})" for dp in analysis['defended_pieces']])
            parts.append(f"✅ **正招作用**: {best_move}保护了{defended_names}，避免被吃")
        
        if loss > 300:
            parts.append(f"💰 **损失评估**: 约{loss/100:.1f}子（重大损失）")
            parts.append("💡 **建议**: 优先保护受攻子力，避免送子")
        elif loss > 200:
            parts.append(f"💰 **损失评估**: 约{loss/100:.1f}子（明显劣势）")
            parts.append("💡 **建议**: 寻找更稳健的走法，保持局面平衡")
        elif loss > 150:
            parts.append(f"💰 **损失评估**: 约{loss/100:.1f}子（轻微劣势）")
            parts.append("💡 **建议**: 改善子力位置，加固防线")
        else:
            parts.append(f"💰 **损失评估**: 约{loss/100:.1f}子（微小偏差）")
            parts.append("💡 **建议**: 注意局面细节，精确计算")
        
        if not parts:
            return "这步棋导致局面劣势，需要改进。"
        
        return "\n".join(parts)
    
    except Exception as e:
        logger.error(f"生成战术解释出错: {e}")
        return f"这步棋导致约{loss/100:.1f}子的损失，正招{best_move}可以改善局面。"

def format_pgn(moves):
    pgn_text = ""
    for i, m in enumerate(moves):
        if i % 2 == 0:
            pgn_text += f"{i//2 + 1}. {m.uci()} "
        else:
            pgn_text += f"{m.uci()} "
    return pgn_text.strip()

@app.route('/api/report/<filename>')
def get_report(filename):
    filename = unquote(filename)
    filename = filename.split(':')[0]
    logger.info(f"获取复盘数据: {filename}")
    
    pgn_path = os.path.join(WATCH, filename)
    
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

@app.route('/api/progress', methods=['POST'])
def save_learning_progress():
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "缺少filename参数"}), 400
    
    progress_data = load_progress()
    
    if filename not in progress_data:
        progress_data[filename] = {}
    
    progress_data[filename]['report_watched'] = data.get('report_watched', False)
    progress_data[filename]['report_progress'] = data.get('report_progress', 0)
    progress_data[filename]['completed_exercises'] = data.get('completed_exercises', [])
    progress_data[filename]['updated_at'] = datetime.datetime.now().isoformat()
    
    if save_progress(progress_data):
        logger.info(f"保存进度成功: {filename}")
        return jsonify({"status": "success", "message": "进度保存成功"})
    else:
        return jsonify({"status": "error", "message": "进度保存失败"}), 500

@app.route('/api/progress/<filename>')
def get_learning_progress(filename):
    filename = unquote(filename)
    filename = filename.split(':')[0]
    
    progress_data = load_progress()
    file_progress = progress_data.get(filename, {})
    
    result = {
        "filename": filename,
        "report_watched": file_progress.get('report_watched', False),
        "report_progress": file_progress.get('report_progress', 0),
        "completed_exercises": file_progress.get('completed_exercises', []),
        "updated_at": file_progress.get('updated_at', None)
    }
    
    return jsonify(result)

import io
import uuid

LIBRARY_DIR = os.path.join(OUT, "library")
PROFILE_DIR = os.path.join(OUT, "profiles")
PLAN_DIR = os.path.join(OUT, "plans")
PLAYERS_DIR = os.path.join(OUT, "players")
EXERCISES_DIR = os.path.join(OUT, "exercises")

os.makedirs(LIBRARY_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(PLAN_DIR, exist_ok=True)
os.makedirs(PLAYERS_DIR, exist_ok=True)
os.makedirs(EXERCISES_DIR, exist_ok=True)

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_SECRET_KEY = os.environ.get("DOUBAO_SECRET_KEY", "")

TOKEN_USAGE_FILE = os.path.join(OUT, "token_usage.json")
TOKEN_ALERTS_FILE = os.path.join(OUT, "token_alerts.json")

class TokenMonitor:
    def __init__(self):
        self.config = {
            "daily_limit": 100000,
            "monthly_limit": 2000000,
            "rpm_limit": 60,
            "daily_warning": 0.8,
            "daily_critical": 0.95,
            "monthly_warning": 0.7,
            "monthly_critical": 0.9
        }
    
    def load_usage(self):
        if os.path.exists(TOKEN_USAGE_FILE):
            try:
                with open(TOKEN_USAGE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_calls": 0,
            "total_tokens": 0,
            "last_updated": datetime.datetime.now().isoformat(),
            "daily": {},
            "rpm": {}
        }
    
    def save_usage(self, usage):
        with open(TOKEN_USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)
    
    def clean_expired_rpm(self, usage):
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(minutes=5)
        usage["rpm"] = {
            k: v for k, v in usage["rpm"].items()
            if datetime.datetime.strptime(k, "%Y-%m-%d %H:%M") >= cutoff
        }
    
    def get_current_rpm(self, usage):
        now = datetime.datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        return usage["rpm"].get(current_minute, 0)
    
    def record_api_call(self, tokens_used=0, call_type="chat"):
        usage = self.load_usage()
        now = datetime.datetime.now()
        
        usage["total_calls"] += 1
        usage["total_tokens"] += tokens_used
        usage["last_updated"] = now.isoformat()
        
        day_key = now.strftime("%Y-%m-%d")
        if day_key not in usage["daily"]:
            usage["daily"][day_key] = {"calls": 0, "tokens": 0}
        usage["daily"][day_key]["calls"] += 1
        usage["daily"][day_key]["tokens"] += tokens_used
        
        minute_key = now.strftime("%Y-%m-%d %H:%M")
        if minute_key not in usage["rpm"]:
            usage["rpm"] = {}
        usage["rpm"][minute_key] = usage["rpm"].get(minute_key, 0) + 1
        
        self.clean_expired_rpm(usage)
        self.save_usage(usage)
        
        return self.check_thresholds(usage)
    
    def check_thresholds(self, usage):
        day_key = datetime.datetime.now().strftime("%Y-%m-%d")
        day_usage = usage["daily"].get(day_key, {"calls": 0, "tokens": 0})
        
        daily_rate = day_usage["tokens"] / self.config["daily_limit"]
        month_key = datetime.datetime.now().strftime("%Y-%m")
        month_tokens = 0
        for date, d in usage["daily"].items():
            if date.startswith(month_key) and isinstance(d, dict) and "tokens" in d:
                month_tokens += d["tokens"]
        month_rate = month_tokens / self.config["monthly_limit"]
        
        alerts = []
        if daily_rate >= self.config["daily_critical"]:
            alerts.append({
                "level": "critical",
                "type": "daily_limit",
                "message": "🚨 今日API使用量已达到95%上限，即将强制断开",
                "current": day_usage["tokens"],
                "limit": self.config["daily_limit"],
                "remaining": self.config["daily_limit"] - day_usage["tokens"]
            })
        elif daily_rate >= self.config["daily_warning"]:
            alerts.append({
                "level": "warning",
                "type": "daily_limit",
                "message": "⚠️ 今日API使用量已达80%，请注意控制使用",
                "current": day_usage["tokens"],
                "limit": self.config["daily_limit"],
                "remaining": self.config["daily_limit"] - day_usage["tokens"]
            })
        
        if month_rate >= self.config["monthly_critical"]:
            alerts.append({
                "level": "critical",
                "type": "monthly_limit",
                "message": "🚨 本月API使用量已达到90%上限",
                "current": month_tokens,
                "limit": self.config["monthly_limit"]
            })
        elif month_rate >= self.config["monthly_warning"]:
            alerts.append({
                "level": "warning",
                "type": "monthly_limit",
                "message": "⚠️ 本月API使用量已达70%",
                "current": month_tokens,
                "limit": self.config["monthly_limit"]
            })
        
        current_rpm = self.get_current_rpm(usage)
        if current_rpm >= self.config["rpm_limit"] * 0.9:
            alerts.append({
                "level": "warning" if current_rpm < self.config["rpm_limit"] else "critical",
                "type": "rpm_limit",
                "message": f"⚠️ 当前请求速率：{current_rpm}/min",
                "current": current_rpm,
                "limit": self.config["rpm_limit"]
            })
        
        for alert in alerts:
            self.send_alert(alert)
        
        return alerts
    
    def send_alert(self, alert):
        messages = []
        if alert["level"] == "critical":
            messages.append("🚨 【紧急】豆包API使用量告警")
        elif alert["level"] == "warning":
            messages.append("⚠️ 【警告】豆包API使用量预警")
        
        messages.append(f"类型：{alert['type']}")
        messages.append(f"信息：{alert['message']}")
        
        logger.warning("\n".join(messages))
        
        alerts = []
        if os.path.exists(TOKEN_ALERTS_FILE):
            try:
                with open(TOKEN_ALERTS_FILE, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            except:
                pass
        
        alerts.append({
            **alert,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        alerts = alerts[-10:]
        
        with open(TOKEN_ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)
    
    def get_usage_stats(self):
        usage = self.load_usage()
        now = datetime.datetime.now()
        day_key = now.strftime("%Y-%m-%d")
        day_usage = usage["daily"].get(day_key, {"calls": 0, "tokens": 0})
        
        month_tokens = 0
        for date, data in usage["daily"].items():
            if date.startswith(now.strftime("%Y-%m")):
                month_tokens += data.get("tokens", 0)
        
        daily_rate = day_usage["tokens"] / self.config["daily_limit"]
        month_rate = month_tokens / self.config["monthly_limit"]
        
        status = "normal"
        if daily_rate >= 0.95:
            status = "critical"
        elif daily_rate >= 0.80:
            status = "warning"
        elif daily_rate >= 0.70:
            status = "notice"
        
        return {
            "status": status,
            "daily_usage": day_usage["tokens"],
            "daily_limit": self.config["daily_limit"],
            "daily_rate": round(daily_rate * 100, 1),
            "monthly_usage": month_tokens,
            "monthly_limit": self.config["monthly_limit"],
            "monthly_rate": round(month_rate * 100, 1),
            "total_calls": usage["total_calls"],
            "total_tokens": usage["total_tokens"],
            "current_rpm": self.get_current_rpm(usage),
            "rpm_limit": self.config["rpm_limit"],
            "last_updated": usage["last_updated"]
        }

class TokenProtection:
    def __init__(self):
        self.protection_config = {
            "warning_threshold": 0.8,
            "critical_threshold": 0.95,
            "rate_limit_delay": 2.0,
            "max_retries": 3,
            "circuit_breaker_timeout": 300
        }
        self.circuit_breaker_active = False
        self.circuit_breaker_endtime = None
    
    def should_allow_request(self):
        if self.circuit_breaker_active:
            if datetime.datetime.now() < self.circuit_breaker_endtime:
                return False, {
                    "blocked": True,
                    "reason": "circuit_breaker",
                    "message": "🚨 熔断保护已启用，请稍后再试",
                    "retry_after": (self.circuit_breaker_endtime - datetime.datetime.now()).seconds
                }
            else:
                self.circuit_breaker_active = False
        
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        if stats["status"] == "critical":
            self.activate_circuit_breaker()
            return False, {
                "blocked": True,
                "reason": "daily_limit",
                "message": "🚨 API配额已用尽，已自动切换到本地模式",
                "switch_to_local": True
            }
        
        if stats["current_rpm"] >= stats["rpm_limit"]:
            return False, {
                "blocked": True,
                "reason": "rate_limit",
                "message": f"请求过于频繁，请等待{self.protection_config['rate_limit_delay']}秒后重试",
                "retry_after": self.protection_config["rate_limit_delay"]
            }
        
        return True, {}
    
    def activate_circuit_breaker(self):
        self.circuit_breaker_active = True
        self.circuit_breaker_endtime = datetime.datetime.now() + datetime.timedelta(
            seconds=self.protection_config["circuit_breaker_timeout"]
        )
        logger.warning("🔥 豆包API熔断保护已激活，切换到本地模式")
    
    def get_protection_status(self):
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        return {
            **stats,
            "circuit_breaker_active": self.circuit_breaker_active,
            "circuit_breaker_resets_at": self.circuit_breaker_endtime.isoformat() if self.circuit_breaker_active else None
        }

token_protection = TokenProtection()

def save_game_to_library(game_data):
    game_id = f"game_{datetime.datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    
    with open(game_path, "w", encoding="utf-8") as f:
        json.dump(game_data, f, ensure_ascii=False, indent=2)
    
    return game_id

def load_game_from_library(game_id):
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    if os.path.exists(game_path):
        with open(game_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def delete_game_from_library(game_id):
    game_path = os.path.join(LIBRARY_DIR, f"{game_id}.json")
    if os.path.exists(game_path):
        os.remove(game_path)
        return True
    return False

def list_games_in_library():
    games = []
    for filename in os.listdir(LIBRARY_DIR):
        if filename.endswith(".json"):
            game_id = filename[:-5]
            try:
                with open(os.path.join(LIBRARY_DIR, filename), "r", encoding="utf-8") as f:
                    game = json.load(f)
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

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")

def call_doubao_api(prompt, temperature=0.7, max_tokens=2048):
    if not DOUBAO_API_KEY:
        logger.warning("豆包API密钥未配置")
        return None
    
    global token_protection
    if token_protection:
        allowed, info = token_protection.should_allow_request()
        if not allowed:
            logger.warning(f"API请求被拦截: {info.get('message')}")
            return None
    
    try:
        import requests
        url = "https://ark.cn-beijing.volces.com/api/v3/responses"
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "doubao-seed-2-0-pro-260215",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"你是一位专业的国际象棋教练，擅长分析棋局并给出专业建议。\n\n{prompt}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        TokenMonitor().record_api_call(max_tokens)
        
        if response.status_code == 200:
            data = response.json()
            output = data.get("output", [])
            
            for output_item in output:
                contents = output_item.get("content", [])
                if isinstance(contents, list):
                    for content in contents:
                        if content.get("type") == "output_text":
                            text = content.get("text", "").strip()
                            logger.info(f"豆包API响应成功，token使用: {data.get('usage', {}).get('total_tokens', 0)}")
                            return text
            
            logger.warning(f"豆包API响应格式异常，尝试从summary提取: {data}")
            for output_item in output:
                summary = output_item.get("summary", [])
                if isinstance(summary, list):
                    for item in summary:
                        if item.get("type") == "summary_text":
                            return item.get("text", "").strip()
            
            logger.error(f"豆包API响应格式错误: {data}")
            return None
        else:
            logger.error(f"豆包API调用失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"调用豆包API异常: {e}")
        return None

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
            
            if eval_score < MISTAKE:
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

@app.route('/api/games', methods=['GET'])
def get_games():
    games = list_games_in_library()
    return jsonify({"games": games})

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game(game_id):
    game = load_game_from_library(game_id)
    if game:
        return jsonify(game)
    return jsonify({"error": "棋局不存在"}), 404

@app.route('/api/game', methods=['POST'])
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
    
    game_id = save_game_to_library(game_data)
    
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

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    if delete_game_from_library(game_id):
        return jsonify({"success": True, "message": "删除成功"})
    return jsonify({"error": "棋局不存在"}), 404

@app.route('/api/game/<game_id>/associate', methods=['POST'])
def associate_game_players(game_id):
    data = request.json
    white_player_id = data.get('white_player_id', '')
    black_player_id = data.get('black_player_id', '')
    
    game = load_game_from_library(game_id)
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
    save_game_to_library(game)
    
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

def remove_game_from_player(player_id, game_id):
    """从棋手记录中移除棋局关联"""
    player = load_player(player_id)
    if player and player.get('game_history'):
        player['game_history'] = [g for g in player['game_history'] if g != game_id]
        player['total_games'] = len(player['game_history'])
        save_player(player)
        return True
    return False

@app.route('/api/exercises/player/<player_id>', methods=['GET'])
def get_player_exercises(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    exercises_path = os.path.join(EXERCISES_DIR, f"exercises_{player_id}.json")
    if os.path.exists(exercises_path):
        with open(exercises_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    
    return jsonify({"exercises": [], "player_id": player_id, "player_name": player.get("name")})

@app.route('/api/exercises/generate/<player_id>', methods=['GET', 'POST'])
def generate_player_exercises(player_id):
    player = load_player(player_id)
    if not player:
        return jsonify({"error": "棋手不存在"}), 404
    
    game_history = player.get("game_history", [])
    
    exercises = []
    
    if game_history:
        all_mistakes = []
        for game_id in game_history[:5]:
            game = load_game_from_library(game_id)
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
            exercises.append({
                "id": i,
                "game_id": mistake["game_id"],
                "filename": mistake["filename"],
                "move_number": mistake.get("move_number", 0),
                "loss": mistake.get("loss", 0),
                "fen": mistake.get("fen", ""),
                "actual_move": mistake.get("move", ""),
                "status": "pending",
                "attempts": 0,
                "completed": False
            })
    else:
        exercises = generate_mock_exercises(player_id)
    
    exercises_data = {
        "player_id": player_id,
        "player_name": player.get("name", ""),
        "exercises": exercises,
        "generated_at": datetime.datetime.now().isoformat(),
        "total_exercises": len(exercises)
    }
    
    exercises_path = os.path.join(EXERCISES_DIR, f"exercises_{player_id}.json")
    with open(exercises_path, "w", encoding="utf-8") as f:
        json.dump(exercises_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": f"生成了 {len(exercises)} 道错题练习",
        "exercises": exercises_data
    })

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
            "status": "pending",
            "attempts": 0,
            "completed": False,
            "category": "tactical",
            "description": "计算深度不足"
        }
    ]
    return exercises

@app.route('/api/exercises/update/<player_id>', methods=['POST'])
def update_exercise_progress(player_id):
    data = request.json
    exercise_id = data.get('exercise_id')
    status = data.get('status')
    
    exercises_path = os.path.join(EXERCISES_DIR, f"exercises_{player_id}.json")
    if not os.path.exists(exercises_path):
        return jsonify({"error": "错题集不存在"}), 404
    
    with open(exercises_path, "r", encoding="utf-8") as f:
        exercises_data = json.load(f)
    
    for ex in exercises_data.get("exercises", []):
        if ex["id"] == exercise_id:
            ex["status"] = status
            ex["attempts"] = ex.get("attempts", 0) + 1
            if status == "completed":
                ex["completed"] = True
            break
    
    with open(exercises_path, "w", encoding="utf-8") as f:
        json.dump(exercises_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({"success": True, "exercises": exercises_data})

@app.route('/api/exercises', methods=['GET'])
def get_all_exercises():
    all_exercises = []
    for filename in os.listdir(EXERCISES_DIR):
        if filename.endswith(".json"):
            player_id = filename.replace("exercises_", "").replace(".json", "")
            try:
                with open(os.path.join(EXERCISES_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_exercises.append({
                        "player_id": player_id,
                        "player_name": data.get("player_name", ""),
                        "total_exercises": data.get("total_exercises", 0),
                        "completed_count": sum(1 for e in data.get("exercises", []) if e.get("completed")),
                        "generated_at": data.get("generated_at", "")
                    })
            except:
                pass
    return jsonify({"exercises": all_exercises})

@app.route('/api/exercises/classify', methods=['POST'])
def classify_exercise():
    data = request.json or {}
    fen = data.get('fen')
    actual_move = data.get('actual_move')
    best_move = data.get('best_move')
    loss = data.get('loss', 0)
    move_number = data.get('move_number', 0)
    
    if not fen:
        return jsonify({"error": "缺少FEN参数"}), 400
    
    logger.info(f"AI错题分类: move_number={move_number}, loss={loss}")
    
    prompt = f"""
你是一位专业的国际象棋教练，擅长分析错误走法并进行分类。

请分析以下错题并进行智能分类：

【FEN】{fen}
【实际走法】{actual_move}
【最佳走法】{best_move}
【分值损失】{loss}
【步数】{move_number}

请输出JSON格式的分类结果，包含以下字段：
- category: 错误类型（开局错误/中局错误/残局错误/战术错误/战略错误/计算错误）
- sub_category: 子类型（如：双攻、牵制、通路兵、王安全、兵结构等）
- difficulty: 难度等级（1-5，1最简单，5最难）
- description: 错误原因描述（不超过100字）
- suggestion: 改进建议（不超过100字）
- common_mistake: 是否为常见错误（true/false）

要求：
1. 分类要准确、专业
2. 描述和建议要具体
3. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api(prompt, temperature=0.3, max_tokens=1000)
    
    if result:
        try:
            classification = json.loads(result)
            classification["classified_at"] = datetime.datetime.now().isoformat()
            classification["generated_by_ai"] = True
            
            logger.info("AI错题分类成功")
            return jsonify({
                "success": True,
                "classification": classification,
                "generated_by_ai": True
            })
        except json.JSONDecodeError as e:
            logger.error(f"AI分类响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地分类")
    classification = generate_local_classification(fen, actual_move, best_move, loss, move_number)
    classification["generated_by_ai"] = False
    
    return jsonify({
        "success": True,
        "classification": classification,
        "generated_by_ai": False
    })

def generate_local_classification(fen, actual_move, best_move, loss, move_number):
    board = chess.Board(fen)
    
    if move_number <= 10:
        category = "开局错误"
        sub_category = "开局准备"
    elif board.piece_count <= 12:
        category = "残局错误"
        sub_category = "残局技巧"
    else:
        category = "中局错误"
        if loss > 200:
            sub_category = "战术错误"
        else:
            sub_category = "战略错误"
    
    difficulty = 3
    if loss > 300:
        difficulty = 5
    elif loss > 200:
        difficulty = 4
    elif loss > 100:
        difficulty = 3
    elif loss > 50:
        difficulty = 2
    else:
        difficulty = 1
    
    description = "需要改进的走法"
    suggestion = "分析最佳走法并练习"
    
    if loss > 200:
        description = "严重失误，导致明显劣势"
        suggestion = "加强战术计算训练"
    elif loss > 100:
        description = "明显失误，影响局面"
        suggestion = "提高局面评估能力"
    else:
        description = "轻微失误，需要注意"
        suggestion = "继续练习，积累经验"
    
    return {
        "category": category,
        "sub_category": sub_category,
        "difficulty": difficulty,
        "description": description,
        "suggestion": suggestion,
        "common_mistake": loss > 100,
        "classified_at": datetime.datetime.now().isoformat()
    }

@app.route('/api/exercises/batch_classify', methods=['POST'])
def batch_classify_exercises():
    data = request.json or {}
    exercises = data.get('exercises', [])
    
    if not exercises:
        return jsonify({"error": "缺少练习数据"}), 400
    
    logger.info(f"批量分类练习: {len(exercises)} 条")
    
    results = []
    for ex in exercises:
        result = classify_exercise_internal(ex)
        results.append(result)
    
    return jsonify({
        "success": True,
        "classifications": results,
        "total_count": len(results)
    })

def classify_exercise_internal(exercise):
    fen = exercise.get('fen')
    actual_move = exercise.get('actual_move')
    best_move = exercise.get('best_move')
    loss = exercise.get('loss', 0)
    move_number = exercise.get('move_number', 0)
    
    prompt = f"""
分析以下错题：

【FEN】{fen}
【实际走法】{actual_move}
【最佳走法】{best_move}
【分值损失】{loss}
【步数】{move_number}

请输出JSON格式：
{{"category": "错误类型", "sub_category": "子类型", "difficulty": 1-5, "description": "描述", "suggestion": "建议"}}
"""
    
    result = call_doubao_api(prompt, temperature=0.3, max_tokens=500)
    
    if result:
        try:
            return json.loads(result)
        except:
            pass
    
    return generate_local_classification(fen, actual_move, best_move, loss, move_number)

@app.route('/api/profile', methods=['GET'])
def get_profile():
    player_id = request.args.get('player_id')
    if player_id:
        profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
    else:
        profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "画像不存在"}), 404

@app.route('/api/profile/generate', methods=['POST'])
def generate_profile():
    data = request.json or {}
    player_id = data.get('player_id', 'player_cd137a6a')
    player_name = data.get('player_name', '刘洪硕')
    use_ai = data.get('use_ai', False)
    
    if use_ai:
        return generate_enhanced_profile(player_id, player_name)
    
    profile = generate_mock_profile(player_id, player_name)
    
    profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": "能力画像生成成功",
        "profile": profile
    })

@app.route('/api/profile/generate/enhanced', methods=['POST'])
def generate_enhanced_profile(player_id=None, player_name=None):
    data = request.json or {}
    if not player_id:
        player_id = data.get('player_id', 'player_cd137a6a')
    if not player_name:
        player_name = data.get('player_name', '刘洪硕')
    
    logger.info(f"生成AI增强能力画像: player_id={player_id}, player_name={player_name}")
    
    games_data = []
    player = load_player(player_id) if player_id else None
    if player:
        game_history = player.get("game_history", [])
        for game_id in game_history[:5]:
            game = load_game_from_library(game_id)
            if game:
                games_data.append(game)
    
    prompt = f"""
你是一位专业的国际象棋教练，擅长分析棋手对局并生成详细的能力画像。

请根据以下棋局分析数据，为棋手【{player_name}】生成专业的能力画像：

【棋手信息】
- 棋手ID: {player_id}
- 棋手姓名: {player_name}
- 对局数量: {len(games_data)}

【棋局分析数据】
{json.dumps(games_data, ensure_ascii=False, indent=2)}

请输出JSON格式的能力画像，包含以下字段：
- strengths: 强项列表，每项包含skill（技能名称）和score（分数0-100）
- weaknesses: 弱项列表，每项包含skill和score
- style: 棋风描述（如：进攻型、稳健型、均衡型、战术型等）
- suggestions: 训练建议列表（最多5条，每条不超过50字）
- overall_rating: 估计等级分（整数，范围1000-2500）
- detailed_analysis: 详细分析报告（中文，不少于200字）
- opening_skill: 开局能力评分（0-100）
- midgame_skill: 中局能力评分（0-100）
- endgame_skill: 残局能力评分（0-100）
- tactical_vision: 战术眼光评分（0-100）
- positional_understanding: 局面理解评分（0-100）

要求：
1. 分析要专业、深入，基于提供的棋局数据
2. 建议要具体可行，有针对性
3. 评分要合理，符合实际水平
4. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api(prompt, temperature=0.5, max_tokens=3000)
    
    if result:
        try:
            profile = json.loads(result)
            profile["generated_at"] = datetime.datetime.now().isoformat()
            profile["games_analyzed"] = len(games_data)
            profile["generated_by_ai"] = True
            
            profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            
            logger.info(f"AI能力画像生成成功: {player_id}")
            return jsonify({
                "success": True,
                "message": "AI增强能力画像生成成功",
                "profile": profile,
                "generated_by_ai": True
            })
        except json.JSONDecodeError as e:
            logger.error(f"AI响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地生成")
    profile = generate_local_profile(games_data)
    profile["generated_by_ai"] = False
    
    profile_path = os.path.join(PROFILE_DIR, f"profile_{player_id}.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": "使用本地算法生成能力画像",
        "profile": profile,
        "generated_by_ai": False
    })

def generate_local_profile(games_data):
    if not games_data:
        return {
            "strengths": [
                {"skill": "残局技巧", "score": 70},
                {"skill": "战术计算", "score": 65}
            ],
            "weaknesses": [
                {"skill": "开局准备", "score": 50},
                {"skill": "时间管理", "score": 55}
            ],
            "style": "均衡型",
            "suggestions": [
                "继续加强战术训练",
                "注意开局准备",
                "提高计算深度"
            ],
            "overall_rating": 1600,
            "generated_at": datetime.datetime.now().isoformat(),
            "games_analyzed": 0
        }
    
    total_mistakes = sum(g.get("summary", {}).get("total_mistakes", 0) for g in games_data)
    avg_mistakes = total_mistakes / len(games_data)
    
    early_mistakes = 0
    mid_mistakes = 0
    late_mistakes = 0
    total_loss = 0
    
    for game in games_data:
        mistakes = game.get("mistakes", [])
        for m in mistakes:
            step = m.get("step", 0)
            loss = m.get("loss", 0)
            total_loss += loss
            if step <= 10:
                early_mistakes += 1
            elif step <= 30:
                mid_mistakes += 1
            else:
                late_mistakes += 1
    
    avg_loss = total_loss / (total_mistakes if total_mistakes > 0 else 1)
    
    strengths = []
    weaknesses = []
    suggestions = []
    
    if avg_mistakes < 2:
        strengths.append({"skill": "战术计算", "score": 85})
    elif avg_mistakes < 4:
        strengths.append({"skill": "战术计算", "score": 70})
    else:
        weaknesses.append({"skill": "战术计算", "score": 50})
        suggestions.append("加强战术计算训练，减少失误")
    
    if early_mistakes <= mid_mistakes and early_mistakes <= late_mistakes:
        strengths.append({"skill": "开局准备", "score": 75})
    else:
        weaknesses.append({"skill": "开局准备", "score": 45})
        suggestions.append("重视开局准备，研究常见开局变化")
    
    if late_mistakes <= early_mistakes and late_mistakes <= mid_mistakes:
        strengths.append({"skill": "残局技巧", "score": 80})
    else:
        weaknesses.append({"skill": "残局技巧", "score": 55})
        suggestions.append("加强残局训练，提高收官能力")
    
    if avg_loss > 200:
        weaknesses.append({"skill": "风险控制", "score": 40})
        suggestions.append("注意风险控制，避免大损失的失误")
    
    if len(suggestions) == 0:
        suggestions = ["继续保持，稳步提升棋力", "增加对局数量以积累经验"]
    
    style = "均衡型"
    if early_mistakes > mid_mistakes * 2:
        style = "进攻型"
    elif late_mistakes > early_mistakes * 2:
        style = "稳健型"
    
    overall_rating = max(1000, min(2000, 1600 - int(avg_mistakes * 50) + len(games_data) * 20))
    
    profile = {
        "strengths": strengths if strengths else [{"skill": "学习态度", "score": 70}],
        "weaknesses": weaknesses if weaknesses else [{"skill": "经验不足", "score": 60}],
        "style": style,
        "suggestions": suggestions[:5],
        "overall_rating": overall_rating,
        "generated_at": datetime.datetime.now().isoformat(),
        "games_analyzed": len(games_data),
        "avg_mistakes_per_game": round(avg_mistakes, 2),
        "avg_loss_per_mistake": round(avg_loss, 2)
    }
    
    return profile

@app.route('/api/profile/export', methods=['GET'])
def export_profile():
    profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            data = f.read()
            response = app.response_class(
                response=data,
                status=200,
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = 'attachment; filename=profile.json'
            return response
    return jsonify({"error": "画像不存在"}), 404

@app.route('/api/analyze/enhanced', methods=['POST'])
def analyze_position_enhanced():
    data = request.json or {}
    fen = data.get('fen')
    move_number = data.get('move_number', 0)
    turn = data.get('turn', 'white')
    context = data.get('context', '')
    
    if not fen:
        return jsonify({"error": "缺少FEN参数"}), 400
    
    logger.info(f"AI深度分析棋局: move_number={move_number}, turn={turn}")
    
    prompt = f"""
你是一位专业的国际象棋特级大师，擅长深度分析棋局。请分析以下局面：

【FEN】{fen}
【当前回合】{turn}
【已走步数】{move_number}
【附加信息】{context}

请输出JSON格式的分析结果，包含以下字段：
- evaluation: 局面评估（如"白方优势"、"黑方优势"、"均势"）
- score: 分数评估（用cp表示，正数表示白方优势，负数表示黑方优势）
- key_tactics: 关键战术机会列表（每项包含name和description）
- recommended_moves: 推荐走法列表（每项包含move和reason）
- threats: 潜在威胁列表（每项包含description）
- strategic_advice: 战略建议（字符串，不超过500字）
- opening_name: 开局名称（如果能识别）
- position_type: 局面类型（开局/中局/残局）

要求：
1. 分析要专业、深入
2. 推荐走法要有具体理由
3. 输出必须是纯JSON格式，不要包含其他文本
"""
    
    result = call_doubao_api(prompt, temperature=0.4, max_tokens=2000)
    
    if result:
        try:
            analysis = json.loads(result)
            analysis["fen"] = fen
            analysis["analyzed_at"] = datetime.datetime.now().isoformat()
            analysis["generated_by_ai"] = True
            
            logger.info("AI棋局分析成功")
            return jsonify({
                "success": True,
                "analysis": analysis,
                "generated_by_ai": True
            })
        except json.JSONDecodeError as e:
            logger.error(f"AI分析响应解析失败: {e}")
            logger.debug(f"原始响应: {result}")
    
    logger.warning("AI调用失败，使用本地分析")
    analysis = generate_local_analysis(fen, move_number, turn)
    analysis["generated_by_ai"] = False
    
    return jsonify({
        "success": True,
        "analysis": analysis,
        "generated_by_ai": False
    })

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

@app.route('/api/training/plan', methods=['GET'])
def get_training_plan():
    plan_path = os.path.join(PLAN_DIR, "current_plan.json")
    if os.path.exists(plan_path):
        with open(plan_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "训练计划不存在"}), 404

@app.route('/api/training/plan/generate', methods=['POST'])
def generate_training_plan():
    profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
    else:
        profile = {
            "strengths": [{"skill": "残局技巧", "score": 70}, {"skill": "战术计算", "score": 65}],
            "weaknesses": [{"skill": "开局准备", "score": 50}, {"skill": "时间管理", "score": 55}],
            "style": "均衡型",
            "overall_rating": 1600
        }
    
    prompt = f"""根据以下能力画像生成训练计划：

能力画像：
{json.dumps(profile, ensure_ascii=False, indent=2)}

请输出JSON格式，包含以下字段：
- plan_id: 计划ID
- target_level: 目标等级
- short_term_goal: 短期目标（1个月）
- long_term_goal: 长期目标（3个月）
- daily_tasks: 每日任务列表，每个包含name、duration、frequency
- weekly_focus: 每周重点
- recommendations: 推荐资源列表，每个包含resource和type
- estimated_time: 预计完成时间

请用中文输出。
"""
    
    result = call_doubao_api(prompt, temperature=0.5)
    
    if result:
        try:
            plan = json.loads(result)
            plan["plan_id"] = f"plan_{datetime.datetime.now().strftime('%Y%m%d')}"
            plan["generated_at"] = datetime.datetime.now().isoformat()
            
            plan_path = os.path.join(PLAN_DIR, "current_plan.json")
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            
            return jsonify({"success": True, "plan": plan})
        except:
            return jsonify({"success": True, "plan_text": result})
    else:
        plan = generate_local_plan(profile)
        plan_path = os.path.join(PLAN_DIR, "current_plan.json")
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": False,
            "message": "豆包API调用失败，使用本地生成",
            "plan": plan
        })

def generate_local_plan(profile):
    weaknesses = profile.get("weaknesses", [])
    weak_skills = [w["skill"] for w in weaknesses if w["score"] < 60]
    strengths = profile.get("strengths", [])
    strong_skills = [s["skill"] for s in strengths if s["score"] > 70]
    
    daily_tasks = []
    weekly_tasks = []
    focus_areas = []
    
    if "战术计算" in weak_skills:
        daily_tasks.append({"name": "战术谜题训练", "duration": "30分钟", "frequency": "每天", "description": "完成10道战术谜题，重点练习组合战术", "completed": False})
        weekly_tasks.append({"name": "战术专项练习", "duration": "2小时", "frequency": "每周", "description": "进行战术专题训练，重点解决计算深度问题"})
        focus_areas.append("战术计算")
    else:
        daily_tasks.append({"name": "战术维持训练", "duration": "15分钟", "frequency": "每天", "description": "保持战术敏感度，完成5道谜题", "completed": False})
    
    if "开局准备" in weak_skills:
        daily_tasks.append({"name": "开局学习", "duration": "20分钟", "frequency": "每天", "description": "学习并记忆1-2个开局变例", "completed": False})
        weekly_tasks.append({"name": "开局复盘", "duration": "1小时", "frequency": "每周", "description": "分析自己的开局走法，找出改进点"})
        focus_areas.append("开局准备")
    
    if "残局技巧" in weak_skills:
        daily_tasks.append({"name": "残局练习", "duration": "15分钟", "frequency": "每天", "description": "练习基础残局（王兵残局、车兵残局等）", "completed": False})
        weekly_tasks.append({"name": "残局专题", "duration": "1小时", "frequency": "每周", "description": "深入学习特定残局类型"})
        focus_areas.append("残局技巧")
    
    if "风险控制" in weak_skills:
        daily_tasks.append({"name": "局面评估练习", "duration": "10分钟", "frequency": "每天", "description": "分析3个复杂局面，评估风险", "completed": False})
        focus_areas.append("风险控制")
    
    daily_tasks.append({"name": "错题回顾", "duration": "15分钟", "frequency": "每天", "description": "复习错题集中的2-3道题目", "completed": False})
    daily_tasks.append({"name": "快速对局", "duration": "30分钟", "frequency": "每天", "description": "进行15分钟快棋练习", "completed": False})
    
    weekly_tasks.append({"name": "深度复盘", "duration": "2小时", "frequency": "每周", "description": "详细分析本周最差的一局棋"})
    weekly_tasks.append({"name": "模拟比赛", "duration": "3小时", "frequency": "每周", "description": "进行一轮模拟比赛"})
    
    target_rating = profile.get("overall_rating", 1600)
    if target_rating < 1400:
        target_level = "L1"
        estimated_time = "2个月"
    elif target_rating < 1600:
        target_level = "L2"
        estimated_time = "3个月"
    elif target_rating < 1800:
        target_level = "L3"
        estimated_time = "4个月"
    else:
        target_level = "L4"
        estimated_time = "5个月"
    
    recommendations = []
    if "战术计算" in weak_skills or "战术计算" in strong_skills:
        recommendations.append({"resource": "《国际象棋战术大全》", "type": "书籍", "priority": "high"})
        recommendations.append({"resource": "CT-ART 4.0", "type": "软件", "priority": "high"})
    
    if "开局准备" in weak_skills:
        recommendations.append({"resource": "《开局百科全书》", "type": "书籍", "priority": "medium"})
    
    if "残局技巧" in weak_skills or "残局技巧" in strong_skills:
        recommendations.append({"resource": "《残局基础》", "type": "书籍", "priority": "high"})
    
    recommendations.extend([
        {"resource": "Lichess战术训练", "type": "在线", "priority": "high"},
        {"resource": "Chess.com练习", "type": "在线", "priority": "medium"},
        {"resource": "观看GM对局视频", "type": "视频", "priority": "low"}
    ])
    
    return {
        "plan_id": f"plan_{datetime.datetime.now().strftime('%Y%m%d')}",
        "target_level": target_level,
        "target_rating": target_rating + 200,
        "short_term_goal": f"在1个月内将等级分提升至 {target_rating + 50}，减少{', '.join(focus_areas) if focus_areas else '战术'}失误",
        "long_term_goal": f"在{estimated_time}内达到 {target_rating + 200} 等级分，成为{target_level}级棋手",
        "daily_tasks": daily_tasks,
        "weekly_tasks": weekly_tasks,
        "weekly_focus": f"本周重点：{'、'.join(focus_areas) if focus_areas else '综合训练'}",
        "focus_areas": focus_areas,
        "recommendations": recommendations,
        "estimated_time": estimated_time,
        "generated_at": datetime.datetime.now().isoformat(),
        "progress": 0,
        "completed_tasks": 0,
        "total_tasks": len(daily_tasks) * 30 + len(weekly_tasks) * 4
    }

@app.route('/api/training/plan/export', methods=['GET'])
def export_training_plan():
    plan_path = os.path.join(PLAN_DIR, "current_plan.json")
    if os.path.exists(plan_path):
        with open(plan_path, "r", encoding="utf-8") as f:
            data = f.read()
            response = app.response_class(
                response=data,
                status=200,
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = 'attachment; filename=training_plan.json'
            return response
    return jsonify({"error": "训练计划不存在"}), 404

def find_player_by_name(name):
    """根据姓名查找棋手"""
    players = list_players()
    for player in players:
        if player.get("name", "").strip() == name.strip():
            return player
    return None

def associate_game_to_player(player_id, game_id):
    """关联棋局到棋手"""
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

@app.route('/api/import/pgn', methods=['POST'])
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
            
            game_id = save_game_to_library(game_data)
            
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

@app.route('/api/import/profile', methods=['POST'])
def import_profile():
    data = request.json
    if not data:
        return jsonify({"error": "缺少数据"}), 400
    
    profile_path = os.path.join(PROFILE_DIR, "current_profile.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return jsonify({"success": True, "message": "画像导入成功"})

@app.route('/api/import/plan', methods=['POST'])
def import_plan():
    data = request.json
    if not data:
        return jsonify({"error": "缺少数据"}), 400
    
    plan_path = os.path.join(PLAN_DIR, "current_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return jsonify({"success": True, "message": "训练计划导入成功"})

def save_player(player_data):
    player_id = player_data.get("player_id", f"player_{uuid.uuid4().hex[:8]}")
    player_path = os.path.join(PLAYERS_DIR, f"{player_id}.json")
    
    player_data["player_id"] = player_id
    player_data["updated_at"] = datetime.datetime.now().isoformat()
    
    if "created_at" not in player_data:
        player_data["created_at"] = player_data["updated_at"]
    
    with open(player_path, "w", encoding="utf-8") as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    return player_id

def load_player(player_id):
    player_path = os.path.join(PLAYERS_DIR, f"{player_id}.json")
    if os.path.exists(player_path):
        with open(player_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

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
                with open(os.path.join(PLAYERS_DIR, filename), "r", encoding="utf-8") as f:
                    player = json.load(f)
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

@app.route('/api/players', methods=['GET'])
def get_players():
    players = list_players()
    return jsonify({"players": players})

@app.route('/api/player/<player_id>', methods=['GET'])
def get_player(player_id):
    player = load_player(player_id)
    if player:
        return jsonify(player)
    return jsonify({"error": "棋手不存在"}), 404

@app.route('/api/player', methods=['POST'])
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

@app.route('/api/player/<player_id>', methods=['PUT'])
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

@app.route('/api/player/<player_id>', methods=['DELETE'])
def delete_player_endpoint(player_id):
    if delete_player(player_id):
        return jsonify({"success": True, "message": "棋手删除成功"})
    return jsonify({"error": "棋手不存在"}), 404

@app.route('/api/player/<player_id>/add_game', methods=['POST'])
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

@app.route('/api/player/<player_id>/stats', methods=['GET'])
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

@app.route('/api/token/status', methods=['GET'])
def get_token_status():
    try:
        global token_protection
        if token_protection:
            status = token_protection.get_protection_status()
        else:
            monitor = TokenMonitor()
            status = monitor.get_usage_stats()
            status["circuit_breaker_active"] = False
            status["circuit_breaker_resets_at"] = None
        
        status["api_key_configured"] = bool(DOUBAO_API_KEY)
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取Token状态失败: {e}")
        return jsonify({"error": "获取Token状态失败"}), 500

@app.route('/api/token/usage', methods=['GET'])
def get_token_usage():
    try:
        monitor = TokenMonitor()
        stats = monitor.get_usage_stats()
        
        usage_history = []
        usage = monitor.load_usage()
        for date, data in usage["daily"].items():
            usage_history.append({
                "date": date,
                "calls": data.get("calls", 0),
                "tokens": data.get("tokens", 0)
            })
        
        stats["usage_history"] = sorted(usage_history, key=lambda x: x["date"])
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取Token使用统计失败: {e}")
        return jsonify({"error": "获取Token使用统计失败"}), 500

@app.route('/api/token/alerts', methods=['GET'])
def get_token_alerts():
    try:
        if os.path.exists(TOKEN_ALERTS_FILE):
            with open(TOKEN_ALERTS_FILE, "r", encoding="utf-8") as f:
                alerts = json.load(f)
        else:
            alerts = []
        
        return jsonify({"alerts": alerts})
    except Exception as e:
        logger.error(f"获取Token告警失败: {e}")
        return jsonify({"error": "获取Token告警失败"}), 500

@app.route('/api/token/config', methods=['POST'])
def update_token_config():
    try:
        data = request.json
        monitor = TokenMonitor()
        
        if "daily_limit" in data:
            monitor.config["daily_limit"] = data["daily_limit"]
        if "monthly_limit" in data:
            monitor.config["monthly_limit"] = data["monthly_limit"]
        if "rpm_limit" in data:
            monitor.config["rpm_limit"] = data["rpm_limit"]
        if "daily_warning" in data:
            monitor.config["daily_warning"] = data["daily_warning"]
        if "daily_critical" in data:
            monitor.config["daily_critical"] = data["daily_critical"]
        if "monthly_warning" in data:
            monitor.config["monthly_warning"] = data["monthly_warning"]
        if "monthly_critical" in data:
            monitor.config["monthly_critical"] = data["monthly_critical"]
        
        return jsonify({
            "success": True,
            "message": "Token监控配置更新成功",
            "config": monitor.config
        })
    except Exception as e:
        logger.error(f"更新Token配置失败: {e}")
        return jsonify({"error": "更新Token配置失败"}), 500

@app.route('/api/token/reset-circuit', methods=['POST'])
def reset_circuit_breaker():
    try:
        global token_protection
        if token_protection:
            token_protection.circuit_breaker_active = False
            token_protection.circuit_breaker_endtime = None
            logger.info("熔断器已手动重置")
        
        return jsonify({
            "success": True,
            "message": "熔断器已重置"
        })
    except Exception as e:
        logger.error(f"重置熔断器失败: {e}")
        return jsonify({"error": "重置熔断器失败"}), 500

@app.route('/api/training/task/complete', methods=['POST'])
def complete_task():
    try:
        data = request.json
        player_id = data.get("player_id", "player_cd137a6a")
        task_id = data.get("task_id")
        completed = data.get("completed", True)
        score = data.get("score", 0)
        duration_minutes = data.get("duration_minutes", 0)
        notes = data.get("notes", "")
        
        plan = generate_mock_training_plan(player_id)
        
        for task in plan["daily_tasks"]:
            if task["task_id"] == task_id:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                task["completion_history"].append({
                    "date": today,
                    "completed": completed,
                    "score": score,
                    "notes": notes
                })
                task["total_completed"] += 1
                if completed:
                    task["streak"] += 1
                    if task["avg_score"] == 0:
                        task["avg_score"] = score
                    else:
                        task["avg_score"] = round((task["avg_score"] * (task["total_completed"] - 1) + score) / task["total_completed"])
                else:
                    task["streak"] = 0
        
        points_earned = 10
        if score >= 80:
            points_earned += 20
        
        return jsonify({
            "success": True,
            "message": "任务完成记录成功",
            "update": {
                "streak": plan["daily_tasks"][0]["streak"],
                "total_completed": plan["daily_tasks"][0]["total_completed"],
                "avg_score": plan["daily_tasks"][0]["avg_score"],
                "points_earned": points_earned
            },
            "reminders": []
        })
    except Exception as e:
        logger.error(f"完成任务失败: {e}")
        return jsonify({"error": "完成任务失败"}), 500

@app.route('/api/training/progress', methods=['GET'])
def get_training_progress():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        progress = generate_mock_progress(player_id)
        return jsonify(progress)
    except Exception as e:
        logger.error(f"获取训练进度失败: {e}")
        return jsonify({"error": "获取训练进度失败"}), 500

@app.route('/api/training/progress/<player_id>', methods=['GET'])
def get_player_progress(player_id):
    try:
        progress = generate_mock_progress(player_id)
        return jsonify(progress)
    except Exception as e:
        logger.error(f"获取选手训练进度失败: {e}")
        return jsonify({"error": "获取选手训练进度失败"}), 500

@app.route('/api/training/reminders', methods=['GET'])
def get_reminders():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders)
    except Exception as e:
        logger.error(f"获取训练提醒失败: {e}")
        return jsonify({"error": "获取训练提醒失败"}), 500

@app.route('/api/training/reminders/<player_id>', methods=['GET'])
def get_player_reminders(player_id):
    try:
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders)
    except Exception as e:
        logger.error(f"获取选手训练提醒失败: {e}")
        return jsonify({"error": "获取选手训练提醒失败"}), 500

@app.route('/api/training/summary/daily', methods=['GET'])
def get_daily_summary():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders["daily_summary"])
    except Exception as e:
        logger.error(f"获取每日总结失败: {e}")
        return jsonify({"error": "获取每日总结失败"}), 500

@app.route('/api/training/summary/weekly', methods=['GET'])
def get_weekly_summary():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        reminders = generate_mock_reminders(player_id)
        return jsonify(reminders["weekly_summary"])
    except Exception as e:
        logger.error(f"获取每周总结失败: {e}")
        return jsonify({"error": "获取每周总结失败"}), 500

@app.route('/api/training/achievements', methods=['GET'])
def get_achievements():
    try:
        player_id = request.args.get("player_id", "player_cd137a6a")
        achievements = generate_mock_achievements(player_id)
        return jsonify(achievements)
    except Exception as e:
        logger.error(f"获取成就失败: {e}")
        return jsonify({"error": "获取成就失败"}), 500

@app.route('/api/training/achievements/<player_id>', methods=['GET'])
def get_player_achievements(player_id):
    try:
        achievements = generate_mock_achievements(player_id)
        return jsonify(achievements)
    except Exception as e:
        logger.error(f"获取选手成就失败: {e}")
        return jsonify({"error": "获取选手成就失败"}), 500

@app.route('/api/training/adjust', methods=['POST'])
def adjust_training_plan():
    try:
        data = request.json
        player_id = data.get("player_id", "player_cd137a6a")
        
        plan = generate_mock_training_plan(player_id)
        progress = generate_mock_progress(player_id)
        
        adjustments = []
        
        for task in plan["daily_tasks"]:
            avg_score = task.get("avg_score", 0)
            if avg_score > 85:
                task["difficulty"] = "hard"
                adjustments.append({
                    "type": "increase_difficulty",
                    "task": task["name"],
                    "change": "难度提升为困难"
                })
            elif avg_score < 50:
                task["difficulty"] = "easy"
                adjustments.append({
                    "type": "decrease_difficulty",
                    "task": task["name"],
                    "change": "难度降低为简单"
                })
        
        return jsonify({
            "success": True,
            "message": "训练计划调整完成",
            "adjustments": adjustments,
            "plan": plan
        })
    except Exception as e:
        logger.error(f"调整训练计划失败: {e}")
        return jsonify({"error": "调整训练计划失败"}), 500

@app.route('/api/mistakes/analysis/<player_id>', methods=['GET'])
def get_mistakes_analysis(player_id):
    try:
        mistakes = generate_mock_mistakes(player_id)
        return jsonify(mistakes)
    except Exception as e:
        logger.error(f"获取错题分析失败: {e}")
        return jsonify({"error": "获取错题分析失败"}), 500

@app.route('/api/training/plan/generate', methods=['POST'])
def generate_training_plan_api():
    try:
        data = request.json
        player_id = data.get("player_id", "player_cd137a6a")
        player_name = data.get("player_name", "刘洪硕")
        
        plan = generate_mock_training_plan(player_id, player_name)
        
        plan_path = os.path.join(PLAN_DIR, f"{plan['plan_id']}.json")
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "message": "训练计划生成成功",
            "plan": plan
        })
    except Exception as e:
        logger.error(f"生成训练计划失败: {e}")
        return jsonify({"error": "生成训练计划失败"}), 500

if __name__ == '__main__':
    os.makedirs(WATCH, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)
    os.makedirs(PLAN_DIR, exist_ok=True)
    os.makedirs(PLAYERS_DIR, exist_ok=True)
    logger.info(f"目录初始化完成")
    app.run(debug=True, host='0.0.0.0', port=5000)