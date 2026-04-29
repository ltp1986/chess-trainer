const { spawn } = require('child_process');
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

let serverProcess = null;

async function waitForServer() {
  for (let i = 0; i < 30; i++) {
    try {
      await axios.get(`${BASE_URL}/api/pgn_files`);
      console.log('✅ 服务器启动成功');
      return true;
    } catch (error) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  console.error('❌ 服务器启动超时');
  return false;
}

async function startServer() {
  console.log('🚀 启动测试服务器...');
  
  serverProcess = spawn('python', ['app.py'], {
    cwd: __dirname,
    stdio: 'inherit'
  });
  
  serverProcess.on('error', (err) => {
    console.error('❌ 启动服务器失败:', err);
    process.exit(1);
  });
  
  serverProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`❌ 服务器异常退出，代码: ${code}`);
    }
  });
  
  return await waitForServer();
}

async function runTests() {
  const { spawnSync } = require('child_process');
  
  console.log('🧪 运行测试...');
  const result = spawnSync('npx', ['jest', '--testPathPattern', 'integration'], {
    cwd: __dirname,
    stdio: 'inherit'
  });
  
  return result.status === 0;
}

async function main() {
  try {
    const serverStarted = await startServer();
    if (!serverStarted) {
      process.exit(1);
    }
    
    const testsPassed = await runTests();
    
    if (serverProcess) {
      console.log('🛑 停止测试服务器...');
      serverProcess.kill();
    }
    
    process.exit(testsPassed ? 0 : 1);
  } catch (error) {
    console.error('❌ 测试过程出错:', error);
    if (serverProcess) {
      serverProcess.kill();
    }
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { startServer, waitForServer };