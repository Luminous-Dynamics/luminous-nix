# 🎯 Immediate Action Plan: Making Luminous Nix Actually Work

## Week 1: Fix the Foundation

### Day 1-2: Clean House
```bash
# 1. Archive the chaos
mkdir -p archive/2025-01-legacy
mv features/v4.0 archive/2025-01-legacy/  # Future features
mv features/v3.0 archive/2025-01-legacy/  # Except XAI which works
mv demos archive/2025-01-legacy/          # Old demos
mv archive/legacy* archive/2025-01-legacy/ # Old archives
mv venv_* archive/2025-01-legacy/         # Multiple venvs

# 2. Keep only what's needed
# src/nix_for_humanity/  - Core code
# tests/                  - Test suite
# docs/                   - Documentation
# bin/                    - Entry points
# features/v3.0/xai/      - Working XAI
```

### Day 3-4: Fix the CLI
```python
# Problem: Missing PersonaManager and other modules
# Solution: Create minimal working versions

# src/nix_for_humanity/nlp/personas.py
class PersonaManager:
    """Minimal persona manager to get CLI working"""
    def get_persona(self, name="default"):
        return {"style": "helpful", "level": "intermediate"}

# Fix all imports to point to real modules
# Test with: ./bin/ask-nix "help"
```

### Day 5: Set Up Poetry Properly
```bash
# Clean setup with Poetry
poetry init
poetry add click colorama requests pyyaml
poetry add textual rich blessed  # For TUI
poetry install

# Test everything works
poetry run ask-nix "help"
poetry run pytest tests/
```

## Week 2: Make It Real

### Core NixOS Operations to Implement
```python
# src/nix_for_humanity/nix/operations.py

class RealNixOperations:
    """ACTUAL NixOS operations, no mocks!"""

    def install_package(self, package: str) -> Result:
        """Actually install a package"""
        cmd = f"nix-env -iA nixos.{package}"
        return self._run_command(cmd)

    def search_packages(self, query: str) -> Result:
        """Actually search nixpkgs"""
        cmd = f"nix search nixpkgs {query}"
        return self._run_command(cmd)

    def update_system(self) -> Result:
        """Actually update NixOS"""
        cmd = "sudo nixos-rebuild switch"
        return self._run_command(cmd, needs_sudo=True)

    def rollback(self) -> Result:
        """Actually rollback to previous generation"""
        cmd = "sudo nixos-rebuild switch --rollback"
        return self._run_command(cmd, needs_sudo=True)
```

### Test Against Real NixOS
```python
# tests/integration/test_real_operations.py

def test_real_package_search():
    """Test we can actually search packages"""
    result = ask_nix("search firefox")
    assert "firefox" in result.output
    assert result.success

def test_real_package_install():
    """Test we can actually install packages"""
    result = ask_nix("install htop", dry_run=True)
    assert "nix-env -iA nixos.htop" in result.command
    # Don't actually install in tests, but verify command
```

## Week 3: Essential Features

### 1. Configuration Generation
```python
def generate_config(request: str) -> str:
    """Generate real configuration.nix snippets"""

    if "docker" in request:
        return """
  # Enable Docker
  virtualisation.docker.enable = true;
  users.extraGroups.docker.members = [ "username" ];
"""
    elif "development" in request:
        return """
  # Development environment
  environment.systemPackages = with pkgs; [
    git
    vim
    tmux
    gcc
  ];
"""
```

### 2. Error Translation
```python
ERROR_TRANSLATIONS = {
    "collision between": "Package conflict: Two packages provide the same file. Use priority to resolve.",
    "cannot coerce": "Type error in configuration: Check your configuration.nix syntax",
    "infinite recursion": "Circular dependency: A package depends on itself"
}
```

### 3. Smart Suggestions
```python
def get_suggestions(error: str) -> List[str]:
    if "not found" in error:
        return [
            "Try: nix search nixpkgs <package>",
            "Check spelling of package name",
            "Package might be in nixpkgs-unstable"
        ]
```

## Success Metrics

### Week 1 Goals ✅
- [ ] CLI runs without import errors
- [ ] Poetry manages all dependencies
- [ ] File structure cleaned up
- [ ] Basic help command works

### Week 2 Goals ✅
- [ ] Can search real packages
- [ ] Can install real packages (with --dry-run)
- [ ] Can update system (with confirmation)
- [ ] Can rollback generations

### Week 3 Goals ✅
- [ ] Configuration snippets generate correctly
- [ ] Errors are translated helpfully
- [ ] Smart suggestions work
- [ ] 90% test coverage

## What NOT to Do

### ❌ Avoid These Traps
1. **Don't add new features** until basics work
2. **Don't create mocks** - use real operations or dry-run
3. **Don't over-engineer** - simple solutions first
4. **Don't skip tests** - every feature needs tests
5. **Don't ignore errors** - fix them properly

## The 80/20 Rule

### Focus on the 20% that gives 80% value:
1. **Package management** (install/remove/search)
2. **Error translation** (make errors understandable)
3. **Configuration help** (generate snippets)
4. **Safety** (dry-run, confirmations)

### Leave for later:
- Voice interfaces
- Multiple personas
- Consciousness visualizations
- Federated learning

## Daily Checklist

### Every Day:
- [ ] One core feature implemented
- [ ] Tests written for that feature
- [ ] Documentation updated
- [ ] Git commit with clear message
- [ ] Test on real NixOS system

## The Mantra

> "Make it work, make it right, make it fast, make it beautiful"

We're stuck at "make it work" - let's fix that first!

---

**Remember**: Users don't care about our beautiful architecture if `ask-nix "install firefox"` doesn't work.

Let's ship something that works! 🚀
