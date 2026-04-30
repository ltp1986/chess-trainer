import chess
import logging

from utils.helpers import explain_loss, get_piece_name, get_piece_value
from engine.stockfish import get_best_move as sf_get_best_move

logger = logging.getLogger(__name__)

def analyze_tactic_situation(board_fen, actual_move, best_move):
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
                        'name': get_piece_name(captured.symbol()),
                        'value': get_piece_value(captured.symbol()),
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
                                'name': get_piece_name(att_piece.symbol()),
                                'from_square': chess.square_name(att_sq),
                                'move': f"{chess.square_name(att_sq)}{chess.square_name(square)}"
                            })
                    
                    if len(attackers) > len(defenders):
                        analysis['attacked_pieces'].append({
                            'piece': piece.symbol(),
                            'name': get_piece_name(piece.symbol()),
                            'square': chess.square_name(square),
                            'attackers': len(attackers),
                            'attack_details': attack_details,
                            'defenders': len(defenders)
                        })
                        
                        for attack in attack_details:
                            analysis['capture_moves'].append({
                                'captured_piece': get_piece_name(piece.symbol()),
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
                                'name': get_piece_name(piece.symbol()),
                                'square': square_name
                            })
    
    except Exception as e:
        logger.error(f"分析战术局面出错: {e}")
    
    return analysis

def generate_mistake_explanation(fen, actual_move, best_move, loss):
    if not fen or not actual_move:
        return explain_loss(loss)
    
    try:
        board = chess.Board(fen)
        analysis = analyze_tactic_situation(fen, actual_move, best_move)
        
        cause = ""
        idea = ""
        
        temp_board = board.copy()
        move_obj = chess.Move.from_uci(actual_move)
        
        if move_obj in temp_board.legal_moves:
            moved_piece = board.piece_at(move_obj.from_square)
            moved_piece_type = moved_piece.symbol().upper() if moved_piece else ''
            moved_piece_name = get_piece_name(moved_piece_type)
            
            moved_to = chess.square_name(move_obj.to_square)
            moved_from = chess.square_name(move_obj.from_square)
            
            before_capture = board.piece_at(move_obj.to_square)
            temp_board.push(move_obj)
            
            if temp_board.is_capture(move_obj):
                captured = temp_board.piece_at(move_obj.to_square)
                
                if captured and moved_piece:
                    captured_value = get_piece_value(captured.symbol())
                    moved_value = get_piece_value(moved_piece_type)
                    
                    attackers_after = temp_board.attackers(not board.turn, move_obj.to_square)
                    defenders_after = temp_board.attackers(board.turn, move_obj.to_square)
                    is_attacked_after = len(attackers_after) > len(defenders_after)
                    
                    if moved_value < captured_value:
                        if is_attacked_after:
                            cause = f"用{moved_piece_name}换{get_piece_name(captured.symbol())}赚分，但新位置{moved_to}被攻击"
                            idea = "评估是否值得冒险，准备后续应对"
                        else:
                            cause = f"用{moved_piece_name}换{get_piece_name(captured.symbol())}，赚分"
                            idea = "继续保持优势，扩大战果"
                    elif moved_value > captured_value:
                        if captured_value == 9:
                            cause = f"牺牲{moved_piece_name}换后，需要精确计算后续战术"
                            idea = "确认后续战术是否成立"
                        else:
                            cause = f"用{moved_piece_name}换{get_piece_name(captured.symbol())}，亏分"
                            idea = "避免得不偿失的交换"
                    else:
                        if before_capture:
                            before_attacked = board.attackers(board.turn, move_obj.to_square)
                            before_defended = board.attackers(not board.turn, move_obj.to_square)
                            was_attacked_before = len(before_attacked) > len(before_defended)
                            
                            if was_attacked_before:
                                cause = f"被迫用{moved_piece_name}兑{get_piece_name(captured.symbol())}"
                                idea = "这是必要的防御，局面保持平衡"
                            elif is_attacked_after:
                                cause = f"主动用{moved_piece_name}兑{get_piece_name(captured.symbol())}，但新位置{moved_to}被攻击"
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

def generate_local_classification(fen, actual_move, best_move, loss, move_number):
    try:
        board = chess.Board(fen)
    except ValueError:
        return {
            "category": "未知",
            "sub_category": "未知",
            "difficulty": 3,
            "description": "无法分析",
            "suggestion": "检查输入数据",
            "common_mistake": False,
            "classified_at": datetime.datetime.now().isoformat()
        }
    
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

import datetime