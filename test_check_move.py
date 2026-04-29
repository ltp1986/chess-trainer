import requests

print('=== 测试走棋验证API ===')

# 获取习题
response = requests.get('http://localhost:5000/api/analyze/败局1.pgn')
data = response.json()
exercises = data.get('exercises', [])

if not exercises:
    print('❌ 没有习题')
    exit(1)

ex = exercises[0]
fen = ex.get('fen')
best_move = ex.get('best_move')

print('测试习题: 第{}步'.format(ex.get('step')))
print('最佳着法: {}'.format(best_move))
print()

# 测试走最佳着法
print('--- 测试走最佳着法 ---')
response = requests.post('http://localhost:5000/api/check_move', json={
    'fen': fen,
    'move': best_move,
    'expected_best': best_move
})

print('HTTP状态码:', response.status_code)
if response.status_code == 200:
    result = response.json()
    print('valid:', result.get('valid'))
    print('correct:', result.get('correct'))
    print('message:', result.get('message'))
else:
    print('响应内容:', response.text)
