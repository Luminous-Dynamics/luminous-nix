# 🤝 Contributing to Nix for Humanity

Thank you for your interest in contributing to Nix for Humanity! We're building technology that makes NixOS accessible to everyone through natural language, and we'd love your help.

## 🌟 Our Philosophy

We follow the **Sacred Trinity** development model:
- **Human** provides vision and testing
- **AI** assists with implementation  
- **Community** guides evolution

This project proves that $200/month in AI tools can achieve what traditionally requires millions in funding.

## How Can I Contribute?

### 🗣️ Add Natural Language Patterns
The easiest way to contribute! Help us understand more ways people express NixOS commands:

```python
# In src/nix_for_humanity/knowledge/patterns.py
INSTALL_PATTERNS = [
    "install {package}",
    "add {package}",
    "get {package}",
    "i need {package}",  # Add your pattern here!
]
```

### 🐛 Report Bugs
Found something that doesn't work? [Create an issue](https://github.com/Luminous-Dynamics/nix-for-humanity/issues/new?template=bug_report.md) with:
- The command you tried
- What you expected
- What actually happened
- Your NixOS version

### 💡 Suggest Enhancements
Have ideas for improvements? [Create an enhancement request](https://github.com/Luminous-Dynamics/nix-for-humanity/issues/new?template=enhancement.md).

### 📖 Improve Documentation
Documentation can always be better! Fix typos, clarify explanations, or add examples.

### 🧪 Add Tests
Help us maintain quality by adding tests:
```bash
poetry run pytest tests/test_your_feature.py
```

## Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
```

2. **Enter development environment**
```bash
nix develop  # Provides all dependencies
# OR
poetry install --all-extras  # If you have Poetry
```

3. **Make your changes**
```bash
# Create a branch
git checkout -b feature/your-feature-name

# Make changes
# ...

# Format code
poetry run black .
poetry run ruff check --fix .

# Run tests
poetry run pytest
```

4. **Test your changes**
```bash
# Test the CLI
./bin/ask-nix "your test command"

# Run demos to ensure nothing broke
./quick-demo.sh
```

## Code Style

We use automated formatting - just run before committing:
```bash
poetry run black .           # Format Python
poetry run ruff check --fix . # Fix linting issues
```

## Commit Messages

Use clear, descriptive commit messages:
```
feat: add support for "please install X" pattern
fix: handle packages with hyphens correctly
docs: clarify natural language examples
test: add coverage for search command
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Add tests** if you're adding features
3. **Update documentation** as needed
4. **Ensure all tests pass**: `poetry run pytest`
5. **Format your code**: `poetry run black .`
6. **Create a Pull Request** with a clear description

## AI Collaboration Welcome!

If you used AI tools (Claude, GPT, Copilot, etc.) to help with your contribution, that's great! Just mention it in your PR - we celebrate AI collaboration here.

## Questions?

Feel free to:
- Open a [discussion](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)
- Ask in an issue
- Email: tristan.stoltz@gmail.com

## Recognition

All contributors will be recognized in our README. Your contributions help make NixOS accessible to everyone!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Remember**: Every contribution, no matter how small, helps make NixOS more accessible. Thank you for being part of this journey! 🙏
