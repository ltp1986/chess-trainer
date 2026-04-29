async function loadPlanPage() {
    const container = document.getElementById('plan-content');
    if (!container) return;
    
    showLoading(container);
    
    loadTrainingProgress();
    loadTokenStatus();
    
    try {
        const data = await apiCall('/api/training/plan');
        if (data && data.daily_tasks) {
            const completedDaily = data.daily_tasks.filter(t => t.completed).length;
            const completedWeekly = data.weekly_tasks ? data.weekly_tasks.filter(t => t.completed).length : 0;
            const totalDaily = data.daily_tasks.length;
            const totalWeekly = data.weekly_tasks ? data.weekly_tasks.length : 0;
            const progress = data.progress || Math.round(((completedDaily + completedWeekly) / (totalDaily + totalWeekly)) * 100);
            
            let html = `
                <div class="mb-6">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-semibold">📊 训练进度</span>
                        <span>${progress}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="bg-blue-500 h-3 rounded-full" style="width: ${progress}%"></div>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div class="bg-blue-50 rounded-lg p-4">
                        <h3 class="font-semibold mb-2">📅 短期目标</h3>
                        <p class="text-sm">${data.short_term_goal || '提升棋力'}</p>
                    </div>
                    <div class="bg-green-50 rounded-lg p-4">
                        <h3 class="font-semibold mb-2">🎯 长期目标</h3>
                        <p class="text-sm">${data.long_term_goal || '成为优秀棋手'}</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="bg-gray-50 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-blue-600">${data.target_level || 'L3'}</div>
                        <div class="text-sm text-gray-600">目标等级</div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-green-600">${data.target_rating || 1800}</div>
                        <div class="text-sm text-gray-600">目标等级分</div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-4 text-center">
                        <div class="text-2xl font-bold text-purple-600">${data.estimated_time || '3个月'}</div>
                        <div class="text-sm text-gray-600">预计时间</div>
                    </div>
                </div>
                
                ${data.focus_areas && data.focus_areas.length > 0 ? `
                    <div class="mb-6">
                        <h3 class="font-semibold mb-2">🎯 重点关注领域</h3>
                        <div class="flex flex-wrap gap-2">
                            ${data.focus_areas.map(area => `<span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">${area}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="mb-6">
                    <div class="flex justify-between items-center mb-3">
                        <h3 class="font-semibold">📝 每日任务</h3>
                        <span class="text-sm text-gray-500">${completedDaily}/${totalDaily} 完成</span>
                    </div>
                    <div class="space-y-2">
                        ${data.daily_tasks.map((task, index) => `
                            <div class="flex items-center gap-3 p-3 border rounded-lg ${task.completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}">
                                <button onclick="toggleTask('daily', ${index})" class="w-6 h-6 rounded-full border-2 flex items-center justify-center ${task.completed ? 'bg-green-500 border-green-500' : 'border-gray-300'}">
                                    ${task.completed ? '✓' : ''}
                                </button>
                                <div class="flex-1">
                                    <div class="font-medium">${task.name}</div>
                                    <div class="text-sm text-gray-500">${task.duration} · ${task.frequency}</div>
                                    ${task.description ? `<div class="text-xs text-gray-400 mt-1">${task.description}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${data.weekly_tasks && data.weekly_tasks.length > 0 ? `
                    <div class="mb-6">
                        <div class="flex justify-between items-center mb-3">
                            <h3 class="font-semibold">📆 每周任务</h3>
                            <span class="text-sm text-gray-500">${completedWeekly}/${totalWeekly} 完成</span>
                        </div>
                        <div class="space-y-2">
                            ${data.weekly_tasks.map((task, index) => `
                                <div class="flex items-center gap-3 p-3 border rounded-lg ${task.completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}">
                                    <button onclick="toggleTask('weekly', ${index})" class="w-6 h-6 rounded-full border-2 flex items-center justify-center ${task.completed ? 'bg-green-500 border-green-500' : 'border-gray-300'}">
                                        ${task.completed ? '✓' : ''}
                                    </button>
                                    <div class="flex-1">
                                        <div class="font-medium">${task.name}</div>
                                        <div class="text-sm text-gray-500">${task.duration} · ${task.frequency}</div>
                                        ${task.description ? `<div class="text-xs text-gray-400 mt-1">${task.description}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div>
                    <h3 class="font-semibold mb-3">📚 推荐学习资源</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${data.recommendations.map(rec => `
                            <div class="p-3 bg-gray-50 rounded-lg">
                                <div class="font-medium">${rec.resource}</div>
                                <div class="flex items-center gap-2 mt-1">
                                    <span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">${rec.type}</span>
                                    ${rec.priority ? `<span class="text-xs px-2 py-0.5 ${rec.priority === 'high' ? 'bg-red-100 text-red-700' : rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'} rounded">${rec.priority === 'high' ? '高优先级' : rec.priority === 'medium' ? '中优先级' : '低优先级'}</span>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="mt-6 flex justify-end">
                    <button onclick="generatePlan()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                        🔄 重新生成计划
                    </button>
                </div>
            `;
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">暂无训练计划</p><button onclick="generatePlan()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">生成计划</button></div>';
        }
    } catch (error) {
        if (error.message.includes('404') || error.message.includes('计划不存在')) {
            container.innerHTML = '<div class="text-center py-10"><p class="text-gray-500">暂无训练计划</p><button onclick="generatePlan()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">生成计划</button></div>';
        } else {
            container.innerHTML = '<div class="text-center py-10 text-red-500">加载失败: ' + error.message + '</div>';
        }
    }
}

async function generatePlan() {
    try {
        await apiCall('/api/training/plan/generate', {}, 'POST');
        loadPlanPage();
        alert('训练计划生成成功!');
    } catch (error) {
        alert('生成失败: ' + error.message);
    }
}

async function toggleTask(type, index) {
    alert(`标记${type === 'daily' ? '每日' : '每周'}任务 #${index + 1} 完成\n\n在实际应用中，这里会更新任务完成状态并保存进度。`);
    loadPlanPage();
}

async function loadTrainingProgress() {
    const container = document.getElementById('progress-summary');
    if (!container) return;
    
    try {
        const data = await apiCall('/api/training/progress');
        
        let html = `
            <div class="space-y-4">
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-600">总进度</span>
                    <span class="font-semibold">${data.overall_progress}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-500 h-2 rounded-full" style="width: ${data.overall_progress}%"></div>
                </div>
                
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-blue-50 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-blue-600">🔥 ${data.daily_progress?.streak || 0}</div>
                        <div class="text-xs text-gray-500">连续打卡</div>
                    </div>
                    <div class="bg-green-50 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-green-600">${data.daily_progress?.completion_rate || 0}%</div>
                        <div class="text-xs text-gray-500">完成率</div>
                    </div>
                </div>
                
                ${data.skill_progress ? `
                    <div>
                        <div class="text-sm font-medium mb-2">技能进度</div>
                        <div class="space-y-2">
                            ${Object.entries(data.skill_progress).map(([skill, info]) => {
                                const skillNames = {
                                    'tactical_calculation': '战术计算',
                                    'opening_preparation': '开局准备',
                                    'endgame_skills': '残局技巧'
                                };
                                return `
                                    <div>
                                        <div class="flex justify-between text-sm">
                                            <span>${skillNames[skill] || skill}</span>
                                            <span>${info.current} → ${info.target}</span>
                                        </div>
                                        <div class="w-full bg-gray-200 rounded-full h-1.5">
                                            <div class="bg-purple-500 h-1.5 rounded-full" style="width: ${(info.current / info.target) * 100}%"></div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="text-center py-4 text-gray-500 text-sm">加载失败</div>';
    }
}

async function loadTokenStatus() {
    const container = document.getElementById('token-status-content');
    if (!container) return;
    
    try {
        const data = await apiCall('/api/token/status');
        
        const statusColors = {
            'normal': 'bg-green-100 text-green-700',
            'notice': 'bg-blue-100 text-blue-700',
            'warning': 'bg-yellow-100 text-yellow-700',
            'critical': 'bg-red-100 text-red-700',
            'circuit_breaker': 'bg-gray-100 text-gray-700'
        };
        
        const statusIcons = {
            'normal': '✅',
            'notice': '💡',
            'warning': '⚠️',
            'critical': '🚨',
            'circuit_breaker': '🔌'
        };
        
        const statusText = {
            'normal': '正常',
            'notice': '注意',
            'warning': '警告',
            'critical': '临界',
            'circuit_breaker': '熔断中'
        };
        
        let html = `
            <div class="space-y-3">
                <div class="flex items-center justify-between">
                    <span>状态</span>
                    <span class="px-2 py-1 rounded-full text-sm ${statusColors[data.status] || statusColors['normal']}">
                        ${statusIcons[data.status] || statusIcons['normal']} ${statusText[data.status] || statusText['normal']}
                    </span>
                </div>
                
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span>今日使用</span>
                        <span>${data.daily_usage || 0} / ${data.daily_limit || 100000}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="${data.status === 'critical' ? 'bg-red-500' : data.status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'} h-2 rounded-full" style="width: ${data.daily_rate || 0}%"></div>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="bg-gray-50 rounded-lg p-2 text-center">
                        <div class="text-xs text-gray-500">本月使用</div>
                        <div>${((data.monthly_rate || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-2 text-center">
                        <div class="text-xs text-gray-500">当前RPM</div>
                        <div>${data.current_rpm || 0}/${data.rpm_limit || 60}</div>
                    </div>
                </div>
                
                ${data.circuit_breaker_active ? `
                    <div class="bg-red-50 border border-red-200 rounded-lg p-2 text-center text-sm text-red-600">
                        🔌 熔断保护已激活<br>
                        <span class="text-xs">预计恢复时间: ${data.circuit_breaker_resets_at ? new Date(data.circuit_breaker_resets_at).toLocaleString() : '未知'}</span>
                    </div>
                ` : ''}
            </div>
        `;
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="text-center py-4 text-gray-500 text-sm">加载失败</div>';
    }
}