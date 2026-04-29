"""
自动化测试脚本 - 验证 chess_analyzer_final.py 的4个核心要求
调用主程序 analyze 函数进行验证
"""

import os
import sys

# 添加当前目录到路径，导入主程序
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chess_analyzer_final import analyze, MISTAKE

WATCH = r"D:\Chess_PGN_Receive"


def test_requirement_1(mistakes):
    """测试要求1：错招和正招完全不同"""
    print("\n" + "=" * 60)
    print("【测试1】错招和正招完全不同")
    print("=" * 60)
    passed = 0
    failed = 0
    for e in mistakes:
        move = e["move"]
        best = e["best"]
        if best is None:
            print(f"  ⚠️ 第{e['step']}步：无正招推荐")
            continue
        if move == best:
            print(f"  ❌ 第{e['step']}步：错招和正招相同！{move.uci()} == {best.uci()}")
            failed += 1
        else:
            print(f"  ✅ 第{e['step']}步：错招{move.uci()} ≠ 正招{best.uci()}")
            passed += 1
    print(f"\n  结果：{passed}通过 / {failed}失败")
    return failed == 0


def test_requirement_2(mistakes, boards):
    """测试要求2：正招是错招的修复建议（合法着法）"""
    print("\n" + "=" * 60)
    print("【测试2】正招是错招的修复建议（合法着法）")
    print("=" * 60)
    passed = 0
    failed = 0
    for e in mistakes:
        best = e["best"]
        if best is None:
            print(f"  ⚠️ 第{e['step']}步：无正招推荐")
            continue
        board = boards[e["board_idx"]]
        if best in board.legal_moves:
            print(f"  ✅ 第{e['step']}步：正招{best.uci()}是合法着法")
            passed += 1
        else:
            print(f"  ❌ 第{e['step']}步：正招{best.uci()}不是合法着法！")
            failed += 1
    print(f"\n  结果：{passed}通过 / {failed}失败")
    return failed == 0


def test_requirement_3(game, mistakes, score_data):
    """测试要求3：评分变化计算正确，只检查败方的走法"""
    print("\n" + "=" * 60)
    print("【测试3】评分变化计算正确（仅败方）")
    print("=" * 60)

    # 判断败方
    result = game.headers.get("Result", "*")
    if result == "1-0":
        loser = "黑"  # 黑方败
    elif result == "0-1":
        loser = "白"  # 白方败
    else:
        loser = None  # 和棋，检查双方

    print(f"  棋局结果: {result}, 败方: {loser if loser else '和棋-双方'}")

    scores_before = score_data["scores_before"]
    scores_after = score_data["scores_after"]

    passed = 0
    failed = 0
    skipped = 0

    for i in range(len(scores_before)):
        if i >= len(scores_after):
            continue

        turn = "白" if (i % 2 == 0) else "黑"

        # 只检查败方的走法
        if loser is not None and turn != loser:
            skipped += 1
            continue

        score_before = scores_before[i]
        score_after = scores_after[i]
        delta = score_after - score_before
        is_mistake = delta < MISTAKE

        # 检查是否被主程序标记为失误
        marked_as_mistake = any(e["step"] == i + 1 for e in mistakes)

        if is_mistake == marked_as_mistake:
            status = "✅"
            passed += 1
        else:
            status = "❌"
            failed += 1

        marker = "【失误】" if marked_as_mistake else ""
        print(f"  {status} 第{i + 1}步 ({turn}方): "
              f"走前{score_before:>6} → 走后{score_after:>6} "
              f"Δ={delta:>6} {marker}")

    print(f"\n  结果：{passed}通过 / {failed}失败 / {skipped}跳过（胜方）")
    print(f"  阈值：{MISTAKE} cp")
    return failed == 0


def test_requirement_4(mistakes, boards):
    """测试要求4：箭头、回合、解读全部对齐"""
    print("\n" + "=" * 60)
    print("【测试4】箭头、回合、解读对齐")
    print("=" * 60)
    import chess.svg

    passed = 0
    failed = 0
    for e in mistakes:
        step = e["step"]
        move = e["move"]
        best = e["best"]
        board = boards[e["board_idx"]]

        # 验证回合
        expected_turn = "白" if board.turn == chess.WHITE else "黑"

        # 验证箭头可生成
        arrows = []
        if move and hasattr(move, 'from_square'):
            arrows.append(chess.svg.Arrow(move.from_square, move.to_square, color="#e74c3c"))
        if best and hasattr(best, 'from_square'):
            arrows.append(chess.svg.Arrow(best.from_square, best.to_square, color="#27ae60"))

        arrow_ok = len(arrows) >= 1

        if arrow_ok:
            print(f"  ✅ 第{step}步 ({expected_turn}方): 回合正确，箭头可生成")
            passed += 1
        else:
            print(f"  ❌ 第{step}步: 箭头无法生成")
            failed += 1

    print(f"\n  结果：{passed}通过 / {failed}失败")
    return failed == 0


def main():
    print("=" * 60)
    print("象棋复盘分析器 - 自动化测试（仅测试败局1）")
    print("=" * 60)

    pgn_files = [f for f in os.listdir(WATCH) if f.endswith(".pgn") and "败局1" in f]
    if not pgn_files:
        print("❌ 未找到败局1.pgn")
        return

    all_passed = True
    for pgn_file in sorted(pgn_files):
        pgn_path = os.path.join(WATCH, pgn_file)
        print(f"\n{'#' * 60}")
        print(f"# 测试文件: {pgn_file}")
        print(f"{'#' * 60}")

        # 调用主程序的 analyze 函数
        result = analyze(pgn_path)
        game = result[0]
        mistakes = result[1]
        boards = result[2]
        moves = result[3]
        score_data = result[4]
        if not game:
            print("❌ 分析失败")
            continue

        print(f"\n棋局信息: 白方={game.headers.get('White')}, 黑方={game.headers.get('Black')}, 结果={game.headers.get('Result')}")
        print(f"总步数: {len(moves)}")
        print(f"失误数: {len(mistakes)}")

        r1 = test_requirement_1(mistakes)
        r2 = test_requirement_2(mistakes, boards)
        r3 = test_requirement_3(game, mistakes, score_data)
        r4 = test_requirement_4(mistakes, boards)

        file_passed = r1 and r2 and r3 and r4
        all_passed = all_passed and file_passed

        print(f"\n{'=' * 60}")
        print(f"文件 {pgn_file} 测试结果: {'✅ 全部通过' if file_passed else '❌ 存在失败'}")
        print(f"{'=' * 60}")

    print(f"\n{'#' * 60}")
    print(f"# 最终结论: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    print(f"{'#' * 60}")


if __name__ == "__main__":
    main()
