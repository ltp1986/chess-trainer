import json
import datetime
import os
from urllib.parse import unquote
import chess

def clean_filename(filename):
    filename = unquote(filename)
    filename = filename.split(':')[0]
    return filename

def format_pgn(moves):
    pgn_text = ""
    for i, m in enumerate(moves):
        if i % 2 == 0:
            pgn_text += f"{i//2 + 1}. {m.uci()} "
        else:
            pgn_text += f"{m.uci()} "
    return pgn_text.strip()

def explain_loss(loss):
    if loss > 500:
        return "严重失误，重大子力损失", "立即评估局面，寻找止损方案"
    elif loss > 300:
        return "送子丢子，漏看战术", "必须保护子力，避开攻击线"
    elif loss > 150:
        return "关键格失守，被突破", "守住要点，加固防线"
    else:
        return "局面判断偏差", "改善子力位置，稳健防守"

def load_json_file(file_path):
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json_file(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"保存文件失败: {e}")
        return False

def get_piece_name(symbol):
    piece_names = {'P': '兵', 'N': '马', 'B': '象', 'R': '车', 'Q': '后', 'K': '王'}
    return piece_names.get(symbol.upper(), '未知')

def get_piece_value(symbol):
    piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100}
    return piece_values.get(symbol.upper(), 0)