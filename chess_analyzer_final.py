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
        # 使用MultiPV获取多个候选着法
        eng.configure({"MultiPV": 5})
        res = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
        eng.quit()
        
        # python-chess MultiPV返回的是列表，每个元素是dict
        if isinstance(res, list):
            for r in res:
                pv = r.get("pv", [])
                if pv and pv[0] != exclude_move:
                    return pv[0]
        # 如果不是列表，尝试从单PV结果中获取
        elif isinstance(res, dict):
            pv = res.get("pv", [])
            # 如果PV第一个就是exclude_move，尝试返回第二个
            if pv and len(pv) > 1 and pv[0] == exclude_move:
                return pv[1]
            # 如果第一个不是exclude_move，直接返回
            elif pv and pv[0] != exclude_move:
                return pv[0]
        
        # 最后的备选：从所有合法着法中随机选一个不同的
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
        
        # 复制棋盘，执行正招
        temp_board = board.copy()
        if best_move and best_move in temp_board.legal_moves:
            temp_board.push(best_move)
        else:
            eng.quit()
            return []
        
        # 分析正招后的局面，获取后续变化线
        res = eng.analyse(temp_board, chess.engine.Limit(depth=depth, time=move_time))
        eng.quit()
        
        pv = res.get("pv", [])
        # 返回前5步（或更少）
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

def analyze_tactic_situation(board, actual_move, best_move):
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
        current_player = board.turn
        opponent = not current_player
        
        if actual_move in board.legal_moves:
            temp_board = board.copy()
            temp_board.push(actual_move)
            
            if temp_board.is_check():
                analysis['threats'].append('将军')
            
            if temp_board.is_capture(actual_move):
                captured = temp_board.piece_at(actual_move.to_square)
                if captured:
                    analysis['captured_piece'] = {
                        'symbol': captured.symbol(),
                        'name': piece_names.get(captured.symbol().upper(), '未知'),
                        'value': piece_values.get(captured.symbol().upper(), 0),
                        'square': chess.square_name(actual_move.to_square)
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
        
        if best_move and best_move in board.legal_moves:
            best_board = board.copy()
            best_board.push(best_move)
            
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
        print(f"  分析战术局面出错: {e}")
    
    return analysis

def get_tactic_explanation(board, actual_move, best_move, loss):
    """生成详细的战术解释"""
    try:
        analysis = analyze_tactic_situation(board, actual_move, best_move)
        parts = []
        
        if analysis['captured_piece']:
            cap = analysis['captured_piece']
            parts.append(f"⚠️ **立即丢子**: 你走{actual_move.uci()}后，{cap['name']}在{cap['square']}被对方直接吃掉")
        
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
            parts.append(f"✅ **正招作用**: {best_move.uci()}保护了{defended_names}，避免被吃")
        
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
        print(f"  生成战术解释出错: {e}")
        return f"这步棋导致约{loss/100:.1f}子的损失，正招{best_move.uci() if best_move else '未知'}可以改善局面。"

# ===================== 核心分析（评分逻辑100%修正） =====================
def analyze(pgn_path):
    with open(pgn_path, "r", encoding="utf-8") as f:
        game = chess.pgn.read_game(f)
    if not game:
        return None, [], []

    # 判断败方：根据Result字段
    # "1-0" -> 白胜，黑方是败方
    # "0-1" -> 黑胜，白方是败方
    # "1/2-1/2" -> 和棋，分析双方
    result = game.headers.get("Result", "*")
    if result == "1-0":
        loser = chess.BLACK  # 黑方败
    elif result == "0-1":
        loser = chess.WHITE  # 白方败
    else:
        loser = None  # 和棋或其他，分析双方

    board = game.board()
    eng = chess.engine.SimpleEngine.popen_uci(find_engine())
    eng.configure({"Threads": 4, "Hash": 512})
    moves = list(game.mainline_moves())
    scores_before, scores_after, boards, bests, legal_moves_list = [], [], [board.copy()], [], []

    for mv in moves:
        # 记录当前走棋方（走棋前的回合）
        current_player = board.turn

        # 1. 走棋前：分析当前局面，获取评分和最佳走法
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

        # 2. 走棋，进入下一个局面
        board.push(mv)

        # 3. 走棋后：分析新局面，获取评分（从走棋方视角）
        res_after = eng.analyse(board, chess.engine.Limit(depth=DEPTH, time=MOVE_TIME))
        if current_player == chess.WHITE:
            score_after = res_after["score"].white().score(mate_score=10000)
        else:
            score_after = res_after["score"].black().score(mate_score=10000)
        scores_after.append(score_after)

    eng.quit()
    mistakes = []

    # 评分变化计算：走棋后评分 - 走棋前评分，负数代表失分
    for i in range(len(scores_before)):
        if i >= len(scores_after):
            continue
        try:
            # 判断当前步是谁走的
            current_turn = chess.WHITE if (i % 2 == 0) else chess.BLACK
            # 如果指定了败方，只分析败方的走法
            if loser is not None and current_turn != loser:
                continue

            delta = scores_after[i] - scores_before[i]
            best_move = bests[i]
            actual_move = moves[i]
            
            # 如果玩家走的就是最佳着法，跳过（不是失误）
            if best_move == actual_move:
                continue
                
            # 只有当失分超过阈值时才标记为失误
            if delta < MISTAKE:
                # 获取正招的后续变化线
                best_line = get_best_line(boards[i+1], best_move) if best_move else []
                tactic_exp = get_tactic_explanation(boards[i+1], actual_move, best_move, abs(delta))
                
                mistakes.append({
                    "step": i+1,
                    "loss": abs(delta),
                    "board_idx": i+1,
                    "move": actual_move,
                    "best": best_move,
                    "best_line": best_line,
                    "tactic_exp": tactic_exp
                })
        except Exception as e:
            print(f"  分析第{i+1}步出错: {e}")
            continue

    mistakes = sorted(mistakes, key=lambda x: x["step"])
    # 同时返回评分数据供测试验证
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

# ===================== 习题集 =====================
def write_exam(mistakes, boards, filename):
    if not mistakes:
        return
    dt = datetime.now().strftime("%m%d%H%M%S")
    html = f'''<!DOCTYPE html>
<meta charset="utf-8">
<title>习题集</title>
<style>
body{{background:#fff;padding:30px}}
.main{{max-width:800px;margin:0 auto}}
.head{{background:#27ae60;color:white;padding:24px;border-radius:12px}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:20px 0}}
img{{width:380px;border-radius:8px}}
</style>
<div class="main">
<div class="head"><h1>📘 战术习题</h1><p>来源：{filename}</p></div>
'''
    for i, e in enumerate(mistakes, 1):
        src = svg_board(boards[e["board_idx"]], f"ex{dt}_{i}.svg")
        turn = "白方走" if boards[e["board_idx"]].turn else "黑方走"
        html += f'''
<div class="card">
<h3>第{i}题｜{turn}</h3>
<img src="{src}">
<p>找出最佳防守着法</p>
</div>
'''
    html += "</div>"
    with open(os.path.join(OUT, f"习题_{filename}_{dt}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ===================== 答案 =====================
def write_answer(mistakes, boards, filename):
    if not mistakes:
        return
    dt = datetime.now().strftime("%m%d%H%M%S")
    html = f'''<!DOCTYPE html>
<meta charset="utf-8">
<title>答案</title>
<style>
body{{background:#fff;padding:30px}}
.main{{max-width:800px;margin:0 auto}}
.head{{background:#8e44ad;color:white;padding:24px;border-radius:12px}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:20px 0}}
.answer-move{{font-size:24px;font-weight:bold;color:#27ae60;margin:12px 0}}
.tactic{{background:#f8f9fa;padding:16px;border-left:4px solid #3498db;margin:12px 0}}
.line{{font-family:monospace;background:#2c3e50;color:#2ecc71;padding:12px;border-radius:6px;margin:12px 0;overflow-x:auto}}
</style>
<div class="main">
<div class="head"><h1>📝 习题答案</h1><p>来源：{filename}</p></div>
'''
    for i, e in enumerate(mistakes, 1):
        # 格式化后续变化线
        line_text = ""
        if e.get("best_line"):
            line_text = format_line(boards[e["board_idx"]], e["best_line"])
        
        # 获取战术解释
        tactic_text = e.get("tactic_exp", "")
        
        # 获取复盘中的原因和思路
        cause, idea = explain(e)
        
        html += f'''
<div class="card">
<h3>第{i}题 · 第{e["step"]}步</h3>
<p>❌ 错招：<span style="color:#e74c3c;font-weight:bold">{e["move"].uci()}</span></p>
<p>原因：{cause}</p>
<div class="answer-move">✅ 正招：{e["best"].uci() if e["best"] else "无推荐"}</div>
<p>思路：{idea}</p>
'''
        if tactic_text:
            html += f'<div class="tactic">💡 战术解读：{tactic_text}</div>\n'
        
        if line_text:
            html += f'<p>后续变化线：</p><div class="line">{line_text}</div>\n'
        
        html += '</div>\n'
    
    html += "</div>"
    with open(os.path.join(OUT, f"答案_{filename}_{dt}.html"), "w", encoding="utf-8") as f:
        f.write(html)

# ===================== 主程序 =====================
def run():
    done = load_done()
    proc = set(done)
    print("✅ 最终修复版：评分逻辑修正，错招正招强制区分")
    while True:
        curr = {f for f in os.listdir(WATCH) if is_valid_pgn(os.path.join(WATCH, f))}
        for fn in curr - proc:
            print(f"正在分析：{fn}")
            game, errs, boards, moves, _ = analyze(os.path.join(WATCH, fn))
            if game:
                write_report(game, errs, boards, moves, fn)
                write_exam(errs, boards, fn)
                write_answer(errs, boards, fn)
                mark_done(fn)
                proc.add(fn)
                print(f"✅ {fn} 完成，找到失误：{len(errs)}个")
        time.sleep(2)

if __name__ == "__main__":
    run()