# Test Strategy Document

## Current State (v1.1.0)
- **Test Coverage**: 12%
- **Collection Errors**: 44 (even after skipping NixOS tests)
- **Collectible Tests**: 1473 (but blocked by errors)
- **Working Tests**: ~150

## Strategic Decision: Accept Technical Debt

### Why We're Not Fixing Tests Now

1. **Time Investment**: 40+ hours to properly fix test architecture
2. **User Impact**: Zero - users don't see test coverage
3. **Opportunity Cost**: Could build voice interface instead
4. **Historical Success**: Shipped v1.0.1 and v1.1.0 successfully with low coverage

### The Test Problems

#### Architectural Issues
- Circular imports between modules
- Mock objects not properly configured
- Tests assume NixOS environment
- Missing test fixtures and utilities
- Import paths inconsistent

#### Example Problems
```python
# Can't import these without NixOS:
from nix_for_humanity.core.native_operations import NativeOperations
from python.native_nix_backend import NativeNixBackend

# These modules don't exist:
from nix_for_humanity.backend.headless_engine import HeadlessEngine
from nix_for_humanity.learning.system import LearningSystem
```

### Our Testing Strategy

#### What We Test
1. **Critical Path**: CLI interface, pattern recognition
2. **User Features**: TUI components, command parsing
3. **Integration**: Manual testing on real NixOS
4. **Regression**: Specific bugs like "i need firefox"

#### What We Don't Test (Yet)
1. **NixOS Integration**: Requires actual NixOS
2. **Learning System**: Not implemented
3. **Native Backend**: Platform-specific
4. **Complex Mocks**: Time-consuming to maintain

### Future Test Plan

#### Phase 1: Stabilization (After v1.2.0)
- Fix import issues systematically
- Create proper mock infrastructure
- Separate unit from integration tests
- Target: 30% coverage

#### Phase 2: Comprehensive Testing (v2.0)
- Docker-based NixOS test environment
- End-to-end integration tests
- Performance benchmarks
- Target: 60% coverage

#### Phase 3: Excellence (v3.0)
- Property-based testing
- Mutation testing
- Security testing
- Target: 80% coverage

### Testing Philosophy

> "Ship early, ship often, test what matters"

We prioritize:
1. **User-facing features** over internal implementation
2. **Manual testing** over automated for complex integrations
3. **Real-world usage** over synthetic tests
4. **Fast iteration** over perfect coverage

### Metrics That Matter

Instead of coverage percentage, we track:
- **User bug reports**: Currently 0 critical, 2 minor
- **Feature delivery**: 2 major releases in 1 week
- **User satisfaction**: Positive feedback on TUI
- **Time to fix**: <24 hours for critical bugs

### The Bottom Line

**We choose to build the future (voice interface) rather than perfect the past (test coverage).**

Tests will improve gradually as the codebase stabilizes and we understand real usage patterns. For now, we test what's critical and rely on rapid iteration to catch issues.

---

*"Perfect tests tomorrow < Working features today"*