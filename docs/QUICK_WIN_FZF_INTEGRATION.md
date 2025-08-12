# 🚀 Quick Win: FZF Integration Guide

*4-hour implementation for massive UX improvement*

## Why FZF/Skim?

### The Problem
```bash
# User types:
"install fierforge"  # Typo!

# Current result:
"No package found: fierforge"  # ❌ Frustrating

# With FZF:
"Did you mean: firefox?"  # ✅ Forgiving
```

## Implementation Plan (4 Hours)

### Hour 1: Setup and Research

#### Option A: Python-FZF (Easier)
```bash
poetry add pyfzf
```

```python
# src/nix_for_humanity/searcher/fuzzy_searcher.py
from pyfzf import FzfPrompt

class FuzzyPackageSearcher:
    def __init__(self):
        self.fzf = FzfPrompt()
    
    def search(self, query: str, packages: List[str]) -> Optional[str]:
        """Fuzzy search through package list"""
        try:
            # Show interactive fuzzy finder
            selected = self.fzf.prompt(
                packages,
                f"--query={query} --select-1 --exit-0"
            )
            return selected[0] if selected else None
        except:
            # Fallback to current exact match
            return self.exact_match(query, packages)
```

#### Option B: Rust Skim (Faster)
```toml
# If using PyO3 for Rust bindings
[dependencies]
skim = "0.10"
pyo3 = "0.20"
```

### Hour 2: Core Integration

```python
# src/nix_for_humanity/nlp/intent_recognition.py

class IntentRecognizer:
    def __init__(self):
        self.fuzzy_searcher = FuzzyPackageSearcher()
        
    def extract_package(self, text: str) -> str:
        """Extract package name with fuzzy matching"""
        
        # First try exact match
        exact = self.exact_match(text)
        if exact:
            return exact
            
        # Fall back to fuzzy search
        words = text.split()
        for word in words:
            if len(word) > 2:  # Skip short words
                matches = self.fuzzy_searcher.search(
                    word, 
                    self.package_database
                )
                if matches:
                    return matches[0]
        
        return None
```

### Hour 3: CLI Integration

```python
# bin/ask-nix

def handle_install(query: str):
    """Handle install commands with fuzzy matching"""
    
    # Extract what user wants
    package_hint = extract_package_hint(query)
    
    # Fuzzy search
    matches = fuzzy_search(package_hint, all_packages)
    
    if len(matches) == 1:
        # Single match - confirm
        print(f"📦 Found: {matches[0]}")
        if confirm(f"Install {matches[0]}?"):
            run_install(matches[0])
    
    elif len(matches) > 1:
        # Multiple matches - let user choose
        print("🔍 Multiple packages found:")
        for i, match in enumerate(matches[:5], 1):
            print(f"  {i}. {match}")
        
        choice = input("Select (1-5): ")
        if choice.isdigit():
            run_install(matches[int(choice)-1])
    
    else:
        # No matches - suggest alternatives
        print(f"❌ No packages found for '{package_hint}'")
        suggest_alternatives(package_hint)
```

### Hour 4: Testing and Polish

```python
# tests/test_fuzzy_search.py

def test_typo_tolerance():
    """Test that common typos are handled"""
    
    searcher = FuzzyPackageSearcher()
    
    # Common typos
    assert searcher.search("fierfox", packages) == "firefox"
    assert searcher.search("chorme", packages) == "chromium"
    assert searcher.search("pythn", packages) == "python3"
    assert searcher.search("dock", packages) == "docker"
    
def test_partial_matches():
    """Test partial name matching"""
    
    assert searcher.search("fire", packages) == "firefox"
    assert searcher.search("vim", packages) in ["vim", "neovim"]
    assert searcher.search("code", packages) == "vscode"
```

## Configuration Options

```python
# src/nix_for_humanity/config/fuzzy_config.py

FUZZY_SETTINGS = {
    # Minimum similarity score (0-100)
    "min_score": 60,
    
    # Maximum results to show
    "max_results": 5,
    
    # Auto-select if score > this
    "auto_select_threshold": 90,
    
    # Search algorithm
    "algorithm": "skim",  # or "fzf", "fuzzy-matcher"
    
    # Interactive mode
    "interactive": True,
    
    # Typo corrections database
    "common_typos": {
        "fierfox": "firefox",
        "pythn": "python",
        "dokcer": "docker",
    }
}
```

## User Experience Improvements

### Before FZF:
```
$ ask-nix "install visul studio code"
❌ Error: Package 'visul' not found
```

### After FZF:
```
$ ask-nix "install visul studio code"
🔍 Did you mean: visual studio code?
📦 Found: vscode
✅ Installing vscode...
```

### Interactive Mode:
```
$ ask-nix "install editor"
🔍 Multiple editors found:
  1. vim
  2. neovim
  3. emacs
  4. vscode
  5. sublime-text
Select (1-5) or type to filter: neo⏎
✅ Installing neovim...
```

## Performance Considerations

```python
# Cache package list for speed
class FuzzySearchCache:
    def __init__(self):
        self._cache = {}
        self._package_list = None
        self._last_update = 0
    
    @property
    def packages(self):
        if time.time() - self._last_update > 3600:  # 1 hour
            self._package_list = self.fetch_packages()
            self._last_update = time.time()
        return self._package_list
```

## Fallback Strategy

```python
def search_with_fallback(query: str) -> str:
    """Multi-level fallback for maximum forgiveness"""
    
    # Level 1: Exact match
    if exact := exact_match(query):
        return exact
    
    # Level 2: Fuzzy match with FZF
    if fuzzy := fuzzy_match(query):
        return fuzzy
    
    # Level 3: Levenshtein distance
    if similar := find_similar(query, max_distance=2):
        return similar[0]
    
    # Level 4: Substring match
    if substr := substring_match(query):
        return substr
    
    # Level 5: Ask user to rephrase
    return ask_user_to_clarify(query)
```

## Success Metrics

- **Before**: 60% successful package finds
- **Goal**: 95% successful package finds
- **Measurement**: Log successful vs failed searches

## Dependencies

```toml
# pyproject.toml additions
[tool.poetry.dependencies]
pyfzf = "^0.3.1"  # Python wrapper for fzf
python-Levenshtein = "^0.20.0"  # Fallback algorithm
rapidfuzz = "^3.0"  # Fast fuzzy matching
```

## Testing Checklist

- [ ] Handles common typos (firefox → firefox)
- [ ] Handles partial names (vim → neovim)
- [ ] Handles multiple matches gracefully
- [ ] Falls back on FZF failure
- [ ] Maintains <100ms response time
- [ ] Works in non-interactive mode
- [ ] Preserves exact match priority

## Next Steps After FZF

Once FZF is working:
1. Add to all search operations (not just packages)
2. Create typo database from common mistakes
3. Add learning to improve over time
4. Integrate with voice interface for forgiveness

---

*"Forgiveness in interfaces is accessibility for all."*