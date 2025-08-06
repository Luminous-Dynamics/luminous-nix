#!/usr/bin/env node

/**
 * Test script for NLP pattern coverage
 * Tests all 50+ natural language patterns
 */

const { patterns, matchPattern } = require('./src/nlp/quick-start-patterns');

// Test cases organized by category
const testCases = {
  'Package Management': [
    // Install variations
    { input: 'install firefox', expected: 'package.install' },
    { input: 'add chrome', expected: 'package.install' },
    { input: 'i need vim', expected: 'package.install' },
    { input: 'get me nodejs', expected: 'package.install' },
    { input: 'python is missing', expected: 'package.install' },
    
    // Remove variations
    { input: 'remove firefox', expected: 'package.remove' },
    { input: 'uninstall chrome', expected: 'package.remove' },
    { input: 'get rid of vim', expected: 'package.remove' },
    { input: 'delete nodejs', expected: 'package.remove' },
    
    // Search variations
    { input: 'search for browser', expected: 'package.search' },
    { input: 'find text editor', expected: 'package.search' },
    { input: 'what is htop', expected: 'package.search' },
    { input: 'show me terminal packages', expected: 'package.search' }
  ],
  
  'System Management': [
    // Update variations
    { input: 'update system', expected: 'system.update' },
    { input: 'upgrade everything', expected: 'system.update' },
    { input: 'run updates', expected: 'system.update' },
    
    // Info variations
    { input: 'system info', expected: 'system.info' },
    { input: 'what version am i running', expected: 'system.info' },
    { input: 'show system', expected: 'system.info' }
  ],
  
  'Network': [
    // WiFi variations
    { input: 'wifi not working', expected: 'network.wifi' },
    { input: 'connect to wifi', expected: 'network.wifi' },
    { input: 'internet not working', expected: 'network.wifi' },
    { input: 'fix my network', expected: 'network.wifi' }
  ],
  
  'Services': [
    // Start variations
    { input: 'start nginx', expected: 'service.start' },
    { input: 'enable ssh', expected: 'service.start' },
    { input: 'start docker service', expected: 'service.start' },
    
    // Stop variations
    { input: 'stop nginx', expected: 'service.stop' },
    { input: 'disable ssh', expected: 'service.stop' },
    { input: 'stop docker service', expected: 'service.stop' },
    
    // Status variations
    { input: 'is nginx running', expected: 'service.status' },
    { input: 'check if ssh is running', expected: 'service.status' },
    { input: 'status of docker', expected: 'service.status' }
  ]
};

// Run tests
console.log('🧪 Testing NLP Pattern Coverage\n');

let totalTests = 0;
let passedTests = 0;
let failedTests = [];

for (const [category, tests] of Object.entries(testCases)) {
  console.log(`\n📋 ${category}:`);
  
  for (const test of tests) {
    totalTests++;
    const result = matchPattern(test.input);
    
    if (result && result.intent === test.expected) {
      console.log(`  ✅ "${test.input}" → ${test.expected}`);
      passedTests++;
    } else {
      const actual = result ? result.intent : 'no match';
      console.log(`  ❌ "${test.input}" → expected ${test.expected}, got ${actual}`);
      failedTests.push({ ...test, actual });
    }
  }
}

// Summary
console.log('\n' + '='.repeat(50));
console.log(`\n📊 Test Summary:`);
console.log(`   Total Tests: ${totalTests}`);
console.log(`   Passed: ${passedTests} (${Math.round(passedTests/totalTests*100)}%)`);
console.log(`   Failed: ${failedTests.length} (${Math.round(failedTests.length/totalTests*100)}%)`);

if (failedTests.length > 0) {
  console.log(`\n❌ Failed Tests:`);
  failedTests.forEach(test => {
    console.log(`   "${test.input}" - expected ${test.expected}, got ${test.actual}`);
  });
}

console.log(`\n✨ Coverage: ${Math.round(passedTests/totalTests*100)}% of patterns working`);

// Test entity extraction
console.log('\n🔍 Testing Entity Extraction:');
const entityTests = [
  'install firefox',
  'remove the vim package',
  'start nginx service',
  'is postgresql running'
];

for (const test of entityTests) {
  const result = matchPattern(test);
  if (result && result.entities) {
    console.log(`   "${test}" → ${JSON.stringify(result.entities)}`);
  }
}

// Exit with appropriate code
process.exit(failedTests.length > 0 ? 1 : 0);