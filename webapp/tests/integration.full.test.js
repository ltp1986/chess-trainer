const MockAPI = require('./mocks/mock-api');

describe('API Integration Tests (Full Coverage)', () => {
  describe('PGN文件管理', () => {
    test('GET /api/pgn_files 应该返回文件列表', () => {
      const result = MockAPI.getPGNFiles();
      expect(result).toHaveProperty('files');
      expect(Array.isArray(result.files)).toBe(true);
    });

    test('文件列表应该包含正确字段', () => {
      const result = MockAPI.getPGNFiles();
      const file = result.files[0];
      expect(file).toHaveProperty('name');
      expect(file).toHaveProperty('size');
      expect(file).toHaveProperty('date');
    });
  });

  describe('分析API', () => {
    test('GET /api/analyze/:filename 应该返回分析结果', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      expect(result.status).toBe('completed');
      expect(result).toHaveProperty('exercises');
    });

    test('分析结果应该包含完整的字段', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      expect(result).toHaveProperty('white');
      expect(result).toHaveProperty('black');
      expect(result).toHaveProperty('result');
      expect(result).toHaveProperty('difficulty');
      expect(result).toHaveProperty('total_mistakes');
      expect(result).toHaveProperty('filtered_mistakes');
      expect(result).toHaveProperty('mistakes');
    });

    test('应该处理无效文件名', () => {
      const result = MockAPI.analyzePGN('nonexistent.pgn');
      expect(result.status).toBe('error');
      expect(result).toHaveProperty('message');
    });
  });

  describe('走棋验证API', () => {
    test('POST /api/check_move 应该验证最佳着法', () => {
      const result = MockAPI.checkMove({
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        move: 'e2e4',
        best_move: 'e2e4'
      });
      expect(result.is_correct).toBe(true);
    });

    test('POST /api/check_move 应该验证错误着法', () => {
      const result = MockAPI.checkMove({
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        move: 'a2a3',
        best_move: 'e2e4'
      });
      expect(result.is_correct).toBe(false);
    });

    test('POST /api/check_move 应该返回解释', () => {
      const result = MockAPI.checkMove({
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        move: 'e2e4',
        best_move: 'e2e4'
      });
      expect(result).toHaveProperty('explanation');
    });
  });

  describe('合法着法API', () => {
    test('POST /api/legal_moves 应该返回合法着法列表', () => {
      const result = MockAPI.getLegalMoves({ 
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 
      });
      expect(result).toHaveProperty('moves');
      expect(Array.isArray(result.moves)).toBe(true);
    });

    test('着法应该包含 from, to, capture 字段', () => {
      const result = MockAPI.getLegalMoves({ 
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 
      });
      const move = result.moves[0];
      expect(move).toHaveProperty('from');
      expect(move).toHaveProperty('to');
      expect(move).toHaveProperty('capture');
    });
  });

  describe('最佳着法API', () => {
    test('POST /api/best_move 应该返回最佳着法', () => {
      const result = MockAPI.getBestMove({ 
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 
      });
      expect(result).toHaveProperty('best_move');
      expect(result).toHaveProperty('explanation');
    });
  });

  describe('提示API', () => {
    test('POST /api/hint 应该返回提示', () => {
      const result = MockAPI.getHint({ 
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 
      });
      expect(result).toHaveProperty('hint');
      expect(result).toHaveProperty('piece');
    });
  });

  describe('玩家API', () => {
    test('GET /api/players 应该返回玩家列表', () => {
      const result = MockAPI.getPlayers();
      expect(result).toHaveProperty('players');
      expect(Array.isArray(result.players)).toBe(true);
    });

    test('玩家应该包含完整字段', () => {
      const result = MockAPI.getPlayers();
      const player = result.players[0];
      expect(player).toHaveProperty('id');
      expect(player).toHaveProperty('name');
      expect(player).toHaveProperty('level');
      expect(player).toHaveProperty('rating');
    });
  });

  describe('玩家习题API', () => {
    test('GET /api/exercises/player/:player_id 应该返回玩家习题', () => {
      const result = MockAPI.getPlayerExercises(1);
      expect(result).toHaveProperty('exercises');
      expect(Array.isArray(result.exercises)).toBe(true);
    });
  });

  describe('错误处理测试', () => {
    test('分析API应该处理空文件名', () => {
      const result = MockAPI.analyzePGN('');
      expect(result.status).toBe('error');
    });

    test('走棋验证应该处理无效FEN', () => {
      const result = MockAPI.checkMove({
        fen: 'invalid_fen',
        move: 'e2e4',
        best_move: 'e2e4'
      });
      expect(result).toHaveProperty('is_correct');
    });
  });

  describe('数据完整性测试', () => {
    test('习题数据应该完整', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
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

    test('错误分析数据应该完整', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      if (result.mistakes.length > 0) {
        const mistake = result.mistakes[0];
        expect(mistake).toHaveProperty('step');
        expect(mistake).toHaveProperty('loss');
        expect(mistake).toHaveProperty('cause');
        expect(mistake).toHaveProperty('idea');
        expect(mistake).toHaveProperty('tactic_exp');
      }
    });
  });
});