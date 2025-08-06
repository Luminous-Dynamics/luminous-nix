#!/usr/bin/env node

/**
 * Demo script showcasing NLP capabilities
 */

const { spawn } = require('child_process');

console.log('🎯 Nix for Humanity - NLP Demo\n');
console.log('Demonstrating natural language understanding with 50+ patterns\n');

// Demo commands to test
const demoCommands = [
  // Package management variations
  "install firefox",
  "i need a text editor",
  "get me nodejs",
  "vim is missing",
  "get rid of old packages",
  "search for browser",
  
  // System commands
  "update my system",
  "what version am i running?",
  
  // Network
  "my wifi isn't working",
  "fix my internet",
  
  // Services
  "start nginx",
  "is postgresql running?",
  
  // Help
  "help"
];

// Run the demo
const nix = spawn('node', ['nix-humanity-unified.js', '--dry-run'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let currentIndex = 0;

// Send commands one by one
function sendNextCommand() {
  if (currentIndex < demoCommands.length) {
    const cmd = demoCommands[currentIndex];
    console.log(`\n👤 User: "${cmd}"`);
    nix.stdin.write(cmd + '\n');
    currentIndex++;
    
    // Wait a bit before next command
    setTimeout(sendNextCommand, 2000);
  } else {
    // Exit after all commands
    nix.stdin.write('exit\n');
  }
}

// Capture and display output
let buffer = '';
nix.stdout.on('data', (data) => {
  buffer += data.toString();
  const lines = buffer.split('\n');
  
  // Process complete lines
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i];
    if (line.includes('Understanding:') || 
        line.includes('✅') || 
        line.includes('❌') ||
        line.includes('Would execute:')) {
      console.log('🤖 Nix:', line.trim());
    }
  }
  
  // Keep the incomplete line in buffer
  buffer = lines[lines.length - 1];
});

nix.on('close', (code) => {
  console.log('\n✨ Demo complete!');
  console.log('\nKey features demonstrated:');
  console.log('- Natural language variations');
  console.log('- Context understanding');
  console.log('- Entity extraction');
  console.log('- Helpful error messages');
  console.log('- 50+ command patterns');
});

// Start the demo after initial output
setTimeout(sendNextCommand, 1000);