import os, sys
sys.path.insert(0, r'f:\trae项目\Chess')
from chess_analyzer_v2 import analyze, write_report, write_exam, write_answer

pgn_path = r"D:\Chess_PGN_Receive\败局1.pgn"
print("=" * 60)
print("测试优化后的习题生成系统")
print("=" * 60)

game, mistakes, boards, moves, score_data = analyze(pgn_path)

print(f"\n找到失误数量: {len(mistakes)}")

for i, e in enumerate(mistakes, 1):
    print(f"\n--- 失误 {i} ---")
    print(f"  第{e['step']}步: {e['move'].uci()} (失分: {e['loss']}cp)")
    print(f"  正招: {e['best'].uci() if e['best'] else '无'}")
    
    exercise = e.get('exercise', {})
    print(f"  生成习题:")
    print(f"    FEN: {exercise.get('fen', '无')[:70]}...")
    print(f"    新正招: {exercise.get('best_move').uci() if exercise.get('best_move') else '无'}")
    print(f"    难度: {exercise.get('difficulty', '无')}")
    print(f"    主题: {exercise.get('theme', '无')}")
    print(f"    错误类型: {exercise.get('mistake_type', '无')}")
    print(f"    描述: {exercise.get('tactic_desc', '无')}")

# 生成报告
if game and mistakes:
    from chess_analyzer_v2 import OUT
    
    # 清理旧文件
    for f in os.listdir(OUT):
        if f.startswith('习题_') or f.startswith('答案_') or f.startswith('复盘_'):
            os.remove(os.path.join(OUT, f))
    
    write_report(game, mistakes, boards, moves, "败局1.pgn")
    write_exam(mistakes, "败局1.pgn")
    write_answer(mistakes, "败局1.pgn")
    print("\n✅ 报告生成完成")
