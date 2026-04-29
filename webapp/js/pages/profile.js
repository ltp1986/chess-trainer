let currentPlayerId = null;

async function loadProfilePage() {
    const container = document.getElementById('profile-content');
    if (!container) return;
    
    showLoading(container);
    
    let playerSelectHtml = '';
    
    try {
        const playersData = await apiCall('/api/players');
        const players = playersData.players || [];
        
        playerSelectHtml = `
            <div class="mb-4 flex items-center gap-4">
                <select id="profile-player-select" class="px-4 py-2 border border-gray-300 rounded-lg">
                    <option value="">-- 选择棋手 (全部棋局) --</option>
        `;
        players.forEach(player => {
            playerSelectHtml += `<option value="${player.player_id}" ${currentPlayerId === player.player_id ? 'selected' : ''}>${player.name}</option>`;
        });
        playerSelectHtml += `
                </select>
                <button onclick="generateProfile()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                    📊 生成画像
                </button>
            </div>
        `;
        
        let url = '/api/profile';
        if (currentPlayerId) {
            url += `?player_id=${currentPlayerId}`;
        }
        
        const data = await apiCall(url);
        if (data && data.strengths) {
            let html = playerSelectHtml;
            if (data.player_name) {
                html += `<div class="mb-4 p-3 bg-blue-50 rounded-lg"><strong>棋手:</strong> ${data.player_name}</div>`;
            }
            html += `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="font-semibold mb-2">🎯 强项</h3>
                        ${data.strengths.map(s => `<div class="mb-2"><span>${s.skill}:</span><div class="w-full bg-gray-200 rounded-full h-2 mt-1"><div class="bg-green-500 h-2 rounded-full" style="width: ${s.score}%"></div></div></div>`).join('')}
                    </div>
                    <div>
                        <h3 class="font-semibold mb-2">⚠️ 弱项</h3>
                        ${data.weaknesses.map(w => `<div class="mb-2"><span>${w.skill}:</span><div class="w-full bg-gray-200 rounded-full h-2 mt-1"><div class="bg-red-500 h-2 rounded-full" style="width: ${w.score}%"></div></div></div>`).join('')}
                    </div>
                </div>
                <div class="mt-4">
                    <h3 class="font-semibold mb-2">🎭 棋风</h3>
                    <p>${data.style || '均衡型'}</p>
                </div>
                <div class="mt-4">
                    <h3 class="font-semibold mb-2">💡 改进建议</h3>
                    <ul>${data.suggestions.map(s => `<li class="mb-1">• ${s}</li>`).join('')}</ul>
                </div>
            `;
            container.innerHTML = html;
            document.getElementById('profile-player-select').addEventListener('change', function(e) {
                currentPlayerId = e.target.value;
                loadProfilePage();
            });
        } else {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10"><p class="text-gray-500">暂无能力画像</p><button onclick="generateProfile()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">生成画像</button></div>';
            document.getElementById('profile-player-select').addEventListener('change', function(e) {
                currentPlayerId = e.target.value;
                loadProfilePage();
            });
        }
    } catch (error) {
        if (!playerSelectHtml) {
            playerSelectHtml = `
                <div class="mb-4 flex items-center gap-4">
                    <select id="profile-player-select" class="px-4 py-2 border border-gray-300 rounded-lg">
                        <option value="">-- 选择棋手 (全部棋局) --</option>
                    </select>
                    <button onclick="generateProfile()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                        📊 生成画像
                    </button>
                </div>
            `;
        }
        if (error.message.includes('404') || error.message.includes('画像不存在')) {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10"><p class="text-gray-500">暂无能力画像</p><button onclick="generateProfile()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">生成画像</button></div>';
        } else {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10 text-red-500">加载失败: ' + error.message + '</div>';
        }
        document.getElementById('profile-player-select').addEventListener('change', function(e) {
            currentPlayerId = e.target.value;
            loadProfilePage();
        });
    }
}

async function generateProfile() {
    try {
        const playerId = document.getElementById('profile-player-select')?.value || currentPlayerId;
        const body = playerId ? { player_id: playerId } : {};
        await apiCall('/api/profile/generate', { method: 'POST', body });
        loadProfilePage();
        alert('画像生成成功!');
    } catch (error) {
        alert('生成失败: ' + error.message);
    }
}