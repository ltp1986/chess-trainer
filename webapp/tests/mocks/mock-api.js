const mockExercises = [
  {
    id: 1,
    step: 15,
    fen: 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 8',
    turn: 'black',
    best_move: 'd7d5',
    loss: 250,
    actual_move: 'g8f6',
    description: '第15步 - 找出最佳着法'
  },
  {
    id: 2,
    step: 23,
    fen: 'rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 12',
    turn: 'white',
    best_move: 'e2e4',
    loss: 180,
    actual_move: 'g1f3',
    description: '第23步 - 找出最佳着法'
  }
];

const mockPGNFiles = [
  { name: 'senserobot VS 棋手1.pgn', size: 1024, date: '2024-01-15' },
  { name: 'senserobot VS 棋手2.pgn', size: 2048, date: '2024-01-16' }
];

const mockAnalysisResult = {
  status: 'completed',
  filename: 'senserobot VS 棋手1.pgn',
  white: 'senserobot',
  black: '棋手1',
  result: '1-0',
  difficulty: 'medium',
  total_mistakes: 5,
  filtered_mistakes: 3,
  mistakes: [
    {
      step: 15,
      loss: 250,
      fen: 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 8',
      turn: 'black',
      actual_move: 'g8f6',
      best_move: 'd7d5',
      cause: '错误的开局选择',
      idea: '应该选择d7d5控制中心',
      tactic_exp: '中心控制战术'
    }
  ],
  exercises: mockExercises
};

const mockLegalMoves = [
  { from: 'e2', to: 'e3', capture: false },
  { from: 'e2', to: 'e4', capture: false },
  { from: 'g1', to: 'f3', capture: false },
  { from: 'b1', to: 'c3', capture: false }
];

const MockAPI = {
  getPGNFiles: () => ({ files: mockPGNFiles }),
  
  analyzePGN: (filename) => {
    if (!filename || filename.trim() === '') {
      return { status: 'error', message: '文件名不能为空' };
    }
    if (filename.includes('senserobot')) {
      return mockAnalysisResult;
    }
    return { status: 'error', message: 'File not found' };
  },
  
  checkMove: (moveData) => {
    const { fen, move, best_move } = moveData;
    
    if (!fen || !move) {
      return {
        is_correct: false,
        best_move: best_move || 'e2e4',
        explanation: '参数无效'
      };
    }
    
    return {
      is_correct: move === best_move,
      best_move: best_move,
      explanation: move === best_move ? '正确！这是最佳着法' : '不正确，请再试一次'
    };
  },
  
  getLegalMoves: (fenData) => {
    const { fen } = fenData;
    if (!fen) {
      return { moves: [] };
    }
    return { moves: mockLegalMoves };
  },
  
  getBestMove: (fenData) => ({ 
    best_move: 'e2e4', 
    explanation: '这是当前局面的最佳着法' 
  }),
  
  getHint: (fenData) => ({ 
    hint: '考虑控制中心', 
    piece: 'e2' 
  }),
  
  getPlayers: () => ({
    players: [
      { id: 1, name: '张三', level: '初级', rating: 1200 },
      { id: 2, name: '李四', level: '中级', rating: 1600 }
    ]
  }),
  
  getPlayerExercises: (playerId) => ({ 
    exercises: mockExercises,
    player_id: playerId,
    total_count: mockExercises.length,
    completed_count: 0
  }),
  
  getPlayerStats: (playerId) => ({
    player_id: playerId,
    total_games: 15,
    wins: 8,
    losses: 5,
    draws: 2,
    avg_rating: 1400,
    best_rating: 1550,
    worst_rating: 1250
  }),
  
  getTrainingProgress: () => ({
    today_exercises: 5,
    weekly_exercises: 23,
    monthly_exercises: 89,
    streak: 7,
    total_completed: 320
  }),
  
  getTrainingPlan: () => ({
    plan: [
      { day: 1, focus: '开局训练', exercises: 5 },
      { day: 2, focus: '中局战术', exercises: 8 },
      { day: 3, focus: '残局练习', exercises: 6 }
    ],
    duration: 7,
    total_exercises: 42
  })
};

module.exports = MockAPI;