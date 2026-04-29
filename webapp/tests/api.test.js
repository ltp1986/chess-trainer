/**
 * API 集成测试
 * 测试前端与后端API的交互
 */

const axios = require('axios');

describe('API Integration Tests', () => {
  const BASE_URL = 'http://localhost:5000';

  // 检查服务器是否运行
  beforeAll(async () => {
    try {
      await axios.get(`${BASE_URL}/`, { timeout: 5000 });
      console.log('✅ 服务器运行正常');
    } catch (error) {
      console.warn('❌ 服务器未运行，跳过集成测试');
      process.exit(0);
    }
  });

  test('GET /api/pgn_files 应该返回文件列表', async () => {
    const response = await axios.get(`${BASE_URL}/api/pgn_files`);
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('files');
    expect(Array.isArray(response.data.files)).toBe(true);
    console.log(`📁 找到 ${response.data.files.length} 个PGN文件`);
  });

  test('GET /api/analyze/senserobot VS 棋手1.pgn 应该返回分析结果', async () => {
    const response = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('status', 'completed');
    expect(response.data).toHaveProperty('exercises');
    expect(Array.isArray(response.data.exercises)).toBe(true);
    
    console.log(`📊 分析结果: ${response.data.white} vs ${response.data.black}`);
    console.log(`🎯 找到 ${response.data.exercises.length} 个习题`);
  });

  test('POST /api/check_move 应该验证走棋', async () => {
    const analyzeResponse = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
    const exercises = analyzeResponse.data.exercises;
    
    if (exercises.length === 0) {
      console.log('⚠️ 没有找到习题，跳过此测试');
      return;
    }
    
    const exercise = exercises[0];
    
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

  test('POST /api/legal_moves 应该返回合法着法', async () => {
    const analyzeResponse = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
    const exercises = analyzeResponse.data.exercises;
    
    if (exercises.length === 0) {
      console.log('⚠️ 没有找到习题，跳过此测试');
      return;
    }
    
    const exercise = exercises[0];
    
    const response = await axios.post(`${BASE_URL}/api/legal_moves`, {
      fen: exercise.fen,
      square: 'f2'
    });
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('legal_moves');
    expect(Array.isArray(response.data.legal_moves)).toBe(true);
    
    console.log(`⚡ f2格的合法着法: ${response.data.legal_moves.join(', ')}`);
  });

  test('POST /api/best_move 应该返回最佳着法', async () => {
    const analyzeResponse = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
    const exercises = analyzeResponse.data.exercises;
    
    if (exercises.length === 0) {
      console.log('⚠️ 没有找到习题，跳过此测试');
      return;
    }
    
    const exercise = exercises[0];
    
    const response = await axios.post(`${BASE_URL}/api/best_move`, {
      fen: exercise.fen
    });
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('best_move');
    
    console.log(`🏆 最佳着法: ${response.data.best_move}`);
  });

  test('POST /api/hint 应该返回提示', async () => {
    const analyzeResponse = await axios.get(`${BASE_URL}/api/analyze/senserobot%20VS%20棋手1.pgn`);
    const exercises = analyzeResponse.data.exercises;
    
    if (exercises.length === 0) {
      console.log('⚠️ 没有找到习题，跳过此测试');
      return;
    }
    
    const exercise = exercises[0];
    
    const response = await axios.post(`${BASE_URL}/api/hint`, {
      fen: exercise.fen
    });
    
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('hint');
    
    console.log(`💡 提示: ${response.data.hint}`);
  });
});
