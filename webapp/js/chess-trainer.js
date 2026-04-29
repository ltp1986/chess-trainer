class ChessTrainer {
    constructor() {
        console.log('♟️ 初始化ChessTrainer...');
        this.boardElement = document.getElementById('board');
        this.exerciseBoard = document.getElementById('exercise-board');
        this.mistakes = [];
        this.currentMistakeIndex = 0;
        this.isPlaying = false;
        this.playInterval = null;
        this.selectedPiece = null;
        this.exercises = [];
        this.currentExerciseIndex = 0;
        this.exerciseStats = { correct: 0, wrong: 0 };

        if (!this.boardElement) {
            console.error('❌ 棋盘元素未找到');
            return;
        }

        this.initBoard(this.boardElement);
        if (this.exerciseBoard) {
            this.initBoard(this.exerciseBoard);
        }
        this.bindEvents();
        console.log('✅ ChessTrainer初始化完成');
    }

    initBoard(boardElement) {
        console.log('🎨 初始化棋盘...');
        const colors = ['#f0d9b5', '#b58863'];
        let html = '';
        const files = 'abcdefgh';
        
        for (let row = 7; row >= 0; row--) {
            for (let col = 0; col < 8; col++) {
                const colorIndex = (row + col) % 2;
                const squareName = this.getSquareName(col, row);
                const rank = row + 1;
                const file = files[col];
                
                let coordHtml = '';
                if (col === 0) {
                    coordHtml += `<span class="coord-rank">${rank}</span>`;
                }
                if (row === 0) {
                    coordHtml += `<span class="coord-file">${file}</span>`;
                }
                
                html += `
                    <div class="chess-square flex items-center justify-center cursor-pointer relative"
                         data-square="${squareName}"
                         style="background-color: ${colors[colorIndex]}">
                        ${coordHtml}
                    </div>
                `;
            }
        }
        boardElement.innerHTML = html;
    }

    getSquareName(col, row) {
        const files = 'abcdefgh';
        return files[col] + (row + 1);
    }

    bindEvents() {
        document.getElementById('load-btn').addEventListener('click', () => this.loadPGN());
        document.getElementById('demo-btn').addEventListener('click', () => this.loadDemoData());
        document.getElementById('prev-btn').addEventListener('click', () => this.prevMistake());
        document.getElementById('next-btn').addEventListener('click', () => this.nextMistake());
        document.getElementById('play-btn').addEventListener('click', () => this.play());
        document.getElementById('pause-btn').addEventListener('click', () => this.pause());
        document.getElementById('review-tab').addEventListener('click', () => this.showReview());
        document.getElementById('exercise-tab').addEventListener('click', () => this.showExercise());
        document.getElementById('exercise-hint').addEventListener('click', () => this.showHint());
        document.getElementById('exercise-answer').addEventListener('click', () => this.showAnswer());
        document.getElementById('exercise-next').addEventListener('click', () => this.nextExercise());
        
        this.boardElement.addEventListener('click', (e) => this.handleBoardClick(e));
        if (this.exerciseBoard) {
            this.exerciseBoard.addEventListener('click', (e) => this.handleExerciseClick(e));
        }
    }

    async loadPGN() {
        const select = document.getElementById('pgn-select');
        const filename = select.value;
        if (!filename) {
            alert('请选择PGN文件');
            return;
        }
        try {
            const data = await apiCall(`/api/analyze/${filename}`);
            this.processAnalysis(data);
        } catch (error) {
            alert('加载失败: ' + error.message);
        }
    }

    async loadDemoData() {
        console.log('📥 加载演示数据...');
        try {
            const demoPGN = `[Event "Demo Game"]
[Site "Local"]
[Date "2024.01.15"]
[White "WhitePlayer"]
[Black "BlackPlayer"]
[Result "0-1"]
1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Nc3 Nxe4 0-1`;
            
            await apiCall('/api/library/game', {
                method: 'POST',
                body: { pgn_content: demoPGN, filename: 'demo_game.pgn' }
            });
            
            await apiCall('/api/player', {
                method: 'POST',
                body: { name: '演示棋手', level: 'L3', rating: 1800 }
            });

            const data = await apiCall('/api/analyze/demo_game.pgn');
            this.processAnalysis(data);
            alert('演示数据加载成功!');
        } catch (error) {
            console.error('❌ 加载演示数据失败:', error);
            alert('加载演示数据失败: ' + error.message);
        }
    }

    processAnalysis(data) {
        console.log('📊 处理分析数据...');
        console.log('原始数据:', data);
        
        this.mistakes = data.mistakes || data.demonstration_mistakes || [];
        this.exercises = data.exercises || [];
        
        if (this.mistakes.length === 0 && data.filtered_mistakes > 0) {
            console.warn('⚠️ 检测到有筛选后的失误但没有mistakes字段，尝试从exercises重建');
            this.mistakes = this.exercises.map((ex, index) => ({
                step: ex.step,
                loss: ex.loss,
                fen: ex.fen,
                turn: ex.turn,
                actual_move: ex.actual_move || '未知',
                best_move: ex.best_move,
                cause: '原因分析',
                idea: '改进思路',
                tactic_exp: '战术解释'
            }));
        }
        
        console.log(`✅ 处理完成: ${this.mistakes.length}个失误, ${this.exercises.length}个习题`);
        
        this.updateMistakeList();
        this.updateProgress(0);
        
        if (this.mistakes.length > 0) {
            this.showMistake(0);
        } else {
            console.error('❌ 没有找到失误数据，请检查PGN文件和分析设置');
        }
        
        document.getElementById('exercise-total').textContent = this.exercises.length;
    }

    updateMistakeList() {
        const list = document.getElementById('mistake-list');
        if (!list || this.mistakes.length === 0) {
            list.innerHTML = '<p class="text-gray-500 text-center py-4">无失误数据</p>';
            return;
        }

        let html = '';
        this.mistakes.forEach((mistake, index) => {
            html += `
                <div class="p-2 rounded-lg cursor-pointer hover:bg-gray-100 ${index === 0 ? 'bg-blue-50' : ''}"
                     onclick="trainer.showMistake(${index})">
                    <div class="flex justify-between">
                        <span class="font-medium">失误 ${index + 1}</span>
                        <span class="text-sm text-red-500">-${mistake.loss}cp</span>
                    </div>
                    <div class="text-sm text-gray-500">第${mistake.step}步</div>
                </div>
            `;
        });
        list.innerHTML = html;
    }

    updateProgress(index) {
        const total = this.mistakes.length;
        const progress = total > 0 ? ((index + 1) / total) * 100 : 0;
        
        document.getElementById('progress-text').textContent = `${index + 1}/${total}`;
        document.getElementById('progress-bar').style.width = `${progress}%`;
        
        const status = document.getElementById('progress-status');
        if (progress === 100) {
            status.textContent = '✅ 已完成复盘，可以开始习题练习';
            document.getElementById('exercise-tab').disabled = false;
            document.getElementById('exercise-tab').classList.remove('bg-gray-200', 'text-gray-700');
            document.getElementById('exercise-tab').classList.add('bg-green-500', 'text-white');
        } else {
            status.textContent = '请观看复盘演示以解锁习题练习';
        }
    }

    showMistake(index) {
        if (index < 0 || index >= this.mistakes.length) return;
        
        this.currentMistakeIndex = index;
        const mistake = this.mistakes[index];
        
        this.clearHighlights();
        this.displayPosition(mistake.fen, this.boardElement);
        document.getElementById('bad-move').textContent = mistake.actual_move;
        document.getElementById('bad-cause').textContent = mistake.cause || '原因分析';
        document.getElementById('good-move').textContent = mistake.best_move;
        document.getElementById('good-idea').textContent = mistake.idea || '改进思路';
        document.getElementById('tactic-exp').textContent = mistake.tactic_exp || '战术解释';
        
        this.highlightMistake(mistake);
        this.updateProgress(index);
        
        document.querySelectorAll('.mistake-item').forEach((el, i) => {
            el.classList.toggle('bg-blue-50', i === index);
        });
        
        if (this.mistakes.length > 5 && index >= 5) {
            document.getElementById('remaining-mistakes').classList.remove('hidden');
        }
    }

    clearHighlights() {
        document.querySelectorAll('.chess-square').forEach(square => {
            square.classList.remove('highlight-error', 'highlight-correct', 'legal-move', 'legal-capture', 'selected-piece');
        });
    }

    highlightMistake(mistake) {
        if (!mistake.actual_move || mistake.actual_move.length < 4) return;
        
        const actualFrom = mistake.actual_move.substring(0, 2);
        const actualTo = mistake.actual_move.substring(2, 4);
        
        const fromSquare = document.querySelector(`#board [data-square="${actualFrom}"]`);
        const toSquare = document.querySelector(`#board [data-square="${actualTo}"]`);
        
        if (fromSquare) fromSquare.classList.add('highlight-error');
        if (toSquare) toSquare.classList.add('highlight-error');
        
        if (mistake.best_move && mistake.best_move.length >= 4) {
            const bestFrom = mistake.best_move.substring(0, 2);
            const bestTo = mistake.best_move.substring(2, 4);
            
            const bestFromSquare = document.querySelector(`#board [data-square="${bestFrom}"]`);
            const bestToSquare = document.querySelector(`#board [data-square="${bestTo}"]`);
            
            if (bestFromSquare && !bestFromSquare.classList.contains('highlight-error')) {
                bestFromSquare.classList.add('highlight-correct');
            }
            if (bestToSquare && !bestToSquare.classList.contains('highlight-error')) {
                bestToSquare.classList.add('highlight-correct');
            }
        }
    }

    displayPosition(fen, boardElement) {
        console.log('🎯 显示局面:', fen);
        const squares = boardElement.querySelectorAll('.chess-square');
        squares.forEach(square => {
            const children = square.querySelectorAll(':not(.coord-rank):not(.coord-file)');
            children.forEach(child => child.remove());
        });
        
        const parts = fen.split(' ');
        const piecePlacement = parts[0];
        const files = 'abcdefgh';
        
        let row = 7;
        let col = 0;
        
        for (const char of piecePlacement) {
            if (char === '/') {
                row--;
                col = 0;
                continue;
            }
            
            if (char >= '1' && char <= '8') {
                col += parseInt(char);
                continue;
            }
            
            const squareName = files[col] + (row + 1);
            const square = boardElement.querySelector(`[data-square="${squareName}"]`);
            if (square) {
                const pieceEl = document.createElement('span');
                pieceEl.className = `chess-piece ${char === char.toUpperCase() ? 'piece-white' : 'piece-black'}`;
                pieceEl.textContent = this.getPieceSymbol(char);
                square.appendChild(pieceEl);
            }
            col++;
        }
    }

    getPieceSymbol(piece) {
        const symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        return symbols[piece] || '';
    }

    prevMistake() {
        if (this.currentMistakeIndex > 0) {
            this.showMistake(this.currentMistakeIndex - 1);
        }
    }

    nextMistake() {
        if (this.currentMistakeIndex < this.mistakes.length - 1) {
            this.showMistake(this.currentMistakeIndex + 1);
        }
    }

    play() {
        if (this.isPlaying || this.mistakes.length === 0) return;
        
        this.isPlaying = true;
        document.getElementById('play-btn').disabled = true;
        document.getElementById('pause-btn').disabled = false;
        
        this.playInterval = setInterval(() => {
            if (this.currentMistakeIndex < this.mistakes.length - 1) {
                this.nextMistake();
            } else {
                this.pause();
            }
        }, 3000);
    }

    pause() {
        this.isPlaying = false;
        clearInterval(this.playInterval);
        document.getElementById('play-btn').disabled = false;
        document.getElementById('pause-btn').disabled = true;
    }

    showReview() {
        document.getElementById('exercise-area').classList.add('hidden');
        document.getElementById('board-container').classList.remove('hidden');
    }

    showExercise() {
        if (this.exercises.length === 0) {
            alert('暂无习题数据');
            return;
        }
        document.getElementById('board-container').classList.add('hidden');
        document.getElementById('exercise-area').classList.remove('hidden');
        this.loadExercise(0);
    }

    loadExercise(index) {
        if (index < 0 || index >= this.exercises.length) return;
        
        this.currentExerciseIndex = index;
        const exercise = this.exercises[index];
        
        document.getElementById('exercise-current').textContent = index + 1;
        this.displayPosition(exercise.fen, this.exerciseBoard);
        this.selectedPiece = null;
        document.getElementById('exercise-feedback').innerHTML = '';
    }

    handleExerciseClick(e) {
        const square = e.target.closest('.chess-square');
        if (!square) return;
        
        const squareName = square.dataset.square;
        const exercise = this.exercises[this.currentExerciseIndex];
        
        if (!this.selectedPiece) {
            const piece = square.querySelector('.chess-piece');
            if (piece) {
                this.selectedPiece = squareName;
                this.showLegalMoves(squareName, exercise.fen);
                square.classList.add('selected-piece');
            }
        } else {
            const from = this.selectedPiece;
            const to = squareName;
            const move = from + to;
            
            this.clearHighlights();
            this.selectedPiece = null;
            
            if (move === exercise.best_move) {
                this.showCorrectFeedback();
                this.exerciseStats.correct++;
            } else {
                this.showWrongFeedback(exercise);
                this.exerciseStats.wrong++;
            }
        }
    }

    showLegalMoves(squareName, fen) {
        this.clearHighlights();
        
        const legalMoves = this.getLegalMoves(fen, squareName);
        
        legalMoves.forEach(move => {
            const targetSquare = document.querySelector(`#exercise-board [data-square="${move.to}"]`);
            if (targetSquare) {
                if (move.capture) {
                    targetSquare.classList.add('legal-capture');
                } else {
                    targetSquare.classList.add('legal-move');
                }
            }
        });
    }

    getLegalMoves(fen, fromSquare) {
        const moves = [];
        const board = this.parseFEN(fen);
        const piece = board[fromSquare];
        
        if (!piece) return moves;
        
        const isWhite = piece === piece.toUpperCase();
        const directions = {
            'P': isWhite ? [[0, -1], [0, -2], [-1, -1], [1, -1]] : [[0, 1], [0, 2], [-1, 1], [1, 1]],
            'N': [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]],
            'B': [[-1, -1], [-1, 1], [1, -1], [1, 1]],
            'R': [[-1, 0], [1, 0], [0, -1], [0, 1]],
            'Q': [[-1, -1], [-1, 1], [1, -1], [1, 1], [-1, 0], [1, 0], [0, -1], [0, 1]],
            'K': [[-1, -1], [-1, 1], [1, -1], [1, 1], [-1, 0], [1, 0], [0, -1], [0, 1]]
        };
        
        const pieceType = piece.toUpperCase();
        const dirs = directions[pieceType] || [];
        
        dirs.forEach(dir => {
            let [dx, dy] = dir;
            let newCol = fromSquare.charCodeAt(0) - 'a'.charCodeAt(0) + dx;
            let newRow = parseInt(fromSquare.charAt(1)) - 1 + dy;
            
            if (pieceType === 'P') {
                if (Math.abs(dy) === 2) {
                    const startRow = isWhite ? 6 : 1;
                    if (parseInt(fromSquare.charAt(1)) - 1 !== startRow) return;
                    const middleSquare = String.fromCharCode('a'.charCodeAt(0) + newCol - dx) + (newRow - dy + 1);
                    if (board[middleSquare]) return;
                }
                if (Math.abs(dx) === 1 && !board[String.fromCharCode('a'.charCodeAt(0) + newCol) + (newRow + 1)]) return;
            }
            
            while (newCol >= 0 && newCol < 8 && newRow >= 0 && newRow < 8) {
                const toSquare = String.fromCharCode('a'.charCodeAt(0) + newCol) + (newRow + 1);
                const targetPiece = board[toSquare];
                
                if (!targetPiece) {
                    if (pieceType === 'P' && Math.abs(dx) === 0) {
                        moves.push({ to: toSquare, capture: false });
                    } else if (pieceType !== 'P') {
                        moves.push({ to: toSquare, capture: false });
                    }
                } else {
                    const targetIsWhite = targetPiece === targetPiece.toUpperCase();
                    if (targetIsWhite !== isWhite) {
                        if (pieceType === 'P' && Math.abs(dx) > 0) {
                            moves.push({ to: toSquare, capture: true });
                        } else if (pieceType !== 'P') {
                            moves.push({ to: toSquare, capture: true });
                        }
                    }
                    break;
                }
                
                if (pieceType === 'N' || pieceType === 'K') break;
                
                newCol += dx;
                newRow += dy;
            }
        });
        
        return moves;
    }

    parseFEN(fen) {
        const board = {};
        const parts = fen.split(' ')[0];
        const rows = parts.split('/');
        
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            let col = 0;
            for (const char of row) {
                if (char >= '1' && char <= '8') {
                    col += parseInt(char);
                } else {
                    const square = String.fromCharCode('a'.charCodeAt(0) + col) + (8 - i);
                    board[square] = char;
                    col++;
                }
            }
        }
        
        return board;
    }

    showCorrectFeedback() {
        const feedback = document.getElementById('exercise-feedback');
        feedback.innerHTML = `
            <div class="bg-green-100 border border-green-300 rounded-lg p-4 feedback-correct">
                <p class="text-green-700 font-bold text-lg">🎉 太棒了！正确！</p>
                <p class="text-green-600 text-sm mt-1">你找到了最佳走法！</p>
            </div>
        `;
        feedback.classList.remove('feedback-wrong');
        feedback.classList.add('feedback-correct');
    }

    showWrongFeedback(exercise) {
        const feedback = document.getElementById('exercise-feedback');
        feedback.innerHTML = `
            <div class="bg-red-100 border border-red-300 rounded-lg p-4 feedback-wrong">
                <p class="text-red-700 font-bold text-lg">😅 差一点！</p>
                <p class="text-red-600 text-sm mt-1">正确答案: <span class="font-mono font-bold">${exercise.best_move}</span></p>
                <p class="text-gray-600 text-sm mt-2">${exercise.idea || '再想想，寻找更好的走法！'}</p>
            </div>
        `;
        feedback.classList.remove('feedback-correct');
        feedback.classList.add('feedback-wrong');
    }

    showHint() {
        const exercise = this.exercises[this.currentExerciseIndex];
        alert('提示: ' + (exercise.hint || '寻找最佳着法'));
    }

    showAnswer() {
        const exercise = this.exercises[this.currentExerciseIndex];
        alert(`正确答案: ${exercise.best_move}`);
    }

    nextExercise() {
        if (this.currentExerciseIndex < this.exercises.length - 1) {
            this.loadExercise(this.currentExerciseIndex + 1);
        } else {
            alert(`练习完成！正确: ${this.exerciseStats.correct}, 错误: ${this.exerciseStats.wrong}`);
        }
    }

    handleBoardClick() {
    }
}