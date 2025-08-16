# 🧪 Test Coverage Action Plan - Reality-Based Approach

## 📊 Current Reality Check

After analyzing the actual code structure:
- **No CLIAdapter class exists** - The CLI is implemented as a main() function
- **Tests are looking for non-existent classes** - This explains 0% coverage
- **Actual implementation uses direct function calls** - Not class-based design

## 🎯 Revised Test Strategy

### Phase 1: Fix Test-Code Alignment (Days 1-3)

#### 1.1 Update CLI Tests to Match Reality
```python
# Instead of testing non-existent CLIAdapter class:
# Test the actual main() function and its components

# Test actual CLI flow:
- Command parsing
- Backend integration
- Output formatting
- Error handling
```

#### 1.2 Create Integration Tests for Real CLI
```bash
# Test actual command execution:
./bin/ask-nix "install firefox"
./bin/ask-nix "search markdown editor"
./bin/ask-nix "generate nginx config"
```

### Phase 2: Increase Coverage Where It Matters (Days 4-7)

#### 2.1 Core Module Coverage (Currently Good)
- Core Engine: 91% → 95%
- Knowledge Base: 94% → 98%
- Execution Engine: 90% → 95%

#### 2.2 New Test Creation for Uncovered Modules
```python
# Priority modules needing tests:
1. Native backend operations
2. Error intelligence system
3. Configuration generation
4. Package discovery
```

### Phase 3: TUI Testing Strategy (Days 8-10)

#### 3.1 Textual-Based TUI Tests
```python
# Use Textual's async test client:
async def test_tui_launch():
    app = NixHumanityTUI()
    async with app.run_test() as pilot:
        # Test UI interactions
        await pilot.press("tab")
        await pilot.type("install firefox")
```

### Phase 4: Real-World Integration Tests (Days 11-14)

#### 4.1 End-to-End Scenarios
```yaml
Test Scenarios:
  - First user experience
  - Common operations (install, search, configure)
  - Error recovery flows
  - Learning system adaptation
```

## 📈 Realistic Coverage Targets

| Module | Current | Week 1 | Week 2 | Final |
|--------|---------|---------|---------|--------|
| Core Engine | 91% | 93% | 95% | 95%+ |
| Knowledge Base | 94% | 95% | 97% | 98%+ |
| CLI (main function) | 0% | 70% | 85% | 90%+ |
| TUI | 0% | 60% | 80% | 85%+ |
| **Overall** | **56.72%** | **75%** | **85%** | **90%+** |

## 🛠️ Immediate Actions

### Day 1: Fix Import Issues
```bash
# 1. Update test imports to match actual code structure
# 2. Remove references to non-existent classes
# 3. Focus on testing actual functions and flows
```

### Day 2: Create Working CLI Tests
```python
# Test the actual CLI entry point
def test_cli_main_function():
    # Mock sys.argv
    # Test command parsing
    # Verify backend calls
    # Check output formatting
```

### Day 3: Enable TUI Tests
```python
# Use Textual's test framework properly
# Test actual UI components that exist
# Focus on user interactions
```

## ✅ Success Metrics

1. **Tests Actually Run** - No import errors
2. **Coverage Reflects Reality** - Testing actual code, not imaginary classes
3. **Integration Tests Pass** - Real commands work
4. **Performance Maintained** - <0.5s operations
5. **User Experience Validated** - Educational errors work

## 🚀 Quick Start Commands

```bash
# Fix imports first
python fix_test_imports.py

# Run working tests
pytest tests/unit/test_core_engine.py -v
pytest tests/unit/test_knowledge_base.py -v

# Check actual coverage
pytest --cov=nix_humanity.core --cov-report=term-missing

# Run integration tests
pytest tests/integration/test_real_commands.py -v
```

## 📋 Reality-Based Testing Principles

1. **Test What Exists** - Not what we imagine
2. **Integration Over Units** - User flows matter more
3. **Performance Always** - Every test validates <0.5s
4. **Educational Errors** - Verify teaching moments
5. **Real NixOS Commands** - Test actual operations

---

*Sacred Testing Truth: The best test is one that validates real user experience, not architectural purity.*