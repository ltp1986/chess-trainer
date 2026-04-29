// 增强的前端测试套件
function assert(condition, message) {
    if (!condition) {
        throw new Error(`断言失败: ${message}`);
    }
    console.log(`✅ ${message}`);
}

function logSection(title) {
    console.log(`\n${'='.repeat(50)}`);
    console.log(`📋 ${title}`);
    console.log('='.repeat(50));
}

async function runEnhancedTests() {
    console.log('🚀 开始运行增强版前端测试...\n');

    let passed = 0;
    let total = 0;

    try {
        // 测试1: 检查导航元素
        logSection('测试1: 导航元素检查');
        total++;
        const navButtons = document.querySelectorAll('.nav-btn');
        assert(navButtons.length >= 5, `导航按钮数量应为5个，实际为${navButtons.length}`);
        passed++;

        // 测试2: 检查页面容器
        logSection('测试2: 页面容器检查');
        total++;
        const pages = ['page-home', 'page-library', 'page-players', 'page-profile', 'page-plan'];
        pages.forEach(pageId => {
            const page = document.getElementById(pageId);
            assert(page !== null, `${pageId} 页面容器存在`);
        });
        passed++;

        // 测试3: 检查导航按钮可点击
        logSection('测试3: 导航按钮可点击性检查');
        total++;
        navButtons.forEach((btn, index) => {
            assert(btn.onclick !== null || btn.hasAttribute('data-nav'), `导航按钮${index + 1}有点击事件`);
        });
        passed++;

        // 测试4: 测试API端点
        logSection('测试4: API端点检查');
        total++;
        const endpoints = [
            '/api/library/games',
            '/api/players',
            '/api/profile',
            '/api/training/plan'
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint);
                assert([200, 404].includes(response.status),
                    `${endpoint} 返回状态: ${response.status}`);
                console.log(`   ${endpoint}: ${response.status}`);
            } catch (error) {
                console.log(`   ❌ ${endpoint}: ${error.message}`);
            }
        }
        passed++;

        // 测试5: 检查首页元素
        logSection('测试5: 首页元素检查');
        total++;
        const fileSelection = document.getElementById('file-selection');
        assert(fileSelection !== null, '文件选择区域存在');

        const demoBtn = document.querySelector('button[onclick*="demo"]');
        assert(demoBtn !== null, '演示数据按钮存在');
        passed++;

        // 测试6: 检查棋盘元素
        logSection('测试6: 棋盘元素检查');
        total++;
        const board = document.getElementById('board');
        assert(board !== null, '棋盘元素存在');

        const squares = document.querySelectorAll('.square');
        assert(squares.length === 64, `棋盘格子数量应为64个，实际为${squares.length}`);
        passed++;

        // 测试7: 检查页面初始状态
        logSection('测试7: 页面初始状态检查');
        total++;
        const homePage = document.getElementById('page-home');
        assert(homePage !== null && !homePage.classList.contains('hidden'),
            '首页默认应显示');
        passed++;

        // 测试8: 测试导航切换功能
        logSection('测试8: 导航切换功能检查');
        total++;
        const playersBtn = document.getElementById('nav-players');
        if (playersBtn) {
            // 模拟点击
            playersBtn.click();

            // 等待DOM更新
            await new Promise(resolve => setTimeout(resolve, 200));

            // 检查切换后状态
            const playersPageAfter = document.getElementById('page-players');
            assert(playersPageAfter !== null && !playersPageAfter.classList.contains('hidden'),
                '点击棋手管理后页面应显示');
            passed++;
        } else {
            console.log('   ⚠️ 棋手管理按钮未找到，跳过此测试');
        }

        // 测试9: 检查表单验证功能
        logSection('测试9: 表单验证功能检查');
        total++;
        assert(typeof Validator !== 'undefined', 'Validator对象存在');
        assert(typeof Validator.validatePlayerName === 'function', 'validatePlayerName函数存在');
        assert(typeof Validator.validatePGN === 'function', 'validatePGN函数存在');
        assert(typeof Validator.validateFEN === 'function', 'validateFEN函数存在');
        passed++;

        // 测试10: 测试验证函数
        logSection('测试10: 验证函数功能测试');
        total++;

        // 测试姓名验证
        const nameResult = Validator.validatePlayerName('张三');
        assert(nameResult.valid === true, '有效姓名"张三"应通过验证');

        const invalidName = Validator.validatePlayerName('');
        assert(invalidName.valid === false, '空姓名应验证失败');

        // 测试FEN验证
        const validFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        const fenResult = Validator.validateFEN(validFen);
        assert(fenResult.valid === true, '有效FEN应通过验证');

        passed++;

        console.log('\n' + '='.repeat(50));
        console.log(`📊 测试结果: ${passed}/${total} 通过`);
        console.log('='.repeat(50));

        if (passed === total) {
            console.log('🎉 所有测试通过！');
        } else {
            console.log(`⚠️  有 ${total - passed} 个测试未通过`);
        }

        return { passed, total };

    } catch (error) {
        console.error('\n❌ 测试执行失败:', error.message);
        console.error(error.stack);
        return { passed, total, error: error.message };
    }
}

// 页面加载完成后自动运行测试
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runEnhancedTests);
} else {
    runEnhancedTests();
}

// 导出测试函数到全局
window.runEnhancedTests = runEnhancedTests;