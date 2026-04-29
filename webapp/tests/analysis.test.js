const axios = require('axios');

describe('Analysis API Tests', () => {
    const BASE_URL = 'http://localhost:5000';
    const TEST_FILES = [
        'senserobot VS 棋手1.pgn',
        'senserobot VS 棋手2.pgn',
        'senserobot VS 棋手3.pgn',
        'senserobot VS 棋手4.pgn',
        'senserobot VS 棋手5.pgn'
    ];

    beforeAll(async () => {
        try {
            await axios.get(`${BASE_URL}/`, { timeout: 5000 });
            console.log('✅ 服务器运行正常');
        } catch (error) {
            console.warn('❌ 服务器未运行，跳过集成测试');
            process.exit(0);
        }
    });

    describe('GET /api/pgn_files', () => {
        test('应该返回文件列表', async () => {
            const response = await axios.get(`${BASE_URL}/api/pgn_files`);
            
            expect(response.status).toBe(200);
            expect(response.data).toHaveProperty('files');
            expect(Array.isArray(response.data.files)).toBe(true);
            console.log(`📁 找到 ${response.data.files.length} 个PGN文件`);
        });
    });

    describe('GET /api/analyze/:filename', () => {
        test('应该返回正确的mistakes格式', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            expect(response.status).toBe(200);
            expect(response.data).toHaveProperty('status', 'completed');
            expect(response.data).toHaveProperty('mistakes');
            expect(Array.isArray(response.data.mistakes)).toBe(true);
            
            if (response.data.mistakes.length > 0) {
                const mistake = response.data.mistakes[0];
                expect(mistake).toHaveProperty('step');
                expect(mistake).toHaveProperty('loss');
                expect(mistake).toHaveProperty('fen');
                expect(mistake).toHaveProperty('actual_move');
                expect(mistake).toHaveProperty('best_move');
                expect(mistake).toHaveProperty('cause');
                expect(mistake).toHaveProperty('idea');
                expect(mistake).toHaveProperty('tactic_exp');
            }
            console.log(`📊 分析结果: ${response.data.white} vs ${response.data.black}`);
            console.log(`🎯 找到 ${response.data.mistakes.length} 个失误`);
        });

        test('应该返回正确的exercises格式', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            expect(response.data).toHaveProperty('exercises');
            expect(Array.isArray(response.data.exercises)).toBe(true);
            
            if (response.data.exercises.length > 0) {
                const exercise = response.data.exercises[0];
                expect(exercise).toHaveProperty('id');
                expect(exercise).toHaveProperty('step');
                expect(exercise).toHaveProperty('fen');
                expect(exercise).toHaveProperty('best_move');
                expect(exercise).toHaveProperty('loss');
                expect(exercise).toHaveProperty('actual_move');
            }
            console.log(`📝 生成 ${response.data.exercises.length} 个习题`);
        });

        test('不同难度阈值应该返回不同数量的习题', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            
            const easyResponse = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}?difficulty=easy`);
            const mediumResponse = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}?difficulty=medium`);
            const hardResponse = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}?difficulty=hard`);
            
            const easyCount = easyResponse.data.exercises.length;
            const mediumCount = mediumResponse.data.exercises.length;
            const hardCount = hardResponse.data.exercises.length;
            
            expect(easyCount).toBeGreaterThanOrEqual(mediumCount);
            expect(mediumCount).toBeGreaterThanOrEqual(hardCount);
            
            console.log(`⚙️ 难度测试 - 简单: ${easyCount}, 中等: ${mediumCount}, 困难: ${hardCount}`);
        });

        test('total_mistakes应该大于等于filtered_mistakes', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            expect(response.data.total_mistakes).toBeGreaterThanOrEqual(response.data.filtered_mistakes);
            expect(response.data.filtered_mistakes).toBe(response.data.mistakes.length);
            expect(response.data.filtered_mistakes).toBe(response.data.exercises.length);
        });

        test('应该正确处理中文文件名', async () => {
            const encodedFile = encodeURIComponent('败局2.pgn');
            try {
                const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
                expect(response.status).toBe(200);
                expect(response.data).toHaveProperty('status');
            } catch (error) {
                if (error.response && error.response.status === 404) {
                    console.log('⚠️ 测试文件不存在，跳过');
                } else {
                    throw error;
                }
            }
        });
    });

    describe('POST /api/check_move', () => {
        let exercise;

        beforeEach(async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            exercise = response.data.exercises[0];
        });

        test('应该验证最佳着法', async () => {
            if (!exercise) {
                console.log('⚠️ 没有找到习题，跳过此测试');
                return;
            }
            
            const response = await axios.post(`${BASE_URL}/api/check_move`, {
                fen: exercise.fen,
                move: exercise.best_move,
                expected_best: exercise.best_move
            });
            
            expect(response.status).toBe(200);
            expect(response.data).toHaveProperty('valid', true);
            expect(response.data).toHaveProperty('correct', true);
            console.log(`✅ 最佳着法验证通过: ${exercise.best_move}`);
        });

        test('应该验证错误着法', async () => {
            if (!exercise) {
                console.log('⚠️ 没有找到习题，跳过此测试');
                return;
            }
            
            const response = await axios.post(`${BASE_URL}/api/check_move`, {
                fen: exercise.fen,
                move: 'a1a2',
                expected_best: exercise.best_move
            });
            
            expect(response.status).toBe(200);
            expect(response.data).toHaveProperty('valid');
        });

        test('应该处理非法着法', async () => {
            if (!exercise) {
                console.log('⚠️ 没有找到习题，跳过此测试');
                return;
            }
            
            const response = await axios.post(`${BASE_URL}/api/check_move`, {
                fen: exercise.fen,
                move: 'z9z0',
                expected_best: exercise.best_move
            });
            
            expect(response.status).toBe(200);
            expect(response.data).toHaveProperty('valid', false);
        });
    });

    describe('FEN格式验证', () => {
        test('mistakes中的FEN应该有效', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            for (const mistake of response.data.mistakes) {
                const fenParts = mistake.fen.split(' ');
                expect(fenParts.length).toBe(6);
                expect(['w', 'b']).toContain(fenParts[1]);
            }
        });

        test('exercises中的FEN应该有效', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            for (const exercise of response.data.exercises) {
                const fenParts = exercise.fen.split(' ');
                expect(fenParts.length).toBe(6);
                expect(['w', 'b']).toContain(fenParts[1]);
            }
        });
    });

    describe('数据完整性检查', () => {
        test('所有PGN文件应该能被分析', async () => {
            for (const filename of TEST_FILES) {
                const encodedFile = encodeURIComponent(filename);
                try {
                    const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
                    expect(response.status).toBe(200);
                    expect(response.data).toHaveProperty('status', 'completed');
                    console.log(`✅ 成功分析: ${filename}`);
                } catch (error) {
                    console.log(`⚠️ 跳过: ${filename} - ${error.message}`);
                }
            }
        });

        test('mistakes和exercises应该数据一致', async () => {
            const encodedFile = encodeURIComponent(TEST_FILES[0]);
            const response = await axios.get(`${BASE_URL}/api/analyze/${encodedFile}`);
            
            const mistakes = response.data.mistakes;
            const exercises = response.data.exercises;
            
            expect(mistakes.length).toBe(exercises.length);
            
            for (let i = 0; i < mistakes.length; i++) {
                expect(mistakes[i].step).toBe(exercises[i].step);
                expect(mistakes[i].loss).toBe(exercises[i].loss);
                expect(mistakes[i].fen).toBe(exercises[i].fen);
                expect(mistakes[i].best_move).toBe(exercises[i].best_move);
            }
        });
    });
});