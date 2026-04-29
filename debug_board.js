/**
 * 调试棋盘交互问题
 * 检查棋子位置获取是否正确
 */

// 模拟 parseFEN
function parseFEN(fen) {
    const board = [];
    const rows = fen.split(' ')[0].split('/');
    for (let row of rows) {
        const boardRow = [];
        for (let char of row) {
            if (/\d/.test(char)) {
                for (let i = 0; i < parseInt(char); i++) boardRow.push(null);
            } else {
                boardRow.push(char);
            }
        }
        board.push(boardRow);
    }
    return board;
}

// 模拟 getPieceAt
function getPieceAt(board, square) {
    const file = square.charCodeAt(0) - 97;
    const rank = 8 - parseInt(square[1]);
    console.log(`getPieceAt(${square}): file=${file}, rank=${rank}`);
    if (rank >= 0 && rank < 8 && file >= 0 && file < 8) {
        const piece = board[rank][file];
        console.log(`  返回: ${piece}`);
        return piece;
    }
    return null;
}

// 测试用FEN（第25步前的状态）
const fen = 'r1b1kb1r/p3p2p/1p3pp1/n1pP4/2P1p2B/2P1P3/P4PPP/1R2KBNR w Kkq - 0 13';
const board = parseFEN(fen);

console.log('=== 测试棋盘交互 ===');
console.log('FEN:', fen);
console.log();

// 测试几个关键位置
const testSquares = ['f2', 'e4', 'd5', 'g4'];
testSquares.forEach(square => {
    const piece = getPieceAt(board, square);
    console.log(`${square}: ${piece || '空'}`);
});

console.log();
console.log('=== 棋盘数组结构 ===');
board.forEach((row, i) => {
    console.log(`${8 - i}: ${row.join(' ')}`);
});