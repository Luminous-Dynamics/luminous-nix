# Code Review Checklist

## Before Starting Development

### Planning Review
- [ ] **Existing Code Check**: Searched for similar functionality?
- [ ] **Architecture Review**: Checked architecture docs for correct approach?
- [ ] **Standards Review**: Read relevant standards in `.standards/`?
- [ ] **Duplication Check**: Ran `find . -name "*pattern*"` to avoid duplicates?

### Design Review
- [ ] **Single Responsibility**: Each module/class has one clear purpose?
- [ ] **Interface Design**: APIs are intuitive and consistent?
- [ ] **Error Handling**: Failure modes identified and handled?
- [ ] **Performance**: Considered performance implications?

## Code Quality

### Structure
- [ ] **No Duplicates**: No `*_v2.py`, `*_enhanced.py` files created?
- [ ] **Correct Location**: Code in proper directory per project structure?
- [ ] **Single Implementation**: One implementation per feature?
- [ ] **Clean Imports**: Imports organized per Python standards?

### Readability
- [ ] **Clear Names**: Functions/variables have descriptive names?
- [ ] **Documentation**: All public functions have docstrings?
- [ ] **Comments**: Complex logic has explanatory comments?
- [ ] **No Magic Numbers**: Constants defined with meaningful names?

### Python Specific
- [ ] **Type Hints**: All public functions have type hints?
- [ ] **Google Docstrings**: Documentation follows Google style?
- [ ] **No Global State**: No mutable global variables?
- [ ] **Error Handling**: Specific exceptions, no bare except?

## Testing

### Test Coverage
- [ ] **Unit Tests**: New code has unit tests?
- [ ] **Edge Cases**: Edge cases tested?
- [ ] **Error Cases**: Error conditions tested?
- [ ] **Integration**: Integration tests for API changes?

### Test Quality
- [ ] **Isolated**: Tests don't depend on each other?
- [ ] **Fast**: Unit tests run quickly (<100ms)?
- [ ] **Deterministic**: Tests produce same results every run?
- [ ] **Mocked**: External dependencies properly mocked?

## Security

### Input Validation
- [ ] **User Input**: All user input sanitized?
- [ ] **Path Validation**: File paths validated and sandboxed?
- [ ] **Command Injection**: No shell=True with user input?
- [ ] **SQL Injection**: Parameterized queries used?

### Secrets Management
- [ ] **No Hardcoded Secrets**: No passwords/keys in code?
- [ ] **Environment Variables**: Secrets from env vars?
- [ ] **Gitignore**: Sensitive files in .gitignore?
- [ ] **Permissions**: Appropriate file permissions?

## Performance

### Efficiency
- [ ] **Algorithm Choice**: Appropriate algorithms used?
- [ ] **Caching**: Expensive operations cached?
- [ ] **Resource Usage**: Memory/CPU usage reasonable?
- [ ] **Async Where Needed**: I/O operations async?

### Optimization
- [ ] **Profiled**: Performance critical code profiled?
- [ ] **No Premature Optimization**: Optimizations justified?
- [ ] **Database Queries**: N+1 queries avoided?
- [ ] **Batch Operations**: Bulk operations where appropriate?

## Documentation

### Code Documentation
- [ ] **Module Docs**: Module has docstring explaining purpose?
- [ ] **Function Docs**: Public functions documented?
- [ ] **Complex Logic**: Tricky code has comments?
- [ ] **Examples**: Usage examples provided?

### Project Documentation
- [ ] **README Updated**: README reflects changes?
- [ ] **API Docs**: API documentation current?
- [ ] **CHANGELOG**: CHANGELOG entry added?
- [ ] **Architecture**: Architecture docs updated if needed?

## Git & Version Control

### Commit Quality
- [ ] **Commit Messages**: Follow conventional format?
- [ ] **Atomic Commits**: Each commit is one logical change?
- [ ] **No Debug Code**: console.log/print statements removed?
- [ ] **No Commented Code**: Old code deleted, not commented?

### Branch Management
- [ ] **Feature Branch**: Created from develop?
- [ ] **Up to Date**: Rebased on latest develop?
- [ ] **Clean History**: No merge commits from develop?
- [ ] **Ready to Merge**: All conflicts resolved?

## Dependencies

### Package Management
- [ ] **Necessary**: All dependencies actually needed?
- [ ] **Versions Pinned**: Dependencies have version constraints?
- [ ] **Security**: Dependencies checked for vulnerabilities?
- [ ] **License Compatible**: Licenses are compatible?

### Updates
- [ ] **Poetry Lock**: poetry.lock updated?
- [ ] **Requirements**: requirements.txt updated?
- [ ] **Documentation**: New dependencies documented?

## Deployment

### Production Readiness
- [ ] **Environment Variables**: All config externalized?
- [ ] **Logging**: Appropriate logging added?
- [ ] **Monitoring**: Metrics/monitoring considered?
- [ ] **Rollback Plan**: Can changes be rolled back?

### Migration
- [ ] **Backwards Compatible**: Changes backwards compatible?
- [ ] **Migration Scripts**: Database migrations included?
- [ ] **Feature Flags**: Large changes behind feature flags?
- [ ] **Deprecation**: Deprecated features marked?

## Final Checks

### Quality Gates
- [ ] **All Tests Pass**: `pytest` succeeds?
- [ ] **Linting Passes**: `flake8` clean?
- [ ] **Type Checks**: `mypy` passes?
- [ ] **Coverage**: Coverage not decreased?

### Self Review
- [ ] **Works Locally**: Tested on local machine?
- [ ] **Cross-Platform**: Considered other platforms?
- [ ] **User Perspective**: Makes sense from user view?
- [ ] **Pride in Code**: Would you be proud to show this code?

## Review Response

### Addressing Feedback
- [ ] **All Comments Addressed**: Every review comment handled?
- [ ] **Explanations Given**: Clarified any questions?
- [ ] **Changes Tested**: Re-tested after changes?
- [ ] **Reviewer Notified**: Requested re-review?

## Approval Criteria

### Must Have
- ✅ No duplicate files/implementations
- ✅ All tests passing
- ✅ Security considerations addressed
- ✅ Documentation updated
- ✅ Follows project standards

### Should Have
- ✅ Performance acceptable
- ✅ Code is maintainable
- ✅ Good test coverage
- ✅ Clear commit history

### Nice to Have
- ✅ Refactors improve code quality
- ✅ Performance improvements
- ✅ Additional test coverage
- ✅ Enhanced documentation

## Common Rejection Reasons

### Immediate Rejection
- ❌ Creating `*_v2.py` or `*_enhanced.py` files
- ❌ Multiple implementations of same feature
- ❌ Hardcoded secrets or credentials
- ❌ Failing tests
- ❌ No tests for new features

### Needs Revision
- ⚠️ Poor naming conventions
- ⚠️ Missing documentation
- ⚠️ Inconsistent code style
- ⚠️ Inadequate error handling
- ⚠️ Performance concerns

## Review Comments Template

### Requesting Changes
```
**Issue**: [Brief description]
**Location**: [File:line]
**Severity**: [Critical/Major/Minor]
**Suggestion**: [How to fix]
```

### Approval
```
LGTM! ✅

**Strengths**:
- Clean implementation
- Good test coverage
- Well documented

**Minor suggestions** (non-blocking):
- Consider caching X for performance
- Could extract Y to separate function
```