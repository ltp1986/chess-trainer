const MockAPI = require('./mocks/mock-api');

describe('API Integration Tests (Mocked)', () => {
  describe('PGN文件管理', () => {
    test('应该返回文件列表', () => {
      const result = MockAPI.getPGNFiles();
      
      expect(result).toHaveProperty('files');
      expect(Array.isArray(result.files)).toBe(true);
      expect(result.files.length).toBeGreaterThan(0);
    });

    test('文件列表应该包含正确的字段', () => {
      const result = MockAPI.getPGNFiles();
      const file = result.files[0];
      
      expect(file).toHaveProperty('name');
      expect(file).toHaveProperty('size');
      expect(file).toHaveProperty('date');
    });
  });

  describe('分析API', () => {
    test('应该返回分析结果', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      
      expect(result.status).toBe('completed');
      expect(result).toHaveProperty('white');
      expect(result).toHaveProperty('black');
      expect(result).toHaveProperty('result');
      expect(result).toHaveProperty('exercises');
      expect(Array.isArray(result.exercises)).toBe(true);
    });

    test('分析结果应该包含正确的习题数据', () => {
      const result = MockAPI.analyzePGN('senserobot VS 棋手1.pgn');
      const exercises = result.exercises;

      if (exercises.length > 0) {
        const exercise = exercises[0];
        expect(exercise).toHaveProperty('id');
        expect(exercise).toHaveProperty('fen');
        expect(exercise).toHaveProperty('best_move');
        expect(exercise).toHaveProperty('turn');
      }
    });

    test('应该处理无效文件名', () => {
      const result = MockAPI.analyzePGN('nonexistent.pgn');
      
      expect(result.status).toBe('error');
      expect(result).toHaveProperty('message');
    });
  });

  describe('走棋验证API', () => {
    test('应该验证最佳着法', () => {
      const moveData = {
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        move: 'e2e4',
        best_move: 'e2e4'
      };
      
      const result = MockAPI.checkMove(moveData);
      
      expect(result.is_correct).toBe(true);
      expect(result.best_move).toBe('e2e4');
    });

    test('应该验证错误着法', () => {
      const moveData = {
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        move: 'a2a3',
        best_move: 'e2e4'
      };
      
      const result = MockAPI.checkMove(moveData);
      
      expect(result.is_correct).toBe(false);
      expect(result.best_move).toBe('e2e4');
    });
  });

  describe('合法着法API', () => {
    test('应该返回合法着法', () => {
      const result = MockAPI.getLegalMoves({ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' });
      
      expect(result).toHaveProperty('moves');
      expect(Array.isArray(result.moves)).toBe(true);
      expect(result.moves.length).toBeGreaterThan(0);
    });

    test('着法应该包含正确的字段', () => {
      const result = MockAPI.getLegalMoves({ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' });
      const move = result.moves[0];
      
      expect(move).toHaveProperty('from');
      expect(move).toHaveProperty('to');
      expect(move).toHaveProperty('capture');
    });
  });

  describe('最佳着法API', () => {
    test('应该返回最佳着法', () => {
      const result = MockAPI.getBestMove({ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' });
      
      expect(result).toHaveProperty('best_move');
      expect(result).toHaveProperty('explanation');
    });
  });

  describe('提示API', () => {
    test('应该返回提示', () => {
      const result = MockAPI.getHint({ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' });
      
      expect(result).toHaveProperty('hint');
      expect(result).toHaveProperty('piece');
    });
  });

  describe('玩家API', () => {
    test('应该返回玩家列表', () => {
      const result = MockAPI.getPlayers();
      
      expect(result).toHaveProperty('players');
      expect(Array.isArray(result.players)).toBe(true);
    });

    test('玩家应该包含正确的字段', () => {
      const result = MockAPI.getPlayers();
      const player = result.players[0];
      
      expect(player).toHaveProperty('id');
      expect(player).toHaveProperty('name');
      expect(player).toHaveProperty('level');
      expect(player).toHaveProperty('rating');
    });
  });
});