import requests

print('=== 检查分析API ===')
response = requests.get('http://localhost:5000/api/analyze/败局1.pgn')
print('HTTP状态码:', response.status_code)

if response.status_code == 200:
    data = response.json()
    print('状态:', data.get('status'))
    print('白方:', data.get('white'))
    print('黑方:', data.get('black'))
    print('结果:', data.get('result'))
    print('习题数量:', len(data.get('exercises', [])))
    
    exercises = data.get('exercises', [])
    if exercises:
        ex = exercises[0]
        print()
        print('第一个习题:')
        print('  步数:', ex.get('step'))
        print('  回合:', ex.get('turn'))
        print('  最佳着法:', ex.get('best_move'))
        print('  FEN:', ex.get('fen'))
else:
    print('响应内容:', response.text)
