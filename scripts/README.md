# 🎓 NixOS Documentation Training Scripts

This directory contains scripts for training local LLM models on NixOS documentation to enhance their ability to assist with NixOS-related queries.

## 📚 Overview

The training pipeline collects NixOS documentation from various sources and prepares it for fine-tuning local models like Mistral-7B and CodeLlama-13B. This creates specialized models that understand NixOS concepts, syntax, and best practices.

## 🔧 Scripts

### Core Pipeline Scripts

1. **`scrape-nixos-docs.py`** - Ethically scrapes NixOS documentation
   - Respects robots.txt and rate limits
   - Collects from official docs, wiki, and Nix Pills
   - Preserves code examples and structure

2. **`process-training-data.py`** - Processes scraped docs into training data
   - Extracts Q&A pairs from content
   - Creates instruction-following examples
   - Identifies troubleshooting patterns

3. **`format-for-training.py`** - Formats data for different training approaches
   - Alpaca format for instruction tuning
   - ShareGPT format for conversational training
   - Completion format for general fine-tuning
   - Ollama modelfile format for easy deployment

4. **`train-nixos-expert.py`** - Orchestrates the complete training pipeline
   - Manages all steps from scraping to model creation
   - Integrates with Ollama for model management
   - Provides progress tracking and error handling

5. **`test-training-pipeline.py`** - Comprehensive test suite
   - Unit tests for each component
   - Integration tests for full pipeline
   - Validates NixOS-specific content preservation

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure you have Python 3.8+ and pip
python3 --version

# Install required packages
pip install -r requirements.txt

# Ensure Ollama is installed (for model management)
ollama --version
```

### Running the Full Pipeline

```bash
# Run complete pipeline with default settings
python3 train-nixos-expert.py

# Skip scraping if you already have data
python3 train-nixos-expert.py --skip-scraping

# Use a different base model
python3 train-nixos-expert.py --base-model codellama:13b --model-name nixos-coder

# Test mode (small dataset)
python3 train-nixos-expert.py --test-mode
```

### Individual Steps

```bash
# 1. Scrape documentation (respects rate limits)
python3 scrape-nixos-docs.py --output-dir ./training-data/nixos-docs

# 2. Process into Q&A pairs
python3 process-training-data.py \
  --input-dir ./training-data/nixos-docs \
  --output-dir ./training-data/processed

# 3. Format for training
python3 format-for-training.py \
  --input-dir ./training-data/processed \
  --output-dir ./training-data/formatted \
  --formats alpaca,sharegpt,ollama

# 4. Create Ollama model (requires formatted data)
ollama create nixos-expert -f ./training-data/formatted/nixos_expert.modelfile
```

## 📊 Training Data Sources

The pipeline collects from:

1. **Official NixOS Manual** - Core documentation
2. **Nixpkgs Manual** - Package-specific docs
3. **NixOS Wiki** - Community knowledge
4. **Nix Pills** - Tutorial series
5. **NixOS Discourse** (optional) - Real Q&A

## 🎯 Training Approaches

### 1. Instruction Fine-tuning (Recommended)
- Uses Alpaca format
- Best for command-style interactions
- Example: "How do I install Firefox?" → detailed response

### 2. Conversational Fine-tuning
- Uses ShareGPT format
- Better for multi-turn dialogues
- Maintains context across exchanges

### 3. LoRA Adaptation
- Efficient fine-tuning method
- Requires less GPU memory
- Creates small adapter weights

### 4. Embedding + Retrieval (Alternative)
- No training required
- Uses vector similarity search
- Good for factual lookups

## 🔒 Ethical Considerations

- **Rate Limiting**: 2-second delay between requests
- **User Agent**: Identifies as educational bot
- **Robots.txt**: Fully respected
- **Attribution**: Sources preserved in metadata
- **Local Only**: All processing stays on your machine

## 📈 Performance Tips

### For Faster Scraping
```bash
# Increase workers (be respectful!)
python3 scrape-nixos-docs.py --max-workers 3

# Skip already downloaded
python3 scrape-nixos-docs.py --skip-existing
```

### For Better Quality
```bash
# More processing passes
python3 process-training-data.py --quality high

# Include code explanations
python3 process-training-data.py --explain-code

# Multi-turn conversations
python3 format-for-training.py --multi-turn 3
```

### For Limited Resources
```bash
# Smaller dataset
python3 train-nixos-expert.py --sample-size 1000

# Use quantized model
python3 train-nixos-expert.py --base-model mistral:7b-q4_0
```

## 🧪 Testing

Run the test suite to ensure everything works:

```bash
# Run all tests
python3 test-training-pipeline.py

# Run specific test category
python3 test-training-pipeline.py TestNixOSDocScraper

# Verbose output
python3 test-training-pipeline.py -v
```

## 📁 Output Structure

```
training-data/
├── nixos-docs/          # Raw scraped documentation
│   ├── manual-*.json
│   ├── wiki-*.json
│   └── pills-*.json
├── processed/           # Extracted Q&A and instructions
│   ├── qa_pairs.json
│   ├── instructions.json
│   └── statistics.json
└── formatted/          # Training-ready formats
    ├── qa_alpaca_train.jsonl
    ├── qa_sharegpt_train.jsonl
    ├── instructions_alpaca_train.jsonl
    └── nixos_expert.modelfile
```

## 🔧 Configuration

### Environment Variables
```bash
# Control scraping behavior
export NIXOS_DOCS_MAX_PAGES=100
export NIXOS_DOCS_RATE_LIMIT=2.0

# Model configuration
export OLLAMA_HOST=http://localhost:11434
export DEFAULT_BASE_MODEL=mistral:7b
```

### Custom Sources

Add sources to `scrape-nixos-docs.py`:
```python
SOURCES = {
    'custom': {
        'base_url': 'https://your-nixos-site.com',
        'paths': ['/docs/', '/guides/'],
        'selector': 'article.content'
    }
}
```

## 🤝 Integration with ask-nix-guru

Once trained, use your model with the ask-nix-guru command:

```bash
# Set your trained model as default
export NIX_GURU_MODEL=nixos-expert

# Ask questions
ask-nix-guru "How do I set up a development environment?"
```

## 📚 Best Practices

1. **Start Small**: Test with a subset before full training
2. **Monitor Quality**: Check generated Q&A pairs
3. **Iterative Improvement**: Fine-tune based on results
4. **Version Control**: Tag your trained models
5. **Document Changes**: Keep notes on what works

## 🐛 Troubleshooting

### Common Issues

**"Connection refused" during scraping**
- Check internet connection
- Verify URLs are accessible
- Increase rate limit delay

**"No module named 'transformers'"**
```bash
pip install transformers torch beautifulsoup4 requests
```

**"Ollama not found"**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

**Out of memory during processing**
- Reduce batch size
- Process in chunks
- Use a smaller model

## 🔮 Future Enhancements

- [ ] Support for man pages
- [ ] Integration with Nix REPL examples
- [ ] Community Q&A incorporation
- [ ] Incremental training updates
- [ ] Multi-language support

## 📄 License

These scripts are part of the Nix for Humanity project and follow the same licensing terms.

## 🙏 Acknowledgments

- NixOS documentation team for excellent docs
- Ollama team for local model management
- The Nix community for continuous improvements

---

*Remember: The goal is to make NixOS knowledge more accessible through AI assistance while respecting the work of documentation authors.*