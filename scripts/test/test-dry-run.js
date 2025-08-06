#!/usr/bin/env node

// Set DRY_RUN explicitly
process.env.DRY_RUN = 'true';

const realExecutor = require('./implementations/nodejs-mvp/services/real-executor');

async function test() {
  console.log('Testing dry run mode...');
  console.log('DRY_RUN env:', process.env.DRY_RUN);
  console.log('isDryRun:', realExecutor.isDryRun);
  
  const result = await realExecutor.execute('install', ['firefox']);
  console.log('Result:', result);
}

test();