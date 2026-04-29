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
  });
});