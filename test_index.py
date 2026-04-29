"""测试索引逻辑"""
import chess

board = chess.Board()
boards = [board.copy()]
moves = ['e2e4', 'e7e5', 'g1f3']

print('初始状态:')
print(f'  boards[0] FEN: {boards[0].fen()}')
print(f'  回合: {"白方" if boards[0].turn == chess.WHITE else "黑方"}')
print()

for i, mv_uci in enumerate(moves):
    print(f'=== 第{i+1}步 ===')
    print(f'  当前状态（走棋前）:')
    print(f'    回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
    
    # 记录当前状态
    boards.append(board.copy())
    print(f'    boards[{i+1}] = 第{i+1}步前的状态')
    
    # 走棋
    mv = chess.Move.from_uci(mv_uci)
    board.push(mv)
    print(f'  走棋: {mv_uci}')
    print(f'  走棋后回合: {"白方" if board.turn == chess.WHITE else "黑方"}')
    print()

print('=== 索引总结 ===')
for i in range(len(boards)):
    turn = '白方' if boards[i].turn == chess.WHITE else '黑方'
    print(f'boards[{i}]: 第{i}步前的状态, 回合={turn}')