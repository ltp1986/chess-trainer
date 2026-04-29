const axios = require('axios');

describe('Analyzer Unit Tests', () => {
    const BASE_URL = 'http://localhost:5000';

    beforeAll(async () => {
        try {
            await axios.get(`${BASE_URL}/`, { timeout: 5000 });
        } catch {
            console.warn('❌ 服务器未运行，跳过单元测试');
            process.exit(0);
        }
    });

    describe('分析算法验证', () => {
        test('应该正确识别败方的失误', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            const mistakes = response.data.mistakes;
            
            if (mistakes.length > 0) {
                const firstMistake = mistakes[0];
                const step = firstMistake.step;
                const isWhiteTurn = step % 2 === 1;
                
                if (response.data.result === '0-1') {
                    expect(isWhiteTurn).toBe(true);
                } else if (response.data.result === '1-0') {
                    expect(isWhiteTurn).toBe(false);
                }
            }
        });

        test('失误应该按步骤排序', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            const mistakes = response.data.mistakes;
            
            for (let i = 1; i < mistakes.length; i++) {
                expect(mistakes[i].step).toBeGreaterThan(mistakes[i - 1].step);
            }
        });

        test('失误损失应该大于等于难度阈值', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn?difficulty=medium`);
            const mistakes = response.data.mistakes;
            const minLoss = 150;
            
            for (const mistake of mistakes) {
                expect(mistake.loss).toBeGreaterThanOrEqual(minLoss);
            }
        });
    });

    describe('数据格式验证', () => {
        test('loss应该为正数', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            
            for (const mistake of response.data.mistakes) {
                expect(mistake.loss).toBeGreaterThan(0);
            }
            
            for (const exercise of response.data.exercises) {
                expect(exercise.loss).toBeGreaterThan(0);
            }
        });

        test('best_move应该是有效的UCI格式', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            
            const uciPattern = /^[a-h][1-8][a-h][1-8][qrbn]?$/;
            
            for (const mistake of response.data.mistakes) {
                if (mistake.best_move) {
                    expect(mistake.best_move).toMatch(uciPattern);
                }
            }
            
            for (const exercise of response.data.exercises) {
                if (exercise.best_move) {
                    expect(exercise.best_move).toMatch(uciPattern);
                }
            }
        });

        test('actual_move应该是有效的UCI格式', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            const uciPattern = /^[a-h][1-8][a-h][1-8][qrbn]?$/;
            
            for (const mistake of response.data.mistakes) {
                expect(mistake.actual_move).toMatch(uciPattern);
            }
        });

        test('cause和idea应该不为空', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            
            for (const mistake of response.data.mistakes) {
                expect(mistake.cause).toBeTruthy();
                expect(mistake.idea).toBeTruthy();
            }
        });
    });

    describe('边界条件测试', () => {
        test('空文件应该返回错误', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/empty.pgn`).catch(e => e.response);
            
            expect(response.status).toBe(404);
        });

        test('不存在的文件应该返回404', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/nonexistent_file.pgn`).catch(e => e.response);
            
            expect(response.status).toBe(404);
        });

        test('难度参数应该默认medium', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            
            expect(response.data.difficulty).toBe('medium');
        });

        test('无效难度参数应该默认为medium', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn?difficulty=invalid`);
            
            expect(response.data.difficulty).toBe('medium');
        });
    });

    describe('性能指标', () => {
        test('分析时间应该在合理范围内', async () => {
            const startTime = Date.now();
            await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            const endTime = Date.now();
            const duration = endTime - startTime;
            
            console.log(`⏱️ 分析耗时: ${duration}ms`);
            expect(duration).toBeLessThan(30000);
        });

        test('应该返回正确的棋手信息', async () => {
            const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
            
            expect(response.data.white).toBeTruthy();
            expect(response.data.black).toBeTruthy();
            expect(response.data.result).toBeTruthy();
        });
    });
});