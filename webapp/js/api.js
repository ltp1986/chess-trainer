async function apiCall(url, body = {}, method = 'GET') {
    console.log(`📡 API调用: ${url}`);
    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (method !== 'GET' && Object.keys(body).length > 0) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${url}`);
        }
        
        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch {
            data = text;
        }
        
        console.log(`✅ API响应成功: ${url}`);
        return data;
    } catch (error) {
        console.error(`❌ API调用失败: ${url}`, error);
        throw error;
    }
}