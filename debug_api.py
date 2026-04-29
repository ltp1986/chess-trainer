"""调试API返回的FEN是否正确"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webapp.app import analyze_pgn, WATCH

pgn_path = os.path.join(WATCH, '败局1.pgn')
print(f'分析文件: {pgn_path}')
print()

game, mistakes = analyze_pgn(pgn_path)

if not game:
    print('分析失败')
    sys.exit(1)

print('棋局信息:')
print(f'  白方: {game.headers.get("White")}')
print(f'  黑方: {game.headers.get("Black")}')
print(f'  结果: {game.headers.get("Result")}')
print()

print('发现的失误:')
for e in mistakes:
    print(f'  第{e["step"]}步:')
    print(f'    board_idx: {e["board_idx"]}')
    print(f'    回合: {e["turn"]}')
    print(f'    FEN: {e["fen"]}')
    print(f'    最佳着法: {e["best"]}')
    print()
    
    # 验证这个FEN
    import chess
    board = chess.Board(e["fen"])
    print(f'    验证FEN:')
    print(f'      实际回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
    print(f'      第几步: {board.fullmove_number}')
    
    if e["best"]:
        move = chess.Move.from_uci(e["best"])
        print(f'      {e["best"]} 是否合法: {move in board.legal_moves}')
    print()