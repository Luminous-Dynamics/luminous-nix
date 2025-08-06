#!/usr/bin/env node

// Quick script to fix the execution path
const fs = require('fs');
const path = require('path');

console.log('🔧 Fixing Nix for Humanity execution path...\n');

// 1. Update executor.js to use real executor
const executorPath = path.join(__dirname, 'implementations/nodejs-mvp/services/executor.js');
if (fs.existsSync(executorPath)) {
  let content = fs.readFileSync(executorPath, 'utf8');
  
  // Replace mock with real
  content = content.replace(
    /const\s+MOCK_COMMANDS\s*=\s*process\.env\.MOCK_COMMANDS\s*!==\s*'false';/,
    "const MOCK_COMMANDS = process.env.MOCK_COMMANDS === 'true'; // Changed default to REAL"
  );
  
  // Add real executor import
  if (!content.includes('real-executor')) {
    content = "const realExecutor = require('./real-executor');\n" + content;
  }
  
  fs.writeFileSync(executorPath, content);
  console.log('✅ Updated executor.js to default to real execution');
}

// 2. Create a simple test script
const testScript = `#!/usr/bin/env node
const executor = require('./implementations/nodejs-mvp/services/real-executor');

async function test() {
  console.log('🧪 Testing real NixOS execution:\\n');
  
  // Test search (safe command)
  console.log('1. Testing search...');
  const result = await executor.execute('search', ['firefox']);
  console.log(result.success ? '✅ Search works!' : '❌ Search failed:', result.error);
  
  // Test with dry run
  process.env.DRY_RUN = 'true';
  console.log('\\n2. Testing install (dry run)...');
  const dryResult = await executor.execute('install', ['firefox']);
  console.log(dryResult.output);
}

test().catch(console.error);
`;

fs.writeFileSync(path.join(__dirname, 'test-real-execution.js'), testScript);
fs.chmodSync(path.join(__dirname, 'test-real-execution.js'), '755');

console.log('✅ Created test-real-execution.js');
console.log('\n📋 Next steps:');
console.log('1. Run: ./test-real-execution.js');
console.log('2. If it works, update the main server to use real executor');
console.log('3. Remove all MOCK_COMMANDS=true from your environment');
console.log('\n🎯 Remember: Start with DRY_RUN=true for safety!');