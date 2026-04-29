module.exports = {
  env: {
    browser: true,
    es2021: true,
    jest: true,
    node: true
  },
  extends: 'eslint:recommended',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  globals: {
    apiCall: 'readonly',
    Chess: 'readonly',
    Validator: 'readonly',
    ChessTrainer: 'readonly',
    showLoading: 'readonly',
    loadLibraryPage: 'readonly',
    loadPlayersPage: 'readonly',
    loadProfilePage: 'readonly',
    loadPlanPage: 'readonly',
    loadExercisesPage: 'readonly',
    initNavigation: 'readonly',
    showAddGameModal: 'readonly',
    addDemoGame: 'readonly',
    deleteGame: 'readonly',
    editGameAssociation: 'readonly',
    showAddPlayerModal: 'readonly',
    openEditModal: 'readonly',
    deletePlayer: 'readonly',
    generateProfileForPlayer: 'readonly',
    generateProfile: 'readonly',
    generatePlan: 'readonly',
    toggleTask: 'readonly',
    generateExercises: 'readonly',
    practiceExercise: 'readonly',
    getWatchDir: 'readonly',
    setWatchDir: 'readonly',
    loadPgnFiles: 'readonly',
    fs: 'readonly',
    path: 'readonly',
    process: 'readonly',
    wasHidden: 'readonly'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'off',
    'no-debugger': 'warn'
  },
  ignorePatterns: [
    'coverage/',
    'node_modules/',
    'backup/'
  ]
};