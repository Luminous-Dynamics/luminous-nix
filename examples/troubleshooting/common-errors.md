# 🔧 Common Errors and Solutions

> Every error is a learning opportunity - let's solve them together!

## Top 10 Most Common Issues

### 1. "Package not found"

**Error:**
```
attribute 'vscode' not found
```

**Traditional debugging:**
```bash
nix search nixpkgs vscode
# Nothing found
nix search nixpkgs code
# Still nothing
nix search nixpkgs "visual studio"
# Finally finds: vscode -> vscodium or vscode-fhs
```

**Nix for Humanity solution:**
```bash
ask-nix "find visual studio code or similar"
# Automatically suggests:
# - vscode-fhs (Microsoft VS Code)
# - vscodium (Open source VS Code)
# - code-server (VS Code in browser)
```

### 2. "Permission denied"

**Error:**
```
error: opening lock file '/nix/var/nix/profiles/per-user/...': Permission denied
```

**Traditional fix:**
```bash
# Check permissions
ls -la /nix/var/nix/profiles/per-user/
# Fix ownership
sudo chown -R $USER /nix/var/nix/profiles/per-user/$USER
```

**Nix for Humanity solution:**
```bash
ask-nix "fix permission denied error for nix profiles"
# Automatically diagnoses and suggests safe fix
```

### 3. "Collision between packages"

**Error:**
```
collision between `/nix/store/abc...-package1/bin/tool` and `/nix/store/xyz...-package2/bin/tool`
```

**Traditional fix:**
```bash
# Remove one package
nix-env -e package1
# Or use priorities
nix-env --set-flag priority 0 package1
```

**Nix for Humanity solution:**
```bash
ask-nix "resolve collision between package1 and package2"
# Offers options:
# 1. Keep package1 (set higher priority)
# 2. Keep package2 (set higher priority)
# 3. Remove one package
# 4. Use both with different names
```

### 4. "No space left on device"

**Error:**
```
error: writing to file: No space left on device
```

**Traditional fix:**
```bash
# Check space
df -h /nix/store
# Clean garbage
nix-collect-garbage -d
# Delete old generations
nix-env --delete-generations old
```

**Nix for Humanity solution:**
```bash
ask-nix "clean up disk space safely"
# Automatically:
# - Shows space usage
# - Identifies safe deletions
# - Keeps recent generations
# - Confirms before deleting
```

### 5. "Build failed"

**Error:**
```
error: build of '/nix/store/...-package.drv' failed
```

**Traditional debugging:**
```bash
# Check build log
nix-store -l /nix/store/...-package.drv
# Try different version
nix-env -iA nixos.package_oldversion
# Check issues on GitHub
```

**Nix for Humanity solution:**
```bash
ask-nix "why did package build fail"
# Automatically:
# - Parses error log
# - Identifies common issues
# - Suggests alternatives
# - Offers to try different version
```

### 6. "Channel not found"

**Error:**
```
error: file 'nixpkgs' was not found in the Nix search path
```

**Traditional fix:**
```bash
# Add channel
nix-channel --add https://nixos.org/channels/nixos-24.11 nixos
nix-channel --update
```

**Nix for Humanity solution:**
```bash
ask-nix "fix missing nixpkgs channel"
# Automatically sets up correct channel for your system
```

### 7. "Syntax error in configuration"

**Error:**
```
error: syntax error, unexpected ')', expecting ';'
```

**Traditional debugging:**
```bash
# Manual inspection of configuration.nix
# Trial and error fixing
# nixos-rebuild dry-build for testing
```

**Nix for Humanity solution:**
```bash
ask-nix "check configuration syntax"
# Points to exact line and character
# Suggests correction
# Offers to fix automatically
```

### 8. "Service failed to start"

**Error:**
```
systemd[1]: nginx.service: Failed with result 'exit-code'
```

**Traditional debugging:**
```bash
systemctl status nginx
journalctl -xe -u nginx
# Read through logs
# Fix configuration
# Restart service
```

**Nix for Humanity solution:**
```bash
ask-nix "debug nginx service failure"
# Automatically:
# - Checks logs
# - Identifies config issues
# - Suggests fixes
# - Tests configuration
```

### 9. "Dependency conflict"

**Error:**
```
error: Package 'python3.11-tensorflow' requires 'python3.11-numpy-1.24.0' but 'python3.11-numpy-1.25.0' is installed
```

**Traditional fix:**
```bash
# Complex dependency resolution
# Manual package pinning
# Override specifications
```

**Nix for Humanity solution:**
```bash
ask-nix "resolve tensorflow numpy dependency conflict"
# Offers solutions:
# 1. Downgrade numpy
# 2. Upgrade tensorflow
# 3. Create isolated environment
# 4. Use compatibility layer
```

### 10. "Network timeout"

**Error:**
```
error: unable to download 'https://cache.nixos.org/...': Timeout
```

**Traditional fix:**
```bash
# Retry
nix-build --option connect-timeout 300
# Use different cache
nix-build --option substituters https://mirror.nixos.org
```

**Nix for Humanity solution:**
```bash
ask-nix "fix download timeout"
# Automatically:
# - Tests connectivity
# - Tries alternative mirrors
# - Adjusts timeout settings
# - Uses local cache if available
```

## Error Categories and Solutions

### 🔴 Installation Errors

| Error Pattern | Ask Nix Command | What It Does |
|--------------|-----------------|--------------|
| "attribute not found" | `ask-nix "find package similar to X"` | Smart search with typo correction |
| "unfree package" | `ask-nix "install unfree package X"` | Handles unfree configuration |
| "broken package" | `ask-nix "install broken package X safely"` | Finds alternatives or older versions |
| "platform unsupported" | `ask-nix "find X for my platform"` | Platform-specific alternatives |

### 🟡 Configuration Errors

| Error Pattern | Ask Nix Command | What It Does |
|--------------|-----------------|--------------|
| "undefined variable" | `ask-nix "fix undefined variable X"` | Identifies missing imports |
| "infinite recursion" | `ask-nix "debug infinite recursion"` | Finds circular dependencies |
| "type error" | `ask-nix "fix type error in config"` | Corrects type mismatches |
| "assertion failed" | `ask-nix "explain assertion failure"` | Clarifies requirements |

### 🔵 System Errors

| Error Pattern | Ask Nix Command | What It Does |
|--------------|-----------------|--------------|
| "read-only file system" | `ask-nix "fix read-only filesystem"` | Identifies mount issues |
| "cannot allocate memory" | `ask-nix "fix memory allocation error"` | Optimizes build settings |
| "connection refused" | `ask-nix "fix connection refused"` | Checks service status |
| "boot failure" | `ask-nix "recover from boot failure"` | Guides through recovery |

## Proactive Error Prevention

### Before Installing

```bash
# Check if package will work
ask-nix "will firefox install successfully"

# Check for conflicts
ask-nix "check conflicts before installing X"

# Verify space
ask-nix "do I have space for X"
```

### Before System Changes

```bash
# Validate configuration
ask-nix "validate system configuration"

# Test changes
ask-nix "test configuration changes"

# Create restore point
ask-nix "create system restore point"
```

### Regular Maintenance

```bash
# Weekly cleanup
ask-nix "weekly system maintenance"

# Check system health
ask-nix "check system health"

# Update safely
ask-nix "safe system update"
```

## Understanding Error Messages

### Cryptic to Clear

**Traditional error:**
```
error: while evaluating the attribute 'config.system.build.toplevel' at /nix/store/...:1:1:
while evaluating...
[500 lines of stack trace]
```

**Nix for Humanity explanation:**
```bash
ask-nix "explain this error: [paste error]"

# Output:
"Configuration error in your system settings:
 - Problem: Missing semicolon in configuration.nix
 - Location: Line 42, after 'package = pkgs.firefox'
 - Fix: Add ';' at the end of line 42
 - Command to fix: ask-nix 'fix syntax error at line 42'"
```

## Emergency Recovery

### System Won't Boot

```bash
# Boot previous generation from GRUB menu, then:
ask-nix "recover from failed boot"

# Guides through:
# 1. Identifying what changed
# 2. Rolling back safely
# 3. Fixing the issue
# 4. Testing before reboot
```

### Completely Broken Environment

```bash
# From recovery shell:
ask-nix "emergency system recovery"

# Provides:
# 1. Minimal repair commands
# 2. Network recovery if needed
# 3. Rollback procedures
# 4. Data preservation steps
```

## Learning from Errors

### Enable Learning Mode

```bash
ask-nix-config preferences --set enable_learning true

# Now the system:
# - Remembers error patterns
# - Suggests preventive measures
# - Adapts to your common issues
# - Improves error messages
```

### View Error History

```bash
ask-nix "show my common errors"

# See:
# - Most frequent errors
# - How they were resolved
# - Prevention suggestions
# - Time saved by automation
```

## Quick Error Reference Card

```bash
# Universal error solver
ask-nix "fix: [paste any error message]"

# Specific helpers
ask-nix "why did this fail"
ask-nix "explain this error"
ask-nix "how do I fix this"
ask-nix "prevent this error"
ask-nix "learn from this error"
```

## Getting More Help

### Built-in Documentation
```bash
ask-nix "show docs for error X"
ask-nix "examples of fixing Y"
```

### Community Support
```bash
ask-nix "search forums for this error"
ask-nix "create bug report for this issue"
```

### Learning Resources
```bash
ask-nix "tutorial on avoiding errors"
ask-nix "best practices for NixOS"
```

---

*Remember: Every error message is now an opportunity to learn, not a source of frustration. Nix for Humanity transforms cryptic errors into clear, actionable solutions.*
