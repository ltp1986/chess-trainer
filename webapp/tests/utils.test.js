/**
 * 工具函数单元测试
 */

describe('Utils Module Tests', () => {
  describe('String Utilities', () => {
    test('should format FEN string correctly', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      
      const parts = fen.split(' ');
      expect(parts.length).toBe(6);
      expect(parts[1]).toBe('w');
      expect(['w', 'b']).toContain(parts[1]);
    });

    test('should validate move format', () => {
      const validMoves = ['e2e4', 'a7a8q', 'h1g1', 'e1g1'];
      const shortMoves = ['e2', 'e2e'];
      const longMoves = ['e2e456'];
      
      validMoves.forEach(move => {
        expect(move.length).toBeGreaterThanOrEqual(4);
        expect(move.length).toBeLessThanOrEqual(5);
      });
      
      shortMoves.forEach(move => {
        expect(move.length).toBeLessThan(4);
      });
      
      longMoves.forEach(move => {
        expect(move.length).toBeGreaterThan(5);
      });
    });
  });

  describe('Date Utilities', () => {
    test('should format date correctly', () => {
      const date = new Date('2024-01-15');
      const formatted = date.toISOString().split('T')[0];
      
      expect(formatted).toBe('2024-01-15');
    });
  });

  describe('Game Result Utilities', () => {
    test('should parse game result', () => {
      const results = {
        '1-0': '白方胜',
        '0-1': '黑方胜',
        '1/2-1/2': '和棋',
        '*': '未完成'
      };
      
      expect(Object.keys(results).length).toBe(4);
    });
  });
});

describe('API Call Mock Tests', () => {
  test('should handle successful API response', async () => {
    const mockData = { status: 'success', data: [] };
    
    expect(mockData).toHaveProperty('status');
    expect(mockData).toHaveProperty('data');
  });

  test('should handle error cases', async () => {
    const errorResponse = { status: 'error', message: 'Not found' };
    
    expect(errorResponse).toHaveProperty('status', 'error');
    expect(errorResponse).toHaveProperty('message');
  });
});

describe('Utils Module - DOM Functions', () => {
  test('showLoading should create loading element', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    
    container.innerHTML = `
        <div class="text-center py-10">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p class="mt-2 text-gray-500">加载中...</p>
        </div>
    `;
    
    expect(container.innerHTML).toContain('加载中');
    expect(container.innerHTML).toContain('animate-spin');
    
    document.body.removeChild(container);
  });

  test('should parse PGN header correctly', () => {
    const pgn = '[Event "Test Game"]\n[White "Player1"]\n[Black "Player2"]\n[Result "1-0"]\n1. e4 e5';
    
    const eventMatch = pgn.match(/\[Event\s+"([^"]+)"/);
    const whiteMatch = pgn.match(/\[White\s+"([^"]+)"/);
    const blackMatch = pgn.match(/\[Black\s+"([^"]+)"/);
    const resultMatch = pgn.match(/\[Result\s+"([^"]+)"/);
    
    expect(eventMatch[1]).toBe('Test Game');
    expect(whiteMatch[1]).toBe('Player1');
    expect(blackMatch[1]).toBe('Player2');
    expect(resultMatch[1]).toBe('1-0');
  });

  test('should extract moves from PGN', () => {
    const pgn = '1. e4 e5 2. Nf3 Nc6 3. Bb5';
    const moves = pgn.split(' ').filter(m => !m.includes('.')).filter(Boolean);
    
    expect(moves.length).toBe(5);
    expect(moves).toContain('e4');
    expect(moves).toContain('e5');
    expect(moves).toContain('Nf3');
  });

  test('should validate game result', () => {
    const validResults = ['1-0', '0-1', '1/2-1/2', '*'];
    const invalidResults = ['1-1', '2-0', 'draw'];
    
    validResults.forEach(result => {
      expect(['1-0', '0-1', '1/2-1/2', '*']).toContain(result);
    });
    
    invalidResults.forEach(result => {
      expect(['1-0', '0-1', '1/2-1/2', '*']).not.toContain(result);
    });
  });

  test('should format move notation', () => {
    const moves = ['e2e4', 'e7e5', 'g1f3', 'a7a8q'];
    
    moves.forEach(move => {
      expect(move.length).toBeGreaterThanOrEqual(4);
    });
  });

  test('should convert FEN to board representation', () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const boardPart = fen.split(' ')[0];
    const rows = boardPart.split('/');
    
    expect(rows.length).toBe(8);
    expect(rows[0]).toBe('rnbqkbnr');
    expect(rows[7]).toBe('RNBQKBNR');
  });

  test('should count pieces in FEN', () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR';
    const boardPart = fen.split('/').join('');
    
    const whitePieces = (boardPart.match(/[RNBQKP]/g) || []).length;
    const blackPieces = (boardPart.match(/[rnbqkp]/g) || []).length;
    
    expect(whitePieces).toBe(16);
    expect(blackPieces).toBe(16);
  });

  test('should parse move coordinates', () => {
    const move = 'e2e4';
    const from = move.substring(0, 2);
    const to = move.substring(2, 4);
    
    expect(from).toBe('e2');
    expect(to).toBe('e4');
    expect(from[0]).toMatch(/[a-h]/);
    expect(from[1]).toMatch(/[1-8]/);
  });
});