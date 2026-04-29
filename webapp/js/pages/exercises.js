let currentExercisePlayerId = '';
let currentPracticeExercise = null;
let selectedPiece = null;
let practiceBoardState = null;

async function loadExercisesPage() {
    const container = document.getElementById('exercises-content');
    const select = document.getElementById('exercises-player-select');
    
    if (!container || !select) return;
    
    showLoading(container);
    
    try {
        const playersData = await apiCall('/api/players');
        const players = playersData.players || [];
        
        select.innerHTML = '<option value="">-- 选择棋手 --</option>';
        players.forEach(player => {
            select.innerHTML += `<option value="${player.player_id}" ${currentExercisePlayerId === player.player_id ? 'selected' : ''}>${player.name}</option>`;
        });
        
        select.addEventListener('change', function(e) {
            currentExercisePlayerId = e.target.value;
            loadExercisesPage();
        });
        
        if (!currentExercisePlayerId) {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">请先选择棋手</p></div>';
            return;
        }
        
        const data = await apiCall(`/api/exercises/player/${currentExercisePlayerId}`);
        
        if (data.exercises && data.exercises.length > 0) {
            const completedCount = data.exercises.filter(e => e.completed).length;
            let html = `
                <div class="mb-4 flex items-center gap-4">
                    <span class="text-gray-600">棋手: ${data.player_name}</span>
                    <span class="text-gray-500">进度: ${completedCount}/${data.exercises.length}</span>
                    <button onclick="generateExercises()" class="ml-auto px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                        🔄 重新生成
                    </button>
                    <button onclick="classifyAllExercises()" class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition">
                        🤖 AI分类
                    </button>
                </div>
                <div class="space-y-3">
            `;
            
            data.exercises.forEach(exercise => {
                const statusClass = exercise.completed ? 'bg-green-100 border-green-300' : 'bg-red-100 border-red-300';
                const statusText = exercise.completed ? '✓ 已完成' : '待练习';
                
                let categoryBadge = '';
                if (exercise.category) {
                    const categoryColors = {
                        '开局错误': 'bg-blue-100 text-blue-700',
                        '中局错误': 'bg-yellow-100 text-yellow-700',
                        '残局错误': 'bg-purple-100 text-purple-700',
                        '战术错误': 'bg-red-100 text-red-700',
                        '战略错误': 'bg-orange-100 text-orange-700',
                        '计算错误': 'bg-pink-100 text-pink-700'
                    };
                    const colorClass = categoryColors[exercise.category] || 'bg-gray-100 text-gray-700';
                    categoryBadge = `<span class="inline-block px-2 py-0.5 rounded-full text-xs ${colorClass}">${exercise.category}</span>`;
                }
                
                let difficultyStars = '';
                if (exercise.difficulty) {
                    difficultyStars = '★'.repeat(exercise.difficulty) + '☆'.repeat(5 - exercise.difficulty);
                }
                
                html += `
                    <div class="border rounded-lg p-4 ${statusClass}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <h4 class="font-medium">错题 #${exercise.id}</h4>
                                    ${categoryBadge}
                                </div>
                                <p class="text-sm text-gray-600">棋局: ${exercise.filename}</p>
                                <p class="text-sm text-gray-600">第 ${exercise.move_number} 步</p>
                                <p class="text-sm text-gray-600">损失: ${exercise.loss} 分</p>
                                ${exercise.description ? `<p class="text-sm text-gray-500 mt-1">${exercise.description}</p>` : ''}
                                ${exercise.suggestion ? `<p class="text-sm text-green-600 mt-1">💡 ${exercise.suggestion}</p>` : ''}
                                ${difficultyStars ? `<div class="text-sm text-yellow-500 mt-1">难度: ${difficultyStars}</div>` : ''}
                            </div>
                            <div class="text-right">
                                <span class="text-sm font-medium ${exercise.completed ? 'text-green-600' : 'text-red-600'}">${statusText}</span>
                                <p class="text-xs text-gray-500">尝试: ${exercise.attempts} 次</p>
                            </div>
                        </div>
                        ${!exercise.completed ? `<button onclick="practiceExercise(${exercise.id})" class="mt-3 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">开始练习</button>` : ''}
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">暂无错题集</p><button onclick="generateExercises()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">生成错题集</button></div>';
        }
    } catch (error) {
        container.innerHTML = `<div class="text-center py-10 text-red-500">加载失败: ${error.message}</div>`;
    }
}

async function generateExercises() {
    if (!currentExercisePlayerId) {
        alert('请先选择棋手');
        return;
    }
    
    const container = document.getElementById('exercises-content');
    showLoading(container);
    
    try {
        const response = await apiCall(`/api/exercises/generate/${currentExercisePlayerId}`, {}, 'POST');
        alert(response.message);
        loadExercisesPage();
    } catch (error) {
        alert('生成失败: ' + error.message);
        loadExercisesPage();
    }
}

async function classifyAllExercises() {
    if (!currentExercisePlayerId) {
        alert('请先选择棋手');
        return;
    }
    
    const container = document.getElementById('exercises-content');
    showLoading(container);
    
    try {
        const data = await apiCall(`/api/exercises/player/${currentExercisePlayerId}`);
        const exercises = data.exercises || [];
        
        if (exercises.length === 0) {
            alert('暂无错题可分类');
            loadExercisesPage();
            return;
        }
        
        const response = await apiCall('/api/exercises/batch_classify', {
            method: 'POST',
            body: { exercises: exercises }
        });
        
        const updatedExercises = data.exercises.map((ex, index) => {
            const classification = response.classifications[index];
            if (classification) {
                return { ...ex, ...classification };
            }
            return ex;
        });
        
        const saveResponse = await apiCall(`/api/exercises/update/${currentExercisePlayerId}`, {
            method: 'POST',
            body: { exercises: updatedExercises }
        });
        
        alert(`🤖 AI分类完成！共分类 ${response.total_count} 道错题`);
        loadExercisesPage();
    } catch (error) {
        alert('分类失败: ' + error.message);
        loadExercisesPage();
    }
}

async function practiceExercise(exerciseId) {
    try {
        const data = await apiCall(`/api/exercises/player/${currentExercisePlayerId}`);
        currentPracticeExercise = data.exercises.find(e => e.id === exerciseId);
        
        if (!currentPracticeExercise) {
            alert('未找到该错题');
            return;
        }
        
        const boardElement = document.getElementById('practice-board');
        if (!boardElement.querySelector('.chess-board')) {
            initPracticeBoard();
        }
        openExerciseModal();
        loadPracticePosition();
    } catch (error) {
        console.error('加载练习失败:', error);
        alert('加载练习失败: ' + error.message);
    }
}

function initPracticeBoard() {
    const boardElement = document.getElementById('practice-board');
    if (!boardElement) return;
    
    practiceBoardState = {
        squares: {}
    };
    
    let html = '<div class="chess-board">';
    
    for (let rank = 8; rank >= 1; rank--) {
        html += '<div class="chess-row">';
        html += `<div class="rank-label">${rank}</div>`;
        
        for (let file = 0; file < 8; file++) {
            const fileName = 'abcdefgh'[file];
            const squareName = fileName + rank;
            const row = 8 - rank;
            const isLight = (row + file) % 2 === 0;
            const colorClass = isLight ? 'light-square' : 'dark-square';
            
            practiceBoardState.squares[squareName] = {
                piece: null,
                isLight: isLight
            };
            
            html += `<div class="chess-square ${colorClass}" data-square="${squareName}"></div>`;
        }
        
        html += '</div>';
    }
    
    html += '<div class="file-labels">';
    for (const file of 'abcdefgh') {
        html += `<div class="file-label">${file}</div>`;
    }
    html += '</div>';
    
    html += '</div>';
    boardElement.innerHTML = html;
    boardElement.addEventListener('click', handlePracticeBoardClick);
}

function openExerciseModal() {
    const modal = document.getElementById('exercise-modal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeExerciseModal() {
    const modal = document.getElementById('exercise-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
    currentPracticeExercise = null;
    selectedPiece = null;
    practiceBoardState = null;
}

function loadPracticePosition() {
    if (!currentPracticeExercise) return;
    
    document.getElementById('practice-filename').textContent = `棋局: ${currentPracticeExercise.filename}`;
    document.getElementById('practice-move-number').textContent = `第 ${currentPracticeExercise.move_number} 步`;
    document.getElementById('practice-loss').textContent = `损失: ${currentPracticeExercise.loss} 分`;
    document.getElementById('practice-feedback').innerHTML = '';
    document.getElementById('practice-hint-text').textContent = '点击"提示"按钮获取帮助';
    
    const fen = currentPracticeExercise.fen;
    const parts = fen.split(' ');
    const piecePlacement = parts[0];
    
    const boardElement = document.getElementById('practice-board');
    boardElement.querySelectorAll('.chess-square').forEach(square => {
        square.innerHTML = '';
        square.classList.remove('selected', 'hint-from', 'hint-to', 'last-move');
    });
    
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
        
        const fileName = 'abcdefgh'[col];
        const rank = row + 1;
        const squareName = fileName + rank;
        const square = boardElement.querySelector(`[data-square="${squareName}"]`);
        
        if (square) {
            const isWhite = char === char.toUpperCase();
            const pieceType = char.toUpperCase();
            const pieceClass = isWhite ? 'piece-white' : 'piece-black';
            
            const pieceIcons = {
                'K': '\u2654',
                'Q': '\u2655',
                'R': '\u2656',
                'B': '\u2657',
                'N': '\u2658',
                'P': '\u2659'
            };
            
            const iconSpan = document.createElement('span');
            iconSpan.className = `chess-piece ${pieceClass}`;
            iconSpan.dataset.piece = char;
            iconSpan.textContent = pieceIcons[pieceType];
            square.appendChild(iconSpan);
            
            if (practiceBoardState) {
                practiceBoardState.squares[squareName].piece = char;
            }
        }
        col++;
    }
}

function handlePracticeBoardClick(e) {
    const square = e.target.closest('.chess-square');
    if (!square || !currentPracticeExercise) return;
    
    const squareName = square.dataset.square;
    
    document.querySelectorAll('.chess-square').forEach(s => s.classList.remove('selected'));
    clearMoveArrows();
    
    if (!selectedPiece) {
        const pieceEl = square.querySelector('.chess-piece');
        if (pieceEl) {
            selectedPiece = squareName;
            square.classList.add('selected');
            showLegalMoves(squareName);
        }
    } else {
        const from = selectedPiece;
        const to = squareName;
        const move = from + to;
        selectedPiece = null;
        
        drawMoveArrow(from, to);
        setTimeout(() => {
            checkMove(move);
        }, 300);
    }
}

function showLegalMoves(squareName) {
    const legalMoves = getLegalMoves(squareName);
    legalMoves.forEach(move => {
        const targetSquare = move.substring(2, 4);
        const targetEl = document.querySelector(`[data-square="${targetSquare}"]`);
        if (targetEl) {
            targetEl.classList.add('legal-move');
        }
    });
}

function getLegalMoves(fromSquare) {
    const moves = [];
    const files = 'abcdefgh';
    const ranks = '12345678';
    
    const piece = practiceBoardState?.squares[fromSquare]?.piece;
    if (!piece) return [];
    
    const pieceType = piece.toUpperCase();
    const isWhite = piece === piece.toUpperCase();
    
    const file = fromSquare[0];
    const rank = parseInt(fromSquare[1]);
    const fileIndex = files.indexOf(file);
    
    if (pieceType === 'P') {
        const direction = isWhite ? 1 : -1;
        if (ranks.includes(String(rank + direction))) {
            moves.push(`${fromSquare}${file}${rank + direction}`);
        }
        if ((rank === 2 && isWhite) || (rank === 7 && !isWhite)) {
            if (ranks.includes(String(rank + 2 * direction))) {
                moves.push(`${fromSquare}${file}${rank + 2 * direction}`);
            }
        }
        const captureFiles = [fileIndex - 1, fileIndex + 1];
        captureFiles.forEach(fi => {
            if (fi >= 0 && fi < 8) {
                const captureFile = files[fi];
                if (ranks.includes(String(rank + direction))) {
                    moves.push(`${fromSquare}${captureFile}${rank + direction}`);
                }
            }
        });
    } else if (pieceType === 'N') {
        const knightMoves = [
            [2, 1], [2, -1], [-2, 1], [-2, -1],
            [1, 2], [1, -2], [-1, 2], [-1, -2]
        ];
        knightMoves.forEach(([df, dr]) => {
            const newFileIndex = fileIndex + df;
            const newRank = rank + dr;
            if (newFileIndex >= 0 && newFileIndex < 8 && newRank >= 1 && newRank <= 8) {
                moves.push(`${fromSquare}${files[newFileIndex]}${newRank}`);
            }
        });
    }
    
    return moves;
}

function checkMove(move) {
    if (!currentPracticeExercise) return;
    
    const bestMove = currentPracticeExercise.best_move;
    
    if (move === bestMove) {
        highlightMove(move);
        document.getElementById('practice-feedback').innerHTML = 
            '<div class="bg-green-100 border border-green-300 rounded-lg p-4"><p class="text-green-600 font-medium">✅ 正确！太棒了！</p></div>';
        markExerciseCompleted();
    } else {
        document.getElementById('practice-feedback').innerHTML = 
            `<div class="bg-red-100 border border-red-300 rounded-lg p-4"><p class="text-red-600 font-medium">❌ 错误！再试试吧！</p></div>`;
    }
}

function highlightMove(move) {
    const from = move.substring(0, 2);
    const to = move.substring(2, 4);
    
    const fromSquare = document.querySelector(`[data-square="${from}"]`);
    const toSquare = document.querySelector(`[data-square="${to}"]`);
    
    if (fromSquare) fromSquare.classList.add('last-move');
    if (toSquare) toSquare.classList.add('last-move');
    
    const fromPiece = fromSquare?.querySelector('.chess-piece');
    if (fromPiece) {
        toSquare.innerHTML = fromSquare.innerHTML;
        fromSquare.innerHTML = '';
    }
}

function showPracticeHint() {
    console.log('showPracticeHint called');
    if (!currentPracticeExercise || !currentPracticeExercise.best_move) {
        console.log('No exercise or best move');
        return;
    }
    
    const bestMove = currentPracticeExercise.best_move;
    const fromSquare = bestMove.substring(0, 2);
    const toSquare = bestMove.substring(2, 4);
    
    console.log(`Hint: ${fromSquare} -> ${toSquare}`);
    
    const hint = `提示：从 ${fromSquare} 移动到 ${toSquare} 附近`;
    document.getElementById('practice-hint-text').textContent = hint;
    
    document.querySelectorAll('.chess-square').forEach(s => {
        s.classList.remove('hint-from', 'hint-to');
    });
    
    const fromEl = document.querySelector(`[data-square="${fromSquare}"]`);
    const toEl = document.querySelector(`[data-square="${toSquare}"]`);
    
    if (fromEl) {
        fromEl.classList.add('hint-from');
        console.log('Added hint-from to', fromSquare);
    }
    if (toEl) {
        toEl.classList.add('hint-to');
        console.log('Added hint-to to', toSquare);
    }
    
    drawMoveArrow(fromSquare, toSquare);
}

function showPracticeAnswer() {
    console.log('showPracticeAnswer called');
    if (!currentPracticeExercise || !currentPracticeExercise.best_move) {
        console.log('No exercise or best move');
        return;
    }
    
    const bestMove = currentPracticeExercise.best_move;
    const fromSquare = bestMove.substring(0, 2);
    const toSquare = bestMove.substring(2, 4);
    
    console.log(`Answer: ${fromSquare} -> ${toSquare}`);
    
    document.querySelectorAll('.chess-square').forEach(s => {
        s.classList.remove('hint-from', 'hint-to');
    });
    
    const fromEl = document.querySelector(`[data-square="${fromSquare}"]`);
    const toEl = document.querySelector(`[data-square="${toSquare}"]`);
    
    if (fromEl) {
        fromEl.classList.add('hint-from');
        console.log('Added hint-from to', fromSquare);
    }
    if (toEl) {
        toEl.classList.add('hint-to');
        console.log('Added hint-to to', toSquare);
    }
    
    drawMoveArrow(fromSquare, toSquare);
    
    document.getElementById('practice-feedback').innerHTML = 
        `<div class="bg-yellow-100 border border-yellow-300 rounded-lg p-4"><p class="text-yellow-800 font-medium">✅ 正确答案: ${bestMove}</p></div>`;
}

function drawMoveArrow(from, to) {
    clearMoveArrows();
    
    const fromEl = document.querySelector(`[data-square="${from}"]`);
    const toEl = document.querySelector(`[data-square="${to}"]`);
    
    if (!fromEl || !toEl) return;
    
    const board = document.querySelector('.chess-board');
    if (!board) return;
    
    const fromRect = fromEl.getBoundingClientRect();
    const toRect = toEl.getBoundingClientRect();
    const boardRect = board.getBoundingClientRect();
    
    const fromX = fromRect.left - boardRect.left + fromRect.width / 2;
    const fromY = fromRect.top - boardRect.top + fromRect.height / 2;
    const toX = toRect.left - boardRect.left + toRect.width / 2;
    const toY = toRect.top - boardRect.top + toRect.height / 2;
    
    const arrowSVG = `
        <svg class="move-arrow-svg" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 100;">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="#FFD700" />
                </marker>
            </defs>
            <line x1="${fromX}" y1="${fromY}" x2="${toX}" y2="${toY}" stroke="#FFD700" stroke-width="4" stroke-linecap="round" marker-end="url(#arrowhead)" />
        </svg>
    `;
    
    board.style.position = 'relative';
    board.innerHTML += arrowSVG;
}

function clearMoveArrows() {
    document.querySelectorAll('.move-arrow-svg').forEach(arrow => arrow.remove());
}

async function markExerciseCompleted() {
    try {
        await apiCall(`/api/exercises/update/${currentExercisePlayerId}`, {
            exercise_id: currentPracticeExercise.id,
            status: 'completed'
        }, 'POST');
        loadExercisesPage();
    } catch (error) {
        console.error('更新练习状态失败:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('practice-hint')?.addEventListener('click', showPracticeHint);
    document.getElementById('practice-answer')?.addEventListener('click', showPracticeAnswer);
    document.getElementById('practice-close')?.addEventListener('click', closeExerciseModal);
});