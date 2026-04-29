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
                <button onclick="generateProfile(false)" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                    📊 生成画像
                </button>
                <button onclick="generateProfile(true)" class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition">
                    🤖 AI增强画像
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
            
            if (data.generated_by_ai) {
                html += `<div class="mb-4 p-3 bg-purple-50 rounded-lg flex items-center gap-2">
                    <span class="text-purple-600 font-medium">🤖 AI生成</span>
                    <span class="text-sm text-purple-500">由豆包AI分析生成</span>
                </div>`;
            }
            
            if (data.games_analyzed) {
                html += `<div class="mb-4 text-sm text-gray-500">分析棋局数: ${data.games_analyzed} 局</div>`;
            }
            
            html += `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                        <h3 class="font-semibold mb-2 text-green-800">🎯 强项</h3>
                        ${data.strengths.map(s => `
                            <div class="mb-3">
                                <div class="flex justify-between text-sm">
                                    <span class="text-green-700">${s.skill}</span>
                                    <span class="font-medium text-green-600">${s.score}%</span>
                                </div>
                                <div class="w-full bg-green-200 rounded-full h-2.5 mt-1">
                                    <div class="bg-green-500 h-2.5 rounded-full transition-all duration-500" style="width: ${s.score}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4">
                        <h3 class="font-semibold mb-2 text-red-800">⚠️ 弱项</h3>
                        ${data.weaknesses.map(w => `
                            <div class="mb-3">
                                <div class="flex justify-between text-sm">
                                    <span class="text-red-700">${w.skill}</span>
                                    <span class="font-medium text-red-600">${w.score}%</span>
                                </div>
                                <div class="w-full bg-red-200 rounded-full h-2.5 mt-1">
                                    <div class="bg-red-500 h-2.5 rounded-full transition-all duration-500" style="width: ${w.score}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                        <h3 class="font-semibold mb-2 text-blue-800">📊 能力细分</h3>
                        ${renderSkillBars(data)}
                    </div>
                </div>
                
                <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white border border-gray-200 rounded-xl p-4">
                        <h3 class="font-semibold mb-2">🎭 棋风类型</h3>
                        <div class="text-2xl font-bold text-blue-600">${data.style || '均衡型'}</div>
                        <div class="mt-2">
                            <span class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                                等级分: ${data.overall_rating || '未评估'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="bg-white border border-gray-200 rounded-xl p-4">
                        <h3 class="font-semibold mb-2">💡 改进建议</h3>
                        <ul class="space-y-2">
                            ${data.suggestions.map((s, i) => `<li class="flex items-start gap-2">
                                <span class="text-green-500">${i + 1}.</span>
                                <span class="text-gray-700">${s}</span>
                            </li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            if (data.detailed_analysis) {
                html += `
                    <div class="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6">
                        <h3 class="font-semibold mb-3 text-indigo-800">📝 AI深度分析报告</h3>
                        <p class="text-gray-700 leading-relaxed">${data.detailed_analysis}</p>
                    </div>
                `;
            }
            
            container.innerHTML = html;
            document.getElementById('profile-player-select').addEventListener('change', function(e) {
                currentPlayerId = e.target.value;
                loadProfilePage();
            });
        } else {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10"><p class="text-gray-500">暂无能力画像</p><button onclick="generateProfile(true)" class="mt-4 bg-purple-500 text-white px-4 py-2 rounded-lg">🤖 生成AI画像</button></div>';
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
                    <button onclick="generateProfile(false)" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                        📊 生成画像
                    </button>
                    <button onclick="generateProfile(true)" class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition">
                        🤖 AI增强画像
                    </button>
                </div>
            `;
        }
        if (error.message.includes('404') || error.message.includes('画像不存在')) {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10"><p class="text-gray-500">暂无能力画像</p><button onclick="generateProfile(true)" class="mt-4 bg-purple-500 text-white px-4 py-2 rounded-lg">🤖 生成AI画像</button></div>';
        } else {
            container.innerHTML = playerSelectHtml + '<div class="text-center py-10 text-red-500">加载失败: ' + error.message + '</div>';
        }
        document.getElementById('profile-player-select').addEventListener('change', function(e) {
            currentPlayerId = e.target.value;
            loadProfilePage();
        });
    }
}

function renderSkillBars(data) {
    const skills = [
        { key: 'opening_skill', label: '开局能力', color: 'green' },
        { key: 'midgame_skill', label: '中局能力', color: 'blue' },
        { key: 'endgame_skill', label: '残局能力', color: 'purple' },
        { key: 'tactical_vision', label: '战术眼光', color: 'orange' },
        { key: 'positional_understanding', label: '局面理解', color: 'cyan' }
    ];
    
    return skills.map(skill => {
        const value = data[skill.key] || 50;
        return `
            <div class="mb-2">
                <div class="flex justify-between text-xs">
                    <span class="text-blue-700">${skill.label}</span>
                    <span class="font-medium text-blue-600">${value}</span>
                </div>
                <div class="w-full bg-blue-200 rounded-full h-1.5 mt-0.5">
                    <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${value}%; background-color: var(--tw-color-${skill.color}-500)"></div>
                </div>
            </div>
        `;
    }).join('');
}

async function generateProfile(useAI) {
    const container = document.getElementById('profile-content');
    if (container) {
        showLoading(container);
    }
    
    try {
        const playerId = document.getElementById('profile-player-select')?.value || currentPlayerId;
        const playerName = document.querySelector('#profile-player-select option:checked')?.text || '未知棋手';
        
        let body = { player_id: playerId || '', player_name: playerName };
        let endpoint = '/api/profile/generate';
        
        if (useAI) {
            endpoint = '/api/profile/generate/enhanced';
        }
        
        const response = await apiCall(endpoint, { method: 'POST', body });
        
        if (response.generated_by_ai) {
            alert('🤖 AI能力画像生成成功!');
        } else {
            alert('📊 能力画像生成成功!');
        }
        
        loadProfilePage();
    } catch (error) {
        alert('生成失败: ' + error.message);
        loadProfilePage();
    }
}