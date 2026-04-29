import chess
import sys
sys.path.insert(0, r'f:\trae项目\Chess')
from chess_analyzer_v2 import analyze, find_engine
import chess.engine

# 分析败局1
pgn_path = r"D:\Chess_PGN_Receive\败局1.pgn"
print("=" * 60)
print("验证习题生成效果")
print("=" * 60)

game, mistakes, boards, moves, score_data = analyze(pgn_path)

if not mistakes:
    print("没有找到失误")
    sys.exit()

# 获取第一个失误
mistake = mistakes[0]
original_board = boards[mistake['board_idx']]
exercise = mistake['exercise']

print(f"\n【原局信息】")
print(f"  第{mistake['step']}步")
print(f"  错招: {mistake['move'].uci()}")
print(f"  正招: {mistake['best'].uci() if mistake['best'] else '无'}")
print(f"  原局面FEN: {original_board.fen()}")

print(f"\n【生成习题信息】")
print(f"  新局面FEN: {exercise['fen']}")
print(f"  新正招: {exercise['best_move'].uci() if exercise['best_move'] else '无'}")
print(f"  难度: {exercise['difficulty']}")
print(f"  主题: {exercise['theme']}")
print(f"  错误类型: {exercise['mistake_type']}")

# 验证1：新局面是否与原局面不同
new_board = chess.Board(exercise['fen'])
print(f"\n【验证1：局面差异性】")
print(f"  原局面棋子数: {len(original_board.piece_map())}")
print(f"  新局面棋子数: {len(new_board.piece_map())}")
print(f"  局面是否相同: {original_board.fen() == exercise['fen']}")

# 验证2：新局面的战术性
print(f"\n【验证2：新局面战术性】")
eng = chess.engine.SimpleEngine.popen_uci(find_engine())
eng.configure({"Threads": 4, "Hash": 512})

# 分析新局面
res = eng.analyse(new_board, chess.engine.Limit(depth=18, time=1.5))
pv = res.get("pv", [])
if pv:
    best = pv[0]
    test_board = new_board.copy()
    test_board.push(best)
    
    print(f"  引擎推荐: {best.uci()}")
    print(f"  是否将军: {test_board.is_check()}")
    print(f"  是否吃子: {new_board.is_capture(best)}")
    
    # 检查是否有悬子
    has_hanging = False
    for sq in chess.SQUARES:
        piece = test_board.piece_at(sq)
        if piece and piece.color == test_board.turn:
            if test_board.is_attacked_by(not test_board.turn, sq):
                has_hanging = True
                break
    print(f"  是否有悬子: {has_hanging}")
    
    # 评分变化
    score_before = res["score"].white().score(mate_score=10000) if new_board.turn == chess.WHITE else res["score"].black().score(mate_score=10000)
    
    # 走正招后的评分
    res_after = eng.analyse(test_board, chess.engine.Limit(depth=18, time=1.5))
    score_after = res_after["score"].white().score(mate_score=10000) if new_board.turn == chess.WHITE else res_after["score"].black().score(mate_score=10000)
    
    delta = score_after - score_before
    print(f"  正招评分变化: {delta} cp")
    print(f"  是否显著改善: {'是' if delta > 50 else '否'}")

eng.quit()

# 验证3：与原局面的战术主题关联性
print(f"\n【验证3：战术主题关联性】")
print(f"  原局面问题: 白方冲g4送兵，黑象可吃")
print(f"  新局面目地: 应该是类似的子力保护问题")

# 检查新局面的关键特征
print(f"\n  新局面特征:")
print(f"  - 轮到谁走: {'白方' if new_board.turn == chess.WHITE else '黑方'}")
print(f"  - 白方子力: {sum(1 for p in new_board.piece_map().values() if p.color == chess.WHITE)}")
print(f"  - 黑方子力: {sum(1 for p in new_board.piece_map().values() if p.color == chess.BLACK)}")

# 王的安全
white_king_sq = new_board.king(chess.WHITE)
black_king_sq = new_board.king(chess.BLACK)
if white_king_sq:
    print(f"  - 白王位置: {chess.square_name(white_king_sq)}")
if black_king_sq:
    print(f"  - 黑王位置: {chess.square_name(black_king_sq)}")

print("\n" + "=" * 60)
print("结论:")
if original_board.fen() != exercise['fen']:
    print("✅ 新局面与原局面不同")
else:
    print("❌ 新局面与原局面相同（需要改进）")
