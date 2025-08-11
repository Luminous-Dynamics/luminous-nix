# Testing Infrastructure for Nix for Humanity v1.1

## Overview

This document describes the comprehensive testing infrastructure created for v1.1 features, including TUI integration tests, voice interface tests, and performance benchmarks.

## 🧪 Test Structure

### 1. TUI Integration Tests
Located in `tests/integration/test_tui_integration.py`

**Coverage Areas:**
- ✅ TUI startup and initialization
- ✅ Command input processing
- ✅ Response display
- ✅ Consciousness orb animations
- ✅ Settings panel functionality
- ✅ Persona switching
- ✅ Keyboard shortcuts
- ✅ Error handling display
- ✅ Loading states
- ✅ Command history navigation

**Accessibility Tests:**
- ✅ Screen reader support
- ✅ High contrast mode
- ✅ Keyboard-only navigation

### 2. Voice Interface Tests
Located in `tests/integration/test_voice_interface.py`

**Coverage Areas:**
- ✅ Voice interface initialization
- ✅ Wake word detection
- ✅ Speech recognition (Whisper)
- ✅ Text-to-speech (Piper)
- ✅ Command processing flow
- ✅ Continuous listening mode
- ✅ Voice feedback settings
- ✅ Noise cancellation
- ✅ Multi-language support
- ✅ Persona-specific adaptations

**Integration Tests:**
- ✅ Voice commands updating TUI
- ✅ Voice persona adaptation
- ✅ Error handling

### 3. Performance Benchmarks
Located in `tests/performance/test_v1_1_benchmarks.py`

**Backend Performance:**
- Intent recognition speed (target: <100ms)
- Native operations performance (target: <50ms)
- Concurrent request handling (target: >50 req/s)
- Memory efficiency (target: <50MB increase)

**TUI Performance:**
- Startup time (target: <2s)
- Input responsiveness (target: <100ms)
- Animation performance (target: >30 FPS)

**Voice Performance:**
- Wake word latency (target: <100ms)
- Speech recognition speed (real-time or better)
- TTS generation speed (target: <1s)

## 🚀 Running Tests

### Quick Test Run
```bash
# Run all v1.1 tests
./tests/run_v1_1_tests.sh

# Run specific test suite
pytest tests/integration/test_tui_integration.py -v
pytest tests/integration/test_voice_interface.py -v
pytest tests/performance/test_v1_1_benchmarks.py -v
```

### Test with Coverage
```bash
pytest tests/integration/test_tui_integration.py --cov=src.nix_humanity.ui --cov-report=html
pytest tests/integration/test_voice_interface.py --cov=src.nix_humanity.interfaces.voice --cov-report=html
```

### Performance Testing
```bash
# Run performance benchmarks
python tests/performance/test_v1_1_benchmarks.py

# Generate performance report
cat test_reports/v1_1_test_results.json
```

## 📊 Test Reports

Test results are saved to `test_reports/` directory:
- `v1_1_test_results.json` - Overall test summary
- `performance_report_v1.1.json` - Detailed performance metrics

## 🔧 Mock Components

### Voice Mocks
Located in `tests/mocks/mock_voice_components.py`

Provides mocks for:
- Audio devices (MockAudioDevice)
- Whisper model (MockWhisperModel)
- Piper TTS (MockPiperTTS)
- Wake word detector (MockWakeWordDetector)
- Voice activity detector (MockVoiceActivityDetector)

### Usage Example
```python
from tests.mocks.mock_voice_components import create_mock_voice_components

mocks = create_mock_voice_components()
audio_device = mocks['audio_device']
whisper = mocks['whisper_model']
```

## 🎯 Performance Targets

### Response Times
- CLI commands: <100ms average
- TUI interactions: <100ms
- Voice wake word: <100ms
- Full voice command: <3s end-to-end

### Resource Usage
- Memory: <300MB total
- CPU: <25% average
- Startup time: <2s

### Throughput
- Concurrent commands: >50/second
- TUI frame rate: >30 FPS

## 🐛 Debugging Failed Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in development environment
   nix develop
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

2. **Missing Dependencies**
   ```bash
   # Install test dependencies
   poetry install -E tui -E voice
   ```

3. **Mock Failures**
   - Check mock setup in test fixtures
   - Verify mock return values match expected types

## 📈 Continuous Integration

### GitHub Actions Integration
```yaml
- name: Run v1.1 Tests
  run: |
    nix develop -c ./tests/run_v1_1_tests.sh
```

### Pre-commit Hooks
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
pytest tests/integration/test_tui_integration.py::TestTUIIntegration::test_tui_launches_successfully
```

## 🔄 Future Enhancements

1. **Visual Regression Testing**
   - Screenshot comparisons for TUI
   - Animation smoothness metrics

2. **Voice Quality Testing**
   - Recognition accuracy metrics
   - TTS naturalness scoring

3. **Load Testing**
   - Simulate 100+ concurrent users
   - Stress test voice processing

4. **Integration Testing**
   - Full user journey tests
   - Cross-feature interaction tests

## 📝 Writing New Tests

### TUI Test Template
```python
@pytest.mark.asyncio
async def test_new_tui_feature(self):
    app = NixForHumanityApp()
    
    async with app.run_test() as pilot:
        # Your test logic here
        await pilot.click("#element")
        assert app.some_property == expected_value
```

### Voice Test Template
```python
@pytest.mark.asyncio
async def test_new_voice_feature(self, voice_interface):
    # Mock the specific component
    with patch.object(voice_interface, 'method') as mock:
        mock.return_value = expected_result
        
        # Test the feature
        result = await voice_interface.do_something()
        assert result == expected
```

---

*Testing infrastructure created for v1.1 release - ensuring quality and performance.*