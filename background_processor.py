import os
import time
import json
import chess
import chess.pgn
import chess.engine
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# ===================== 路径配置 =====================
WATCH       = r"D:\Chess_PGN_Receive"
OUT         = r"D:\Chess_Output"
LOG         = os.path.join(OUT, "analyzed.txt")
STATUS_FILE = os.path.join(OUT, "processing_status.json")
DEPTH       = 14  # 优化后的深度
MOVE_TIME   = 0.8  # 优化后的时间
MISTAKE     = -100
# ====================================================

os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "images"), exist_ok=True)

# ===================== 工具函数 =====================
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

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

# ===================== 核心分析 =====================
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
                
                mistakes.append({
                    "step": i+1,
                    "loss": abs(delta),
                    "board_idx": i+1,
                    "move": actual_move.uci(),
                    "best": best_move.uci() if best_move else None
                })
        except:
            continue

    mistakes = sorted(mistakes, key=lambda x: x["step"])
    score_data = {"scores_before": scores_before, "scores_after": scores_after}
    return game, mistakes, boards, moves, score_data

# ===================== 生成报告 =====================
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
        html += f'''
<div class="card">
<h3>第{i}失误 · 第{e["step"]}步 · 失分{e["loss"]}cp</h3>
<p>❌ 错招：{e["move"]}</p>
<p>✅ 正招：{e["best"] if e["best"] else "无推荐"}</p>
</div>
'''
    html += "</div>"
    report_path = os.path.join(OUT, f"复盘_{filename}_{dt}.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    return report_path

# ===================== 处理单个文件 =====================
def process_file(pgn_path):
    filename = os.path.basename(pgn_path)
    status = load_status()
    
    try:
        status[filename] = {
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "path": pgn_path
        }
        save_status(status)
        
        print(f"正在分析：{filename}")
        game, errs, boards, moves, _ = analyze(pgn_path)
        
        if game:
            report_path = write_report(game, errs, boards, moves, filename)
            mark_done(filename)
            status[filename] = {
                "status": "completed",
                "start_time": status[filename]["start_time"],
                "end_time": datetime.now().isoformat(),
                "path": pgn_path,
                "report_path": report_path,
                "mistakes_count": len(errs)
            }
            print(f"✅ {filename} 完成，找到失误：{len(errs)}个")
        else:
            status[filename] = {
                "status": "failed",
                "start_time": status[filename]["start_time"],
                "end_time": datetime.now().isoformat(),
                "path": pgn_path,
                "error": "无法解析PGN文件"
            }
            print(f"❌ {filename} 分析失败")
    except Exception as e:
        status[filename] = {
            "status": "failed",
            "start_time": status[filename]["start_time"],
            "end_time": datetime.now().isoformat(),
            "path": pgn_path,
            "error": str(e)
        }
        print(f"❌ {filename} 处理出错：{e}")
    finally:
        save_status(status)

# ===================== 扫描和处理 =====================
def scan_and_process():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始扫描PGN文件...")
    done = load_done()
    status = load_status()
    
    if not os.path.exists(WATCH):
        print("PGN目录不存在，跳过扫描")
        return
    
    for filename in os.listdir(WATCH):
        if filename.endswith(".pgn") and filename not in done:
            pgn_path = os.path.join(WATCH, filename)
            if is_valid_pgn(pgn_path):
                file_status = status.get(filename, {})
                if file_status.get("status") not in ["processing", "completed"]:
                    process_file(pgn_path)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 扫描完成")

# ===================== 主函数 =====================
def main():
    print("✅ 后台PGN处理器启动")
    print(f"监控目录：{WATCH}")
    print(f"输出目录：{OUT}")
    
    # 立即执行一次扫描
    scan_and_process()
    
    # 创建后台调度器
    scheduler = BackgroundScheduler()
    
    # 每5分钟执行一次扫描
    scheduler.add_job(scan_and_process, 'interval', minutes=5, id='scan_pgn_files')
    
    # 启动调度器
    scheduler.start()
    
    print("✅ 定时任务已启动，每5分钟扫描一次")
    print("按 Ctrl+C 退出...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止后台处理器...")
        scheduler.shutdown()
        print("✅ 后台处理器已停止")

if __name__ == "__main__":
    main()
