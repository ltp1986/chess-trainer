/**
 * 集成测试
 * 测试前端与后端API的交互
 */

const axios = require('axios');

describe('API Integration Tests', () => {
  const BASE_URL = 'http://localhost:5000';

  beforeAll(async () => {
    // 确保服务器正在运行
    try {
      await axios.get(`${BASE_URL}/`);
    } catch (error) {
      console.warn('服务器未运行，跳过集成测试');
      return;
    }
  });

  describe('PGN文件管理', () => {
    test('GET /api/pgn_files 应该返回文件列表', async () => {
      const response = await axios.get(`${BASE_URL}/api/pgn_files`);
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('files');
      expect(Array.isArray(response.data.files)).toBe(true);
    });
  });

  describe('分析API', () => {
    test('GET /api/analyze/:filename 应该返回分析结果', async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('status', 'completed');
      expect(response.data).toHaveProperty('white');
      expect(response.data).toHaveProperty('black');
      expect(response.data).toHaveProperty('result');
      expect(response.data).toHaveProperty('exercises');
      expect(Array.isArray(response.data.exercises)).toBe(true);
    });

    test('分析结果应该包含正确的习题数据', async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      const exercises = response.data.exercises;
      
      if (exercises.length > 0) {
        const exercise = exercises[0];
        
        expect(exercise).toHaveProperty('id');
        expect(exercise).toHaveProperty('step');
        expect(exercise).toHaveProperty('fen');
        expect(exercise).toHaveProperty('turn');
        expect(exercise).toHaveProperty('best_move');
        
        // 验证FEN格式
        const fenParts = exercise.fen.split(' ');
        expect(fenParts.length).toBe(6);
        expect(['w', 'b']).toContain(fenParts[1]);
      }
    });
  });

  describe('走棋验证API', () => {
    let exercise;

    beforeEach(async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      exercise = response.data.exercises[0];
    });

    test('POST /api/check_move 应该验证最佳着法', async () => {
      const response = await axios.post(`${BASE_URL}/api/check_move`, {
        fen: exercise.fen,
        move: exercise.best_move,
        expected_best: exercise.best_move
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('valid', true);
      expect(response.data).toHaveProperty('correct', true);
    });

    test('POST /api/check_move 应该验证错误着法', async () => {
      const response = await axios.post(`${BASE_URL}/api/check_move`, {
        fen: exercise.fen,
        move: 'a1a2', // 随机一个非法或非最佳着法
        expected_best: exercise.best_move
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('valid');
    });

    test('POST /api/check_move 应该处理非法着法', async () => {
      const response = await axios.post(`${BASE_URL}/api/check_move`, {
        fen: exercise.fen,
        move: 'z9z0', // 完全非法的着法
        expected_best: exercise.best_move
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('valid', false);
    });
  });

  describe('合法着法API', () => {
    let exercise;

    beforeEach(async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      exercise = response.data.exercises[0];
    });

    test('POST /api/legal_moves 应该返回合法着法', async () => {
      const response = await axios.post(`${BASE_URL}/api/legal_moves`, {
        fen: exercise.fen,
        square: 'e2'
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('square', 'e2');
      expect(response.data).toHaveProperty('legal_moves');
      expect(Array.isArray(response.data.legal_moves)).toBe(true);
    });
  });

  describe('最佳着法API', () => {
    let exercise;

    beforeEach(async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      exercise = response.data.exercises[0];
    });

    test('POST /api/best_move 应该返回最佳着法', async () => {
      const response = await axios.post(`${BASE_URL}/api/best_move`, {
        fen: exercise.fen
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('best_move');
    });
  });

  describe('提示API', () => {
    let exercise;

    beforeEach(async () => {
      const response = await axios.get(`${BASE_URL}/api/analyze/败局1.pgn`);
      exercise = response.data.exercises[0];
    });

    test('POST /api/hint 应该返回提示', async () => {
      const response = await axios.post(`${BASE_URL}/api/hint`, {
        fen: exercise.fen
      });
      
      expect(response.status).toBe(200);
      expect(response.data).toHaveProperty('hint');
    });
  });
});
