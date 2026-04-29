const BoardUtils = {
  files: 'abcdefgh',
  
  getSquareName(col, row) {
    return this.files[col] + (row + 1);
  },

  getPieceSymbol(piece) {
    const symbols = {
      'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
      'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    };
    return symbols[piece] || '';
  },

  isLightSquare(col, row) {
    return (row + col) % 2 === 1;
  },

  parseFEN(fen) {
    const board = {};
    const parts = fen.split(' ')[0];
    const rows = parts.split('/');
    
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      let col = 0;
      for (const char of row) {
        if (char >= '1' && char <= '8') {
          col += parseInt(char);
        } else {
          const square = this.files[col] + (8 - i);
          board[square] = char;
          col++;
        }
      }
    }
    return board;
  },

  renderBoard(boardElement, fen, options = {}) {
    const board = this.parseFEN(fen);
    let html = '';
    
    for (let row = 7; row >= 0; row--) {
      for (let col = 0; col < 8; col++) {
        const squareName = this.getSquareName(col, row);
        const isLight = this.isLightSquare(col, row);
        const piece = board[squareName];
        
        let pieceHtml = '';
        if (piece) {
          const isWhite = piece === piece.toUpperCase();
          pieceHtml = `<span class="chess-piece ${isWhite ? 'piece-white' : 'piece-black'}">${this.getPieceSymbol(piece)}</span>`;
        }
        
        html += `
          <div class="chess-square ${isLight ? 'light-square' : 'dark-square'}" 
               data-square="${squareName}">
            ${pieceHtml}
          </div>
        `;
      }
    }
    
    boardElement.innerHTML = html;
  },

  validateFEN(fen) {
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
    if (!/^(-|[KQkq]+)$/.test(parts[2])) return false;
    if (!/^(-|[a-h][1-8])$/.test(parts[3])) return false;
    if (!/^\d+$/.test(parts[4])) return false;
    if (!/^\d+$/.test(parts[5]) || parseInt(parts[5]) < 1) return false;

    return true;
  },

  getLegalMoves(fen, fromSquare) {
    const moves = [];
    const board = this.parseFEN(fen);
    const piece = board[fromSquare];
    
    if (!piece) return moves;
    
    const isWhite = piece === piece.toUpperCase();
    const pieceType = piece.toUpperCase();
    
    const fileIndex = this.files.indexOf(fromSquare[0]);
    const rank = parseInt(fromSquare[1]);
    
    if (pieceType === 'P') {
      const direction = isWhite ? 1 : -1;
      
      if (rank + direction >= 1 && rank + direction <= 8) {
        const singleMove = this.files[fileIndex] + (rank + direction);
        if (!board[singleMove]) {
          moves.push({ to: singleMove, capture: false });
          
          if ((isWhite && rank === 2) || (!isWhite && rank === 7)) {
            const doubleMove = this.files[fileIndex] + (rank + 2 * direction);
            if (!board[doubleMove]) {
              moves.push({ to: doubleMove, capture: false });
            }
          }
        }
      }
      
      for (const dx of [-1, 1]) {
        const newFileIndex = fileIndex + dx;
        const newRank = rank + direction;
        if (newFileIndex >= 0 && newFileIndex < 8 && newRank >= 1 && newRank <= 8) {
          const captureSquare = this.files[newFileIndex] + newRank;
          const targetPiece = board[captureSquare];
          if (targetPiece) {
            const targetIsWhite = targetPiece === targetPiece.toUpperCase();
            if (targetIsWhite !== isWhite) {
              moves.push({ to: captureSquare, capture: true });
            }
          }
        }
      }
    } else {
      const directions = {
        'N': [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]],
        'B': [[-1, -1], [-1, 1], [1, -1], [1, 1]],
        'R': [[-1, 0], [1, 0], [0, -1], [0, 1]],
        'Q': [[-1, -1], [-1, 1], [1, -1], [1, 1], [-1, 0], [1, 0], [0, -1], [0, 1]],
        'K': [[-1, -1], [-1, 1], [1, -1], [1, 1], [-1, 0], [1, 0], [0, -1], [0, 1]]
      };
      
      const dirs = directions[pieceType] || [];
      
      dirs.forEach(([dx, dy]) => {
        let newFileIndex = fileIndex + dx;
        let newRank = rank + dy;
        
        while (newFileIndex >= 0 && newFileIndex < 8 && newRank >= 1 && newRank <= 8) {
          const toSquare = this.files[newFileIndex] + newRank;
          const targetPiece = board[toSquare];
          
          if (!targetPiece) {
            moves.push({ to: toSquare, capture: false });
          } else {
            const targetIsWhite = targetPiece === targetPiece.toUpperCase();
            if (targetIsWhite !== isWhite) {
              moves.push({ to: toSquare, capture: true });
            }
            break;
          }
          
          if (pieceType === 'N' || pieceType === 'K') break;
          
          newFileIndex += dx;
          newRank += dy;
        }
      });
    }
    
    return moves;
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = BoardUtils;
}