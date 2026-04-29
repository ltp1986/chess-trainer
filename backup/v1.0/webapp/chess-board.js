// 简单可靠的国际象棋棋盘组件
// 使用 chess.js 处理规则，前端只负责渲染和交互

class SimpleChessBoard {
    constructor(elementId, options = {}) {
        this.element = document.getElementById(elementId);
        this.game = new Chess(); // chess.js 实例
        this.selectedSquare = null;
        this.legalMoves = []; // 当前选中棋子的合法目标位置
        this.lastMove = null;
        this.onMove = options.onMove || null; // 走子回调
        this.orientation = options.orientation || 'white'; // white | black
        this.readonly = options.readonly || false;

        this.pieceSymbols = {
            'w': { 'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙' },
            'b': { 'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟' }
        };

        this.init();
    }

    init() {
        this.render();
    }

    // 从 chess.js 获取棋盘数组并渲染
    render() {
        this.element.innerHTML = '';
        const board = this.game.board(); // 8x8 数组，null 或 {type, color}

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                // 根据视角计算实际显示的行列
                const r = this.orientation === 'white' ? 7 - row : row;
                const c = this.orientation === 'white' ? col : 7 - col;

                const squareName = String.fromCharCode(97 + c) + (r + 1);
                const piece = board[r][c];

                const square = document.createElement('div');
                square.className = `chess-square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
                square.dataset.square = squareName;

                // 坐标标签
                if (c === 0) {
                    const rank = document.createElement('span');
                    rank.className = 'coord-rank';
                    rank.textContent = r + 1;
                    square.appendChild(rank);
                }
                if (r === 0) {
                    const file = document.createElement('span');
                    file.className = 'coord-file';
                    file.textContent = String.fromCharCode(97 + c);
                    square.appendChild(file);
                }

                // 棋子
                if (piece) {
                    const pieceEl = document.createElement('div');
                    pieceEl.className = `chess-piece ${piece.color === 'w' ? 'white' : 'black'}`;
                    pieceEl.textContent = this.pieceSymbols[piece.color][piece.type];
                    square.appendChild(pieceEl);
                }

                // 高亮上次移动
                if (this.lastMove && (squareName === this.lastMove.from || squareName === this.lastMove.to)) {
                    square.classList.add('last-move');
                }

                // 高亮选中
                if (this.selectedSquare === squareName) {
                    square.classList.add('selected');
                }

                // 合法着法标记
                if (this.legalMoves.includes(squareName)) {
                    square.classList.add('legal-target');
                    if (piece) square.classList.add('capture');
                }

                if (!this.readonly) {
                    square.addEventListener('click', () => this.onSquareClick(squareName));
                }

                this.element.appendChild(square);
            }
        }
    }

    onSquareClick(square) {
        if (this.readonly) return;

        const piece = this.game.get(square);
        const turn = this.game.turn();

        // 已选中棋子
        if (this.selectedSquare) {
            const from = this.selectedSquare;
            const to = square;

            // 点击同一格 = 取消
            if (from === to) {
                this.clearSelection();
                return;
            }

            // 点击自己的其他棋子 = 切换选中
            if (piece && piece.color === turn) {
                this.selectSquare(square);
                return;
            }

            // 尝试走子
            this.tryMove(from, to);
            return;
        }

        // 未选中，点击自己的棋子 = 选中
        if (piece && piece.color === turn) {
            this.selectSquare(square);
        }
    }

    selectSquare(square) {
        this.selectedSquare = square;

        // 使用 chess.js 计算合法着法
        const moves = this.game.moves({
            square: square,
            verbose: true
        });
        this.legalMoves = moves.map(m => m.to);

        this.render();
    }

    clearSelection() {
        this.selectedSquare = null;
        this.legalMoves = [];
        this.render();
    }

    tryMove(from, to) {
        // 使用 chess.js 验证并执行着法
        const move = this.game.move({
            from: from,
            to: to,
            promotion: 'q' // 自动升变为后
        });

        if (move) {
            // 走子成功
            this.lastMove = { from: move.from, to: move.to };
            this.clearSelection();

            if (this.onMove) {
                this.onMove({
                    san: move.san,
                    from: move.from,
                    to: move.to,
                    promotion: move.promotion,
                    fen: this.game.fen()
                });
            }
        } else {
            // 非法着法，取消选中
            this.clearSelection();
        }
    }

    // 公共API
    setPosition(fen) {
        this.game.load(fen);
        this.lastMove = null;
        this.clearSelection();
    }

    getFen() {
        return this.game.fen();
    }

    getTurn() {
        return this.game.turn();
    }

    undo() {
        const move = this.game.undo();
        if (move) {
            this.lastMove = null;
            this.render();
        }
        return move;
    }

    flip() {
        this.orientation = this.orientation === 'white' ? 'black' : 'white';
        this.render();
    }

    highlightSquare(square, type) {
        const sq = this.element.querySelector(`[data-square="${square}"]`);
        if (sq) {
            const className = type === 'correct' ? 'highlight-correct' : 'highlight-wrong';
            sq.classList.add(className);
            setTimeout(() => sq.classList.remove(className), 1500);
        }
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimpleChessBoard;
}
