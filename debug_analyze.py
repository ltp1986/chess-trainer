import chess, chess.pgn, chess.engine

pgn_path = r'D:\Chess_PGN_Receive\败局1.pgn'
engine_path = r'D:\stockfish\stockfish-windows-x86-64-avx2.exe'

with open(pgn_path, 'r') as f:
    game = chess.pgn.read_game(f)

print('Result:', game.headers.get('Result'))
print('白方:', game.headers.get('White'))
print('黑方:', game.headers.get('Black'))

board = game.board()
eng = chess.engine.SimpleEngine.popen_uci(engine_path)
eng.configure({'Threads': 4, 'Hash': 512})
moves = list(game.mainline_moves())

print('\n=== 白方走法详细分析（修复后逻辑）===')
for i, mv in enumerate(moves):
    turn = '白' if i % 2 == 0 else '黑'
    current_player = board.turn  # 记录走棋方
    
    res_before = eng.analyse(board, chess.engine.Limit(depth=18, time=1.5))
    if current_player == chess.WHITE:
        score_before = res_before['score'].white().score(mate_score=10000)
    else:
        score_before = res_before['score'].black().score(mate_score=10000)
    
    board.push(mv)
    
    res_after = eng.analyse(board, chess.engine.Limit(depth=18, time=1.5))
    if current_player == chess.WHITE:
        score_after = res_after['score'].white().score(mate_score=10000)
    else:
        score_after = res_after['score'].black().score(mate_score=10000)
    
    delta = score_after - score_before
    
    if turn == '白':
        marker = '【失误】' if delta < -100 else ''
        print(f'白方第{i+1}步: {mv.uci()}, 走前{score_before:>6} → 走后{score_after:>6}, Δ={delta:>6} {marker}')

eng.quit()
