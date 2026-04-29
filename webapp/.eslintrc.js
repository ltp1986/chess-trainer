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
    showLoading: 'readonly',
    loadLibraryPage: 'readonly',
    loadPlayersPage: 'readonly',
    loadProfilePage: 'readonly',
    loadPlanPage: 'readonly',
    loadExercisesPage: 'readonly'
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