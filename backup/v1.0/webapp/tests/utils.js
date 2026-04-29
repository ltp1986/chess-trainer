/**
 * 测试工具函数
 * 提供模拟数据和辅助方法
 */

/**
 * 创建模拟棋盘状态
 */
exports.createMockBoard = () => {
  return {
    onMoveCallback: null,
    setPosition: jest.fn(),
    forceTurn: null,
    highlightMove: jest.fn(),
    setLastMove: jest.fn(),
    getPieceAt: jest.fn(),
    handleSquareClick: jest.fn(),
    clearSelection: jest.fn(),
    fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    board: [
      ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
      ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null, null],
      ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
      ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
  };
};

/**
 * 创建模拟习题数据
 */
exports.createMockExercises = (count = 3) => {
  const exercises = [];
  for (let i = 1; i <= count; i++) {
    exercises.push({
      id: i,
      step: 10 + i * 5,
      fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      turn: 'white',
      best_move: 'e2e4',
      loss: 150 + i * 50,
      description: `第${10 + i * 5}步 - 找出最佳着法`
    });
  }
  return exercises;
};

/**
 * 创建模拟API响应
 */
exports.createMockApiResponse = (type = 'success') => {
  const responses = {
    success: {
      valid: true,
      correct: true,
      message: '✅ 正确！这就是最佳着法。',
      feedback_type: 'success',
      user_move: 'e2e4',
      best_move: 'e2e4',
      delta: 0,
      is_mistake: false,
      score_before: 100,
      score_after: 100
    },
    wrong: {
      valid: true,
      correct: false,
      message: '❌ 失误！这步棋导致局面失分约300分。',
      feedback_type: 'error',
      user_move: 'd2d4',
      best_move: 'e2e4',
      delta: -300,
      is_mistake: true,
      score_before: 100,
      score_after: -200
    },
    invalid: {
      valid: false,
      message: '❌ 非法着法！'
    }
  };
  return responses[type];
};

/**
 * 模拟fetch函数
 */
exports.mockFetch = (response) => {
  global.fetch = jest.fn().mockResolvedValue({
    json: jest.fn().mockResolvedValue(response)
  });
};

/**
 * 模拟DOM环境
 */
exports.mockDOM = () => {
  const mockElement = {
    textContent: '',
    innerHTML: '',
    className: '',
    value: '',
    disabled: false,
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn().mockReturnValue(false)
    },
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    style: {}
  };

  global.document = {
    getElementById: jest.fn().mockReturnValue(mockElement),
    createElement: jest.fn().mockReturnValue({ ...mockElement }),
    querySelector: jest.fn().mockReturnValue(mockElement),
    querySelectorAll: jest.fn().mockReturnValue([])
  };

  global.window = {
    addEventListener: jest.fn()
  };
};

/**
 * 生成随机FEN
 */
exports.generateRandomFEN = () => {
  const pieces = 'rnbqkbnrppppppppPPPPPPPPRNBQKBNR';
  let fen = '';
  
  for (let i = 0; i < 8; i++) {
    let row = '';
    let empty = 0;
    
    for (let j = 0; j < 8; j++) {
      if (Math.random() > 0.5) {
        if (empty > 0) {
          row += empty;
          empty = 0;
        }
        row += pieces[Math.floor(Math.random() * pieces.length)];
      } else {
        empty++;
      }
    }
    
    if (empty > 0) {
      row += empty;
    }
    
    fen += row + '/';
  }
  
  fen = fen.slice(0, -1); // 移除最后一个斜杠
  fen += ' w KQkq - 0 1';
  
  return fen;
};

/**
 * 验证FEN格式
 */
exports.validateFEN = (fen) => {
  const parts = fen.split(' ');
  
  if (parts.length !== 6) return false;
  
  // 检查棋盘部分
  const boardPart = parts[0];
  const rows = boardPart.split('/');
  if (rows.length !== 8) return false;
  
  for (const row of rows) {
    let count = 0;
    for (const char of row) {
      if (/\d/.test(char)) {
        count += parseInt(char);
      } else if (/[rnbqkpRNBQKP]/.test(char)) {
        count++;
      } else {
        return false;
      }
    }
    if (count !== 8) return false;
  }
  
  // 检查回合
  if (!['w', 'b'].includes(parts[1])) return false;
  
  // 检查王车易位
  if (!/^[-KQkq]*$/.test(parts[2])) return false;
  
  return true;
};
