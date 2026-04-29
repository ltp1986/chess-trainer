/**
 * 前端测试运行器 - Node.js环境
 */

const fs = require('fs');
const path = require('path');

// 加载验证模块
const Validator = require('../js/validation.js');

console.log('='.repeat(60));
console.log('国际象棋学习训练系统 - 前端验证测试');
console.log('='.repeat(60));

let passed = 0;
let total = 0;

// 测试PGN验证
console.log('\n【测试1】PGN验证');

total++;
const pgnResult = Validator.validatePGN('[Event "Test"]\n1. e4 e5');
if (pgnResult.valid) {
    console.log('  ✅ 有效PGN验证通过');
    passed++;
} else {
    console.log('  ❌ 有效PGN验证失败');
}

total++;
const emptyPgnResult = Validator.validatePGN('');
if (!emptyPgnResult.valid && emptyPgnResult.errors.length > 0) {
    console.log('  ✅ 空PGN验证通过');
    passed++;
} else {
    console.log('  ❌ 空PGN验证失败');
}

total++;
const invalidPgnResult = Validator.validatePGN('not a pgn');
if (!invalidPgnResult.valid) {
    console.log('  ✅ 无效PGN验证通过');
    passed++;
} else {
    console.log('  ❌ 无效PGN验证失败');
}

// 测试姓名验证
console.log('\n【测试2】姓名验证');

total++;
const nameResult = Validator.validatePlayerName('张三');
if (nameResult.valid) {
    console.log('  ✅ 有效姓名验证通过');
    passed++;
} else {
    console.log('  ❌ 有效姓名验证失败');
}

total++;
const shortNameResult = Validator.validatePlayerName('张');
if (!shortNameResult.valid) {
    console.log('  ✅ 短姓名验证通过');
    passed++;
} else {
    console.log('  ❌ 短姓名验证失败');
}

total++;
const invalidNameResult = Validator.validatePlayerName('张@三');
if (!invalidNameResult.valid) {
    console.log('  ✅ 无效字符姓名验证通过');
    passed++;
} else {
    console.log('  ❌ 无效字符姓名验证失败');
}

// 测试邮箱验证
console.log('\n【测试3】邮箱验证');

total++;
const emailResult = Validator.validateEmail('test@example.com');
if (emailResult.valid) {
    console.log('  ✅ 有效邮箱验证通过');
    passed++;
} else {
    console.log('  ❌ 有效邮箱验证失败');
}

total++;
const invalidEmailResult = Validator.validateEmail('invalid-email');
if (!invalidEmailResult.valid) {
    console.log('  ✅ 无效邮箱验证通过');
    passed++;
} else {
    console.log('  ❌ 无效邮箱验证失败');
}

// 测试评级验证
console.log('\n【测试4】评级验证');

total++;
const ratingResult = Validator.validateRating('1800');
if (ratingResult.valid) {
    console.log('  ✅ 有效评级验证通过');
    passed++;
} else {
    console.log('  ❌ 有效评级验证失败');
}

total++;
const highRatingResult = Validator.validateRating('3500');
if (!highRatingResult.valid) {
    console.log('  ✅ 超出范围评级验证通过');
    passed++;
} else {
    console.log('  ❌ 超出范围评级验证失败');
}

// 测试等级验证
console.log('\n【测试5】等级验证');

total++;
const levelResult = Validator.validateLevel('L3');
if (levelResult.valid) {
    console.log('  ✅ 有效等级验证通过');
    passed++;
} else {
    console.log('  ❌ 有效等级验证失败');
}

total++;
const invalidLevelResult = Validator.validateLevel('L5');
if (!invalidLevelResult.valid) {
    console.log('  ✅ 无效等级验证通过');
    passed++;
} else {
    console.log('  ❌ 无效等级验证失败');
}

// 测试FEN验证
console.log('\n【测试6】FEN验证');

total++;
const fenResult = Validator.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
if (fenResult.valid) {
    console.log('  ✅ 有效FEN验证通过');
    passed++;
} else {
    console.log('  ❌ 有效FEN验证失败');
}

total++;
const invalidFenResult = Validator.validateFEN('invalid fen');
if (!invalidFenResult.valid) {
    console.log('  ✅ 无效FEN验证通过');
    passed++;
} else {
    console.log('  ❌ 无效FEN验证失败');
}

// 测试表单验证
console.log('\n【测试7】表单验证');

total++;
const formResult = Validator.validateForm({
    name: '张三',
    email: 'zhangsan@example.com',
    rating: '1800',
    level: 'L3'
});
if (formResult.valid) {
    console.log('  ✅ 有效表单验证通过');
    passed++;
} else {
    console.log('  ❌ 有效表单验证失败');
}

total++;
const invalidFormResult = Validator.validateForm({
    name: '张',
    email: 'invalid',
    rating: 'abc'
});
if (!invalidFormResult.valid && Object.keys(invalidFormResult.errors).length > 0) {
    console.log('  ✅ 无效表单验证通过');
    passed++;
} else {
    console.log('  ❌ 无效表单验证失败');
}

// 测试走法验证
console.log('\n【测试8】走法验证');

total++;
const validMoves = ['e2e4', 'e7e5', 'Nf3', 'Nc6'];
if (Validator.validateMove('e2e4', validMoves)) {
    console.log('  ✅ 有效走法验证通过');
    passed++;
} else {
    console.log('  ❌ 有效走法验证失败');
}

total++;
if (!Validator.validateMove('invalid', validMoves)) {
    console.log('  ✅ 无效走法验证通过');
    passed++;
} else {
    console.log('  ❌ 无效走法验证失败');
}

// 测试错误显示
console.log('\n【测试9】错误显示功能');

total++;
try {
    // 测试getFieldLabel
    const label = Validator.getFieldLabel('name');
    if (label === '姓名') {
        console.log('  ✅ 字段标签获取通过');
        passed++;
    } else {
        console.log('  ❌ 字段标签获取失败');
    }
} catch {
    console.log('  ❌ 字段标签获取失败');
}

console.log('\n' + '='.repeat(60));
console.log('测试结果汇总');
console.log('='.repeat(60));
console.log(`总测试数: ${total}`);
console.log(`通过数: ${passed}`);
console.log(`通过率: ${((passed / total) * 100).toFixed(1)}%`);

if (passed === total) {
    console.log('\n🎉 所有前端验证测试通过！');
    process.exit(0);
} else {
    console.log(`\n⚠️ ${total - passed} 个测试失败`);
    process.exit(1);
}