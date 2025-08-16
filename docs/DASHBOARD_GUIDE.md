# 📊 Real-Time Dashboard Guide

## Overview

The Luminous Nix Self-Healing Dashboard provides real-time visualization of system health, healing metrics, and performance trends in a beautiful terminal interface.

## Features

### 🎨 Rich Dashboard (Full Features)
- **Live system metrics** - CPU, memory, disk, network
- **Healing statistics** - Issues detected/resolved, success rates
- **Event log** - Recent healing actions and system events
- **Performance trends** - Sparkline charts showing historical data
- **Auto-refresh** - Updates every second
- **Color-coded status** - Visual health indicators (🟢🟡🔴)

### 📝 Simple Dashboard (Fallback)
- **Basic metrics** - Essential system information
- **Text-based** - Works in any terminal
- **Lightweight** - Minimal dependencies

## Installation

The dashboard is included with Luminous Nix. Dependencies are managed by Poetry:

```bash
# Dependencies already included in pyproject.toml:
# - rich (for beautiful UI)
# - psutil (for system metrics)
# - aiohttp (for fetching healing metrics)
```

## Usage

### Basic Launch
```bash
# Using the launcher script
./bin/luminous-dashboard

# Or with Poetry
poetry run python -m luminous_nix.self_healing.dashboard
```

### Custom Metrics Endpoint
```bash
# Specify a different metrics URL
./bin/luminous-dashboard http://localhost:8080/metrics
```

### Running with Self-Healing Engine
```python
# The healing engine exposes metrics automatically
from luminous_nix.self_healing.healing_engine import SelfHealingEngine

engine = SelfHealingEngine()
await engine.start_monitoring()

# Metrics available at http://localhost:9090/metrics
# Dashboard will connect automatically
```

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│        🌟 Luminous Nix Self-Healing Dashboard           │
│         ⏰ 2025-01-15 12:00:00  ⬆️ Uptime: 1:23:45      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────┐  ┌─────────────────────────────────┐
│  📊 System Health   │  │    🔧 Healing Engine            │
├─────────────────────┤  ├─────────────────────────────────┤
│ CPU:     25.3% 🟢   │  │ Issues Detected:     42         │
│ Memory:  65.2% 🟡   │  │ Issues Resolved:     38         │
│ Disk:    45.1% 🟢   │  │ Success Rate:        90.5%      │
│ Temp:    72°C  🟡   │  │ Plans Generated:     38         │
│ Procs:   245   🟢   │  │ Backups Created:     12         │
├─────────────────────┤  ├─────────────────────────────────┤
│ 📈 Performance      │  │        📜 Event Log             │
├─────────────────────┤  ├─────────────────────────────────┤
│ CPU: ▂▄▅▃▇▆▄▃ 25%  │  │ 12:00:15 Resolved CPU spike     │
│ MEM: ▄▅▅▆▆▇▆▅ 65%  │  │ 11:58:42 Detected high memory   │
└─────────────────────┘  │ 11:58:43 Generated healing plan │
                         │ 11:58:45 Executed memory clear  │
                         └─────────────────────────────────┘

[q] Quit  [r] Refresh  [h] Help
```

## Metrics Displayed

### System Metrics
- **CPU Usage** - Percentage and frequency
- **CPU Temperature** - If sensors available
- **Memory** - Used/Total GB and percentage
- **Swap** - Usage if configured
- **Disk** - Root filesystem usage
- **Network** - Bytes sent/received
- **Processes** - Total running processes

### Healing Metrics
- **Issues Detected** - Total count from start
- **Issues Resolved** - Successfully healed issues
- **Success Rate** - Resolution percentage
- **Plans Generated** - Healing plans created
- **Backups Created** - Safety backups made
- **Timing Metrics** - Average operation durations

### Status Indicators
- 🟢 **Green** - Healthy (CPU <50%, Memory <70%, Disk <70%)
- 🟡 **Yellow** - Warning (CPU 50-80%, Memory 70-90%, Disk 70-90%)
- 🔴 **Red** - Critical (CPU >80%, Memory >90%, Disk >90%)

## Performance Trends

The dashboard shows sparkline charts for historical data:
- **Last 20 data points** displayed
- **Updates every second**
- **Visual trend indicators** using Unicode blocks

Example sparkline: `▁▂▃▄▅▆▇█▇▆▅▄▃▂▁`

## Keyboard Controls

- **q** - Quit dashboard
- **r** - Force refresh (automatic every 1s)
- **h** - Show help (future feature)
- **Ctrl+C** - Emergency exit

## Integration with Prometheus

The dashboard can connect to any Prometheus-compatible metrics endpoint:

```python
# Example: Custom metrics endpoint
dashboard = MetricsDashboard(
    metrics_url="http://localhost:9090/metrics"
)
```

### Expected Metrics Format
```
# HELP luminous_healing_issues_detected_total Total issues detected
# TYPE luminous_healing_issues_detected_total counter
luminous_healing_issues_detected_total 42

# HELP luminous_healing_issues_resolved_total Total issues resolved
# TYPE luminous_healing_issues_resolved_total counter
luminous_healing_issues_resolved_total 38
```

## Customization

### Creating Custom Panels
```python
from luminous_nix.self_healing.dashboard import MetricsDashboard

class CustomDashboard(MetricsDashboard):
    def create_custom_panel(self):
        table = Table(title="Custom Metrics")
        table.add_column("Metric")
        table.add_column("Value")
        
        # Add your metrics
        table.add_row("Custom 1", "Value 1")
        
        return Panel(table, title="🎯 Custom Panel")
```

### Modifying Layout
```python
def create_layout(self):
    layout = Layout()
    
    # Custom layout structure
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="custom", size=10),
        Layout(name="footer", size=3)
    )
    
    return layout
```

## Troubleshooting

### Dashboard Won't Start
```bash
# Check dependencies
poetry show | grep -E "rich|psutil|aiohttp"

# Reinstall if needed
poetry install --all-extras
```

### No Metrics Displayed
```bash
# Check if metrics endpoint is accessible
curl http://localhost:9090/metrics

# Verify healing engine is running
ps aux | grep luminous
```

### Display Issues
```bash
# Check terminal capabilities
echo $TERM

# Try simple dashboard mode
SIMPLE_DASHBOARD=1 ./bin/luminous-dashboard
```

### Performance Impact
The dashboard has minimal overhead:
- **CPU**: <1% typical usage
- **Memory**: ~20MB RAM
- **Network**: 1 request/second to metrics endpoint

## Examples

### Running with Docker
```bash
docker run -it --rm \
  --network host \
  luminous-nix \
  luminous-dashboard
```

### Running in tmux/screen
```bash
# Create new session
tmux new -s dashboard

# Run dashboard
./bin/luminous-dashboard

# Detach: Ctrl+B, D
# Reattach: tmux attach -t dashboard
```

### Monitoring Multiple Systems
```python
# Create dashboard for remote system
dashboard = MetricsDashboard(
    metrics_url="http://remote-host:9090/metrics"
)
await dashboard.run()
```

## API Reference

### MetricsDashboard Class
```python
class MetricsDashboard:
    def __init__(self, metrics_url: str = "http://localhost:9090/metrics")
    async def run(self)
    def get_system_metrics(self) -> Dict[str, Any]
    async def fetch_healing_metrics(self) -> Dict[str, Any]
    def create_layout(self) -> Layout
```

### SimpleDashboard Class
```python
class SimpleDashboard:
    def __init__(self, metrics_url: str = "http://localhost:9090/metrics")
    async def run(self)
```

## Best Practices

1. **Run in dedicated terminal** - Full-screen mode works best
2. **Use tmux/screen** - For persistent monitoring
3. **Monitor resource usage** - Watch for memory leaks
4. **Set up alerts** - Combine with alerting system
5. **Log important events** - Dashboard is for real-time view

## Future Enhancements

- 📈 Historical graphs with configurable time ranges
- 🔔 Alert notifications for critical events
- 💾 Export metrics to CSV/JSON
- 🎨 Customizable color themes
- 📱 Web-based dashboard option
- 🔍 Drill-down into specific metrics
- ⚙️ Configuration file support

---

*The dashboard brings visibility to the self-healing system's operations, making it easy to monitor system health and healing effectiveness in real-time.* 📊✨