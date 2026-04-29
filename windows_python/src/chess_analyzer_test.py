# -*- coding: utf-8 -*-
"""
象棋自动复盘系统 - 测试程序（改进版）
"""
import os
import sys
import time
import datetime
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import chess
import chess.svg
import chess.pgn
import io
import config_test as config


def register_chinese_font():
    """注册中文字体"""
    font_paths = [
        r'C:\Windows\Fonts\simhei.ttf',
        r'C:\Windows\Fonts\simsun.ttc',
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\SIMSUN.TTF',
    ]
    
    font_name = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                font_name = 'ChineseFont'
                print(f"✅ 使用中文字体: {font_path}")
                break
            except Exception as e:
                continue
    
    if not font_name:
        print("⚠️ 未找到中文字体，使用默认字体")
        font_name = 'Helvetica'
    
    return font_name


def render_board_to_image(board, size=200):
    """将棋盘渲染为图片"""
    svg_data = chess.svg.board(board=board, size=size)
    return svg_data


def svg_to_pil_image(svg_data, size=200):
    """将SVG转换为PIL图片（简化版，我们用简单的方式表示棋盘）"""
    return None


def draw_chess_board(c, x, y, board, size=150):
    """在PDF画布上绘制棋盘"""
    cell_size = size / 8
    colors_board = [colors.HexColor("#f0d9b5"), colors.HexColor("#b58863")]
    
    pieces = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    }
    
    # 绘制棋盘格子
    for row in range(8):
        for col in range(8):
            color_idx = (row + col) % 2
            c.setFillColor(colors_board[color_idx])
            c.rect(x + col * cell_size, y + (7 - row) * cell_size, cell_size, cell_size, fill=1, stroke=0)
    
    # 绘制棋子
    c.setFont("Helvetica", cell_size * 0.7)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            piece_char = pieces.get(piece.symbol(), '?')
            c.drawString(
                x + col * cell_size + cell_size * 0.2,
                y + (7 - row) * cell_size + cell_size * 0.15,
                piece_char
            )
    
    # 绘制坐标
    c.setFont("ChineseFont", 8)
    c.setFillColor(colors.black)
    for i in range(8):
        # 横线坐标
        c.drawString(x - 15, y + i * cell_size + cell_size * 0.4, str(i + 1))
        # 竖线坐标
        c.drawString(x + i * cell_size + cell_size * 0.4, y - 10, chr(97 + i))


def create_board_image_page(story, board, font_name, title):
    """创建带棋盘的页面"""
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=getSampleStyleSheet()['Heading2'],
        fontName=font_name,
        fontSize=14,
        spaceAfter=6
    )
    story.append(Paragraph(title, heading2_style))
    story.append(Spacer(1, 10))
    return story


def load_analyzed_files():
    """加载已分析的文件列表"""
    analyzed = set()
    if os.path.exists(config.ANALYZED_FILE):
        with open(config.ANALYZED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    analyzed.add(line)
    return analyzed


def save_analyzed_file(filename):
    """记录已分析的文件"""
    with open(config.ANALYZED_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')


def ensure_directories():
    """确保所有必要的目录存在"""
    for directory in [config.WATCH_DIR, config.REPORT_DIR, config.EXERCISE_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)


def parse_pgn(pgn_path):
    """解析PGN文件"""
    with open(pgn_path, 'r', encoding='utf-8') as f:
        game = chess.pgn.read_game(f)
    
    board = game.board()
    moves = list(game.mainline_moves())
    
    return {
        'game': game,
        'board': board,
        'moves': moves,
        'headers': game.headers,
        'white': game.headers.get('White', '未知'),
        'black': game.headers.get('Black', '未知'),
        'date': game.headers.get('Date', '未知'),
        'result': game.headers.get('Result', '未知')
    }


def analyze_game(pgn_info):
    """简单模拟分析棋局"""
    analysis = []
    board = pgn_info['board'].copy()
    
    # 遍历所有走法
    for i, move in enumerate(pgn_info['moves']):
        board.push(move)
        
        # 模拟评估分数
        if (i + 1) % 3 == 0:
            analysis.append({
                'move_num': i + 1,
                'move': move.uci(),
                'evaluation': f"{(-0.5 + i * 0.1):.2f}",
                'comment': "正常着法" if i < 10 else "进入中局"
            })
    
    return analysis


def generate_report_pdf(pgn_path, pgn_info, font_name):
    """生成复盘PDF报告（改进版）"""
    filename = os.path.basename(pgn_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = filename.replace('.pgn', '').replace(' ', '_')
    pdf_path = os.path.join(config.REPORT_DIR, f"report_{safe_filename}_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 样式定义
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=12,
        spaceAfter=6
    )
    
    # 标题
    story.append(Paragraph("♟ 象棋复盘报告 ♟", title_style))
    story.append(Spacer(1, 12))
    
    # 对局信息
    story.append(Paragraph("一、对局信息", heading2_style))
    story.append(Spacer(1, 12))
    
    info_data = [
        ['红方', pgn_info['white']],
        ['黑方', pgn_info['black']],
        ['日期', pgn_info['date']],
        ['结果', pgn_info['result']],
        ['回合数', str(len(pgn_info['moves']))]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#d0d0d0")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # 关键回合分析
    story.append(Paragraph("二、关键回合分析", heading2_style))
    story.append(Spacer(1, 12))
    
    board = pgn_info['board'].copy()
    moves_to_show = min(5, len(pgn_info['moves']))
    
    for i in range(moves_to_show):
        move = pgn_info['moves'][i]
        
        move_num = i + 1
        is_white = (i % 2 == 0)
        player = "红方" if is_white else "黑方"
        
        story.append(Paragraph(f"第 {move_num} 回合 - {player}", bold_style))
        
        # 显示着法
        san_move = board.san(move)
        story.append(Paragraph(f"着法: {san_move}", normal_style))
        
        # 走棋
        board.push(move)
        
        # 模拟分析
        if move_num == 4:
            story.append(Paragraph("📌 这是一个关键转折点！黑方选择了积极的弃兵战术。", normal_style))
            story.append(Paragraph("💡 建议: 此时红方应谨慎接受，或者考虑变招。", normal_style))
        elif move_num == 8:
            story.append(Paragraph("⚠️ 这里出现了一个小失误！", normal_style))
            story.append(Paragraph("💡 更好的着法: 可以考虑稳健的发展子力。", normal_style))
        
        story.append(Spacer(1, 12))
    
    story.append(Spacer(1, 12))
    
    # 总结
    story.append(Paragraph("三、复盘总结", heading2_style))
    story.append(Spacer(1, 12))
    
    summary_points = [
        "1. 开局阶段: 红方选择了后兵开局，黑方应以印度防御，整体开局正常。",
        "2. 中局阶段: 双方在中心展开争夺，第8-12回合是关键期。",
        "3. 关键失误: 红方在第8回合的 queenside 进攻选择值得商榷，被黑方利用。",
        "4. 制胜因素: 黑方在第13回合抓住机会，弃子攻杀，取得胜利。",
        "5. 学习建议: 注重中心控制和子力协调，避免过早暴露后翼弱点。"
    ]
    
    for point in summary_points:
        story.append(Paragraph(point, normal_style))
        story.append(Spacer(1, 6))
    
    doc.build(story)
    print(f"✅ 复盘报告已生成: {pdf_path}")
    return pdf_path


def generate_exercise_pdf(pgn_path, pgn_info, font_name):
    """生成习题PDF（改进版 - 含棋谱提示）"""
    filename = os.path.basename(pgn_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = filename.replace('.pgn', '').replace(' ', '_')
    pdf_path = os.path.join(config.EXERCISE_DIR, f"exercise_{safe_filename}_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 样式定义
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=13,
        spaceAfter=8
    )
    
    # 标题
    story.append(Paragraph("♞ 象棋习题集 ♞", title_style))
    story.append(Spacer(1, 12))
    
    # 难度信息
    story.append(Paragraph(f"📚 难度: {config.DIFFICULTY_LEVEL}", normal_style))
    story.append(Paragraph(f"🏆 题库: 大师题库（锁定）", normal_style))
    story.append(Paragraph(f"📝 题量: {config.EXERCISE_COUNT}道", normal_style))
    story.append(Spacer(1, 20))
    
    # 习题列表
    exercise_types = ['杀法练习', '得子战术', '防守反击', '占位技巧', '中局突破']
    board = pgn_info['board'].copy()
    
    for i in range(config.EXERCISE_COUNT):
        exercise_type = exercise_types[i % len(exercise_types)]
        move_offset = (i * 2) % len(pgn_info['moves'])
        
        # 前进到相应局面
        temp_board = pgn_info['board'].copy()
        for j in range(min(move_offset, len(pgn_info['moves']))):
            temp_board.push(pgn_info['moves'][j])
        
        story.append(Paragraph(f"第 {i+1} 题 - {exercise_type}", bold_style))
        story.append(Paragraph(f"题干: 如图局面，红方先行，请找出最佳着法。", normal_style))
        
        # 显示当前局面FEN（供参考）
        fen = temp_board.fen()
        story.append(Paragraph(f"参考局面: {fen[:60]}...", normal_style))
        
        # 提示
        hints = [
            "提示: 注意黑王的位置，寻找连将杀。",
            "提示: 寻找捉双或闪击的机会。",
            "提示: 先稳固防守，再寻找反击机会。",
            "提示: 占据关键位置，控制中心。",
            "提示: 突破对方防线，打开进攻线路。"
        ]
        story.append(Paragraph(hints[i % 5], ParagraphStyle(
            'HintStyle',
            parent=normal_style,
            textColor=colors.HexColor("#555555")
        )))
        
        story.append(Spacer(1, 16))
        
        # 每5题后分页
        if (i + 1) % 5 == 0 and i < config.EXERCISE_COUNT - 1:
            story.append(Spacer(1, 30))
    
    doc.build(story)
    print(f"✅ 习题集已生成: {pdf_path}")
    return pdf_path


def process_pgn(pgn_path, font_name):
    """处理单个PGN文件"""
    filename = os.path.basename(pgn_path)
    analyzed = load_analyzed_files()
    
    if filename in analyzed:
        print(f"⏭️ 文件已分析过，跳过: {filename}")
        return
    
    print(f"\n🔍 开始分析: {filename}")
    print("-" * 50)
    
    try:
        pgn_info = parse_pgn(pgn_path)
        print(f"   对局: {pgn_info['white']} VS {pgn_info['black']}")
        print(f"   结果: {pgn_info['result']}")
        print(f"   回合数: {len(pgn_info['moves'])}")
        
        generate_report_pdf(pgn_path, pgn_info, font_name)
        generate_exercise_pdf(pgn_path, pgn_info, font_name)
        
        save_analyzed_file(filename)
        print(f"🎉 分析完成: {filename}")
        
    except Exception as e:
        print(f"❌ 分析出错: {e}")
        import traceback
        traceback.print_exc()


def scan_existing_files(font_name):
    """扫描并处理已存在但未分析的文件"""
    print("扫描已有文件...")
    analyzed = load_analyzed_files()
    
    count = 0
    if os.path.exists(config.WATCH_DIR):
        for filename in os.listdir(config.WATCH_DIR):
            if filename.endswith('.pgn') and filename not in analyzed:
                pgn_path = os.path.join(config.WATCH_DIR, filename)
                process_pgn(pgn_path, font_name)
                count += 1
    
    return count


def main():
    """主函数"""
    print("=" * 60)
    print("           象棋自动复盘系统 - 测试模式（改进版）")
    print("=" * 60)
    print(f"测试目录: {config.WATCH_DIR}")
    print(f"报告输出: {config.REPORT_DIR}")
    print(f"习题输出: {config.EXERCISE_DIR}")
    print("=" * 60)
    print()
    
    if os.path.exists(config.ANALYZED_FILE):
        os.remove(config.ANALYZED_FILE)
    
    ensure_directories()
    font_name = register_chinese_font()
    count = scan_existing_files(font_name)
    
    print()
    print("=" * 60)
    if count > 0:
        print(f"测试完成！共处理了 {count} 个PGN文件")
        print(f"请查看 test_output/ 目录下的生成结果")
    else:
        print("没有找到新的PGN文件需要分析")
    print("=" * 60)


if __name__ == "__main__":
    main()
