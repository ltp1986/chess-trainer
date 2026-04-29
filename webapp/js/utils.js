function showLoading(container) {
    if (!container) return;
    container.innerHTML = `
        <div class="text-center py-10">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p class="mt-2 text-gray-500">加载中...</p>
        </div>
    `;
}

async function loadPgnFiles() {
    try {
        const response = await apiCall('/api/pgn_files');
        const select = document.getElementById('pgn-select');
        const pathInput = document.getElementById('pgn-path-input');
        
        if (pathInput && response.watch_dir) {
            pathInput.value = response.watch_dir;
        }
        
        if (select) {
            select.innerHTML = '<option value="">-- 请选择PGN文件 --</option>';
            response.files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载PGN文件列表失败:', error);
    }
}

async function getWatchDir() {
    try {
        const response = await apiCall('/api/config/watch_dir');
        const pathInput = document.getElementById('pgn-path-input');
        if (pathInput) {
            pathInput.value = response.watch_dir;
        }
        return response.watch_dir;
    } catch (error) {
        console.error('获取PGN目录失败:', error);
        return '';
    }
}

async function setWatchDir(newDir) {
    try {
        const response = await apiCall('/api/config/watch_dir', {
            method: 'POST',
            body: { watch_dir: newDir }
        });
        
        if (response.success) {
            const pathInput = document.getElementById('pgn-path-input');
            if (pathInput) {
                pathInput.value = response.watch_dir;
            }
            await loadPgnFiles();
            alert('PGN目录设置成功！');
        } else {
            alert('设置失败: ' + response.message);
        }
    } catch (error) {
        console.error('设置PGN目录失败:', error);
        alert('设置失败: ' + error.message);
    }
}