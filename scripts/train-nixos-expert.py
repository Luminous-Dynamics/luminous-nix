
    
    def step_8_create_ask_nix_guru_integration(self, model_name: str) -> bool:
        """Step 8: Integrate with ask-nix-guru command"""
        logger.info("=== Step 8: Creating ask-nix-guru Integration ===")
        
        # Create configuration for the trained model
        config = {
            'models': {
                'nixos-expert': {
                    'name': model_name,
                    'description': 'NixOS expert trained on official documentation',
                    'context_window': 8192,
                    'system_prompt': 'You are a NixOS expert assistant...',
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            },
            'default_model': 'nixos-expert'
        }
        
        config_path = self.base_dir / 'config' / 'trained-models.json'
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created configuration: {config_path}")
        
        # Create wrapper script
        wrapper_script = self.base_dir / 'bin' / 'ask-nix-expert'
        wrapper_script.parent.mkdir(exist_ok=True)
        
        script_content = f"""#!/usr/bin/env bash
# Ask NixOS Expert - Powered by trained model

MODEL="{model_name}"
QUESTION="$*"

if [ -z "$QUESTION" ]; then
    echo "Usage: ask-nix-expert <question>"
    echo "Example: ask-nix-expert How do I install Docker?"
    exit 1
fi

# Use the trained model
ollama run "$MODEL" "$QUESTION"
"""
        
        with open(wrapper_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        wrapper_script.chmod(0o755)
        
        logger.info(f"Created wrapper script: {wrapper_script}")
        logger.info("You can now use: ask-nix-expert 'your question here'")
        
        return True
    
    def create_training_report(self, results: Dict) -> Path:
        """Create a comprehensive training report"""
        report_path = self.models_dir / f"training-report-{int(time.time())}.md"
        
        report = f"""# NixOS Model Training Report

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Base Model**: {results.get('base_model', 'Unknown')}
- **Model Name**: {results.get('model_name', 'Unknown')}
- **Training Duration**: {results.get('duration', 'Unknown')}
- **Status**: {results.get('status', 'Unknown')}

## Pipeline Steps

"""
        
        for step, status in results.get('steps', {}).items():
            icon = '✅' if status else '❌'
            report += f"{icon} {step}\n"
        
        report += f"""
## Data Statistics

- Documents Scraped: {results.get('doc_count', 0)}
- Q&A Pairs: {results.get('qa_count', 0)}
- Instructions: {results.get('instruction_count', 0)}
- Concepts: {results.get('concept_count', 0)}
- Troubleshooting Items: {results.get('troubleshooting_count', 0)}

## Next Steps

1. Test the model thoroughly with real NixOS questions
2. Collect user feedback for improvements
3. Schedule regular retraining with updated documentation
4. Consider training specialized models for specific topics

## Usage

```bash
# Direct usage
ollama run {results.get('model_name', 'nixos-expert')} "Your NixOS question"

# Using wrapper
ask-nix-expert "How do I configure networking?"
```
"""
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Training report saved: {report_path}")
        return report_path
    
    def run_full_pipeline(self, base_model: str = "mistral:7b", 
                         model_name: str = "nixos-expert",
                         skip_scraping: bool = False) -> bool:
        """Run the complete training pipeline"""
        start_time = time.time()
        results = {
            'base_model': base_model,
            'model_name': model_name,
            'steps': {},
            'start_time': start_time
        }
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("Missing dependencies. Please install required tools.")
            return False
        
        # Step 1: Scrape documentation (optional)
        if not skip_scraping:
            results['steps']['1_scrape'] = self.step_1_scrape_documentation()
            if not results['steps']['1_scrape']:
                logger.error("Scraping failed. Aborting.")
                return False
        else:
            logger.info("Skipping scraping step (using existing data)")
            results['steps']['1_scrape'] = True
        
        # Step 2: Process data
        results['steps']['2_process'] = self.step_2_process_data()
        if not results['steps']['2_process']:
            logger.error("Processing failed. Aborting.")
            return False
        
        # Load statistics
        stats_file = self.data_dir / 'processed' / 'statistics.json'
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)
                results.update({
                    'doc_count': stats.get('documents', 0),
                    'qa_count': stats.get('qa_pairs', 0),
                    'instruction_count': stats.get('instructions', 0),
                    'concept_count': stats.get('concepts', 0),
                    'troubleshooting_count': stats.get('troubleshooting', 0)
                })
        
        # Step 3: Format training data
        results['steps']['3_format'] = self.step_3_format_training_data()
        if not results['steps']['3_format']:
            logger.error("Formatting failed. Aborting.")
            return False
        
        # Step 4: Create modelfile
        modelfile_path = self.step_4_create_ollama_modelfile(base_model)
        results['steps']['4_modelfile'] = modelfile_path is not None
        
        # Step 5: Create LoRA adapter (future)
        adapter_path = self.step_5_create_lora_adapter(base_model)
        results['steps']['5_lora'] = adapter_path is not None
        
        # Step 6: Create Ollama model
        results['steps']['6_create_model'] = self.step_6_create_ollama_model(modelfile_path, model_name)
        if not results['steps']['6_create_model']:
            logger.error("Model creation failed. Aborting.")
            return False
        
        # Step 7: Test model
        results['steps']['7_test'] = self.step_7_test_model(model_name)
        
        # Step 8: Create integration
        results['steps']['8_integration'] = self.step_8_create_ask_nix_guru_integration(model_name)
        
        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        results['duration'] = f"{duration/60:.1f} minutes"
        results['status'] = 'Success' if all(results['steps'].values()) else 'Partial Success'
        
        # Create report
        report_path = self.create_training_report(results)
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING PIPELINE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Model Name: {model_name}")
        logger.info(f"Duration: {results['duration']}")
        logger.info(f"Status: {results['status']}")
        logger.info(f"Report: {report_path}")
        logger.info("\nTry your new model:")
        logger.info(f"  ollama run {model_name} 'How do I install Docker in NixOS?'")
        logger.info("  ask-nix-expert 'What is a flake?'")
        
        return results['status'] == 'Success'


def main():
    parser = argparse.ArgumentParser(
        description='Train NixOS expert models from documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default settings
  %(prog)s
  
  # Use CodeLlama as base model
  %(prog)s --base-model codellama:13b --model-name nixos-codellama
  
  # Skip scraping (use existing data)
  %(prog)s --skip-scraping
  
  # Custom directories
  %(prog)s --base-dir /path/to/project
""")
    
    parser.add_argument('--base-model', default='mistral:7b',
                       help='Base model to fine-tune (default: mistral:7b)')
    parser.add_argument('--model-name', default='nixos-expert',
                       help='Name for the trained model (default: nixos-expert)')
    parser.add_argument('--skip-scraping', action='store_true',
                       help='Skip documentation scraping (use existing data)')
    parser.add_argument('--base-dir', 
                       default='/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity',
                       help='Base directory for the project')
    
    args = parser.parse_args()
    
    trainer = NixOSModelTrainer(args.base_dir)
    success = trainer.run_full_pipeline(
        base_model=args.base_model,
        model_name=args.model_name,
        skip_scraping=args.skip_scraping
    )
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()