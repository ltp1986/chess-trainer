const { createMockExercises, mockFetch } = require('./utils');

let currentPracticeExercise = null;

describe('Exercises Module Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    currentPracticeExercise = null;
  });

  describe('Exercise Data Handling', () => {
    test('should generate mock exercises correctly', () => {
      const exercises = createMockExercises(3);
      
      expect(exercises).toHaveLength(3);
      exercises.forEach((ex, index) => {
        expect(ex).toHaveProperty('id', index + 1);
        expect(ex).toHaveProperty('fen');
        expect(ex).toHaveProperty('best_move');
        expect(ex).toHaveProperty('loss');
      });
    });

    test('should validate FEN format', () => {
      const validFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const invalidFEN = 'invalid/fen/format';
      
      expect(validateFEN(validFEN)).toBe(true);
      expect(validateFEN(invalidFEN)).toBe(false);
    });
  });

  describe('Board Initialization', () => {
    test('should get correct square name', () => {
      expect(getSquareName(0, 0)).toBe('a1');
      expect(getSquareName(7, 7)).toBe('h8');
      expect(getSquareName(3, 4)).toBe('d5');
      expect(getSquareName(4, 3)).toBe('e4');
    });

    test('should convert piece characters to symbols', () => {
      expect(getPieceSymbol('K')).toBe('♔');
      expect(getPieceSymbol('Q')).toBe('♕');
      expect(getPieceSymbol('R')).toBe('♖');
      expect(getPieceSymbol('B')).toBe('♗');
      expect(getPieceSymbol('N')).toBe('♘');
      expect(getPieceSymbol('P')).toBe('♙');
      expect(getPieceSymbol('k')).toBe('♚');
      expect(getPieceSymbol('q')).toBe('♛');
      expect(getPieceSymbol('r')).toBe('♜');
      expect(getPieceSymbol('b')).toBe('♝');
      expect(getPieceSymbol('n')).toBe('♞');
      expect(getPieceSymbol('p')).toBe('♟');
      expect(getPieceSymbol('X')).toBe('');
    });
  });

  describe('Move Validation', () => {
    test('should check correct move', () => {
      currentPracticeExercise = {
        id: 1,
        best_move: 'e2e4',
        filename: 'test.pgn',
        move_number: 1,
        loss: 150,
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
      };

      const mockFeedback = { innerHTML: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-feedback') return mockFeedback;
        return originalGetElementById.call(document, id);
      });

      checkMove('e2e4');

      expect(mockFeedback.innerHTML).toContain('正确');
      document.getElementById = originalGetElementById;
    });

    test('should check incorrect move', () => {
      currentPracticeExercise = {
        id: 1,
        best_move: 'e2e4',
        filename: 'test.pgn',
        move_number: 1,
        loss: 150,
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
      };

      const mockFeedback = { innerHTML: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-feedback') return mockFeedback;
        return originalGetElementById.call(document, id);
      });

      checkMove('d2d4');

      expect(mockFeedback.innerHTML).toContain('错误');
      document.getElementById = originalGetElementById;
    });

    test('should not check move without exercise', () => {
      currentPracticeExercise = null;

      const mockFeedback = { innerHTML: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-feedback') return mockFeedback;
        return originalGetElementById.call(document, id);
      });

      checkMove('e2e4');

      expect(mockFeedback.innerHTML).toBe('');
      document.getElementById = originalGetElementById;
    });
  });

  describe('Hint and Answer Display', () => {
    test('should show hint', () => {
      currentPracticeExercise = {
        id: 1,
        best_move: 'e2e4',
        filename: 'test.pgn',
        move_number: 1,
        loss: 150,
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
      };

      const mockHintElement = { textContent: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-hint-text') return mockHintElement;
        return originalGetElementById.call(document, id);
      });

      showPracticeHint();

      expect(mockHintElement.textContent).toContain('e2');
      expect(mockHintElement.textContent).toContain('e4');
      document.getElementById = originalGetElementById;
    });

    test('should show answer', () => {
      currentPracticeExercise = {
        id: 1,
        best_move: 'e2e4',
        filename: 'test.pgn',
        move_number: 1,
        loss: 150,
        fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
      };

      const mockFeedback = { innerHTML: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-feedback') return mockFeedback;
        return originalGetElementById.call(document, id);
      });

      showPracticeAnswer();

      expect(mockFeedback.innerHTML).toContain('e2e4');
      document.getElementById = originalGetElementById;
    });

    test('should not show hint without exercise', () => {
      currentPracticeExercise = null;

      const mockHintElement = { textContent: 'original text' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-hint-text') return mockHintElement;
        return originalGetElementById.call(document, id);
      });

      showPracticeHint();

      expect(mockHintElement.textContent).toBe('original text');
      document.getElementById = originalGetElementById;
    });

    test('should not show answer without exercise', () => {
      currentPracticeExercise = null;

      const mockFeedback = { innerHTML: '' };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'practice-feedback') return mockFeedback;
        return originalGetElementById.call(document, id);
      });

      showPracticeAnswer();

      expect(mockFeedback.innerHTML).toBe('');
      document.getElementById = originalGetElementById;
    });
  });

  describe('Modal Operations', () => {
    test('should open exercise modal', () => {
      const mockModal = {
        classList: {
          remove: jest.fn(),
          contains: jest.fn().mockReturnValue(false)
        }
      };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'exercise-modal') return mockModal;
        return originalGetElementById.call(document, id);
      });

      openExerciseModal();

      expect(mockModal.classList.remove).toHaveBeenCalledWith('hidden');
      expect(document.body.style.overflow).toBe('hidden');
      document.getElementById = originalGetElementById;
    });

    test('should close exercise modal', () => {
      const mockModal = {
        classList: {
          add: jest.fn(),
          contains: jest.fn().mockReturnValue(true)
        }
      };
      const originalGetElementById = document.getElementById;
      document.getElementById = jest.fn((id) => {
        if (id === 'exercise-modal') return mockModal;
        return originalGetElementById.call(document, id);
      });

      closeExerciseModal();

      expect(mockModal.classList.add).toHaveBeenCalledWith('hidden');
      expect(document.body.style.overflow).toBe('');
      expect(currentPracticeExercise).toBe(null);
      document.getElementById = originalGetElementById;
    });
  });

  describe('API Integration', () => {
    test('should fetch player exercises', async () => {
      const mockExercises = createMockExercises(5);
      mockFetch({
        exercises: mockExercises,
        player_id: 'test_player',
        player_name: 'Test Player'
      });

      const data = await apiCall('/api/exercises/player/test_player');

      expect(data.exercises).toHaveLength(5);
      expect(data.player_id).toBe('test_player');
      expect(data.player_name).toBe('Test Player');
    });

    test('should update exercise status', async () => {
      mockFetch({
        status: 'success',
        message: '练习状态已更新'
      });

      const response = await apiCall(
        '/api/exercises/update/test_player',
        { exercise_id: 1, status: 'completed' },
        'POST'
      );

      expect(response.status).toBe('success');
      expect(response.message).toBe('练习状态已更新');
    });
  });
});

function getSquareName(col, row) {
  const files = 'abcdefgh';
  return files[col] + (row + 1);
}

function getPieceSymbol(piece) {
  const symbols = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
  };
  return symbols[piece] || '';
}

function validateFEN(fen) {
  const parts = fen.split(' ');
  if (parts.length !== 6) return false;

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

  if (!['w', 'b'].includes(parts[1])) return false;
  if (!/^[-KQkq]*$/.test(parts[2])) return false;

  return true;
}

async function apiCall(url, body = {}, method = 'GET') {
  const options = {
    method: method,
    headers: { 'Content-Type': 'application/json' }
  };

  if (method !== 'GET' && Object.keys(body).length > 0) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  return response.json();
}

function openExerciseModal() {
  const modal = document.getElementById('exercise-modal');
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function closeExerciseModal() {
  const modal = document.getElementById('exercise-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
  currentPracticeExercise = null;
}

function checkMove(move) {
  if (!currentPracticeExercise) return;

  const bestMove = currentPracticeExercise.best_move;
  const feedback = document.getElementById('practice-feedback');

  if (!feedback) return;

  if (move === bestMove) {
    feedback.innerHTML = '<div><p class="text-green-600">✅ 正确！太棒了！</p></div>';
  } else {
    feedback.innerHTML = '<div><p class="text-red-600">❌ 错误！再试试吧！</p></div>';
  }
}

function showPracticeHint() {
  if (!currentPracticeExercise) return;

  const bestMove = currentPracticeExercise.best_move;
  const fromSquare = bestMove.substring(0, 2);
  const toSquare = bestMove.substring(2, 4);

  const hint = `提示：从 ${fromSquare} 移动到 ${toSquare} 附近`;
  const hintElement = document.getElementById('practice-hint-text');
  if (hintElement) {
    hintElement.textContent = hint;
  }
}

function showPracticeAnswer() {
  if (!currentPracticeExercise) return;

  const bestMove = currentPracticeExercise.best_move;
  const feedback = document.getElementById('practice-feedback');
  if (feedback) {
    feedback.innerHTML = `<div><p>✅ 正确答案: ${bestMove}</p></div>`;
  }
}