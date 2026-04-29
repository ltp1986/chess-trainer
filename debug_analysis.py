import requests

response = requests.get('http://localhost:5000/api/analyze/败局1.pgn')
data = response.json()

print('分析结果:')
print(f"白方: {data.get('white')}")
print(f"黑方: {data.get('black')}")
print(f"结果: {data.get('result')}")
print()

exercises = data.get('exercises', [])
for ex in exercises:
    print(f"习题ID: {ex.get('id')}")
    print(f"步数: {ex.get('step')}")
    print(f"回合: {ex.get('turn')}")
    print(f"FEN: {ex.get('fen')}")
    print(f"最佳着法: {ex.get('best_move')}")
    print()

# 验证FEN
import chess
if exercises:
    ex = exercises[0]
    board = chess.Board(ex.get('fen'))
    print("验证FEN:")
    print(f"  回合: {'白方' if board.turn == chess.WHITE else '黑方'}")
    print(f"  第几步: {board.fullmove_number}")
