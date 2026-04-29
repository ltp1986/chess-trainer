const MockAPI = require('./mocks/mock-api');

describe('棋局库 API 测试', () => {
  describe('棋局列表 API', () => {
    test('GET /api/games 应该返回棋局列表', () => {
      const result = MockAPI.getPGNFiles();
      
      expect(result).toHaveProperty('files');
      expect(Array.isArray(result.files)).toBe(true);
    });

    test('棋局列表应该包含正确字段', () => {
      const result = MockAPI.getPGNFiles();
      const game = result.files[0];
      
      expect(game).toHaveProperty('name');
      expect(game).toHaveProperty('size');
      expect(game).toHaveProperty('date');
    });
  });

  describe('分析 API（棋局分析）', () => {
    test('GET /api/analyze/:filename 应该返回分析结果', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      
      expect(result.status).toBe('completed');
      expect(result).toHaveProperty('white');
      expect(result).toHaveProperty('black');
      expect(result).toHaveProperty('result');
      expect(result).toHaveProperty('exercises');
    });

    test('分析结果应该包含完整的棋局数据', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      
      expect(result).toHaveProperty('total_mistakes');
      expect(result).toHaveProperty('filtered_mistakes');
      expect(result).toHaveProperty('difficulty');
      expect(Array.isArray(result.exercises)).toBe(true);
      expect(Array.isArray(result.mistakes)).toBe(true);
    });

    test('应该处理无效文件名', () => {
      const result = MockAPI.analyzePGN('nonexistent.pgn');
      
      expect(result.status).toBe('error');
      expect(result).toHaveProperty('message');
    });

    test('应该处理空文件名', () => {
      const result = MockAPI.analyzePGN('');
      
      expect(result.status).toBe('error');
      expect(result.message).toBe('文件名不能为空');
    });
  });

  describe('玩家统计 API', () => {
    test('GET /api/player/:player_id/stats 应该返回玩家统计数据', () => {
      const result = MockAPI.getPlayerStats(1);
      
      expect(result).toHaveProperty('player_id', 1);
      expect(result).toHaveProperty('total_games');
      expect(result).toHaveProperty('wins');
      expect(result).toHaveProperty('losses');
      expect(result).toHaveProperty('draws');
      expect(result).toHaveProperty('avg_rating');
    });

    test('统计数据应该合理', () => {
      const result = MockAPI.getPlayerStats(1);
      
      expect(result.total_games).toBeGreaterThanOrEqual(result.wins + result.losses + result.draws);
      expect(result.avg_rating).toBeGreaterThan(0);
    });
  });

  describe('训练进度 API', () => {
    test('GET /api/training/progress 应该返回训练进度', () => {
      const result = MockAPI.getTrainingProgress();
      
      expect(result).toHaveProperty('today_exercises');
      expect(result).toHaveProperty('weekly_exercises');
      expect(result).toHaveProperty('monthly_exercises');
      expect(result).toHaveProperty('streak');
      expect(result).toHaveProperty('total_completed');
    });

    test('进度数据应该为非负整数', () => {
      const result = MockAPI.getTrainingProgress();
      
      expect(result.today_exercises).toBeGreaterThanOrEqual(0);
      expect(result.weekly_exercises).toBeGreaterThanOrEqual(0);
      expect(result.monthly_exercises).toBeGreaterThanOrEqual(0);
      expect(result.streak).toBeGreaterThanOrEqual(0);
      expect(result.total_completed).toBeGreaterThanOrEqual(0);
    });
  });

  describe('训练计划 API', () => {
    test('GET /api/training/plan 应该返回训练计划', () => {
      const result = MockAPI.getTrainingPlan();
      
      expect(result).toHaveProperty('plan');
      expect(result).toHaveProperty('duration');
      expect(result).toHaveProperty('total_exercises');
      expect(Array.isArray(result.plan)).toBe(true);
    });

    test('训练计划应该包含正确的字段', () => {
      const result = MockAPI.getTrainingPlan();
      const dayPlan = result.plan[0];
      
      expect(dayPlan).toHaveProperty('day');
      expect(dayPlan).toHaveProperty('focus');
      expect(dayPlan).toHaveProperty('exercises');
    });
  });

  describe('玩家习题 API', () => {
    test('GET /api/exercises/player/:player_id 应该返回玩家习题', () => {
      const result = MockAPI.getPlayerExercises(1);
      
      expect(result).toHaveProperty('exercises');
      expect(result).toHaveProperty('player_id', 1);
      expect(result).toHaveProperty('total_count');
      expect(result).toHaveProperty('completed_count');
      expect(Array.isArray(result.exercises)).toBe(true);
    });

    test('习题数据应该完整', () => {
      const result = MockAPI.getPlayerExercises(1);
      if (result.exercises.length > 0) {
        const exercise = result.exercises[0];
        
        expect(exercise).toHaveProperty('id');
        expect(exercise).toHaveProperty('step');
        expect(exercise).toHaveProperty('fen');
        expect(exercise).toHaveProperty('turn');
        expect(exercise).toHaveProperty('best_move');
        expect(exercise).toHaveProperty('loss');
        expect(exercise).toHaveProperty('actual_move');
        expect(exercise).toHaveProperty('description');
      }
    });
  });

  describe('错误处理测试', () => {
    test('分析 API 应该处理无效文件名', () => {
      const result = MockAPI.analyzePGN('invalid_file.pgn');
      
      expect(result.status).toBe('error');
      expect(result.message).toBe('File not found');
    });

    test('走棋验证应该处理无效参数', () => {
      const result = MockAPI.checkMove({
        fen: '',
        move: '',
        best_move: 'e2e4'
      });
      
      expect(result.is_correct).toBe(false);
      expect(result.explanation).toBe('参数无效');
    });

    test('合法着法 API 应该处理无效 FEN', () => {
      const result = MockAPI.getLegalMoves({ fen: '' });
      
      expect(result.moves).toEqual([]);
    });
  });
});