import chess
import chess.pgn
import io

with open(r'D:\Chess_PGN_Receive\败局1.pgn', 'r', encoding='utf-8') as f:
    content = f.read()

game = chess.pgn.read_game(io.StringIO(content))
board = game.board()
moves = list(game.mainline_moves())

print('总步数:', len(moves))
print()

# 走24步，到达第25步前的状态
for i in range(24):
    mv = moves[i]
    board.push(mv)

print('第25步前的状态:')
print('FEN:', board.fen())
print('回合:', '白方' if board.turn == chess.WHITE else '黑方')
print('第几步:', board.fullmove_number)
print()

# 检查最佳着法 h7h5 是否合法
move = chess.Move.from_uci('h7h5')
print('h7h5 是否合法:', move in board.legal_moves)

# 检查白方的合法着法
print()
print('白方合法着法示例:')
for mv in list(board.legal_moves)[:5]:
    print('  ', mv.uci())