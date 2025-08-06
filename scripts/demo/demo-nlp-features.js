#!/usr/bin/env node

/**
 * Demo script showing all NLP features working together
 * Run this to see the enhanced Natural Language Processing in action!
 */

const readline = require('readline');
const chalk = require('chalk');

// Import our unified implementation with all NLP improvements
const NixForHumanity = require('./nix-humanity-unified');

// Demo scenarios to showcase
const demoScenarios = [
  {
    title: '🔤 Typo Tolerance',
    commands: [
      { input: 'instal firefox', expected: 'Corrects to "install firefox"' },
      { input: 'remov git', expected: 'Corrects to "remove git"' },
      { input: 'serch browser', expected: 'Corrects to "search browser"' }
    ]
  },
  {
    title: '💬 Context Awareness',
    commands: [
      { input: 'search text editor', expected: 'Shows editor options' },
      { input: 'install the first one', expected: 'Installs first result from search' },
      { input: 'remove it', expected: 'Removes the just-installed package' }
    ]
  },
  {
    title: '📦 Package Aliases',
    commands: [
      { input: 'install chrome', expected: 'Resolves to google-chrome' },
      { input: 'install node', expected: 'Resolves to nodejs' },
      { input: 'install python', expected: 'Resolves to python3 or python311' }
    ]
  },
  {
    title: '🏷️ Category Requests',
    commands: [
      { input: 'install a browser', expected: 'Shows browser options' },
      { input: 'I need a database', expected: 'Shows database options' },
      { input: 'install a music player', expected: 'Shows music player options' }
    ]
  },
  {
    title: '🔧 Error Recovery',
    commands: [
      { input: 'install nonexistentpackage', expected: 'Suggests similar packages' },
      { input: 'install ffmpeg', expected: 'If fails, suggests correct package name' }
    ]
  },
  {
    title: '🧠 Combined Intelligence',
    commands: [
      { input: 'instal the second one', expected: 'Typo + context awareness' },
      { input: 'remov chrome', expected: 'Typo + alias resolution' },
      { input: 'i need somthing to edit photos', expected: 'Typo + category + natural language' }
    ]
  }
];

// Color helpers
const color = {
  title: (text) => chalk.blue.bold(text),
  input: (text) => chalk.yellow(text),
  success: (text) => chalk.green(text),
  info: (text) => chalk.cyan(text),
  dim: (text) => chalk.gray(text)
};

async function runDemo() {
  console.clear();
  console.log(color.title(`
╔════════════════════════════════════════════════════════╗
║        🌟 Nix for Humanity - NLP Features Demo 🌟      ║
║                                                        ║
║  Experience all the natural language improvements!     ║
╚════════════════════════════════════════════════════════╝
`));

  console.log(color.info('This demo will showcase:'));
  console.log('  • Typo correction (fuzzy matching)');
  console.log('  • Context awareness (conversational commands)');
  console.log('  • Package aliases (common names → NixOS names)');
  console.log('  • Category requests ("install a browser")');
  console.log('  • Error recovery (helpful suggestions)');
  console.log('  • User learning (preference tracking)\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  // Ask if they want automated demo or interactive mode
  const mode = await new Promise(resolve => {
    rl.question(color.info('Choose mode: [A]utomated demo or [I]nteractive? (A/I): '), answer => {
      resolve(answer.toLowerCase() === 'i' ? 'interactive' : 'automated');
    });
  });

  if (mode === 'automated') {
    await runAutomatedDemo(rl);
  } else {
    await runInteractiveDemo(rl);
  }
}

async function runAutomatedDemo(rl) {
  console.log(color.success('\n🎬 Starting automated demo...\n'));

  // Initialize in dry-run mode for demo
  process.argv.push('--dry-run');
  const nfh = new NixForHumanity();
  await nfh.nlpEngine.ensureInitialized();

  for (const scenario of demoScenarios) {
    console.log(color.title(`\n${scenario.title}\n`));
    
    for (const command of scenario.commands) {
      console.log(color.input(`> ${command.input}`));
      console.log(color.dim(`  (${command.expected})`));
      
      const result = await nfh.processInput(command.input);
      
      // Show the magic happening
      const nlpResult = await nfh.nlpEngine.processInput(command.input);
      
      if (nlpResult.hadCorrections) {
        console.log(color.success(`  ✏️  Corrected: "${nlpResult.processed}"`));
      }
      
      if (nlpResult.result?.packageInfo) {
        const info = nlpResult.result.packageInfo;
        console.log(color.success(`  📦 Resolved: ${info.resolved} (${info.reason})`));
      }
      
      console.log(color.info(`  💬 ${result.message.split('\n')[0]}`)); // First line only
      
      await sleep(1500); // Pause for effect
    }
  }

  console.log(color.title('\n\n✨ Demo complete! All NLP features are working together.\n'));
  
  rl.question(color.info('Press Enter to exit or type "interactive" to try it yourself: '), answer => {
    if (answer.toLowerCase() === 'interactive') {
      runInteractiveDemo(rl);
    } else {
      rl.close();
      process.exit(0);
    }
  });
}

async function runInteractiveDemo(rl) {
  console.log(color.success('\n🎮 Interactive mode - Try the NLP features yourself!\n'));
  console.log(color.info('Some things to try:'));
  console.log('  • Misspell commands: "instal firefox", "remov git"');
  console.log('  • Use context: "search browser" then "install the first one"');
  console.log('  • Use common names: "install chrome", "install node"');
  console.log('  • Request categories: "install a text editor"');
  console.log('  • Reference previous: "remove it", "install that again"');
  console.log(color.dim('\nType "exit" to quit or "demo" to see automated demo\n'));

  // Remove --dry-run if it exists
  process.argv = process.argv.filter(arg => arg !== '--dry-run');
  process.argv.push('--dry-run'); // Add it back for safety
  
  const nfh = new NixForHumanity();
  await nfh.nlpEngine.ensureInitialized();

  async function promptUser() {
    rl.question(color.yellow('> '), async (input) => {
      if (input.toLowerCase() === 'exit') {
        console.log(color.success('\n👋 Thanks for trying Nix for Humanity!\n'));
        rl.close();
        process.exit(0);
      } else if (input.toLowerCase() === 'demo') {
        await runAutomatedDemo(rl);
        return;
      }

      const result = await nfh.processInput(input);
      
      // Show NLP processing details
      const nlpResult = await nfh.nlpEngine.processInput(input);
      
      if (nlpResult.hadCorrections) {
        console.log(color.success(`✏️  Corrected to: "${nlpResult.processed}"`));
      }
      
      if (nlpResult.result?.packageInfo && nlpResult.result.packageInfo.confidence < 1) {
        const info = nlpResult.result.packageInfo;
        console.log(color.success(`📦 Resolved: "${info.resolved}" (${info.reason})`));
      }
      
      console.log(color.info(result.message));
      
      if (result.suggestions && result.suggestions.length > 0) {
        console.log(color.info('\n💡 Suggestions:'));
        result.suggestions.forEach(s => console.log(`   • ${s}`));
      }
      
      console.log(''); // Empty line
      promptUser();
    });
  }

  promptUser();
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Handle graceful exit
process.on('SIGINT', () => {
  console.log(color.success('\n\n👋 Thanks for exploring Nix for Humanity!\n'));
  process.exit(0);
});

// Run the demo
runDemo().catch(console.error);