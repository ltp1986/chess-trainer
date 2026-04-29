import chess
import sys
sys.path.insert(0, 'webapp')
from app import analyze_tactic_situation, get_tactic_explanation

def test_tactic_analysis():
    print("=== 测试战术分析功能 ===\n")
    
    test_cases = [
        {
            'name': '送马测试',
            'fen': 'rnbqkbnr/pppp1ppp/8/4p3/8/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3',
            'actual_move': 'f3f6',
            'best_move': 'f3h4',
            'loss': 300
        },
        {
            'name': '将军测试',
            'fen': 'rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3',
            'actual_move': 'e4e5',
            'best_move': 'g1f3',
            'loss': 250
        },
        {
            'name': '受攻测试',
            'fen': 'rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3',
            'actual_move': 'd4d5',
            'best_move': 'c2c4',
            'loss': 150
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"--- 测试用例 {i+1}: {case['name']} ---")
        print(f"FEN: {case['fen']}")
        print(f"错招: {case['actual_move']}")
        print(f"正招: {case['best_move']}")
        
        analysis = analyze_tactic_situation(case['fen'], case['actual_move'], case['best_move'])
        print("\n分析结果:")
        if analysis['captured_piece']:
            print(f"  被吃子: {analysis['captured_piece']['name']}")
        if analysis['attacked_pieces']:
            for ap in analysis['attacked_pieces']:
                print(f"  受攻子: {ap['name']}在{ap['square']} ({ap['attackers']}攻{ap['defenders']}守)")
        if analysis['threats']:
            print(f"  威胁: {analysis['threats']}")
        if analysis['defended_pieces']:
            print(f"  被保护子: {[dp['name'] for dp in analysis['defended_pieces']]}")
        
        explanation = get_tactic_explanation(case['fen'], case['actual_move'], case['best_move'], case['loss'])
        print(f"\n战术解释:\n{explanation}\n")

if __name__ == '__main__':
    test_tactic_analysis()