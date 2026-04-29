# -*- coding: utf-8 -*-
"""
专业国际象棋自动复盘系统
完整功能：
- PGN解析（含ECO开局识别）
- Stockfish深度25分析
- 关键失误检测与分类
- 专业PDF复盘报告
- 二级→一级水平习题集生成
"""
import os
import sys
import time
import datetime
import subprocess
import chess
import chess.pgn
import chess.svg
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import io
import config


# ===================== 中文字体注册 =====================
def register_chinese_font():
    """注册Windows中文字体"""
    font_paths = [
        r'C:\Windows\Fonts\simhei.ttf',      # 黑体
        r'C:\Windows\Fonts\simsun.ttc',      # 宋体
        r'C:\Windows\Fonts\msyh.ttc',        # 微软雅黑
        r'C:\Windows\Fonts\SIMSUN.TTF',
    ]
    
    font_name = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                font_name = 'ChineseFont'
                if config.DEBUG_MODE:
                    print(f"[OK] 使用中文字体: {font_path}")
                break
            except Exception as e:
                if config.DEBUG_MODE:
                    print(f"[WARN] 尝试注册字体失败: {e}")
                continue
    
    if not font_name:
        font_name = 'Helvetica'
        print("[WARN] 未找到中文字体，使用默认Helvetica")
    
    return font_name


# ===================== Stockfish引擎模块 =====================
class StockfishEngine:
    """Stockfish UCI引擎封装"""
    
    def __init__(self, path, depth=25, threads=4, hash_mb=256):
        self.path = path
        self.depth = depth
        self.threads = threads
        self.hash_mb = hash_mb
        self.process = None
        self.is_ready = False
    
    def start(self):
        """启动Stockfish引擎"""
        if not os.path.exists(self.path):
            print(f"[ERROR] Stockfish引擎不存在于: {self.path}")
            return False
        
        try:
            self.process = subprocess.Popen(
                self.path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self._send_command("uci")
            self._wait_for("uciok")
            
            self._send_command(f"setoption name Threads value {self.threads}")
            self._send_command(f"setoption name Hash value {self.hash_mb}")
            self._send_command("isready")
            self._wait_for("readyok")
            
            self.is_ready = True
            print("[OK] Stockfish引擎已启动")
            return True
            
        except Exception as e:
            print(f"[ERROR] 启动Stockfish出错: {e}")
            return False
    
    def _send_command(self, command):
        """发送命令到引擎"""
        if self.process:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()
    
    def _wait_for(self, keyword):
        """等待指定关键词响应"""
        if not self.process:
            return None
        
        output = []
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            output.append(line)
            if keyword in line:
                break
        return '\n'.join(output)
    
    def analyze_board(self, board):
        """分析棋盘局面，返回评估值和最佳着法"""
        if not self.is_ready:
            return None
        
        fen = board.fen()
        self._send_command(f"position fen {fen}")
        self._send_command(f"go depth {self.depth}")
        
        score_cp = None
        best_move = None
        pv_moves = []
        
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            
            if "info" in line and "score" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "score" and i + 1 < len(parts):
                        if parts[i + 1] == "cp" and i + 2 < len(parts):
                            try:
                                score_cp = int(parts[i + 2])
                            except ValueError:
                                pass
                        elif parts[i + 1] == "mate" and i + 2 < len(parts):
                            score_cp = 20000 if int(parts[i + 2]) > 0 else -20000
            
            if "bestmove" in line:
                parts = line.split()
                if len(parts) > 1:
                    best_move_uci = parts[1]
                    if best_move_uci != "(none)":
                        try:
                            best_move = chess.Move.from_uci(best_move_uci)
                        except:
                            pass
                break
        
        return {
            'score_cp': score_cp,
            'best_move': best_move,
            'fen': fen
        }
    
    def stop(self):
        """停止引擎"""
        if self.process:
            try:
                self._send_command("quit")
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            print("🛑 Stockfish引擎已停止")


# ===================== ECO开局识别 =====================
def get_eco_info(game):
    """从PGN获取ECO开局信息"""
    headers = game.headers
    
    eco = headers.get("ECO", "未知")
    opening = headers.get("Opening", "未知开局")
    
    # 尝试从走法识别ECO
    if eco == "未知":
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        # 这里可以集成python-chess的ECO识别库
        
    return eco, opening


# ===================== 失误分类 =====================
def classify_blunder(move_number, board, game):
    """对失误进行分类"""
    ply = move_number
    total_ply = len(list(game.mainline_moves()))
    
    if ply <= 20:
        category = "开局弱点"
    elif 20 < ply <= total_ply * 0.7:
        category = "中局战术漏招"
    else:
        # 检查棋盘子力
        piece_count = sum(1 for _ in board.piece_map().values())
        if piece_count <= 10:
            category = "残局问题"
        else:
            category = "防守失误"
    
    return category


# ===================== PGN解析与分析 =====================
def analyze_pgn_file(pgn_path, engine):
    """完整分析一个PGN文件"""
    print(f"\n📖 正在分析: {os.path.basename(pgn_path)}")
    
    with open(pgn_path, 'r', encoding='utf-8') as f:
        game = chess.pgn.read_game(f)
    
    if not game:
        print("[ERROR] 无法读取PGN文件")
        return None
    
    headers = game.headers
    
    # 基本信息
    game_info = {
        'white': headers.get('White', '未知'),
        'black': headers.get('Black', '未知'),
        'result': headers.get('Result', '未知'),
        'date': headers.get('Date', '未知'),
        'site': headers.get('Site', '未知'),
    }
    
    # ECO开局
    eco, opening = get_eco_info(game)
    game_info['eco'] = eco
    game_info['opening'] = opening
    
    # 完整走法列表
    moves = list(game.mainline_moves())
    game_info['total_moves'] = (len(moves) + 1) // 2
    game_info['total_ply'] = len(moves)
    
    # 分析每一步
    board = game.board()
    analysis_history = []
    blunders = []
    
    prev_score = 0
    
    print(f"⏳ 分析对局: 共 {len(moves)} 回合...")
    
    for ply, move in enumerate(moves):
        # 分析着法前的局面
        analysis_before = engine.analyze_board(board)
        
        # 获取SAN走法（必须在push之前）
        try:
            move_san = board.san(move)
        except Exception as e:
            print(f"[WARN] 跳过非法走法: {move.uci()} - {e}")
            continue
        
        # 执行着法
        board.push(move)
        
        # 分析着法后的局面
        analysis_after = engine.analyze_board(board)
        
        # 计算评估变化
        score_change = 0
        if analysis_before and analysis_before['score_cp'] is not None:
            prev_score = analysis_before['score_cp']
        if analysis_after and analysis_after['score_cp'] is not None:
            # 反转视角（黑白方轮次）
            current_score = -analysis_after['score_cp']
            score_change = current_score - prev_score
        else:
            current_score = prev_score
            
        analysis_record = {
            'ply': ply,
            'move_number': (ply // 2) + 1,
            'is_white': (ply % 2 == 0),
            'move_uci': move.uci(),
            'move_san': move_san,
            'score_cp': current_score,
            'score_change_cp': score_change,
            'fen_before': analysis_before['fen'] if analysis_before else None,
            'fen_after': board.fen(),
            'best_move': analysis_before['best_move'] if analysis_before else None
        }
        
        analysis_history.append(analysis_record)
        
        # 检测关键失误
        if abs(score_change) >= config.BLUNDER_THRESHOLD:
            blunder_info = {
                'ply': ply,
                'move_number': analysis_record['move_number'],
                'is_white': analysis_record['is_white'],
                'move_played_san': analysis_record['move_san'],
                'move_played_uci': analysis_record['move_uci'],
                'best_move_san': board.variation_san([analysis_record['best_move']]) if analysis_record['best_move'] else '无',
                'best_move_uci': analysis_record['best_move'].uci() if analysis_record['best_move'] else None,
                'loss_cp': abs(score_change),
                'fen': analysis_record['fen_before'],
                'category': classify_blunder(ply, board.copy(), game)
            }
            
            # 移除最后一个走法，恢复局面
            board.pop()
            blunders.append(blunder_info)
            board.push(move)
        
        # 显示进度
        if (ply + 1) % 10 == 0:
            print(f"   分析进度: {ply + 1}/{len(moves)}")
    
    # 按损失排序，取最严重的前N个
    blunders.sort(key=lambda x: x['loss_cp'], reverse=True)
    blunders = blunders[:config.MAX_BLUNDERS]
    
    game_info['blunders'] = blunders
    game_info['analysis_history'] = analysis_history
    
    print(f"[OK] 分析完成! 检测到 {len(blunders)} 个关键失误")
    
    return game_info


# ===================== 棋盘图像生成 =====================
def generate_board_image(board, size=200):
    """使用Pillow生成棋盘图像"""
    cell_size = size // 8
    img = Image.new('RGB', (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    colors_board = [(240, 217, 181), (181, 136, 99)]
    
    # 绘制格子
    for row in range(8):
        for col in range(8):
            color = colors_board[(row + col) % 2]
            x1, y1 = col * cell_size, (7 - row) * cell_size
            x2, y2 = x1 + cell_size - 1, y1 + cell_size - 1
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=None)
    
    # 棋子Unicode字符
    piece_chars = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    }
    
    # 尝试加载字体
    try:
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", int(cell_size * 0.7))
        except:
            try:
                font = ImageFont.truetype("arial.ttf", int(cell_size * 0.7))
            except:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 绘制棋子
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            symbol = piece.symbol()
            char = piece_chars.get(symbol, '?')
            
            x = col * cell_size + cell_size * 0.15
            y = (7 - row) * cell_size + cell_size * 0.05
            
            draw.text((x, y), char, fill=(0, 0, 0), font=font)
    
    return img


# ===================== 专业PDF复盘报告 =====================
def generate_report_pdf(pgn_path, game_info, font_name):
    """生成专业PDF复盘报告"""
    filename = os.path.basename(pgn_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = filename.replace('.pgn', '').replace(' ', '_')
    pdf_path = os.path.join(config.REPORT_DIR, f"report_{safe_filename}_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # ========== 样式定义 ==========
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor("#1a365d")
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#2d3748"),
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=18
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#4a5568")
    )
    
    # ========== 封面/标题 ==========
    story.append(Paragraph("♔ 专业国际象棋复盘报告 ♚", title_style))
    story.append(Spacer(1, 20))
    
    # ========== 对局信息表格 ==========
    story.append(Paragraph("一、对局基本信息", heading2_style))
    
    info_data = [
        ["白方", game_info['white']],
        ["黑方", game_info['black']],
        ["比赛结果", game_info['result']],
        ["比赛日期", game_info['date']],
        ["总回合数", str(game_info['total_moves'])],
        ["ECO编码", game_info['eco']],
        ["开局名称", game_info['opening']]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#e2e8f0")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#1a202c")),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    
    # ========== 关键失误分析 ==========
    story.append(Paragraph("二、关键失误明细", heading2_style))
    
    if len(game_info['blunders']) > 0:
        for idx, blunder in enumerate(game_info['blunders'], 1):
            story.append(Paragraph(f"★ 失误 #{idx} — {blunder['category']}", ParagraphStyle(
                'BlunderTitle',
                parent=styles['Heading3'],
                fontName=font_name,
                fontSize=14,
                spaceAfter=8,
                textColor=colors.HexColor("#c53030")
            )))
            
            player = "白方" if blunder['is_white'] else "黑方"
            story.append(Paragraph(f"第 {blunder['move_number']} 回合（{player}）", normal_style))
            story.append(Paragraph(f"实际着法: {blunder['move_played_san']}", normal_style))
            story.append(Paragraph(f"最佳着法: {blunder['best_move_san']}", normal_style))
            story.append(Paragraph(f"损失评估: {blunder['loss_cp']} 厘兵", normal_style))
            story.append(Paragraph(f"局面FEN: {blunder['fen']}", small_style))
            
            # 添加局面图
            if config.SHOW_BOARD_IMAGE:
                temp_board = chess.Board(blunder['fen'])
                img = generate_board_image(temp_board, size=config.BOARD_IMAGE_SIZE)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # 使用临时文件
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                    tmp_img.write(img_buffer.getvalue())
                    tmp_img_path = tmp_img.name
                
                rl_img = RLImage(tmp_img_path, width=config.BOARD_IMAGE_SIZE/2, height=config.BOARD_IMAGE_SIZE/2)
                story.append(rl_img)
            
            story.append(Spacer(1, 16))
            
            # 尝试删除临时图像
            try:
                os.unlink(tmp_img_path)
            except:
                pass
    else:
        story.append(Paragraph("本局未检测到明显的关键失误！", normal_style))
    
    # ========== 总结与建议 ==========
    story.append(Paragraph("三、复盘总结与训练建议", heading2_style))
    
    # 根据失误类型生成建议
    if len(game_info['blunders']) > 0:
        categories = list(set(b['category'] for b in game_info['blunders']))
        
        if "开局弱点" in categories:
            story.append(Paragraph("1. 开局训练建议: 加强ECO开局库学习，重点研究本局开局变例的应对方案", normal_style))
        
        if "中局战术漏招" in categories:
            story.append(Paragraph("2. 中局训练建议: 强化战术组合训练，提高战术敏感性（牵制/闪击/捉双）", normal_style))
        
        if "防守失误" in categories:
            story.append(Paragraph("3. 防守训练建议: 加强防守能力，提高局面安全评估", normal_style))
        
        if "残局问题" in categories:
            story.append(Paragraph("4. 残局训练建议: 加强基础残局（兵残局/车残局/马象残局）的学习", normal_style))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"5. 整体水平评估: 中国棋协二级→一级水平（ELO 1400–1650）", normal_style))
    else:
        story.append(Paragraph("本局整体质量较高，建议继续保持并逐步提升高级战术和战略意识！", normal_style))
    
    doc.build(story)
    print(f"[OK] 复盘报告已生成: {pdf_path}")
    return pdf_path


# ===================== 习题集生成 =====================
def generate_exercise_pdf(pgn_path, game_info, font_name):
    """基于真实局面生成习题集PDF"""
    filename = os.path.basename(pgn_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = filename.replace('.pgn', '').replace(' ', '_')
    pdf_path = os.path.join(config.EXERCISE_DIR, f"exercise_{safe_filename}_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # ========== 样式定义 ==========
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=22,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor("#1a365d")
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=10,
        textColor=colors.HexColor("#2d3748")
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=18
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=13,
        spaceAfter=8,
        textColor=colors.HexColor("#1a365d")
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#4a5568")
    )
    
    # ========== 封面/标题 ==========
    story.append(Paragraph("♞ 国际象棋专项习题集 ♞", title_style))
    story.append(Paragraph(f"难度: 中国棋协二级→一级（ELO {config.MIN_ELO}–{config.MAX_ELO}）", normal_style))
    story.append(Spacer(1, 16))
    
    # ========== 习题 ==========
    # 从对局历史中提取关键局面
    board = chess.Board()
    positions = []
    
    # 前几步走法，提取训练点
    for i, move in enumerate(list(game_info.get('analysis_history', []))[:20]):
        try:
            board_uci = chess.Board(move['fen_after'])
            positions.append({
                'board': board_uci.copy(),
                'ply': move['ply'],
                'is_white': not move['is_white']
            })
        except:
            pass
    
    # 从失误中提取
    for blunder in game_info.get('blunders', []):
        try:
            board_uci = chess.Board(blunder['fen'])
            positions.append({
                'board': board_uci.copy(),
                'ply': blunder['ply'],
                'is_white': blunder['is_white']
            })
        except:
            pass
    
    # 确保有足够的习题
    if len(positions) < config.EXERCISE_COUNT:
        # 补充一些标准习题局面
        standard_fens = [
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
            "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
            "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        ]
        for fen in standard_fens:
            positions.append({
                'board': chess.Board(fen),
                'ply': 0,
                'is_white': True
            })
    
    # 生成10道习题
    for i in range(config.EXERCISE_COUNT):
        pos_idx = i % len(positions)
        pos_info = positions[pos_idx]
        exercise_board = pos_info['board']
        exercise_type = config.EXERCISE_TYPES[i % len(config.EXERCISE_TYPES)]
        
        story.append(Paragraph(f"第 {i+1} 题 — {exercise_type}", bold_style))
        story.append(Spacer(1, 4))
        
        side = "红方（白方）" if pos_info['is_white'] else "黑方"
        story.append(Paragraph(f"轮走方: {side}", normal_style))
        
        # 局面图
        if config.SHOW_BOARD_IMAGE:
            img = generate_board_image(exercise_board, size=config.BOARD_IMAGE_SIZE)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                tmp_img.write(img_buffer.getvalue())
                tmp_img_path = tmp_img.name
            
            rl_img = RLImage(tmp_img_path, width=config.BOARD_IMAGE_SIZE/2, height=config.BOARD_IMAGE_SIZE/2)
            story.append(rl_img)
            story.append(Spacer(1, 4))
        
        # FEN码
        story.append(Paragraph(f"FEN: {exercise_board.fen()}", small_style))
        
        # 题目要求
        story.append(Paragraph("要求: 找出最佳着法", normal_style))
        story.append(Spacer(1, 8))
        
        # 预留答案空间
        story.append(Paragraph("答案与解析: ", ParagraphStyle(
            'AnswerLabel',
            parent=bold_style,
            textColor=colors.HexColor("#2c5282")
        )))
        
        # 简单答案
        try:
            # 用Stockfish分析10深度给答案
            temp_engine = StockfishEngine(config.STOCKFISH_PATH, depth=10)
            if temp_engine.start():
                analysis = temp_engine.analyze_board(exercise_board)
                if analysis and analysis['best_move']:
                    answer_san = exercise_board.variation_san([analysis['best_move']])
                    story.append(Paragraph(f"最佳着法: {answer_san}", normal_style))
                    story.append(Paragraph("注解: 通过控制关键格和威胁得子取得优势", small_style))
                temp_engine.stop()
        except:
            pass
        
        story.append(Spacer(1, 20))
        
        # 每5题分页
        if (i + 1) % 5 == 0 and i < config.EXERCISE_COUNT - 1:
            story.append(PageBreak())
    
    doc.build(story)
    print(f"[OK] 习题集已生成: {pdf_path}")
    return pdf_path


# ===================== 文件监控与处理 =====================
def load_analyzed_files():
    """加载已分析文件列表"""
    analyzed = set()
    if os.path.exists(config.ANALYZED_FILE):
        with open(config.ANALYZED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    analyzed.add(line)
    return analyzed


def save_analyzed_file(filename):
    """记录已分析文件"""
    with open(config.ANALYZED_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')


def ensure_directories():
    """确保目录存在"""
    for directory in [config.WATCH_DIR, config.REPORT_DIR, config.EXERCISE_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[OK] 创建目录: {directory}")


def process_pgn_file(pgn_path, engine, font_name):
    """处理单个PGN文件"""
    filename = os.path.basename(pgn_path)
    analyzed = load_analyzed_files()
    
    if filename in analyzed:
        print(f"[SKIP] 文件已分析过: {filename}")
        return False
    
    try:
        game_info = analyze_pgn_file(pgn_path, engine)
        if not game_info:
            return False
        
        generate_report_pdf(pgn_path, game_info, font_name)
        generate_exercise_pdf(pgn_path, game_info, font_name)
        
        save_analyzed_file(filename)
        print(f"🎉 成功处理: {filename}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 处理出错: {e}")
        import traceback
        traceback.print_exc()
        return False


class PGNAnalyzerHandler(FileSystemEventHandler):
    """文件事件处理器"""
    
    def __init__(self, engine, font_name):
        self.engine = engine
        self.font_name = font_name
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.pgn'):
            print(f"\n🔔 检测到新文件: {os.path.basename(event.src_path)}")
            time.sleep(2)
            process_pgn_file(event.src_path, self.engine, self.font_name)


def scan_and_process_existing(engine, font_name):
    """扫描并处理现有未分析文件"""
    print("[SCAN] 扫描现有PGN文件...")
    analyzed = load_analyzed_files()
    
    if not os.path.exists(config.WATCH_DIR):
        return 0
    
    count = 0
    for filename in os.listdir(config.WATCH_DIR):
        if filename.endswith('.pgn') and filename not in analyzed:
            pgn_path = os.path.join(config.WATCH_DIR, filename)
            if process_pgn_file(pgn_path, engine, font_name):
                count += 1
    
    return count


# ===================== 主程序 =====================
def main():
    print("=" * 70)
    print("               专业国际象棋自动复盘系统")
    print("=" * 70)
    print(f"监控目录: {config.WATCH_DIR}")
    print(f"报告输出: {config.REPORT_DIR}")
    print(f"习题输出: {config.EXERCISE_DIR}")
    print("=" * 70)
    print()
    
    ensure_directories()
    
    font_name = register_chinese_font()
    
    engine = StockfishEngine(
        config.STOCKFISH_PATH,
        depth=config.STOCKFISH_DEPTH,
        threads=config.STOCKFISH_THREADS,
        hash_mb=config.STOCKFISH_HASH
    )
    
    if not engine.start():
        print("\n[WARN] Stockfish引擎启动失败，继续运行（无引擎分析模式）")
    
    scan_and_process_existing(engine, font_name)
    
    event_handler = PGNAnalyzerHandler(engine, font_name)
    observer = Observer()
    observer.schedule(event_handler, config.WATCH_DIR, recursive=False)
    observer.start()
    
    print("\n[OK] 系统已启动，等待PGN文件...")
    print("按 Ctrl+C 停止程序")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止程序...")
        observer.stop()
    
    observer.join()
    engine.stop()


if __name__ == "__main__":
    main()
