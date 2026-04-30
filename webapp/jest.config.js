/**
 * Jest 配置文件
 */

module.exports = {
  // 测试文件匹配模式
  testMatch: [
    '**/tests/**/*.test.js'
  ],

  // 测试环境
  testEnvironment: 'jsdom',

  // 模块文件扩展名
  moduleFileExtensions: ['js', 'json'],

  // 显示测试结果
  verbose: true,

  // 测试超时时间
  testTimeout: 30000,

  // 报告器配置 - 生成 JSON 格式报告
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'test-results',
        outputName: 'junit-results.xml',
        suiteName: 'chess-trainer-tests',
        includeConsoleOutput: true
      }
    ]
  ],

  // 覆盖率配置
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['json', 'lcov', 'text']
};
