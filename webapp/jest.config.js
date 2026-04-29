/**
 * Jest 配置文件 - 简化版
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

  // 跳过覆盖率检查
  collectCoverage: false
};
