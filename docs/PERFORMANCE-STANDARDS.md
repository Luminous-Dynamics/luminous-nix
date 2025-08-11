# ⚡ Performance Standards - Nix for Humanity

**Status**: ACTIVE
**Version**: 1.0.0
**Last Updated**: 2025-08-11
**Priority**: 🟡 MEDIUM - Critical for user experience

## 📋 Executive Summary

Performance is accessibility. Every second of delay excludes users with limited patience, attention, or time. Our performance budgets are promises to our 10 personas.

## 🎯 Core Performance Principles

1. **Speed is a Feature**: Performance is not optional
2. **Persona-Driven Budgets**: Different users have different needs
3. **Measure Everything**: If it's not measured, it's not managed
4. **Progressive Enhancement**: Fast for everyone, faster for some
5. **Fail Fast**: Better to error quickly than hang indefinitely

## ⏱️ Performance Budgets by Operation

### 🚀 Startup Performance

| Metric | Target | Maximum | Persona Impact |
|--------|--------|---------|----------------|
| **Cold Start** | <1s | 3s | Maya (ADHD) needs instant response |
| **Warm Start** | <500ms | 1s | David (tired parent) has no patience |
| **First Interaction** | <2s | 5s | Grandma Rose might think it's broken |
| **Full Feature Load** | <5s | 10s | Progressive loading for all |

```python
# Measurement code
import time
from nix_for_humanity import initialize

start = time.perf_counter()
app = initialize()
startup_time = time.perf_counter() - start

assert startup_time < 3.0, f"Startup too slow: {startup_time:.2f}s"
```

### 💬 Command Processing

| Operation | Target | Maximum | Critical For |
|-----------|--------|---------|--------------|
| **Parse Natural Language** | <100ms | 500ms | Maya (ADHD) |
| **Command Generation** | <200ms | 1s | All personas |
| **Dry Run Execution** | <500ms | 2s | Viktor (validation) |
| **Real Execution** | <2s | 30s* | Dr. Sarah (research) |

*With progress indicator after 2s

```python
# Performance monitoring decorator
from functools import wraps
import time

def performance_budget(max_seconds: float):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            if elapsed > max_seconds:
                logger.warning(
                    f"{func.__name__} exceeded budget: "
                    f"{elapsed:.2f}s > {max_seconds}s"
                )

            return result
        return wrapper
    return decorator

# Usage
@performance_budget(max_seconds=0.5)
def parse_command(text: str) -> Intent:
    # Must complete in 500ms
    pass
```

### 🎨 UI Responsiveness

| Metric | Target | Maximum | Why |
|--------|--------|---------|-----|
| **Keystroke Response** | <50ms | 100ms | Feel "instant" |
| **Button Click** | <100ms | 200ms | Acknowledge input |
| **Page Transition** | <200ms | 500ms | Maintain flow |
| **Search Results** | <300ms | 1s | Keep attention |
| **Autocomplete** | <150ms | 300ms | Feel predictive |

### 🎙️ Voice Interface (Future)

| Operation | Target | Maximum | Persona |
|-----------|--------|---------|---------|
| **Wake Word Detection** | <200ms | 500ms | Grandma Rose |
| **Speech Recognition** | <1s | 3s | Viktor (ESL) |
| **Response Generation** | <500ms | 2s | Natural conversation |
| **TTS Output Start** | <300ms | 1s | Feel responsive |

## 💾 Resource Budgets

### Memory Usage

| Component | Target | Maximum | Notes |
|-----------|--------|---------|--------|
| **Base Process** | <50MB | 100MB | Minimal footprint |
| **With TUI** | <100MB | 200MB | Textual overhead |
| **With Voice** | <200MB | 500MB | Model in memory |
| **With ML Features** | <500MB | 1GB | Optional features |
| **Cache Size** | <100MB | 500MB | Auto-cleanup |

```python
# Memory monitoring
import psutil
import os

def check_memory():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024

    if mem_mb > 100:  # Base budget
        logger.warning(f"Memory usage high: {mem_mb:.1f}MB")

    if mem_mb > 200:  # Maximum
        raise MemoryError(f"Memory limit exceeded: {mem_mb:.1f}MB")
```

### CPU Usage

| State | Target | Maximum | Duration |
|-------|--------|---------|----------|
| **Idle** | <1% | 5% | Continuous |
| **Active Command** | <30% | 80% | <5 seconds |
| **Background Tasks** | <10% | 20% | Continuous |
| **Indexing/Learning** | <50% | 100% | <30 seconds |

### Disk I/O

| Operation | Target | Maximum | Frequency |
|-----------|--------|---------|-----------|
| **Config Read** | <10ms | 50ms | Once at startup |
| **Cache Write** | <50ms | 200ms | Async only |
| **Log Write** | <5ms | 20ms | Buffered |
| **Database Query** | <20ms | 100ms | Indexed only |

## 📊 Performance Monitoring

### Required Metrics

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class PerformanceMetrics:
    """Track performance for each operation."""

    operation: str
    start_time: float
    end_time: float
    memory_before: int
    memory_after: int
    cpu_percent: float

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def memory_delta(self) -> int:
        return self.memory_after - self.memory_before

    def check_budget(self, max_seconds: float) -> bool:
        return self.duration <= max_seconds

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, list[PerformanceMetrics]] = {}

    def record(self, metric: PerformanceMetrics):
        if metric.operation not in self.metrics:
            self.metrics[metric.operation] = []
        self.metrics[metric.operation].append(metric)

        # Check for degradation
        if len(self.metrics[metric.operation]) > 10:
            self._check_trend(metric.operation)

    def _check_trend(self, operation: str):
        recent = self.metrics[operation][-10:]
        avg_duration = sum(m.duration for m in recent) / len(recent)

        if avg_duration > self.budgets[operation]:
            logger.error(
                f"Performance degradation in {operation}: "
                f"{avg_duration:.2f}s average"
            )
```

### Performance Testing

```python
import pytest
import time
from nix_for_humanity import parse_command, execute_command

class TestPerformance:
    """Performance regression tests."""

    @pytest.mark.performance
    def test_parse_speed(self, benchmark):
        """Parsing must be under 100ms."""
        result = benchmark(parse_command, "install firefox")
        assert benchmark.stats['mean'] < 0.1  # 100ms

    @pytest.mark.performance
    def test_startup_time(self):
        """Cold start must be under 3 seconds."""
        start = time.perf_counter()
        from nix_for_humanity import initialize
        app = initialize()
        duration = time.perf_counter() - start
        assert duration < 3.0, f"Startup too slow: {duration:.2f}s"

    @pytest.mark.performance
    @pytest.mark.parametrize("command,max_time", [
        ("install vim", 2.0),
        ("search editor", 1.0),
        ("list packages", 1.5),
    ])
    def test_command_performance(self, command, max_time):
        """Commands must complete within budget."""
        start = time.perf_counter()
        execute_command(command, dry_run=True)
        duration = time.perf_counter() - start
        assert duration < max_time
```

## 🚨 Performance Optimization Strategies

### 1. Lazy Loading
```python
# ✅ GOOD - Load only when needed
class NixForHumanity:
    def __init__(self):
        self._nlp_engine = None  # Lazy load

    @property
    def nlp_engine(self):
        if self._nlp_engine is None:
            self._nlp_engine = self._load_nlp_engine()
        return self._nlp_engine

# ❌ BAD - Load everything upfront
class NixForHumanity:
    def __init__(self):
        self.nlp_engine = load_nlp_engine()  # Slow startup
        self.voice_engine = load_voice_engine()  # May not be used
        self.ml_models = load_all_models()  # Definitely too much
```

### 2. Caching Strategy
```python
from functools import lru_cache
import hashlib

class PackageCache:
    def __init__(self, max_size_mb: int = 100):
        self.max_size = max_size_mb * 1024 * 1024
        self.cache = {}
        self.access_times = {}

    @lru_cache(maxsize=1000)
    def search_packages(self, query: str) -> List[Package]:
        """Cache search results for common queries."""
        return self._search_impl(query)

    def cache_key(self, query: str) -> str:
        """Generate stable cache key."""
        return hashlib.md5(query.encode()).hexdigest()
```

### 3. Progressive Enhancement
```python
class ProgressiveInterface:
    """Load features as needed."""

    def __init__(self):
        self.core_loaded = True
        self.tui_loaded = False
        self.voice_loaded = False

    async def load_tui(self):
        if not self.tui_loaded:
            # Load TUI components async
            from nix_for_humanity.tui import TUI
            self.tui = TUI()
            self.tui_loaded = True

    async def load_voice(self):
        if not self.voice_loaded:
            # Load voice components async
            from nix_for_humanity.voice import Voice
            self.voice = Voice()
            self.voice_loaded = True
```

### 4. Batch Operations
```python
# ✅ GOOD - Batch database queries
def get_packages(names: List[str]) -> List[Package]:
    query = "SELECT * FROM packages WHERE name IN (%s)" % (
        ','.join(['?'] * len(names))
    )
    return db.execute(query, names).fetchall()

# ❌ BAD - N+1 queries
def get_packages(names: List[str]) -> List[Package]:
    results = []
    for name in names:
        pkg = db.execute("SELECT * FROM packages WHERE name=?", [name])
        results.append(pkg)
    return results
```

## 📈 Performance Monitoring Dashboard

```python
def generate_performance_report() -> str:
    """Generate performance report for monitoring."""
    return f"""
    ⚡ Performance Report - {datetime.now()}
    =====================================

    Startup Metrics:
    - Cold Start: {metrics.cold_start:.2f}s (Budget: 3s)
    - Warm Start: {metrics.warm_start:.2f}s (Budget: 1s)

    Command Performance (last 100):
    - Average Parse: {metrics.avg_parse:.3f}s (Budget: 0.1s)
    - Average Execute: {metrics.avg_execute:.2f}s (Budget: 2s)
    - P95 Response: {metrics.p95_response:.2f}s
    - P99 Response: {metrics.p99_response:.2f}s

    Resource Usage:
    - Memory: {metrics.memory_mb:.1f}MB (Budget: 100MB)
    - CPU (avg): {metrics.cpu_percent:.1f}% (Budget: 30%)
    - Cache Size: {metrics.cache_mb:.1f}MB (Budget: 100MB)

    Violations:
    {format_violations(metrics.violations)}

    Recommendations:
    {generate_recommendations(metrics)}
    """
```

## 🎭 Persona-Specific Performance

### Performance Profiles

```python
PERSONA_PROFILES = {
    "grandma_rose": {
        "tolerance": "high",  # Patient
        "feedback": "immediate",  # Needs confirmation
        "timeout": 30,  # Willing to wait
    },
    "maya_adhd": {
        "tolerance": "none",  # Instant or forget
        "feedback": "continuous",  # Progress indicators
        "timeout": 5,  # Will abandon
    },
    "dr_sarah": {
        "tolerance": "medium",  # Task-focused
        "feedback": "detailed",  # Wants to know why
        "timeout": 60,  # Complex operations OK
    },
}

def adapt_performance(persona: str, operation: str):
    """Adapt performance strategy to persona."""
    profile = PERSONA_PROFILES.get(persona, {})

    if profile.get("tolerance") == "none":
        # Use aggressive caching
        # Preload likely next actions
        # Show immediate feedback
        pass
```

## 🚀 Performance Optimization Checklist

### Before Release:
- [ ] Run performance test suite
- [ ] Check all operations against budgets
- [ ] Profile memory usage over time
- [ ] Test with slow network (Viktor's connection)
- [ ] Test on minimal hardware (Marcus's old laptop)
- [ ] Verify cache cleanup works
- [ ] Check background task impact

### Optimization Priority:
1. 🔴 Operations exceeding maximum budget
2. 🟠 Operations exceeding target budget
3. 🟡 Memory leaks or growth
4. 🟢 Nice-to-have speed improvements

## 📊 Performance SLA

We commit to:
- **99% of operations** complete within target time
- **99.9% of operations** complete within maximum time
- **Zero operations** exceed 30 seconds without progress indication
- **Memory usage** stays within budget for 24-hour sessions
- **CPU usage** allows multitasking at all times

## 🎉 Summary

Performance standards ensure:
1. **Accessibility**: Fast enough for Maya's ADHD
2. **Reliability**: Predictable for Grandma Rose
3. **Efficiency**: Respects David's limited time
4. **Scalability**: Works on Marcus's hardware
5. **Trust**: Meets expectations consistently

---

*"Performance is not about speed, it's about respect for the user's time and attention."*
