/**
 * Validator模块单元测试
 */

const Validator = require('../js/validation');

describe('Validator Module Tests', () => {
  describe('validatePlayerName', () => {
    test('should validate empty name', () => {
      const result = Validator.validatePlayerName('');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('姓名不能为空');
    });

    test('should validate short name', () => {
      const result = Validator.validatePlayerName('A');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('姓名至少需要2个字符');
    });

    test('should validate long name', () => {
      const longName = 'A'.repeat(51);
      const result = Validator.validatePlayerName(longName);
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('姓名不能超过50个字符');
    });

    test('should validate valid Chinese name', () => {
      const result = Validator.validatePlayerName('张三');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    test('should validate valid English name', () => {
      const result = Validator.validatePlayerName('John_Doe');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    test('should reject invalid characters', () => {
      const result = Validator.validatePlayerName('张@三');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('姓名只能包含中文、英文、数字、下划线和连字符');
    });
  });

  describe('validateEmail', () => {
    test('should accept empty email', () => {
      const result = Validator.validateEmail('');
      expect(result.valid).toBe(true);
    });

    test('should validate valid email', () => {
      const result = Validator.validateEmail('test@example.com');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    test('should reject invalid email', () => {
      const result = Validator.validateEmail('invalid-email');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('邮箱格式不正确');
    });
  });

  describe('validateRating', () => {
    test('should accept empty rating', () => {
      const result = Validator.validateRating('');
      expect(result.valid).toBe(true);
    });

    test('should validate valid rating', () => {
      const result = Validator.validateRating('1800');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    test('should reject non-numeric rating', () => {
      const result = Validator.validateRating('abc');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('评级必须是数字');
    });

    test('should reject rating below 0', () => {
      const result = Validator.validateRating('-1');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('评级范围应在0-3000之间');
    });

    test('should reject rating above 3000', () => {
      const result = Validator.validateRating('3500');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('评级范围应在0-3000之间');
    });
  });

  describe('validateLevel', () => {
    test('should accept empty level', () => {
      const result = Validator.validateLevel('');
      expect(result.valid).toBe(true);
    });

    test('should validate valid levels', () => {
      ['L1', 'L2', 'L3', 'L4'].forEach(level => {
        const result = Validator.validateLevel(level);
        expect(result.valid).toBe(true);
      });
    });

    test('should reject invalid level', () => {
      const result = Validator.validateLevel('L5');
      expect(result.valid).toBe(false);
      expect(result.errors[0]).toContain('L1、L2、L3、L4');
    });
  });

  describe('validateFEN', () => {
    test('should reject empty FEN', () => {
      const result = Validator.validateFEN('');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('FEN不能为空');
    });

    test('should validate standard starting position', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    test('should reject FEN with wrong row count', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(false);
    });

    test('should reject FEN with invalid characters', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNRX w KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(false);
    });
  });

  describe('validatePGN', () => {
    test('should reject empty PGN', () => {
      const result = Validator.validatePGN('');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('PGN内容不能为空');
    });

    test('should reject PGN without brackets', () => {
      const result = Validator.validatePGN('1. e4 e5 2. Nf3');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('PGN格式不正确，应以[开头');
    });

    test('should reject PGN without moves', () => {
      const result = Validator.validatePGN('[Event "Test"]');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('PGN格式不正确，缺少走法记录');
    });

    test('should validate valid PGN', () => {
      const pgn = '[Event "Test"]\n[White "Player1"]\n[Black "Player2"]\n1. e4 e5 2. Nf3 Nc6';
      const result = Validator.validatePGN(pgn);
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual([]);
    });
  });

  describe('validateForm', () => {
    test('should validate complete form', () => {
      const formData = {
        name: '张三',
        email: 'test@example.com',
        rating: '1800',
        level: 'L2'
      };
      const result = Validator.validateForm(formData);
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual({});
    });

    test('should validate form with errors', () => {
      const formData = {
        name: 'A',
        email: 'invalid',
        rating: '3500',
        level: 'L5'
      };
      const result = Validator.validateForm(formData);
      expect(result.valid).toBe(false);
      expect(result.errors).toHaveProperty('name');
      expect(result.errors).toHaveProperty('email');
      expect(result.errors).toHaveProperty('rating');
      expect(result.errors).toHaveProperty('level');
    });
  });

  describe('validateMove', () => {
    test('should validate valid move', () => {
      const validMoves = ['e2e4', 'e7e5', 'g1f3'];
      const result = Validator.validateMove('e2e4', validMoves);
      expect(result).toBe(true);
    });

    test('should reject invalid move', () => {
      const validMoves = ['e2e4', 'e7e5', 'g1f3'];
      const result = Validator.validateMove('a1a2', validMoves);
      expect(result).toBe(false);
    });
  });

  describe('showValidationErrors', () => {
    test('should show validation errors in container', () => {
      const container = document.createElement('div');
      container.id = 'test-container';
      document.body.appendChild(container);
      
      const errors = {
        name: ['姓名不能为空'],
        email: ['邮箱格式不正确']
      };
      
      Validator.showValidationErrors(errors, 'test-container');
      
      expect(container.innerHTML).toContain('姓名');
      expect(container.innerHTML).toContain('邮箱');
      expect(container.innerHTML).toContain('validation-error');
      
      document.body.removeChild(container);
    });

    test('should handle null container', () => {
      expect(() => Validator.showValidationErrors({}, 'non-existent')).not.toThrow();
    });
  });

  describe('getFieldLabel', () => {
    test('should return correct label', () => {
      expect(Validator.getFieldLabel('name')).toBe('姓名');
      expect(Validator.getFieldLabel('email')).toBe('邮箱');
      expect(Validator.getFieldLabel('rating')).toBe('评级');
      expect(Validator.getFieldLabel('level')).toBe('等级');
      expect(Validator.getFieldLabel('pgn')).toBe('PGN内容');
    });

    test('should return field name for unknown fields', () => {
      expect(Validator.getFieldLabel('unknown')).toBe('unknown');
    });
  });

  describe('validateForm with PGN', () => {
    test('should validate form with PGN', () => {
      const validPgn = '[Event "Test"]\n[White "Player1"]\n[Black "Player2"]\n1. e4 e5';
      const formData = {
        name: '张三',
        pgn: validPgn
      };
      const result = Validator.validateForm(formData);
      expect(result.valid).toBe(true);
    });

    test('should reject form with invalid PGN', () => {
      const invalidPgn = 'invalid pgn content';
      const formData = {
        name: '张三',
        pgn: invalidPgn
      };
      const result = Validator.validateForm(formData);
      expect(result.valid).toBe(false);
      expect(result.errors).toHaveProperty('pgn');
    });
  });

  describe('validateFEN edge cases', () => {
    test('should validate FEN with castling rights', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(true);
    });

    test('should validate FEN with en passant target', () => {
      const fen = 'rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(true);
    });

    test('should reject FEN with invalid turn', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR x KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(false);
    });

    test('should reject FEN with incomplete rows', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP/RNBQKBNR w KQkq - 0 1';
      const result = Validator.validateFEN(fen);
      expect(result.valid).toBe(false);
    });
  });

  describe('validatePGN edge cases', () => {
    test('should reject PGN with mismatched brackets', () => {
      const pgn = '[Event "Test"\n1. e4';
      const result = Validator.validatePGN(pgn);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors.some(e => e.includes(']') || e.includes('括号'))).toBe(true);
    });

    test('should validate minimal valid PGN', () => {
      const pgn = '[Event "T"]\n1. e4';
      const result = Validator.validatePGN(pgn);
      expect(result.valid).toBe(true);
    });
  });
});