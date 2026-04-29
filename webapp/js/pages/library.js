async function loadLibraryPage() {
    const container = document.getElementById('library-content');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const data = await apiCall('/api/library/games');
        const playersData = await apiCall('/api/players');
        const playersMap = {};
        playersData.players.forEach(p => {
            playersMap[p.player_id] = p.name;
        });
        
        if (data.games && data.games.length > 0) {
            let html = '<div id="library-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
            data.games.forEach(game => {
                const whiteName = game.white_player_id ? playersMap[game.white_player_id] || '未知' : game.white;
                const blackName = game.black_player_id ? playersMap[game.black_player_id] || '未知' : game.black;
                const hasAssociation = game.white_player_id || game.black_player_id;
                
                html += `
                    <div class="bg-white rounded-xl shadow-md p-4">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="font-semibold text-gray-800">${game.filename}</h3>
                                <p class="text-sm text-gray-600">
                                    ${whiteName} <span class="text-gray-400">vs</span> ${blackName}
                                    ${hasAssociation ? '<span class="text-xs bg-green-100 text-green-600 px-1.5 py-0.5 rounded ml-1">已关联</span>' : ''}
                                </p>
                                <p class="text-sm text-gray-500">结果: ${game.result}</p>
                            </div>
                            <div class="flex gap-2">
                                <button onclick="editGameAssociation('${game.game_id}')" class="px-3 py-1 bg-yellow-500 text-white rounded-lg text-sm">关联棋手</button>
                                <button onclick="deleteGame('${game.game_id}', '${game.filename}')" class="px-3 py-1 bg-red-500 text-white rounded-lg text-sm">删除</button>
                                <span class="px-2 py-1 bg-red-100 text-red-600 rounded-full text-xs">${game.total_mistakes || 0}个失误</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">暂无棋局数据</p><button onclick="showAddGameModal()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">添加</button></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="text-center py-10 text-red-500">加载失败</div>';
    }
}

async function editGameAssociation(gameId) {
    try {
        const gameData = await apiCall(`/api/library/game/${gameId}`);
        await loadPlayersToSelects();
        
        document.getElementById('white-player-select').value = gameData.white_player_id || '';
        document.getElementById('black-player-select').value = gameData.black_player_id || '';
        document.getElementById('game-pgn').value = gameData.pgn_content || '';
        document.getElementById('game-filename').value = gameData.filename || '';
        document.getElementById('game-modal').classList.remove('hidden');
        
        const form = document.getElementById('game-form');
        
        form.onsubmit = async function(e) {
            e.preventDefault();
            
            const whitePlayerId = document.getElementById('white-player-select').value;
            const blackPlayerId = document.getElementById('black-player-select').value;
            
            try {
                await apiCall(`/api/library/game/${gameId}/associate`, {
                    method: 'POST',
                    body: {
                        white_player_id: whitePlayerId,
                        black_player_id: blackPlayerId
                    }
                });
                closeGameModal();
                loadLibraryPage();
                alert('棋手关联更新成功!');
            } catch (error) {
                alert('更新失败: ' + error.message);
            }
        };
    } catch (error) {
        alert('加载棋局失败: ' + error.message);
    }
}

async function showAddGameModal() {
    await loadPlayersToSelects();
    document.getElementById('game-modal').classList.remove('hidden');
    
    document.getElementById('game-file').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('game-filename').value = file.name;
        }
    });
}

function closeGameModal() {
    document.getElementById('game-modal').classList.add('hidden');
    document.getElementById('game-form').reset();
}

async function loadPlayersToSelects() {
    try {
        const data = await apiCall('/api/players');
        const whiteSelect = document.getElementById('white-player-select');
        const blackSelect = document.getElementById('black-player-select');
        
        whiteSelect.innerHTML = '<option value="">-- 选择棋手 --</option>';
        blackSelect.innerHTML = '<option value="">-- 选择棋手 --</option>';
        
        data.players.forEach(player => {
            const option = `<option value="${player.player_id}">${player.name}</option>`;
            whiteSelect.innerHTML += option;
            blackSelect.innerHTML += option;
        });
    } catch (error) {
        console.error('加载棋手列表失败:', error);
    }
}

let isSubmitting = false;

document.getElementById('game-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (isSubmitting) {
        alert('操作进行中，请稍候...');
        return;
    }
    
    const fileInput = document.getElementById('game-file');
    const pgnContent = document.getElementById('game-pgn').value;
    const filename = document.getElementById('game-filename').value;
    const whitePlayerId = document.getElementById('white-player-select').value;
    const blackPlayerId = document.getElementById('black-player-select').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!fileInput.files[0] && !pgnContent.trim()) {
        alert('请选择PGN文件或粘贴PGN内容');
        return;
    }
    
    if (!filename.trim()) {
        alert('请输入文件名');
        return;
    }
    
    try {
        const existingGames = await apiCall('/api/library/games');
        const exists = existingGames.games.some(game => game.filename === filename);
        if (exists) {
            alert(`文件名 "${filename}" 已存在，请使用其他文件名`);
            return;
        }
        
        isSubmitting = true;
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';
        
        if (fileInput.files[0]) {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('white_player_id', whitePlayerId);
            formData.append('black_player_id', blackPlayerId);
            
            const response = await fetch('/api/import/pgn', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error);
            }
        } else {
            await apiCall('/api/library/game', {
                method: 'POST',
                body: { 
                    pgn_content: pgnContent, 
                    filename: filename,
                    white_player_id: whitePlayerId,
                    black_player_id: blackPlayerId
                }
            });
        }
        
        closeGameModal();
        loadLibraryPage();
        alert('棋局添加成功!');
    } catch (error) {
        alert('添加失败: ' + error.message);
    } finally {
        isSubmitting = false;
        submitBtn.disabled = false;
        submitBtn.textContent = '保存';
    }
});

async function deleteGame(gameId, filename) {
    if (!confirm(`确定要删除棋局 "${filename}" 吗？`)) return;
    
    try {
        await apiCall(`/api/library/game/${gameId}`, { method: 'DELETE' });
        loadLibraryPage();
        alert('删除成功!');
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

async function addDemoGame() {
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
        loadLibraryPage();
        alert('演示棋局添加成功!');
    } catch (error) {
        alert('添加失败: ' + error.message);
    }
}