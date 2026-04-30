const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function runTests() {
  const testResults = [];
  const testResultsDir = path.join(__dirname, 'test-results');
  
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
  }
  
  const jestProcess = spawn('npx', ['jest', '--testPathPattern', 'tests/', '--passWithNoTests'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe'],
    shell: true
  });
  
  let stdout = '';
  let stderr = '';
  
  jestProcess.stdout.on('data', (data) => {
    stdout += data.toString();
  });
  
  jestProcess.stderr.on('data', (data) => {
    stderr += data.toString();
  });
  
  return new Promise((resolve, reject) => {
    jestProcess.on('close', (code) => {
      const results = parseJestOutput(stdout, stderr);
      
      const report = {
        timestamp: new Date().toISOString(),
        exitCode: code,
        total: results.total,
        passed: results.passed,
        failed: results.failed,
        errors: results.errors,
        failures: results.failures,
        stdout: stdout,
        stderr: stderr
      };
      
      const outputPath = path.join(testResultsDir, 'test-results.json');
      fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
      
      console.log(`测试报告已生成: ${outputPath}`);
      console.log(`总计: ${results.total}, 通过: ${results.passed}, 失败: ${results.failed}`);
      
      resolve(report);
    });
  });
}

function parseJestOutput(stdout, stderr) {
  const results = {
    total: 0,
    passed: 0,
    failed: 0,
    errors: [],
    failures: []
  };
  
  const output = stdout + '\n' + stderr;
  
  const summaryMatch = output.match(/Tests:\s*(\d+) failed,\s*(\d+) passed/);
  if (summaryMatch) {
    results.failed = parseInt(summaryMatch[1]);
    results.passed = parseInt(summaryMatch[2]);
    results.total = results.passed + results.failed;
  } else {
    const altMatch = output.match(/(\d+) passed, (\d+) failed/);
    if (altMatch) {
      results.passed = parseInt(altMatch[1]);
      results.failed = parseInt(altMatch[2]);
      results.total = results.passed + results.failed;
    }
  }
  
  const failBlocks = output.split('FAIL ');
  for (let i = 1; i < failBlocks.length; i++) {
    const block = failBlocks[i];
    const fileMatch = block.match(/^(.+?\.test\.js)/);
    const file = fileMatch ? fileMatch[1] : '';
    
    const testLines = block.split('\n');
    let inTestSection = false;
    
    for (let j = 0; j < testLines.length; j++) {
      const line = testLines[j];
      
      if (line.includes('Tests:')) {
        break;
      }
      
      const firstChar = line.trim().charAt(0);
      if (firstChar === '✓' || firstChar === '✕' || firstChar === '×' ||
          firstChar === '\u2714' || firstChar === '\u2718' || firstChar === '\u00d7' ||
          firstChar === '\u2716') {
        
        const testName = line.trim().substring(1).trim();
        if (testName) {
          const isFailed = firstChar === '\u2718' || firstChar === '\u2716' || 
                          firstChar === '✕' || firstChar === '×' || firstChar === '\u00d7';
          
          if (isFailed) {
            results.failures.push({
              name: testName,
              status: 'failed',
              error: 'Test failed',
              traceback: '',
              file: file
            });
          }
        }
      }
    }
  }
  
  return results;
}

runTests().then((report) => {
  process.exit(report.exitCode);
}).catch((error) => {
  console.error('测试运行失败:', error);
  process.exit(1);
});