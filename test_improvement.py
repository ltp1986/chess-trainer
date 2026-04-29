import sys
sys.path.insert(0, 'webapp')

from app import generate_mistake_explanation

# 测试案例1: 白后吃黑后，但会被黑车反吃
test_fen = "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 3"
actual_move = "g6e8"
best_move = "d1d8"
loss = 500

cause, idea = generate_mistake_explanation(test_fen, actual_move, best_move, loss)
print(f"测试案例1 - 吃后陷阱")
print(f"FEN: {test_fen}")
print(f"实际走法: {actual_move}")
print(f"最佳走法: {best_move}")
print(f"损失: {loss}cp")
print(f"错误原因: {cause}")
print(f"改进建议: {idea}")
print()

# 测试案例2: 简单的子力损失
test_fen2 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
actual_move2 = "e7e5"
best_move2 = "c7c5"
loss2 = 150

cause2, idea2 = generate_mistake_explanation(test_fen2, actual_move2, best_move2, loss2)
print(f"测试案例2 - 开局走法")
print(f"FEN: {test_fen2}")
print(f"实际走法: {actual_move2}")
print(f"最佳走法: {best_move2}")
print(f"损失: {loss2}cp")
print(f"错误原因: {cause2}")
print(f"改进建议: {idea2}")
print()

# 测试案例3: 重大失误
test_fen3 = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 1 3"
actual_move3 = "f3e5"
best_move3 = "f3h4"
loss3 = 400

cause3, idea3 = generate_mistake_explanation(test_fen3, actual_move3, best_move3, loss3)
print(f"测试案例3 - 送子失误")
print(f"FEN: {test_fen3}")
print(f"实际走法: {actual_move3}")
print(f"最佳走法: {best_move3}")
print(f"损失: {loss3}cp")
print(f"错误原因: {cause3}")
print(f"改进建议: {idea3}")