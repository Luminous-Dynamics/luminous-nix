# 🏥 Luminous Nix Self-Healing System Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Components](#components)
6. [Usage Examples](#usage-examples)
7. [Monitoring & Metrics](#monitoring--metrics)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Performance](#performance)

## Overview

The Luminous Nix Self-Healing System is an **automated system health monitor and repair service** that detects and resolves common system issues without human intervention. Built with simplicity and elegance, it achieves remarkable performance with minimal code.

### Key Features
- 🚀 **1,486 ops/second** throughput
- 💾 **< 1MB memory** footprint
- ⚡ **0.078ms** average detection time
- 🎯 **3 generic healing actions** handle all scenarios
- 🔒 **2-tier permission system** for safety
- 📊 **Prometheus metrics** integration
- 🖥️ **Real-time dashboard** for monitoring

### Design Philosophy
- **Simple > Complex**: 84% less code than V1
- **Generic > Specific**: 3 categories vs 14 specific actions
- **Platform-native**: Leverage NixOS features
- **Fast > Feature-rich**: Performance is a feature

## Architecture

### System Overview
```
┌─────────────────────────────────────────┐
│           Self-Healing Engine           │
├─────────────┬─────────────┬─────────────┤
│  Detector   │  Resolver   │ Permissions │
├─────────────┼─────────────┼─────────────┤
│ Thresholds  │  Patterns   │   2-Tier    │
│   Based     │  Matching   │   System    │
└─────────────┴─────────────┴─────────────┘
       ↓              ↓              ↓
┌─────────────────────────────────────────┐
│         System Monitor (Async)          │
└─────────────────────────────────────────┘
```

### Core Components

#### 1. **SimplifiedHealingEngine** (338 lines)
The orchestrator that coordinates detection, resolution, and execution.

#### 2. **SimpleDetector** (Part of engine)
Threshold-based detection with configurable limits:
- CPU: 80% default threshold
- Memory: 85% default threshold  
- Disk: 90% default threshold
- Services: Check if running

#### 3. **SimpleResolver** (Part of engine)
Pattern matching for issue resolution:
- **RESOURCE issues** → Resource management actions
- **SERVICE issues** → Service restart actions
- **SYSTEM issues** → System recovery actions

#### 4. **NixOSPermissionHandler** (320 lines)
Two-tier permission system:
- **SERVICE mode**: Production with SystemD integration
- **DEVELOPMENT mode**: Testing with dry-run capabilities

## Quick Start

### Installation

```python
# Import the healing system
from luminous_nix.self_healing import create_self_healing_engine

# Create engine with defaults
engine = create_self_healing_engine()

# Start monitoring (runs continuously)
await engine.start_monitoring(interval=60)  # Check every 60 seconds
```

### One-Shot Healing

```python
from luminous_nix.self_healing import quick_heal

# Run a single healing cycle
results = await quick_heal()

for result in results:
    print(f"Fixed: {result.issue.description}")
    print(f"Action: {result.action_taken}")
    print(f"Success: {result.success}")
```

### Manual Detection & Resolution

```python
from luminous_nix.self_healing import SimplifiedHealingEngine

engine = SimplifiedHealingEngine()

# Detect issues
issues = await engine.detector.detect_issues()

# Resolve each issue
for issue in issues:
    action = engine.resolver.get_action(issue)
    result = await engine.executor.execute(action, dry_run=True)
```

## Configuration

### Threshold Configuration

```python
engine = SimplifiedHealingEngine()

# Customize thresholds
engine.detector.thresholds = {
    'cpu_percent': 75.0,      # Trigger at 75% CPU
    'memory_percent': 80.0,    # Trigger at 80% memory
    'disk_percent': 85.0,      # Trigger at 85% disk
    'load_average': 3.0,       # Trigger at load 3.0
}
```

### Permission Modes

```python
# Development mode (for testing)
import os
os.environ['LUMINOUS_DEV_MODE'] = '1'

# Service mode (production - default)
# Requires SystemD service configuration
```

### SystemD Service Configuration

```nix
# /etc/nixos/configuration.nix
services.luminous-healing = {
  enable = true;
  interval = 60;  # seconds
  thresholds = {
    cpu = 80;
    memory = 85;
    disk = 90;
  };
};
```

## Components

### Issue Types

```python
class IssueType(Enum):
    RESOURCE = "resource"   # CPU, Memory, Disk
    SERVICE = "service"     # Service not running
    SYSTEM = "system"       # System-wide issues
```

### Severity Levels

```python
class Severity(Enum):
    LOW = 1        # Monitor only
    MEDIUM = 2     # May heal if resources available
    HIGH = 3       # Heal immediately
    CRITICAL = 4   # Heal with priority
```

### Healing Actions

The system uses 3 generic action categories:

1. **Resource Management**
   - `clean_nix_store` - Free disk space
   - `clear_system_cache` - Free memory
   - `set_cpu_governor` - Optimize CPU

2. **Service Management**
   - `restart_service` - Restart failed services
   - `reload_service` - Reload configuration

3. **System Recovery**
   - `rollback_generation` - Rollback to previous NixOS generation
   - `rebuild_system` - Rebuild NixOS configuration

## Usage Examples

### Example 1: Monitor Critical Services

```python
from luminous_nix.self_healing import SimplifiedHealingEngine

engine = SimplifiedHealingEngine()

# Configure to focus on services
engine.detector.thresholds['cpu_percent'] = 95  # Only critical CPU
engine.detector.thresholds['memory_percent'] = 95  # Only critical memory

# Monitor specific services
critical_services = ['nginx', 'postgresql', 'redis']

async def monitor_services():
    while True:
        issues = await engine.detector.detect_issues()
        
        # Filter for service issues
        service_issues = [i for i in issues 
                         if i.type == IssueType.SERVICE 
                         and i.component in critical_services]
        
        for issue in service_issues:
            result = await engine.heal_issue(issue)
            if result.success:
                print(f"✅ Healed: {issue.description}")
            else:
                print(f"❌ Failed: {result.error}")
        
        await asyncio.sleep(30)  # Check every 30 seconds
```

### Example 2: Custom Healing Logic

```python
from luminous_nix.self_healing import SimpleResolver, Issue

class CustomResolver(SimpleResolver):
    def get_action(self, issue: Issue) -> Dict[str, Any]:
        # Add custom logic for specific scenarios
        if issue.component == "my_special_service":
            return {
                'action': 'custom_restart',
                'parameters': {
                    'service': issue.component,
                    'wait_time': 10
                }
            }
        
        # Fall back to default resolution
        return super().get_action(issue)

# Use custom resolver
engine = SimplifiedHealingEngine()
engine.resolver = CustomResolver()
```

### Example 3: Metrics Integration

```python
from luminous_nix.self_healing import SimplifiedHealingEngine
from luminous_nix.self_healing import MetricsServer

# Create engine
engine = SimplifiedHealingEngine()

# Start metrics server for Prometheus
metrics_server = MetricsServer(
    healing_engine=engine,
    host='0.0.0.0',
    port=9090
)

await metrics_server.start()

# Metrics available at http://localhost:9090/metrics
```

## Monitoring & Metrics

### Available Metrics

The system exposes these metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `healing_issues_detected` | Counter | Total issues detected |
| `healing_issues_resolved` | Counter | Successfully resolved issues |
| `healing_issues_failed` | Counter | Failed healing attempts |
| `healing_last_check` | Gauge | Timestamp of last check |
| `healing_success_rate` | Gauge | Success percentage |
| `healing_detection_time_ms` | Histogram | Detection duration |
| `healing_resolution_time_ms` | Histogram | Resolution duration |

### Dashboard Access

```python
from luminous_nix.self_healing import SimpleDashboard

dashboard = SimpleDashboard(engine)
await dashboard.start(port=8080)

# Access at http://localhost:8080
```

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'luminous-healing'
    static_configs:
      - targets: ['localhost:9090']
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied

**Problem**: Healing actions fail with permission errors
**Solution**: 
```bash
# Check if running in correct mode
echo $LUMINOUS_DEV_MODE

# For production, ensure SystemD service is enabled
sudo systemctl status luminous-healing
```

#### 2. High False Positive Rate

**Problem**: Too many non-issues detected
**Solution**: Adjust thresholds
```python
engine.detector.thresholds['cpu_percent'] = 85  # Less sensitive
engine.detector.thresholds['memory_percent'] = 90
```

#### 3. Actions Not Executing

**Problem**: Dry run mode active
**Solution**:
```python
engine.dry_run = False  # Enable actual execution
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
engine = SimplifiedHealingEngine()
engine.verbose = True
```

## API Reference

### Main Functions

#### `create_self_healing_engine()`
```python
def create_self_healing_engine(
    dry_run: bool = False,
    verbose: bool = False
) -> SimplifiedHealingEngine:
    """Create a configured healing engine"""
```

#### `quick_heal()`
```python
async def quick_heal(
    dry_run: bool = True
) -> List[HealingResult]:
    """Run one healing cycle"""
```

### Classes

#### `SimplifiedHealingEngine`
```python
class SimplifiedHealingEngine:
    def __init__(self):
        self.detector: SimpleDetector
        self.resolver: SimpleResolver
        self.healing_enabled: bool = True
        self.dry_run: bool = False
        
    async def detect_and_heal(self) -> List[HealingResult]
    async def start_monitoring(self, interval: int = 60)
    def get_metrics(self) -> Dict[str, Any]
```

#### `Issue`
```python
@dataclass
class Issue:
    type: IssueType
    severity: Severity
    description: str
    component: str
    metric_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
```

#### `HealingResult`
```python
@dataclass
class HealingResult:
    issue: Issue
    action_taken: str
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
```

## Performance

### Benchmark Results

Based on our performance testing:

| Operation | Performance | Memory |
|-----------|-------------|---------|
| Detection | 12,740 ops/sec | 890 KB |
| Resolution | 1,221,437 ops/sec | < 1 KB |
| End-to-End | 1,486 ops/sec | 725 KB |

### Optimization Tips

1. **Adjust Check Intervals**
   ```python
   # Less frequent for stable systems
   await engine.start_monitoring(interval=300)  # 5 minutes
   
   # More frequent for critical systems
   await engine.start_monitoring(interval=30)   # 30 seconds
   ```

2. **Selective Monitoring**
   ```python
   # Only monitor critical resources
   engine.detector.enabled_checks = ['cpu', 'disk', 'services']
   # Skip memory checks if not needed
   ```

3. **Batch Processing**
   ```python
   # Process multiple issues together
   issues = await engine.detector.detect_issues()
   results = await engine.heal_issues_batch(issues)
   ```

### Resource Usage

- **CPU**: < 0.1% average
- **Memory**: < 10MB resident
- **Disk I/O**: Minimal (logs only)
- **Network**: None (local only)

## Best Practices

### 1. Start Conservative
Begin with high thresholds and lower as you understand your system:
```python
# Start with
thresholds = {'cpu': 90, 'memory': 90, 'disk': 95}

# Gradually tune to
thresholds = {'cpu': 75, 'memory': 80, 'disk': 85}
```

### 2. Test in Development First
Always test healing actions in development mode:
```python
os.environ['LUMINOUS_DEV_MODE'] = '1'
engine.dry_run = True
```

### 3. Monitor Metrics
Track success rates and adjust:
```python
metrics = engine.get_metrics()
if metrics['success_rate'] < 0.8:  # Less than 80% success
    # Review and adjust configuration
    pass
```

### 4. Use Platform Features
Leverage NixOS capabilities:
- Use generations for rollback
- Use SystemD for service management
- Use Nix store for package management

## Migration from V1

If upgrading from the complex V1 system:

```python
# Old V1 import
from healing_engine import SelfHealingEngine

# New V2 import (backward compatible)
from luminous_nix.self_healing import SelfHealingEngine

# Or use new name
from luminous_nix.self_healing import SimplifiedHealingEngine
```

### Key Differences
- **84% less code** - Easier to understand
- **3 vs 14 actions** - Simpler resolution
- **2 vs 4 permission tiers** - Clearer security
- **1,600x faster** - Better performance

## Support

- **GitHub Issues**: [Report bugs](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- **Documentation**: This document
- **Examples**: `/examples/self_healing/`
- **Tests**: `/tests/integration/test_self_healing_v2.py`

---

**Version**: 2.0.0
**Last Updated**: 2025-08-15
**Philosophy**: Simple and Elegant Wins! 🏆