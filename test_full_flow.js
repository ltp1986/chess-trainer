/**
 * 模拟完整的前端交互流程
 */

// 模拟棋盘对象
class MockBoard {
    constructor() {
        this.selectedSquare = null;
        this.legalMoves = [];
        this.board = this.parseFEN('r1b1kb1r/p3p2p/1p3pp1/n1pP4/2P1p2B/2P1P3/P4PPP/1R2KBNR w Kkq - 0 13');
        this.forceTurn = 'w'; // 白方回合
    }

    parseFEN(fen) {
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

    getPieceAt(square) {
        const file = square.charCodeAt(0) - 97;
        const rank = 8 - parseInt(square[1]);
        return this.board[rank][file];
    }

    handleSquareClick(square) {
        const piece = this.getPieceAt(square);
        const turn = this.forceTurn;
        
        console.log(`点击格子: ${square}`);
        console.log(`格子上的棋子: ${piece || '空'}`);
        console.log(`当前回合: ${turn === 'w' ? '白方' : '黑方'}`);
        
        if (!piece) {
            console.log('❌ 格子上没有棋子');
            return;
        }
        
        const isMyPiece = (turn === 'w' && piece === piece.toUpperCase()) || 
                          (turn === 'b' && piece === piece.toLowerCase());
        
        if (!isMyPiece) {
            console.log(`❌ 这不是${turn === 'w' ? '白方' : '黑方'}的棋子`);
            return;
        }
        
        console.log(`✅ 选中${turn === 'w' ? '白方' : '黑方'}棋子`);
        
        if (this.selectedSquare) {
            const from = this.selectedSquare;
            const to = square;
            
            if (from === to) {
                console.log('⚠️ 点击同一个格子，取消选中');
                this.clearSelection();
                return;
            }
            
            console.log(`检查 ${to} 是否在合法着法中...`);
            
            if (this.legalMoves.includes(to)) {
                const moveUCI = from + to;
                console.log(`✅ 执行着法: ${moveUCI}`);
                this.makeMove(moveUCI);
            } else {
                console.log(`❌ ${to} 不是合法着法`);
                this.clearSelection();
            }
            return;
        }
        
        this.selectSquare(square);
    }

    selectSquare(square) {
        this.selectedSquare = square;
        console.log(`选中格子: ${square}`);
        this.fetchLegalMoves(square);
    }

    async fetchLegalMoves(square) {
        // 模拟后端调用
        console.log(`获取 ${square} 的合法着法...`);
        
        // 模拟异步获取
        return new Promise(resolve => {
            setTimeout(() => {
                // 模拟后端返回
                const mockResponse = {
                    legal_moves: ['f3', 'f4'],
                    square: 'f2'
                };
                
                if (mockResponse.legal_moves) {
                    this.legalMoves = mockResponse.legal_moves;
                    console.log(`获取到合法着法: ${this.legalMoves}`);
                    this.render();
                }
                resolve();
            }, 100);
        });
    }

    render() {
        console.log('渲染棋盘，高亮合法着法:', this.legalMoves);
    }

    makeMove(uci) {
        console.log(`执行着法: ${uci}`);
        this.clearSelection();
    }

    clearSelection() {
        this.selectedSquare = null;
        this.legalMoves = [];
        console.log('清除选中状态');
    }
}

// 测试流程
async function runTest() {
    console.log('=== 测试前端交互流程 ===');
    console.log();
    
    const board = new MockBoard();
    
    console.log('步骤1: 点击f2（白兵）');
    await board.handleSquareClick('f2');
    console.log();
    
    console.log('步骤2: 点击f3（合法着法）');
    await board.handleSquareClick('f3');
    console.log();
    
    // 重置
    board.clearSelection();
    
    console.log('步骤3: 点击f2（白兵）');
    await board.handleSquareClick('f2');
    console.log();
    
    console.log('步骤4: 点击g3（非法着法）');
    await board.handleSquareClick('g3');
}

runTest();