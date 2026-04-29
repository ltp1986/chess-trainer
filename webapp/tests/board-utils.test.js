const BoardUtils = require('../js/board-utils');

describe('BoardUtils', () => {
  describe('getSquareName', () => {
    test('should return correct square names', () => {
      expect(BoardUtils.getSquareName(0, 0)).toBe('a1');
      expect(BoardUtils.getSquareName(7, 7)).toBe('h8');
      expect(BoardUtils.getSquareName(3, 4)).toBe('d5');
      expect(BoardUtils.getSquareName(4, 3)).toBe('e4');
    });
  });

  describe('getPieceSymbol', () => {
    test('should return correct piece symbols', () => {
      expect(BoardUtils.getPieceSymbol('K')).toBe('♔');
      expect(BoardUtils.getPieceSymbol('Q')).toBe('♕');
      expect(BoardUtils.getPieceSymbol('R')).toBe('♖');
      expect(BoardUtils.getPieceSymbol('B')).toBe('♗');
      expect(BoardUtils.getPieceSymbol('N')).toBe('♘');
      expect(BoardUtils.getPieceSymbol('P')).toBe('♙');
      expect(BoardUtils.getPieceSymbol('k')).toBe('♚');
      expect(BoardUtils.getPieceSymbol('q')).toBe('♛');
      expect(BoardUtils.getPieceSymbol('r')).toBe('♜');
      expect(BoardUtils.getPieceSymbol('b')).toBe('♝');
      expect(BoardUtils.getPieceSymbol('n')).toBe('♞');
      expect(BoardUtils.getPieceSymbol('p')).toBe('♟');
      expect(BoardUtils.getPieceSymbol('X')).toBe('');
    });
  });

  describe('isLightSquare', () => {
    test('should correctly identify light and dark squares', () => {
      expect(BoardUtils.isLightSquare(0, 0)).toBe(false);   // a1 - dark
      expect(BoardUtils.isLightSquare(1, 0)).toBe(true);   // b1 - light
      expect(BoardUtils.isLightSquare(0, 1)).toBe(true);   // a2 - light
      expect(BoardUtils.isLightSquare(7, 7)).toBe(false);  // h8 - dark
      expect(BoardUtils.isLightSquare(7, 6)).toBe(true);   // h7 - light
    });
  });

  describe('parseFEN', () => {
    test('should parse standard starting position correctly', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const board = BoardUtils.parseFEN(fen);
      
      expect(board['a1']).toBe('R');
      expect(board['h1']).toBe('R');
      expect(board['a8']).toBe('r');
      expect(board['h8']).toBe('r');
      expect(board['e1']).toBe('K');
      expect(board['e8']).toBe('k');
      expect(board['d4']).toBeUndefined();
    });

    test('should parse empty squares correctly', () => {
      const fen = '8/8/8/8/8/8/8/8 w KQkq - 0 1';
      const board = BoardUtils.parseFEN(fen);
      
      expect(Object.keys(board).length).toBe(0);
    });
  });

  describe('getLegalMoves', () => {
    test('should return legal moves for pawn', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e2');

      expect(moves.some(m => m.to === 'e3')).toBe(true);
      expect(moves.some(m => m.to === 'e4')).toBe(true);
    });

    test('should return legal moves for knight', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 3';
      const moves = BoardUtils.getLegalMoves(fen, 'f3');

      expect(moves.some(m => m.to === 'g5')).toBe(true);
      expect(moves.some(m => m.to === 'h4')).toBe(true);
      expect(moves.some(m => m.to === 'd4')).toBe(true);
      expect(moves.some(m => m.to === 'e5')).toBe(true);
    });

    test('should return empty for non-existent piece', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'd4');

      expect(moves).toEqual([]);
    });

    test('should return pawn capture moves', () => {
      const fen = 'rnbqkbnr/pppp1ppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e4');

      expect(moves.some(m => m.to === 'e5')).toBe(true);
    });

    test('should return rook capture moves', () => {
      const fen = '8/8/8/8/8/1r6/R7/8 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'a2');

      expect(moves.length).toBe(14);
      expect(moves.some(m => m.to === 'b2')).toBe(true);
    });

    test('should return sliding piece moves', () => {
      const fen = '8/8/8/8/8/8/R7/8 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'a2');

      expect(moves.length).toBe(14);
    });

    test('should return bishop moves', () => {
      const fen = '8/8/8/8/4B3/8/8/8 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e4');

      expect(moves.length).toBe(13);
    });

    test('should return queen moves', () => {
      const fen = '8/8/8/8/4Q3/8/8/8 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e4');

      expect(moves.length).toBe(27);
    });

    test('should return king moves', () => {
      const fen = '8/8/8/8/4K3/8/8/8 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e4');

      expect(moves.length).toBe(8);
    });

    test('should return black pawn moves', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'e7');

      expect(moves.some(m => m.to === 'e6')).toBe(true);
      expect(moves.some(m => m.to === 'e5')).toBe(true);
    });

    test('should return black piece moves', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'b8');

      expect(moves.some(m => m.to === 'a6')).toBe(true);
      expect(moves.some(m => m.to === 'c6')).toBe(true);
    });

    test('should return pawn double move from starting rank', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'a2');

      expect(moves.some(m => m.to === 'a3' && !m.capture)).toBe(true);
      expect(moves.some(m => m.to === 'a4' && !m.capture)).toBe(true);
    });

    test('should not return blocked pawn moves', () => {
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'd2');

      expect(moves.some(m => m.to === 'd3')).toBe(true);
      expect(moves.some(m => m.to === 'd4')).toBe(true);
    });

    test('should return knight moves at board edge', () => {
      const fen = '8/8/8/8/8/8/8/N7 w KQkq - 0 1';
      const moves = BoardUtils.getLegalMoves(fen, 'a1');

      expect(moves.length).toBe(2);
      expect(moves.some(m => m.to === 'b3')).toBe(true);
      expect(moves.some(m => m.to === 'c2')).toBe(true);
    });
  });

  describe('renderBoard', () => {
    test('should render board correctly', () => {
      const boardElement = { innerHTML: '' };
      const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      
      BoardUtils.renderBoard(boardElement, fen);
      
      expect(boardElement.innerHTML).toContain('chess-square');
      expect(boardElement.innerHTML).toContain('light-square');
      expect(boardElement.innerHTML).toContain('dark-square');
      expect(boardElement.innerHTML).toContain('piece-white');
      expect(boardElement.innerHTML).toContain('piece-black');
    });
    
    test('should render empty board', () => {
      const boardElement = { innerHTML: '' };
      const fen = '8/8/8/8/8/8/8/8 w KQkq - 0 1';
      
      BoardUtils.renderBoard(boardElement, fen);
      
      expect(boardElement.innerHTML).toContain('chess-square');
    });
  });

  describe('validateFEN', () => {
    test('should validate correct FEN', () => {
      const validFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      expect(BoardUtils.validateFEN(validFEN)).toBe(true);
    });

    test('should reject invalid FEN', () => {
      expect(BoardUtils.validateFEN('invalid')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR x KQkq - 0 1')).toBe(false);
    });

    test('should reject FEN with invalid characters', () => {
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')).toBe(true);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq x 0 1')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq-a 0 1')).toBe(false);
    });

    test('should validate en passant square', () => {
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e3 0 1')).toBe(true);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')).toBe(true);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq i9 0 1')).toBe(false);
    });

    test('should validate halfmove and fullmove numbers', () => {
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')).toBe(true);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - abc 1')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 abc')).toBe(false);
      expect(BoardUtils.validateFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0')).toBe(false);
    });
  });
});