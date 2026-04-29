/**
 * 测试合法着法处理逻辑
 */

// 模拟后端返回
const backendResponse = {
    legal_moves: ['f3', 'f4'],
    square: 'f2'
};

// 模拟前端代码
const legalMoves = backendResponse.legal_moves;

// 测试检查逻辑
const testCases = [
    { selected: 'f2', clicked: 'f3', expected: true },
    { selected: 'f2', clicked: 'f4', expected: true },
    { selected: 'f2', clicked: 'g3', expected: false },
    { selected: 'f2', clicked: 'f2', expected: false } // 点击同一个格子
];

console.log('=== 测试合法着法检查 ===');
console.log('合法着法:', legalMoves);
console.log();

testCases.forEach((test, i) => {
    const { selected, clicked, expected } = test;
    
    if (selected && selected !== clicked) {
        const isValid = legalMoves.includes(clicked);
        const status = isValid === expected ? '✅' : '❌';
        console.log(`${status} 测试${i+1}: 选中${selected}, 点击${clicked} → ${isValid} (期望: ${expected})`);
    } else {
        console.log(`⚠️ 测试${i+1}: 跳过（未选中或点击同一格子）`);
    }
});

console.log();
console.log('=== 检查格式是否正确 ===');
console.log('legalMoves 类型:', typeof legalMoves);
console.log('是否为数组:', Array.isArray(legalMoves));
console.log('数组内容:', legalMoves.map(m => `'${m}'`).join(', '));