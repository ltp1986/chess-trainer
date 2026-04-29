import chess, chess.pgn, chess.engine

pgn_path = r'D:\Chess_PGN_Receive\败局1.pgn'
engine_path = r'D:\stockfish\stockfish-windows-x86-64-avx2.exe'

with open(pgn_path, 'r') as f:
    game = chess.pgn.read_game(f)

board = game.board()
eng = chess.engine.SimpleEngine.popen_uci(engine_path)
eng.configure({'Threads': 4, 'Hash': 512})
moves = list(game.mainline_moves())

print('=== 第25步 g2g4 详细分析 ===')
# 走到第24步后的局面
for i in range(24):
    board.push(moves[i])

print(f'第24步后局面:')
print(board)
print(f'轮到: {"白方" if board.turn == chess.WHITE else "黑方"}')

res_before = eng.analyse(board, chess.engine.Limit(depth=18, time=1.5))
score_white_before = res_before['score'].white().score(mate_score=10000)
score_black_before = res_before['score'].black().score(mate_score=10000)
print(f'走棋前评分(白视角): {score_white_before}')
print(f'走棋前评分(黑视角): {score_black_before}')

# 白方走g4
mv = moves[24]  # 第25步 (索引24)
print(f'\n白方走: {mv.uci()}')
board.push(mv)

print(f'\n第25步后局面:')
print(board)

res_after = eng.analyse(board, chess.engine.Limit(depth=18, time=1.5))
score_white_after = res_after['score'].white().score(mate_score=10000)
score_black_after = res_after['score'].black().score(mate_score=10000)
print(f'走棋后评分(白视角): {score_white_after}')
print(f'走棋后评分(黑视角): {score_black_after}')

print(f'\n评分变化(白视角): {score_white_after - score_white_before}')
print(f'评分变化(黑视角): {score_black_after - score_black_before}')

eng.quit()
