import os
import sys
import json
import datetime
import chess
import chess.pgn
import chess.engine
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from urllib.parse import unquote

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

WATCH = r"D:\Chess_PGN_Receive"
OUT = r"D:\Chess_Output"
STATUS_FILE = os.path.join(OUT, "processing_status.json")
PROGRESS_FILE = os.path.join(OUT, "learning_progress.json")
DEPTH = 14
MOVE_TIME = 0.8
MISTAKE = -100

DIFFICULTY_THRESHOLD = {
    "easy": 100,
    "medium": 150,
    "hard": 250
}

MAX_DEMONSTRATION_MISTAKES = 5

engine = None

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
            if delta < MISTAKE:
                actual_move = moves[i]

                # 第156行核心修复：安全获取pv键，避免KeyError
                info = eng.analyse(boards[i], chess.engine.Limit(depth=12, time=0.2))
                pv = info.get("pv", [])
                best_move = pv[0].uci() if pv else None

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

@app.route('/api/pgn_files')
def get_pgn_files():
    logger.info("获取PGN文件列表")
    if not os.path.exists(WATCH):
        logger.warning(f"PGN目录不存在: {WATCH}")
        return jsonify({"files": []})
    files = [f for f in os.listdir(WATCH) if f.endswith('.pgn')]
    logger.info(f"找到 {len(files)} 个PGN文件: {files}")
    return jsonify({"files": files})

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

    game, mistakes = analyze_pgn(pgn_path)
    if not game:
        logger.error(f"解析PGN文件失败: {filename}")
        return jsonify({"error": "PGN文件解析失败，请检查文件格式是否正确"}), 400

    # 根据难度筛选习题
    min_loss = DIFFICULTY_THRESHOLD[difficulty]
    filtered_mistakes = [m for m in mistakes if m["loss"] >= min_loss]

    exercises = []
    for i, e in enumerate(filtered_mistakes, 1):
        exercises.append({
            "id": i,
            "step": e["step"],
            "fen": e["fen"],
            "turn": e["turn"],
            "best_move": e["best"],
            "loss": e["loss"],
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
        "exercises": exercises
    })

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
    if current_player == chess.WHITE:
        score_before = res_before["score"].white().score(mate_score=10000)
    else:
        score_before = res_before["score"].black().score(mate_score=10000)

    board.push(move)
    res_after = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
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
    if loss > 300:
        return "送子丢子，漏看战术", "必须保护子力，避开攻击线"
    elif loss > 150:
        return "关键格失守，被突破", "守住要点，加固防线"
    else:
        return "局面判断偏差", "改善子力位置，稳健防守"

def get_tactic_explanation(board_fen, actual_move, best_move, loss):
    try:
        board = chess.Board(board_fen)
        move = chess.Move.from_uci(actual_move)
        if move in board.legal_moves:
            board.push(move)
            if board.is_capture(move):
                return "这步棋白白送掉了子力，没有获得任何补偿。"
        
        if loss > 300:
            return "这步棋导致子力损失或局面崩溃，正招可以避免重大损失。"
        elif loss > 200:
            return "这步棋让对手获得明显优势，正招能保持局面均衡。"
        elif loss > 150:
            return "这步棋削弱了关键位置，正招能更好地巩固防线。"
        else:
            return "这步棋稍有偏差，正招能更精确地处理局面。"
    except:
        return ""

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
        cause, idea = explain_loss(m["loss"])
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

if __name__ == '__main__':
    # 启动前自动创建目录，避免不存在报错
    os.makedirs(WATCH, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    logger.info(f"目录初始化完成: WATCH={WATCH}, OUT={OUT}")
    app.run(debug=True, host='0.0.0.0', port=5000)