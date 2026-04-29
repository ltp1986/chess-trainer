const { spawn } = require('child_process');
const fs = require('fs');

const runCommand = (command, args, cwd) => {
  return new Promise((resolve, reject) => {
    const process = spawn(command, args, { cwd, stdio: 'inherit' });
    
    process.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    process.on('error', (err) => {
      reject(err);
    });
  });
};

const main = async () => {
  console.log('🚀 开始执行测试套件...\n');
  
  try {
    console.log('🔍 1/5 - 运行 lint 检查');
    await runCommand('npx', ['eslint', '.'], './webapp');
    console.log('✅ lint 检查通过\n');
    
    console.log('🧪 2/5 - 运行单元测试');
    await runCommand('npx', ['jest', '--testPathPattern', 'unit'], './webapp');
    console.log('✅ 单元测试通过\n');
    
    console.log('🧪 3/5 - 运行集成测试');
    await runCommand('npx', ['jest', '--testPathPattern', 'integration'], './webapp');
    console.log('✅ 集成测试通过\n');
    
    console.log('🧪 4/5 - 运行API测试');
    await runCommand('npx', ['jest', '--testPathPattern', 'api'], './webapp');
    console.log('✅ API测试通过\n');
    
    console.log('🧪 5/5 - 运行棋盘工具测试');
    await runCommand('npx', ['jest', '--testPathPattern', 'board-utils'], './webapp');
    console.log('✅ 棋盘工具测试通过\n');
    
    console.log('🎉 所有测试通过！');
    process.exit(0);
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    process.exit(1);
  }
};

main();