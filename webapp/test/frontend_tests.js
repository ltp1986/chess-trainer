/**
 * 前端自动化测试套件
 * 运行方式：在浏览器控制台中执行，或使用Node.js运行
 */

const FrontendTests = {
    testValidation: function() {
        console.log('===== 开始验证功能测试 =====');
        
        let passed = 0;
        let total = 0;
        
        // 测试PGN验证
        total++;
        const pgnResult = Validator.validatePGN('[Event "Test"]\n1. e4 e5');
        if (pgnResult.valid) {
            console.log('✅ PGN验证 - 有效PGN');
            passed++;
        } else {
            console.log('❌ PGN验证 - 有效PGN');
        }
        
        total++;
        const emptyPgnResult = Validator.validatePGN('');
        if (!emptyPgnResult.valid && emptyPgnResult.errors.length > 0) {
            console.log('✅ PGN验证 - 空PGN');
            passed++;
        } else {
            console.log('❌ PGN验证 - 空PGN');
        }
        
        total++;
        const invalidPgnResult = Validator.validatePGN('not a pgn');
        if (!invalidPgnResult.valid) {
            console.log('✅ PGN验证 - 无效PGN');
            passed++;
        } else {
            console.log('❌ PGN验证 - 无效PGN');
        }
        
        // 测试姓名验证
        total++;
        const nameResult = Validator.validatePlayerName('张三');
        if (nameResult.valid) {
            console.log('✅ 姓名验证 - 有效姓名');
            passed++;
        } else {
            console.log('❌ 姓名验证 - 有效姓名');
        }
        
        total++;
        const shortNameResult = Validator.validatePlayerName('张');
        if (!shortNameResult.valid) {
            console.log('✅ 姓名验证 - 短姓名');
            passed++;
        } else {
            console.log('❌ 姓名验证 - 短姓名');
        }
        
        total++;
        const invalidNameResult = Validator.validatePlayerName('张@三');
        if (!invalidNameResult.valid) {
            console.log('✅ 姓名验证 - 无效字符');
            passed++;
        } else {
            console.log('❌ 姓名验证 - 无效字符');
        }
        
        // 测试邮箱验证
        total++;
        const emailResult = Validator.validateEmail('test@example.com');
        if (emailResult.valid) {
            console.log('✅ 邮箱验证 - 有效邮箱');
            passed++;
        } else {
            console.log('❌ 邮箱验证 - 有效邮箱');
        }
        
        total++;
        const invalidEmailResult = Validator.validateEmail('invalid-email');
        if (!invalidEmailResult.valid) {
            console.log('✅ 邮箱验证 - 无效邮箱');
            passed++;
        } else {
            console.log('❌ 邮箱验证 - 无效邮箱');
        }
        
        // 测试评级验证
        total++;
        const ratingResult = Validator.validateRating('1800');
        if (ratingResult.valid) {
            console.log('✅ 评级验证 - 有效评级');
            passed++;
        } else {
            console.log('❌ 评级验证 - 有效评级');
        }
        
        total++;
        const highRatingResult = Validator.validateRating('3500');
        if (!highRatingResult.valid) {
            console.log('✅ 评级验证 - 超出范围');
            passed++;
        } else {
            console.log('❌ 评级验证 - 超出范围');
        }
        
        // 测试等级验证
        total++;
        const levelResult = Validator.validateLevel('L3');
        if (levelResult.valid) {
            console.log('✅ 等级验证 - 有效等级');
            passed++;
        } else {
            console.log('❌ 等级验证 - 有效等级');
        }
        
        total++;
        const invalidLevelResult = Validator.validateLevel('L5');
        if (!invalidLevelResult.valid) {
            console.log('✅ 等级验证 - 无效等级');
            passed++;
        } else {
            console.log('❌ 等级验证 - 无效等级');
        }
        
        // 测试FEN验证
        total++;
        const fenResult = Validator.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
        if (fenResult.valid) {
            console.log('✅ FEN验证 - 有效FEN');
            passed++;
        } else {
            console.log('❌ FEN验证 - 有效FEN');
        }
        
        total++;
        const invalidFenResult = Validator.validateFEN('invalid fen');
        if (!invalidFenResult.valid) {
            console.log('✅ FEN验证 - 无效FEN');
            passed++;
        } else {
            console.log('❌ FEN验证 - 无效FEN');
        }
        
        // 测试表单验证
        total++;
        const formResult = Validator.validateForm({
            name: '张三',
            email: 'zhangsan@example.com',
            rating: '1800',
            level: 'L3'
        });
        if (formResult.valid) {
            console.log('✅ 表单验证 - 有效表单');
            passed++;
        } else {
            console.log('❌ 表单验证 - 有效表单');
        }
        
        total++;
        const invalidFormResult = Validator.validateForm({
            name: '张',
            email: 'invalid',
            rating: 'abc'
        });
        if (!invalidFormResult.valid && Object.keys(invalidFormResult.errors).length > 0) {
            console.log('✅ 表单验证 - 无效表单');
            passed++;
        } else {
            console.log('❌ 表单验证 - 无效表单');
        }
        
        console.log(`\n===== 验证功能测试完成 =====`);
        console.log(`通过: ${passed}/${total}`);
        
        return { passed, total };
    },
    
    testBoardRendering: function() {
        console.log('\n===== 开始棋盘渲染测试 =====');
        
        let passed = 0;
        let total = 0;
        
        // 测试棋盘初始化
        total++;
        const boardContainer = document.getElementById('chess-board');
        if (boardContainer) {
            console.log('✅ 棋盘容器存在');
            passed++;
        } else {
            console.log('❌ 棋盘容器不存在');
        }
        
        // 测试方块数量
        total++;
        const squares = document.querySelectorAll('.square');
        if (squares.length === 64) {
            console.log('✅ 棋盘方块数量正确 (64个)');
            passed++;
        } else {
            console.log(`❌ 棋盘方块数量错误 (实际: ${squares.length})`);
        }
        
        // 测试棋盘颜色交替
        total++;
        const lightSquares = document.querySelectorAll('.square.light');
        const darkSquares = document.querySelectorAll('.square.dark');
        if (lightSquares.length === 32 && darkSquares.length === 32) {
            console.log('✅ 棋盘颜色交替正确');
            passed++;
        } else {
            console.log(`❌ 棋盘颜色错误 (亮: ${lightSquares.length}, 暗: ${darkSquares.length})`);
        }
        
        console.log('\n===== 棋盘渲染测试完成 =====');
        console.log(`通过: ${passed}/${total}`);
        
        return { passed, total };
    },
    
    testGameLogic: function() {
        console.log('\n===== 开始游戏逻辑测试 =====');
        
        let passed = 0;
        let total = 0;
        
        // 测试FEN解析
        total++;
        const testFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        const fenResult = Validator.validateFEN(testFEN);
        if (fenResult.valid) {
            console.log('✅ FEN解析 - 起始位置');
            passed++;
        } else {
            console.log('❌ FEN解析 - 起始位置');
        }
        
        // 测试走法格式验证
        total++;
        const validMoves = ['e2e4', 'e7e5', 'Nf3', 'Nc6'];
        if (Validator.validateMove('e2e4', validMoves)) {
            console.log('✅ 走法验证 - 有效走法');
            passed++;
        } else {
            console.log('❌ 走法验证 - 有效走法');
        }
        
        total++;
        if (!Validator.validateMove('invalid', validMoves)) {
            console.log('✅ 走法验证 - 无效走法');
            passed++;
        } else {
            console.log('❌ 走法验证 - 无效走法');
        }
        
        console.log('\n===== 游戏逻辑测试完成 =====');
        console.log(`通过: ${passed}/${total}`);
        
        return { passed, total };
    },
    
    testUIElements: function() {
        console.log('\n===== 开始UI元素测试 =====');
        
        let passed = 0;
        let total = 0;
        
        // 测试标签页按钮
        const tabs = ['report-tab', 'exercise-tab'];
        tabs.forEach(tabId => {
            total++;
            const tab = document.getElementById(tabId);
            if (tab) {
                console.log(`✅ UI元素 - ${tabId} 存在`);
                passed++;
            } else {
                console.log(`❌ UI元素 - ${tabId} 不存在`);
            }
        });
        
        // 测试控制按钮
        const buttons = ['play-demo-btn', 'pause-demo-btn', 'prev-demo-btn', 'next-demo-btn'];
        buttons.forEach(btnId => {
            total++;
            const btn = document.getElementById(btnId);
            if (btn) {
                console.log(`✅ UI元素 - ${btnId} 存在`);
                passed++;
            } else {
                console.log(`❌ UI元素 - ${btnId} 不存在`);
            }
        });
        
        // 测试信息显示区域
        const infoElements = ['white-player', 'black-player', 'game-result', 'report-progress-bar'];
        infoElements.forEach(elId => {
            total++;
            const el = document.getElementById(elId);
            if (el) {
                console.log(`✅ UI元素 - ${elId} 存在`);
                passed++;
            } else {
                console.log(`❌ UI元素 - ${elId} 不存在`);
            }
        });
        
        console.log('\n===== UI元素测试完成 =====');
        console.log(`通过: ${passed}/${total}`);
        
        return { passed, total };
    },
    
    testAPIIntegration: async function() {
        console.log('\n===== 开始API集成测试 =====');
        
        let passed = 0;
        let total = 0;
        
        try {
            // 测试获取棋局列表
            total++;
            const gamesResponse = await fetch('/api/library/games');
            if (gamesResponse.ok) {
                const data = await gamesResponse.json();
                if (data && Array.isArray(data.games)) {
                    console.log('✅ API测试 - 获取棋局列表');
                    passed++;
                }
            } else {
                console.log('❌ API测试 - 获取棋局列表');
            }
            
            // 测试获取棋手列表
            total++;
            const playersResponse = await fetch('/api/players');
            if (playersResponse.ok) {
                const data = await playersResponse.json();
                if (data && Array.isArray(data.players)) {
                    console.log('✅ API测试 - 获取棋手列表');
                    passed++;
                }
            } else {
                console.log('❌ API测试 - 获取棋手列表');
            }
            
            // 测试获取画像
            total++;
            const profileResponse = await fetch('/api/profile');
            if (profileResponse.ok || profileResponse.status === 404) {
                console.log('✅ API测试 - 获取画像');
                passed++;
            } else {
                console.log('❌ API测试 - 获取画像');
            }
            
            // 测试获取训练计划
            total++;
            const planResponse = await fetch('/api/training/plan');
            if (planResponse.ok || planResponse.status === 404) {
                console.log('✅ API测试 - 获取训练计划');
                passed++;
            } else {
                console.log('❌ API测试 - 获取训练计划');
            }
            
        } catch (error) {
            console.log(`⚠️ API测试网络错误: ${error.message}`);
        }
        
        console.log('\n===== API集成测试完成 =====');
        console.log(`通过: ${passed}/${total}`);
        
        return { passed, total };
    },
    
    runAllTests: async function() {
        console.log('='.repeat(60));
        console.log('国际象棋学习训练系统 - 前端自动化测试');
        console.log('='.repeat(60));
        
        const results = [];
        
        results.push(this.testValidation());
        results.push(this.testBoardRendering());
        results.push(this.testGameLogic());
        results.push(this.testUIElements());
        results.push(await this.testAPIIntegration());
        
        console.log('\n' + '='.repeat(60));
        console.log('测试结果汇总');
        console.log('='.repeat(60));
        
        const totalPassed = results.reduce((sum, r) => sum + r.passed, 0);
        const totalTests = results.reduce((sum, r) => sum + r.total, 0);
        
        console.log(`总测试数: ${totalTests}`);
        console.log(`通过数: ${totalPassed}`);
        console.log(`通过率: ${((totalPassed / totalTests) * 100).toFixed(1)}%`);
        
        if (totalPassed === totalTests) {
            console.log('\n🎉 所有测试通过！');
        } else {
            console.log(`\n⚠️ ${totalTests - totalPassed} 个测试失败`);
        }
        
        return { totalPassed, totalTests };
    }
};

// 如果在浏览器环境中，添加全局函数
if (typeof window !== 'undefined') {
    window.runFrontendTests = function() {
        FrontendTests.runAllTests();
    };
    
    // 添加页面加载完成后的自动测试
    document.addEventListener('DOMContentLoaded', function() {
        console.log('页面加载完成，准备运行前端测试...');
        // 延迟1秒运行测试，确保所有组件加载完成
        setTimeout(() => {
            FrontendTests.runAllTests();
        }, 1000);
    });
}

// 如果在Node.js环境中，导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FrontendTests;
}