# -*- coding: utf-8 -*-
"""
专业国际象棋自动复盘系统 Pro版
基于真实PGN + Stockfish深度25分析
适配中国棋协二级→一级水平（1400-1650 ELO）
"""
import os
import time
import chess
import chess.pgn
import chess.engine
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
from PIL import Image, ImageDraw
import io

# 注册中文字体
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT_CN = 'STSong-Light'

# ===================== 配置 =====================
WATCH_FOLDER = r"f:\trae项目\Chess\test"
STOCKFISH_PATH = r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"
OUTPUT_ROOT = r"f:\trae项目\Chess\test_output"
ANALYZED_LOG = os.path.join(OUTPUT_ROOT, "analyzed.txt")
ANALYSIS_DEPTH = 25
EXERCISE_COUNT = 10
LEVEL = "二级→一级（1400-1650）"
BLUNDER_THRESHOLD = 150  # CP失分阈值
# =================================================

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_ROOT, "report"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_ROOT, "exercise"), exist_ok=True)


def load_analyzed():
    """加载已分析文件列表"""
    if not os.path.exists(ANALYZED_LOG):
        return set()
    with open(ANALYZED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_analyzed(name):
    """记录已分析文件"""
    with open(ANALYZED_LOG, "a", encoding="utf-8") as f:
        f.write(name + "\n")


def generate_board_image(fen, size=200):
    """生成棋盘图像"""
    board = chess.Board(fen)
    img = Image.new('RGB', (size, size), '#F0D9B5')
    draw = ImageDraw.Draw(img)
    
    square_size = size // 8
    colors = ['#F0D9B5', '#B58863']
    
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            x1 = col * square_size
            y1 = row * square_size
            x2 = x1 + square_size
            y2 = y1 + square_size
            draw.rectangle([x1, y1, x2, y2], fill=color)
            
            piece = board.piece_at(chess.square(col, 7-row))
            if piece:
                piece_chars = {
                    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
                    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
                }
                char = piece_chars.get(piece.symbol(), '?')
                text_color = '#FFFFFF' if piece.color else '#000000'
                bbox = draw.textbbox((0, 0), char)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                text_x = x1 + (square_size - text_w) // 2
                text_y = y1 + (square_size - text_h) // 2
                draw.text((text_x, text_y), char, fill=text_color)
    
    return img


def analyze_game(pgn_path):
    """分析PGN对局"""
    analyzed = load_analyzed()
    pgn_name = os.path.basename(pgn_path)
    
    if pgn_name in analyzed:
        print(f"[SKIP] 已分析: {pgn_name}")
        return None, None

    with open(pgn_path, encoding="utf-8") as f:
        game = chess.pgn.read_game(f)
    
    if not game:
        print(f"[ERROR] 无法读取: {pgn_name}")
        return None, None

    print(f"[ANALYZE] {pgn_name}")
    
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    scores = []
    moves = list(game.mainline_moves())
    print(f"  总回合: {len(moves)}")
    
    for idx, move in enumerate(moves):
        res = engine.analyse(board, chess.engine.Limit(depth=ANALYSIS_DEPTH))
        score = res["score"].white().score(mate_score=1000)
        scores.append(score)
        board.push(move)
    
    engine.quit()

    # 检测关键失误
    key_mistakes = []
    for i in range(1, len(scores)):
        delta = scores[i] - scores[i-1]
        if delta < -BLUNDER_THRESHOLD:
            key_mistakes.append({
                "step": i+1,
                "move": moves[i].uci(),
                "loss": abs(delta),
                "fen": board.fen()  # 当前局面
            })
            if len(key_mistakes) >= 3:
                break

    print(f"  关键失误: {len(key_mistakes)}个")
    return game, key_mistakes


def make_pdf_report(game, mistakes, pgn_name):
    """生成复盘报告PDF"""
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(OUTPUT_ROOT, "report", f"report_{pgn_name}_{dt}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # 标题
    c.setFont(FONT_CN, 18)
    c.drawString(50, height-50, "专业国际象棋复盘报告")
    
    # 对局信息
    c.setFont(FONT_CN, 12)
    y = height - 100
    c.drawString(50, y, f"白方: {game.headers.get('White', '?')}")
    y -= 25
    c.drawString(50, y, f"黑方: {game.headers.get('Black', '?')}")
    y -= 25
    c.drawString(50, y, f"结果: {game.headers.get('Result', '?')}")
    y -= 25
    c.drawString(50, y, f"日期: {game.headers.get('Date', '?')}")
    y -= 25
    c.drawString(50, y, f"等级: {LEVEL}")
    y -= 25
    c.drawString(50, y, f"引擎深度: {ANALYSIS_DEPTH}")
    
    # 关键失误
    y -= 40
    c.setFont(FONT_CN, 14)
    c.drawString(50, y, "=== 关键失误分析 ===")
    y -= 30
    
    c.setFont(FONT_CN, 11)
    if mistakes:
        for m in mistakes:
            c.drawString(50, y, f"第{m['step']}步 | 失分: {m['loss']}cp | 着法: {m['move']}")
            y -= 20
            # 添加棋盘图
            if y < 200:
                c.showPage()
                c.setFont(FONT_CN, 11)
                y = height - 50
            try:
                board_img = generate_board_image(m['fen'], 150)
                img_buffer = io.BytesIO()
                board_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                c.drawImage(img_buffer, 50, y-160, width=150, height=150)
                y -= 180
            except Exception as e:
                print(f"[WARN] 棋盘图生成失败: {e}")
    else:
        c.drawString(50, y, "本局未检测到明显失误（>150cp）")
    
    c.save()
    print(f"[OK] 复盘报告: {pdf_path}")
    return pdf_path


def make_pdf_exercise(game, mistakes, pgn_name):
    """生成习题集PDF"""
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(OUTPUT_ROOT, "exercise", f"exercise_{pgn_name}_{dt}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # 标题
    c.setFont(FONT_CN, 18)
    c.drawString(50, height-50, "国际象棋专项习题集")
    
    # 信息
    c.setFont(FONT_CN, 12)
    y = height - 100
    c.drawString(50, y, f"等级：{LEVEL}")
    y -= 25
    c.drawString(50, y, f"来源：{pgn_name}")
    y -= 25
    c.drawString(50, y, f"题量：{EXERCISE_COUNT}题")
    y -= 25
    c.drawString(50, y, "说明：基于本局失误局面生成，找出最佳着法")
    
    # 习题
    y -= 40
    c.setFont(FONT_CN, 14)
    c.drawString(50, y, "=== 习题 ===")
    y -= 30
    
    board = game.board()
    moves = list(game.mainline_moves())
    
    # 从失误中提取局面作为习题
    exercise_fens = []
    for m in mistakes[:3]:
        exercise_fens.append(m['fen'])
    
    # 补充到10题
    for i in range(len(moves)):
        if len(exercise_fens) >= EXERCISE_COUNT:
            break
        board.push(moves[i])
        if i % 5 == 0 and board.fen() not in exercise_fens:
            exercise_fens.append(board.fen())
    
    c.setFont(FONT_CN, 11)
    for i, fen in enumerate(exercise_fens[:EXERCISE_COUNT], 1):
        if y < 250:
            c.showPage()
            c.setFont(FONT_CN, 11)
            y = height - 50
        
        c.drawString(50, y, f"第{i}题：请找出最佳着法")
        y -= 20
        c.drawString(50, y, f"FEN: {fen[:60]}...")
        y -= 20
        
        # 添加棋盘图
        try:
            board_img = generate_board_image(fen, 150)
            img_buffer = io.BytesIO()
            board_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            c.drawImage(img_buffer, 50, y-160, width=150, height=150)
            y -= 180
        except Exception as e:
            print(f"[WARN] 棋盘图生成失败: {e}")
            y -= 20
        
        # 答案区域
        c.drawString(50, y, "答案：________________")
        y -= 30
    
    c.save()
    print(f"[OK] 习题集: {pdf_path}")
    return pdf_path


def run_monitor():
    """主监控循环"""
    print("="*60)
    print("    专业国际象棋自动复盘系统（二级→一级）")
    print("="*60)
    print(f"[OK] 监控目录：{WATCH_FOLDER}")
    print(f"[OK] 引擎深度：{ANALYSIS_DEPTH}")
    print(f"[OK] 每局习题：{EXERCISE_COUNT}题")
    print(f"[OK] 输出目录：{OUTPUT_ROOT}")
    print("="*60)
    print()

    while True:
        try:
            files = [f for f in os.listdir(WATCH_FOLDER) if f.endswith(".pgn")]
            analyzed = load_analyzed()
            
            for fname in files:
                if fname in analyzed:
                    continue
                
                path = os.path.join(WATCH_FOLDER, fname)
                game, mistakes = analyze_game(path)
                
                if not game:
                    continue
                
                make_pdf_report(game, mistakes, fname)
                make_pdf_exercise(game, mistakes, fname)
                save_analyzed(fname)
                
                print(f"[OK] 完成：{fname}")
                print()
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n[OK] 程序已停止")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    run_monitor()
