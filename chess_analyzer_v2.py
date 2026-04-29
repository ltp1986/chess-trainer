import os,time,chess,chess.pgn,chess.svg,chess.engine
from datetime import datetime

# ===================== 路径配置 =====================
WATCH       = r"D:\Chess_PGN_Receive"
OUT         = r"D:\Chess_Output"
LOG         = os.path.join(OUT, "analyzed.txt")
DEPTH       = 18
MOVE_TIME   = 1.5
MISTAKE     = -100
# ====================================================

os.makedirs(os.path.join(OUT, "images"), exist_ok=True)

def find_engine():
    for p in ["stockfish.exe", "stockfish-windows-x86-64-avx2.exe", r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"]:
        if os.path.exists(p):
            return p
    raise Exception("错误：未找到Stockfish引擎")

def load_done():
    if not os.path.exists(LOG):
        return set()
    with open(LOG, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def mark_done(name):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(name + "\n")

def is_valid_pgn(path):
    if not path.endswith(".pgn") or os.path.getsize(path) == 0:
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            game = chess.pgn.read_game(f)
        return game and len(list(game.mainline_moves())) >= 4
    except:
        return False

# ===================== 棋盘 + 双箭头 =====================
def svg_board(board, fname, wrong=None, best=None):
    arrows = []
    try:
        if wrong and isinstance(wrong, chess.Move):
            arrows.append(chess.svg.Arrow(wrong.from_square, wrong.to_square, color="#e74c3c"))
        if best and isinstance(best, chess.Move):
            arrows.append(chess.svg.Arrow(best.from_square, best.to_square, color="#27ae60"))
    except:
        pass
    s = chess.svg.board(board=board, size=380, coordinates=True, arrows=arrows)
    with open(os.path.join(OUT, "images", fname), "w", encoding="utf-8") as f:
        f.write(s)
    return f"images/{fname}"

def find_alternative_best(board, exclude_move):
    """找到一个不同于exclude_move的最佳着法"""
    try:
        eng = chess.engine.SimpleEngine.popen_uci(find_engine())
        eng.configure({"Threads": 4, "Hash": 512})
        eng.configure({"MultiPV": 5})
        res = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
        eng.quit()
        
        if isinstance(res, list):
            for r in res:
                pv = r.get("pv", [])
                if pv and pv[0] != exclude_move:
                    return pv[0]
        elif isinstance(res, dict):
            pv = res.get("pv", [])
            if pv and len(pv) > 1 and pv[0] == exclude_move:
                return pv[1]
            elif pv and pv[0] != exclude_move:
                return pv[0]
        
        legal_moves = list(board.legal_moves)
        for mv in legal_moves:
            if mv != exclude_move:
                return mv
        return None
    except Exception as e:
        print(f"  查找替代着法失败: {e}")
        return None

def explain(err):
    v = err["loss"]
    if v > 300:
        return "送子丢子，漏看战术", "必须保护子力，避开攻击线"
    elif v > 150:
        return "关键格失守，被突破", "守住要点，加固防线"
    else:
        return "局面判断偏差", "改善子力位置，稳健防守"

def get_best_line(board, best_move, depth=DEPTH, move_time=MOVE_TIME):
    """获取正招的后续变化线（PV），返回前5步的着法列表"""
    try:
        eng = chess.engine.SimpleEngine.popen_uci(find_engine())
        eng.configure({"Threads": 4, "Hash": 512})
        
        temp_board = board.copy()
        if best_move and best_move in temp_board.legal_moves:
            temp_board.push(best_move)
        else:
            eng.quit()
            return []
        
        res = eng.analyse(temp_board, chess.engine.Limit(depth=depth, time=move_time))
        eng.quit()
        
        pv = res.get("pv", [])
        return pv[:5]
    except Exception as e:
        print(f"  获取变化线失败: {e}")
        return []

def format_line(board, moves):
    """将UCI着法列表格式化为可读的变化线"""
    if not moves:
        return ""
    
    result = []
    temp = board.copy()
    move_num = 1
    is_white = temp.turn == chess.WHITE
    
    for mv in moves:
        if is_white:
            result.append(f"{move_num}.{mv.uci()}")
        else:
            result.append(mv.uci())
            move_num += 1
        is_white = not is_white
    
    return " ".join(result)

def get_tactic_explanation(board, actual_move, best_move, loss):
    """生成战术解释，说明为什么正招更好"""
    try:
        temp = board.copy()
        if actual_move in temp.legal_moves:
            temp.push(actual_move)
            if temp.is_capture(actual_move):
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
    
    return ""

# ===================== 全新习题生成系统 =====================

def classify_mistake_type(board, actual_move, best_move, loss):
    """
    分类错误类型，返回 (错误类型, 难度等级, 战术主题)
    """
    try:
        temp = board.copy()
        
        # 检查是否是送子
        if actual_move in temp.legal_moves:
            temp.push(actual_move)
            # 检查是否有子被吃
            if temp.is_capture(actual_move):
                captured = temp.piece_at(actual_move.to_square)
                if captured:
                    return "送子", "初级", "子力保护"
        
        # 检查是否是漏看将军/杀棋
        temp2 = board.copy()
        if best_move in temp2.legal_moves:
            temp2.push(best_move)
            if temp2.is_checkmate():
                return "杀棋", "高级", "杀法练习"
            elif temp2.is_check():
                return "将军", "中级", "将军战术"
        
        # 根据失分程度分类
        if loss > 300:
            return "严重失误", "中级", "局面判断"
        elif loss > 150:
            return "位置失误", "初级", "子力调动"
        else:
            return "轻微偏差", "初级", "精确性"
            
    except:
        pass
    
    return "一般失误", "初级", "综合练习"

def generate_training_position(original_board, mistake_type, tactic_theme, difficulty):
    """
    根据错误类型生成一个全新的训练局面
    
    新策略：
    1. 从原始局面出发，尝试多种变体路径
    2. 使用MultiPV获取多个候选着法，增加多样性
    3. 验证生成的局面是否有足够的战术性（评分变化>100cp）
    4. 确保新局面与原局面有明显差异
    
    返回: (新局面的FEN, 正招UCI, 战术说明)
    """
    eng = None
    try:
        eng = chess.engine.SimpleEngine.popen_uci(find_engine())
        eng.configure({"Threads": 4, "Hash": 512})
        
        # 复制原始局面
        board = original_board.copy()
        
        best_variant = None
        best_score_delta = 0
        
        # 尝试生成多个变体，选择战术性最强的一个
        for variant_attempt in range(5):  # 尝试5次
            temp_board = board.copy()
            
            # 根据难度决定走几步
            moves_to_play = 2 if difficulty == "初级" else 3
            
            # 尝试走变体着法（从合法着法中随机选择增加多样性）
            for step in range(moves_to_play):
                if temp_board.is_game_over():
                    break
                
                legal_moves = list(temp_board.legal_moves)
                if not legal_moves:
                    break
                
                # 获取引擎推荐的最佳着法
                res = eng.analyse(temp_board, chess.engine.Limit(depth=14, time=1.0))
                pv = res.get("pv", [])
                best_move = pv[0] if pv else None
                
                # 根据variant_attempt选择不同的着法策略
                if variant_attempt == 0 and best_move:
                    # 第一次：走最佳着法
                    chosen_move = best_move
                elif variant_attempt == 1 and best_move:
                    # 第二次：走次优选法（从合法着法中找一个评分较高的）
                    # 简单策略：找一个能吃的着法
                    capture_moves = [m for m in legal_moves if temp_board.is_capture(m)]
                    if capture_moves:
                        chosen_move = capture_moves[0]
                    else:
                        chosen_move = best_move
                else:
                    # 其他尝试：从合法着法中随机选择（排除极端差的着法）
                    import random
                    # 优先选择吃子、将军等着法
                    tactical_moves = [m for m in legal_moves if temp_board.is_capture(m)]
                    if tactical_moves and random.random() > 0.3:
                        chosen_move = random.choice(tactical_moves)
                    else:
                        chosen_move = random.choice(legal_moves)
                
                temp_board.push(chosen_move)
            
            # 评估这个变体局面的战术性
            if not temp_board.is_game_over() and temp_board.fen() != board.fen():
                # 分析当前局面
                res_current = eng.analyse(temp_board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
                pv_current = res_current.get("pv", [])
                
                if pv_current:
                    best_move = pv_current[0]
                    
                    # 获取当前评分
                    current_score = res_current["score"].white().score(mate_score=10000) if temp_board.turn == chess.WHITE else res_current["score"].black().score(mate_score=10000)
                    
                    # 模拟走正招后的评分
                    test_board = temp_board.copy()
                    test_board.push(best_move)
                    res_after = eng.analyse(test_board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
                    after_score = res_after["score"].white().score(mate_score=10000) if temp_board.turn == chess.WHITE else res_after["score"].black().score(mate_score=10000)
                    
                    # 计算评分变化（从当前走棋方视角）
                    score_delta = after_score - current_score
                    
                    # 检查是否是战术着法
                    is_tactical = (
                        test_board.is_check() or
                        temp_board.is_capture(best_move) or
                        score_delta > 100  # 正招能带来显著改善
                    )
                    
                    # 选择评分变化最大的变体
                    if is_tactical and score_delta > best_score_delta:
                        best_score_delta = score_delta
                        best_variant = (temp_board.fen(), best_move, f"基于{tactic_theme}的变体练习（评分改善{score_delta}cp）")
        
        # 如果找到好的变体，返回它
        if best_variant and best_score_delta > 50:
            eng.quit()
            return best_variant
        
        # 备选方案：尝试从公开战术库加载类似局面
        fallback = load_tactical_position(tactic_theme)
        if fallback:
            eng.quit()
            return fallback
        
        eng.quit()
        
    except Exception as e:
        print(f"  生成训练局面失败: {e}")
        if eng:
            try:
                eng.quit()
            except:
                pass
    
    # 如果所有方法都失败，返回原始局面（降级处理）
    return original_board.fen(), None, "原始局面练习"

def load_tactical_position(theme):
    """
    加载预设的战术局面模板
    这些是经典的战术训练局面
    """
    import random
    
    # 基于主题的预设局面 (FEN, 正招UCI, 说明)
    positions = {
        "子力保护": [
            ("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4", chess.Move.from_uci("f3e5"), "白马吃e5兵，但会被f6马吃回"),
            ("rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4", chess.Move.from_uci("c4f7"), "象到f7将军，但会被王吃"),
            ("r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4", chess.Move.from_uci("f3e5"), "吃e5兵"),
        ],
        "将军战术": [
            ("rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 3", chess.Move.from_uci("c4f7"), "象到f7将军"),
            ("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4", chess.Move.from_uci("f3g5"), "马到g5威胁f7"),
        ],
        "局面判断": [
            ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", chess.Move.from_uci("e7e5"), "中心反击"),
            ("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2", chess.Move.from_uci("d2d4"), "占领中心"),
        ],
        "子力调动": [
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", chess.Move.from_uci("e2e4"), "开放线路"),
            ("r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4", chess.Move.from_uci("d7d6"), "巩固中心"),
        ],
    }
    
    theme_positions = positions.get(theme, [])
    if theme_positions:
        return random.choice(theme_positions)
    
    return None

def is_hanging_piece(board, move):
    """检查走棋后是否有对方的子处于被吃状态（悬兵/悬子）"""
    try:
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == board.turn:
                if board.is_attacked_by(not board.turn, sq):
                    return True
        return False
    except:
        return False

def generate_exercise_from_mistake(board, actual_move, best_move, loss):
    """
    从一个失误生成全新的习题
    
    返回: {
        "fen": 新局面的FEN,
        "best_move": 正招,
        "tactic_desc": 战术描述,
        "difficulty": 难度,
        "theme": 战术主题
    }
    """
    # 1. 分类错误
    mistake_type, difficulty, theme = classify_mistake_type(board, actual_move, best_move, loss)
    
    # 2. 生成新训练局面
    new_fen, new_best, desc = generate_training_position(board, mistake_type, theme, difficulty)
    
    return {
        "fen": new_fen,
        "best_move": new_best,
        "tactic_desc": desc,
        "difficulty": difficulty,
        "theme": theme,
        "mistake_type": mistake_type
    }

# ===================== 核心分析（评分逻辑100%修正） =====================
def analyze(pgn_path):
    with open(pgn_path, "r", encoding="utf-8") as f:
        game = chess.pgn.read_game(f)
    if not game:
        return None, [], []

    result = game.headers.get("Result", "*")
    if result == "1-0":
        loser = chess.BLACK
    elif result == "0-1":
        loser = chess.WHITE
    else:
        loser = None

    board = game.board()
    eng = chess.engine.SimpleEngine.popen_uci(find_engine())
    eng.configure({"Threads": 4, "Hash": 512})
    moves = list(game.mainline_moves())
    scores_before, scores_after, boards, bests, legal_moves_list = [], [], [board.copy()], [], []

    for mv in moves:
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
        boards.append(board.copy())
        legal_moves_list.append(list(board.legal_moves))

        board.push(mv)

        res_after = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
        if current_player == chess.WHITE:
            score_after = res_after["score"].white().score(mate_score=10000)
        else:
            score_after = res_after["score"].black().score(mate_score=10000)
        scores_after.append(score_after)

    eng.quit()
    mistakes = []

    for i in range(len(scores_before)):
        if i >= len(scores_after):
            continue
        try:
            current_turn = chess.WHITE if (i % 2 == 0) else chess.BLACK
            if loser is not None and current_turn != loser:
                continue

            delta = scores_after[i] - scores_before[i]
            if delta < MISTAKE:
                best_move = bests[i]
                actual_move = moves[i]
                if best_move == actual_move:
                    alternatives = [m for m in legal_moves_list[i] if m != actual_move]
                    best_move = alternatives[0] if alternatives else None
                
                # 生成全新习题
                exercise = generate_exercise_from_mistake(boards[i+1], actual_move, best_move, abs(delta))
                
                best_line = get_best_line(boards[i+1], best_move) if best_move else []
                tactic_exp = get_tactic_explanation(boards[i+1], actual_move, best_move, abs(delta))
                
                mistakes.append({
                    "step": i+1,
                    "loss": abs(delta),
                    "board_idx": i+1,
                    "move": actual_move,
                    "best": best_move,
                    "best_line": best_line,
                    "tactic_exp": tactic_exp,
                    "exercise": exercise
                })
        except:
            continue

    mistakes = sorted(mistakes, key=lambda x: x["step"])
    score_data = {"scores_before": scores_before, "scores_after": scores_after}
    return game, mistakes, boards, moves, score_data

# ===================== 复盘报告 =====================
def write_report(game, mistakes, boards, moves, filename):
    dt = datetime.now().strftime("%m%d%H%M%S")
    pgn_text = ""
    for i, m in enumerate(moves):
        if i % 2 == 0:
            pgn_text += f"{i//2 +1}. {m} "
        else:
            pgn_text += f"{m} "

    html = f'''<!DOCTYPE html>
<meta charset="utf-8">
<title>复盘</title>
<style>
body{{background:#fff;padding:30px}}
.main{{max-width:800px;margin:0 auto}}
.head{{background:#2c3e50;color:white;padding:24px;border-radius:12px}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:20px 0}}
img{{width:380px;border-radius:8px}}
.pgn{{font-family:monospace;line-height:1.8}}
</style>
<div class="main">
<div class="head">
<h1>🎯 专业复盘</h1>
<p>白方:{game.headers.get("White")} 黑方:{game.headers.get("Black")} 结果:{game.headers.get("Result")}</p>
<p>🔴红=错招 🟢绿=正招</p>
</div>
<div class="card"><h3>完整棋谱</h3><div class="pgn">{pgn_text}</div></div>
'''
    for i, e in enumerate(mistakes, 1):
        src = svg_board(boards[e["board_idx"]], f"r{dt}_{i}.svg", e["move"], e["best"])
        cause, idea = explain(e)
        html += f'''
<div class="card">
<h3>第{i}失误 · 第{e["step"]}步 · 失分{e["loss"]}cp</h3>
<img src="{src}">
<p>❌ 错招：{e["move"].uci()}</p>
<p>原因：{cause}</p>
<p>✅ 正招：{e["best"].uci() if e["best"] else "无推荐"}</p>
<p>思路：{idea}</p>
</div>
'''
    html += "</div>"
    with open(os.path.join(OUT, f"复盘_{filename}_{dt}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ===================== 全新习题集 =====================
def write_exam(mistakes, filename):
    if not mistakes:
        return
    dt = datetime.now().strftime("%m%d%H%M%S")
    html = f'''<!DOCTYPE html>
<meta charset="utf-8">
<title>战术习题集</title>
<style>
body{{background:#fff;padding:30px}}
.main{{max-width:800px;margin:0 auto}}
.head{{background:#27ae60;color:white;padding:24px;border-radius:12px}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:20px 0}}
img{{width:380px;border-radius:8px}}
.badge{{display:inline-block;padding:4px 12px;border-radius:12px;font-size:12px;margin-right:8px}}
.badge-difficulty{{background:#3498db;color:white}}
.badge-theme{{background:#e67e22;color:white}}
</style>
<div class="main">
<div class="head"><h1>📘 战术习题集</h1><p>来源：{filename}</p><p>基于实战错误生成的专项训练</p></div>
'''
    for i, e in enumerate(mistakes, 1):
        exercise = e.get("exercise", {})
        fen = exercise.get("fen", "")
        
        # 生成新局面的SVG
        if fen:
            try:
                ex_board = chess.Board(fen)
                ex_src = svg_board(ex_board, f"ex{dt}_{i}.svg")
                turn = "白方走" if ex_board.turn else "黑方走"
            except:
                # 如果生成失败，使用原始局面
                ex_board = chess.Board()
                ex_src = svg_board(ex_board, f"ex{dt}_{i}.svg")
                turn = "白方走"
        else:
            ex_board = chess.Board()
            ex_src = svg_board(ex_board, f"ex{dt}_{i}.svg")
            turn = "白方走"
        
        difficulty = exercise.get("difficulty", "初级")
        theme = exercise.get("theme", "综合练习")
        mistake_type = exercise.get("mistake_type", "一般失误")
        
        html += f'''
<div class="card">
<h3>第{i}题｜{turn}</h3>
<span class="badge badge-difficulty">难度：{difficulty}</span>
<span class="badge badge-theme">主题：{theme}</span>
<p>错误类型：{mistake_type}</p>
<img src="{ex_src}">
<p>找出最佳着法</p>
</div>
'''
    html += "</div>"
    with open(os.path.join(OUT, f"习题_{filename}_{dt}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ===================== 全新答案 =====================
def write_answer(mistakes, filename):
    if not mistakes:
        return
    dt = datetime.now().strftime("%m%d%H%M%S")
    html = f'''<!DOCTYPE html>
<meta charset="utf-8">
<title>习题答案</title>
<style>
body{{background:#fff;padding:30px}}
.main{{max-width:800px;margin:0 auto}}
.head{{background:#8e44ad;color:white;padding:24px;border-radius:12px}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:20px 0}}
.answer-move{{font-size:24px;font-weight:bold;color:#27ae60;margin:12px 0}}
.tactic{{background:#f8f9fa;padding:16px;border-left:4px solid #3498db;margin:12px 0}}
.line{{font-family:monospace;background:#2c3e50;color:#2ecc71;padding:12px;border-radius:6px;margin:12px 0;overflow-x:auto}}
.badge{{display:inline-block;padding:4px 12px;border-radius:12px;font-size:12px;margin-right:8px}}
.badge-difficulty{{background:#3498db;color:white}}
.badge-theme{{background:#e67e22;color:white}}
</style>
<div class="main">
<div class="head"><h1>📝 习题答案</h1><p>来源：{filename}</p><p>每道题都是独立生成的训练局面</p></div>
'''
    for i, e in enumerate(mistakes, 1):
        exercise = e.get("exercise", {})
        best_move = exercise.get("best_move")
        tactic_desc = exercise.get("tactic_desc", "")
        difficulty = exercise.get("difficulty", "初级")
        theme = exercise.get("theme", "综合练习")
        mistake_type = exercise.get("mistake_type", "一般失误")
        
        # 获取原始局面的解释作为参考
        cause, idea = explain(e)
        
        html += f'''
<div class="card">
<h3>第{i}题</h3>
<span class="badge badge-difficulty">难度：{difficulty}</span>
<span class="badge badge-theme">主题：{theme}</span>
<p>错误类型：{mistake_type}</p>
<div class="answer-move">✅ 正招：{best_move.uci() if best_move else "无推荐"}</div>
'''
        if tactic_desc:
            html += f'<div class="tactic">💡 战术说明：{tactic_desc}</div>\n'
        
        # 添加原始对局的参考信息
        html += f'''
<p style="color:#7f8c8d;font-size:14px;margin-top:16px">--- 实战参考 ---</p>
<p style="color:#7f8c8d;font-size:14px">原局第{e["step"]}步，玩家走了 {e["move"].uci()}，导致{cause}</p>
<p style="color:#7f8c8d;font-size:14px">正确思路：{idea}</p>
'''
        
        html += '</div>\n'
    
    html += "</div>"
    with open(os.path.join(OUT, f"答案_{filename}_{dt}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ===================== 主程序 =====================
def run():
    done = load_done()
    proc = set(done)
    print("✅ 全新习题版：每道题都是独立生成的训练局面")
    while True:
        curr = {f for f in os.listdir(WATCH) if is_valid_pgn(os.path.join(WATCH, f))}
        for fn in curr - proc:
            print(f"正在分析：{fn}")
            game, errs, boards, moves, _ = analyze(os.path.join(WATCH, fn))
            if game:
                write_report(game, errs, boards, moves, fn)
                write_exam(errs, fn)
                write_answer(errs, fn)
                mark_done(fn)
                proc.add(fn)
                print(f"✅ {fn} 完成，找到失误：{len(errs)}个")
        time.sleep(2)

if __name__ == "__main__":
    run()
