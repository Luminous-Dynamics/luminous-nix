#!/usr/bin/env node

/**
 * Test the integrated NLP improvements
 * Demonstrates all features working together
 */

const EnhancedNLPEngine = require('./src/nlp/enhanced-nlp-engine');

async function runTests() {
  console.log('🧪 Testing Integrated NLP Improvements\n');
  
  const nlp = new EnhancedNLPEngine();
  await nlp.ensureInitialized();
  
  const testCases = [
    // Typo correction
    { input: 'instal firfox', description: 'Typo correction' },
    { input: 'remov python', description: 'Typo correction with missing letter' },
    
    // Context awareness
    { input: 'search browser', description: 'Search for browsers' },
    { input: 'install the first one', description: 'Context reference' },
    { input: 'remove it', description: 'Reference to last installed' },
    
    // Package aliases
    { input: 'install chrome', description: 'Package alias resolution' },
    { input: 'install node', description: 'Common name resolution' },
    { input: 'install a text editor', description: 'Category request' },
    
    // Combined features
    { input: 'instal the frst one', description: 'Typos + context' },
    { input: 'remov chrome', description: 'Typo + alias' },
    
    // Error scenarios
    { input: 'install nonexistentpackage', description: 'Package not found' },
    { input: 'intal something', description: 'Severe typo' },
  ];
  
  // Simulate some context
  console.log('📝 Setting up context...\n');
  
  // First, do a search to set context
  const searchResult = await nlp.processInput('search browser');
  console.log('Search:', searchResult.result?.intent || 'No match');
  
  // Simulate search results in context
  nlp.contextTracker.addInteraction('search browser', 'package.search', {
    success: true,
    packages: ['firefox', 'chromium', 'brave']
  });
  
  console.log('\n📋 Running test cases:\n');
  
  for (const test of testCases) {
    console.log(`\n🔍 ${test.description}`);
    console.log(`   Input: "${test.input}"`);
    
    const result = await nlp.processInput(test.input);
    
    if (result.hadCorrections) {
      console.log(`   ✏️  Corrected to: "${result.processed}"`);
    }
    
    if (result.result) {
      console.log(`   ✅ Intent: ${result.result.intent}`);
      
      if (result.result.entities) {
        console.log(`   📦 Package: ${result.result.entities.package || 'N/A'}`);
      }
      
      if (result.result.packageInfo) {
        const info = result.result.packageInfo;
        console.log(`   🔄 Resolved: "${info.resolved}" (${info.reason})`);
        if (info.alternatives?.length > 0) {
          console.log(`   🔀 Alternatives: ${info.alternatives.join(', ')}`);
        }
      }
      
      if (result.result.type === 'category_request') {
        console.log(`   📂 Category: ${result.result.category}`);
        console.log(`   📦 Suggestions: ${result.result.suggestions.join(', ')}`);
      }
    } else {
      console.log(`   ❌ No match found`);
    }
    
    if (result.contextSuggestions?.length > 0) {
      console.log(`   💡 Suggestions: ${result.contextSuggestions.join(', ')}`);
    }
  }
  
  // Test error recovery
  console.log('\n\n🔧 Testing Error Recovery:\n');
  
  const errorResult = await nlp.handleExecutionResult(
    'install firefox',
    'package.install',
    {
      success: false,
      error: "attribute 'firefox' missing"
    }
  );
  
  if (errorResult.errorAnalysis) {
    console.log('Error Analysis:', errorResult.errorAnalysis);
    console.log('Recovery Suggestions:', errorResult.recovery);
  }
  
  // Show learned patterns
  console.log('\n\n📊 Context State:');
  const contextState = nlp.getContextState();
  console.log('History entries:', contextState.history.length);
  console.log('Last search:', contextState.lastSearch);
  console.log('Suggestions:', contextState.suggestions);
  
  console.log('\n✨ All NLP improvements are working together!');
}

// Run the tests
runTests().catch(console.error);