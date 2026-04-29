async function loadPlayersPage() {
    const container = document.getElementById('players-content');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const data = await apiCall('/api/players');
        if (data.players && data.players.length > 0) {
            let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
            data.players.forEach(player => {
                const gameCount = player.total_games || 0;
                const canGenerateProfile = gameCount > 0;
                html += `
                    <div class="player-card bg-white rounded-xl shadow-md p-4">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="font-semibold text-gray-800">${player.name}</h3>
                                <p class="text-sm text-gray-600">等级: ${player.level}</p>
                                <p class="text-sm text-gray-500">评级: ${player.rating || '-'}</p>
                                <p class="text-sm text-gray-500">关联棋局: ${gameCount} 局</p>
                            </div>
                            <div class="flex gap-2">
                                <button onclick="openEditModal('${player.player_id}', '${player.name}', '${player.level}', '${player.rating || ''}')" class="px-3 py-1 bg-yellow-500 text-white rounded-lg text-sm">编辑</button>
                                <button onclick="deletePlayer('${player.player_id}')" class="px-3 py-1 bg-red-500 text-white rounded-lg text-sm">删除</button>
                            </div>
                        </div>
                        <div class="mt-3 pt-3 border-t border-gray-100">
                            ${canGenerateProfile ? `
                                <button onclick="generateProfileForPlayer('${player.player_id}', '${player.name}')" class="w-full px-3 py-2 bg-green-500 text-white rounded-lg text-sm">
                                    📊 生成能力画像
                                </button>
                            ` : `
                                <button class="w-full px-3 py-2 bg-gray-200 text-gray-500 rounded-lg text-sm cursor-not-allowed" disabled>
                                    📊 生成能力画像 (需关联棋局)
                                </button>
                            `}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">暂无棋手数据</p><button onclick="showAddPlayerModal()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">添加棋手</button></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="text-center py-10 text-red-500">加载失败</div>';
    }
}

async function generateProfileForPlayer(playerId, playerName) {
    try {
        await apiCall('/api/profile/generate', { 
            method: 'POST', 
            body: { player_id: playerId } 
        });
        alert(`${playerName} 的能力画像生成成功!`);
        document.getElementById('nav-profile').click();
    } catch (error) {
        alert('生成失败: ' + error.message);
    }
}

function showAddPlayerModal() {
    document.getElementById('modal-title').textContent = '添加棋手';
    document.getElementById('player-id').value = '';
    document.getElementById('player-name').value = '';
    document.getElementById('player-level').value = 'L3';
    document.getElementById('player-rating').value = '';
    document.getElementById('player-modal').classList.remove('hidden');
}

function openEditModal(playerId, name, level, rating) {
    document.getElementById('modal-title').textContent = '编辑棋手';
    document.getElementById('player-id').value = playerId;
    document.getElementById('player-name').value = name;
    document.getElementById('player-level').value = level;
    document.getElementById('player-rating').value = rating;
    document.getElementById('player-modal').classList.remove('hidden');
}

function closePlayerModal() {
    document.getElementById('player-modal').classList.add('hidden');
}

document.getElementById('player-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const playerId = document.getElementById('player-id').value;
    const data = {
        name: document.getElementById('player-name').value,
        level: document.getElementById('player-level').value,
        rating: parseInt(document.getElementById('player-rating').value) || 0
    };
    
    try {
        if (playerId) {
            await apiCall(`/api/player/${playerId}`, { method: 'PUT', body: data });
        } else {
            await apiCall('/api/player', { method: 'POST', body: data });
        }
        closePlayerModal();
        loadPlayersPage();
        alert('操作成功!');
    } catch (error) {
        alert('操作失败: ' + error.message);
    }
});

async function deletePlayer(playerId) {
    if (!confirm('确定要删除吗?')) return;
    try {
        await apiCall(`/api/player/${playerId}`, { method: 'DELETE' });
        loadPlayersPage();
        alert('删除成功!');
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}