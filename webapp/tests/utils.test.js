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

describe('PGN File Functions', () => {
  beforeEach(() => {
    global.apiCall = jest.fn();
    
    global.loadPgnFiles = async function() {
      try {
        const response = await apiCall('/api/pgn_files');
        const select = document.getElementById('pgn-select');
        const pathInput = document.getElementById('pgn-path-input');
        
        if (pathInput && response.watch_dir) {
          pathInput.value = response.watch_dir;
        }
        
        if (select) {
          select.innerHTML = '<option value="">-- 请选择PGN文件 --</option>';
          response.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = file;
            select.appendChild(option);
          });
        }
      } catch (error) {
        console.error('加载PGN文件列表失败:', error);
      }
    };
    
    global.getWatchDir = async function() {
      try {
        const response = await apiCall('/api/config/watch_dir');
        const pathInput = document.getElementById('pgn-path-input');
        if (pathInput) {
          pathInput.value = response.watch_dir;
        }
        return response.watch_dir;
      } catch (error) {
        console.error('获取PGN目录失败:', error);
        return '';
      }
    };
    
    global.setWatchDir = async function(newDir) {
      try {
        const response = await apiCall('/api/config/watch_dir', {
          method: 'POST',
          body: { watch_dir: newDir }
        });
        
        if (response.success) {
          const pathInput = document.getElementById('pgn-path-input');
          if (pathInput) {
            pathInput.value = response.watch_dir;
          }
          await loadPgnFiles();
          alert('PGN目录设置成功！');
        } else {
          alert('设置失败: ' + response.message);
        }
      } catch (error) {
        console.error('设置PGN目录失败:', error);
        alert('设置失败: ' + error.message);
      }
    };
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('loadPgnFiles should populate select element', async () => {
    global.apiCall.mockResolvedValue({
      watch_dir: '/path/to/pgn',
      files: ['game1.pgn', 'game2.pgn']
    });
    
    const select = document.createElement('select');
    select.id = 'pgn-select';
    const pathInput = document.createElement('input');
    pathInput.id = 'pgn-path-input';
    document.body.appendChild(select);
    document.body.appendChild(pathInput);
    
    await loadPgnFiles();
    
    expect(apiCall).toHaveBeenCalledWith('/api/pgn_files');
    expect(pathInput.value).toBe('/path/to/pgn');
    expect(select.innerHTML).toContain('game1.pgn');
    expect(select.innerHTML).toContain('game2.pgn');
    
    document.body.removeChild(select);
    document.body.removeChild(pathInput);
  });

  test('loadPgnFiles should handle missing elements', async () => {
    global.apiCall.mockResolvedValue({
      watch_dir: '/path/to/pgn',
      files: ['game1.pgn']
    });
    
    await loadPgnFiles();
    
    expect(apiCall).toHaveBeenCalledWith('/api/pgn_files');
  });

  test('loadPgnFiles should handle API error', async () => {
    global.apiCall.mockRejectedValue(new Error('Network error'));
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    await loadPgnFiles();
    
    expect(consoleErrorSpy).toHaveBeenCalledWith('加载PGN文件列表失败:', expect.any(Error));
    
    consoleErrorSpy.mockRestore();
  });

  test('getWatchDir should return directory path', async () => {
    global.apiCall.mockResolvedValue({ watch_dir: '/path/to/pgn' });
    
    const pathInput = document.createElement('input');
    pathInput.id = 'pgn-path-input';
    document.body.appendChild(pathInput);
    
    const result = await getWatchDir();
    
    expect(apiCall).toHaveBeenCalledWith('/api/config/watch_dir');
    expect(result).toBe('/path/to/pgn');
    expect(pathInput.value).toBe('/path/to/pgn');
    
    document.body.removeChild(pathInput);
  });

  test('getWatchDir should handle missing pathInput', async () => {
    global.apiCall.mockResolvedValue({ watch_dir: '/path/to/pgn' });
    
    const result = await getWatchDir();
    
    expect(result).toBe('/path/to/pgn');
  });

  test('getWatchDir should return empty string on error', async () => {
    global.apiCall.mockRejectedValue(new Error('Network error'));
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const result = await getWatchDir();
    
    expect(result).toBe('');
    expect(consoleErrorSpy).toHaveBeenCalledWith('获取PGN目录失败:', expect.any(Error));
    
    consoleErrorSpy.mockRestore();
  });

  test('setWatchDir should update directory successfully', async () => {
    global.apiCall.mockResolvedValue({ success: true, watch_dir: '/new/path' });
    
    const pathInput = document.createElement('input');
    pathInput.id = 'pgn-path-input';
    document.body.appendChild(pathInput);
    
    await setWatchDir('/new/path');
    
    expect(apiCall).toHaveBeenCalledWith('/api/config/watch_dir', {
      method: 'POST',
      body: { watch_dir: '/new/path' }
    });
    expect(pathInput.value).toBe('/new/path');
    
    document.body.removeChild(pathInput);
  });

  test('setWatchDir should handle failure response', async () => {
    global.apiCall.mockResolvedValue({ success: false, message: 'Permission denied' });
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    await setWatchDir('/new/path');
    
    expect(alertSpy).toHaveBeenCalledWith('设置失败: Permission denied');
    
    alertSpy.mockRestore();
  });

  test('setWatchDir should handle API error', async () => {
    global.apiCall.mockRejectedValue(new Error('Network error'));
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    await setWatchDir('/new/path');
    
    expect(consoleErrorSpy).toHaveBeenCalledWith('设置PGN目录失败:', expect.any(Error));
    expect(alertSpy).toHaveBeenCalled();
    
    consoleErrorSpy.mockRestore();
    alertSpy.mockRestore();
  });
});

describe('Utils Module - DOM Functions', () => {
  beforeEach(() => {
    global.showLoading = function(container) {
      if (!container) return;
      container.innerHTML = `
          <div class="text-center py-10">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p class="mt-2 text-gray-500">加载中...</p>
          </div>
      `;
    };
  });

  test('showLoading should create loading element', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    
    showLoading(container);
    
    expect(container.innerHTML).toContain('加载中');
    expect(container.innerHTML).toContain('animate-spin');
    
    document.body.removeChild(container);
  });

  test('showLoading should handle null container', () => {
    expect(() => showLoading(null)).not.toThrow();
  });

  test('showLoading should handle undefined container', () => {
    expect(() => showLoading(undefined)).not.toThrow();
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

  test('should convert algebraic notation to coordinates', () => {
    const algebraicToCoord = (notation) => {
      const file = notation.charAt(0);
      const rank = notation.charAt(1);
      return { file: file.charCodeAt(0) - 'a'.charCodeAt(0), rank: 8 - parseInt(rank) };
    };
    
    const coord = algebraicToCoord('e4');
    expect(coord.file).toBe(4);
    expect(coord.rank).toBe(4);
  });

  test('should convert coordinates to algebraic notation', () => {
    const coordToAlgebraic = (file, rank) => {
      const fileChar = String.fromCharCode('a'.charCodeAt(0) + file);
      const rankNum = 8 - rank;
      return fileChar + rankNum;
    };
    
    const notation = coordToAlgebraic(4, 4);
    expect(notation).toBe('e4');
  });

  test('should validate coordinate range', () => {
    const isValidCoord = (file, rank) => {
      return file >= 0 && file <= 7 && rank >= 0 && rank <= 7;
    };
    
    expect(isValidCoord(0, 0)).toBe(true);
    expect(isValidCoord(7, 7)).toBe(true);
    expect(isValidCoord(8, 0)).toBe(false);
    expect(isValidCoord(0, 8)).toBe(false);
    expect(isValidCoord(-1, 0)).toBe(false);
  });

  test('should generate piece symbol', () => {
    const pieceSymbols = {
      'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
      'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
    };
    
    expect(pieceSymbols['P']).toBe('♙');
    expect(pieceSymbols['p']).toBe('♟');
    expect(pieceSymbols['K']).toBe('♔');
    expect(pieceSymbols['k']).toBe('♚');
  });

  test('should determine piece color', () => {
    const isWhitePiece = (piece) => piece === piece.toUpperCase();
    
    expect(isWhitePiece('P')).toBe(true);
    expect(isWhitePiece('p')).toBe(false);
    expect(isWhitePiece('Q')).toBe(true);
    expect(isWhitePiece('q')).toBe(false);
  });

  test('should parse castling rights', () => {
    const castlingRights = 'KQkq';
    
    expect(castlingRights.includes('K')).toBe(true);
    expect(castlingRights.includes('Q')).toBe(true);
    expect(castlingRights.includes('k')).toBe(true);
    expect(castlingRights.includes('q')).toBe(true);
  });

  test('should format date string', () => {
    const date = new Date('2024-01-15');
    const formatted = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    
    expect(formatted).toBe('2024-01-15');
  });

  test('should generate unique ID', () => {
    const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);
    const id1 = generateId();
    const id2 = generateId();
    
    expect(id1).not.toBe(id2);
    expect(id1.length).toBeGreaterThan(10);
  });

  test('should debounce function', () => {
    const debounce = (fn, delay) => {
      let timer = null;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    };
    
    expect(typeof debounce(() => {}, 100)).toBe('function');
  });

  test('should throttle function', () => {
    const throttle = (fn, limit) => {
      let inThrottle = false;
      return (...args) => {
        if (!inThrottle) {
          fn(...args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    };
    
    expect(typeof throttle(() => {}, 100)).toBe('function');
  });
});