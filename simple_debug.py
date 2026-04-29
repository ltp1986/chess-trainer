"""简单调试：一步一步跟踪分析过程"""

import chess
import chess.pgn
import io

# 读取PGN
with open(r'D:\Chess_PGN_Receive\败局1.pgn', 'r', encoding='utf-8') as f:
    content = f.read()

game = chess.pgn.read_game(io.StringIO(content))
board = game.board()
moves = list(game.mainline_moves())

print('=' * 60)
print('一步一步跟踪分析过程')
print('=' * 60)
print(f'总步数: {len(moves)}')
print(f'结果: {game.headers.get("Result")}')
print()

# 标记败方
result = game.headers.get("Result")
if result == "1-0":
    loser = chess.BLACK
    loser_name = "黑方"
elif result == "0-1":
    loser = chess.WHITE
    loser_name = "白方"
else:
    loser = None
    loser_name = "双方"

print(f'败方: {loser_name}')
print()

# 一步步跟踪
for i, mv in enumerate(moves):
    step = i + 1
    current_turn = chess.WHITE if (i % 2 == 0) else chess.BLACK
    turn_name = "白方" if current_turn == chess.WHITE else "黑方"
    
    # 检查是否是败方的走法
    is_loser_move = (loser is None) or (current_turn == loser)
    
    print(f'第{step}步 ({turn_name}): {mv.uci()}')
    print(f'  走棋前FEN: {board.fen()[:50]}...')
    print(f'  走棋前回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
    
    # 走棋
    board.push(mv)
    
    print(f'  走棋后FEN: {board.fen()[:50]}...')
    print(f'  走棋后回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
    print(f'  是否败方走法: {"是" if is_loser_move else "否"}')
    print()
    
    # 重点标记第25步
    if step == 25:
        print('=' * 60)
        print('⚠️ 重点：第25步')
        print(f'  第25步前的回合应该是: 白方')
        print(f'  当前走棋方: {turn_name}')
        print(f'  走棋后回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
        print('=' * 60)
        print()