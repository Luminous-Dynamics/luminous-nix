"""Performance benchmarking suite for Nix for Humanity."""

import json
import os
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    
    name: str
    category: str
    duration_seconds: float
    memory_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    
    name: str
    version: str
    results: List[BenchmarkResult]
    environment: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.results:
            return {}
        
        durations = [r.duration_seconds for r in self.results if r.success]
        memory = [r.memory_mb for r in self.results if r.success]
        cpu = [r.cpu_percent for r in self.results if r.success]
        
        return {
            "total_tests": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "duration": {
                "mean": statistics.mean(durations) if durations else 0,
                "median": statistics.median(durations) if durations else 0,
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "stdev": statistics.stdev(durations) if len(durations) > 1 else 0,
            },
            "memory_mb": {
                "mean": statistics.mean(memory) if memory else 0,
                "max": max(memory) if memory else 0,
            },
            "cpu_percent": {
                "mean": statistics.mean(cpu) if cpu else 0,
                "max": max(cpu) if cpu else 0,
            },
        }
    
    def save(self, filepath: Path) -> None:
        """Save results to JSON file."""
        data = {
            "name": self.name,
            "version": self.version,
            "timestamp": self.timestamp,
            "environment": self.environment,
            "summary": self.get_summary(),
            "results": [asdict(r) for r in self.results],
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    def __init__(self, name: str, category: str = "general"):
        """Initialize benchmark.
        
        Args:
            name: Benchmark name
            category: Benchmark category
        """
        self.name = name
        self.category = category
        self.process = psutil.Process()
    
    def setup(self) -> None:
        """Setup before benchmark (override in subclasses)."""
        pass
    
    def teardown(self) -> None:
        """Cleanup after benchmark (override in subclasses)."""
        pass
    
    def run_benchmark(self) -> Any:
        """Run the actual benchmark (override in subclasses)."""
        raise NotImplementedError
    
    def execute(self, iterations: int = 1) -> BenchmarkResult:
        """Execute benchmark with measurements.
        
        Args:
            iterations: Number of iterations to run
            
        Returns:
            Benchmark result
        """
        try:
            # Setup
            self.setup()
            
            # Collect initial metrics
            self.process.cpu_percent()  # First call to initialize
            initial_memory = self.process.memory_info().rss / 1024 / 1024
            
            # Run benchmark
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                result = self.run_benchmark()
            
            duration = time.perf_counter() - start_time
            
            # Collect final metrics
            cpu_percent = self.process.cpu_percent()
            final_memory = self.process.memory_info().rss / 1024 / 1024
            memory_used = final_memory - initial_memory
            
            # Teardown
            self.teardown()
            
            return BenchmarkResult(
                name=self.name,
                category=self.category,
                duration_seconds=duration / iterations,
                memory_mb=memory_used,
                cpu_percent=cpu_percent,
                success=True,
                metadata={"iterations": iterations},
            )
            
        except Exception as e:
            return BenchmarkResult(
                name=self.name,
                category=self.category,
                duration_seconds=0,
                memory_mb=0,
                cpu_percent=0,
                success=False,
                error=str(e),
            )


# Specific benchmark implementations

class CLIBenchmark(PerformanceBenchmark):
    """Benchmark CLI command execution."""
    
    def __init__(self, command: str, args: List[str] = None):
        """Initialize CLI benchmark.
        
        Args:
            command: Command to execute
            args: Command arguments
        """
        super().__init__(f"CLI: {command}", "cli")
        self.command = command
        self.args = args or []
    
    def run_benchmark(self) -> subprocess.CompletedProcess:
        """Run CLI command."""
        cmd = [sys.executable, "-m", "nix_for_humanity.cli.main", self.command] + self.args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, "NIX_HUMANITY_PYTHON_BACKEND": "true"},
        )


class PackageSearchBenchmark(PerformanceBenchmark):
    """Benchmark package search performance."""
    
    def __init__(self, query: str):
        """Initialize search benchmark.
        
        Args:
            query: Search query
        """
        super().__init__(f"Search: {query}", "search")
        self.query = query
    
    def setup(self) -> None:
        """Import required modules."""
        from nix_for_humanity.core import NixForHumanityBackend
        self.backend = NixForHumanityBackend()
    
    def run_benchmark(self) -> List[str]:
        """Run package search."""
        return self.backend.search_packages(self.query)


class CommandExecutionBenchmark(PerformanceBenchmark):
    """Benchmark command execution performance."""
    
    def __init__(self, natural_command: str):
        """Initialize command benchmark.
        
        Args:
            natural_command: Natural language command
        """
        super().__init__(f"Command: {natural_command[:30]}...", "command")
        self.natural_command = natural_command
    
    def setup(self) -> None:
        """Import required modules."""
        from nix_for_humanity.core import NixForHumanityBackend
        self.backend = NixForHumanityBackend()
    
    def run_benchmark(self) -> str:
        """Execute natural language command."""
        return self.backend.process_natural_language(self.natural_command)


class DatabaseBenchmark(PerformanceBenchmark):
    """Benchmark database operations."""
    
    def __init__(self, operation: str, query_count: int = 100):
        """Initialize database benchmark.
        
        Args:
            operation: Database operation type
            query_count: Number of queries to execute
        """
        super().__init__(f"DB: {operation}", "database")
        self.operation = operation
        self.query_count = query_count
    
    def setup(self) -> None:
        """Setup database connection."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        self.engine = create_engine("sqlite:///nixos_knowledge.db")
        self.Session = sessionmaker(bind=self.engine)
    
    def run_benchmark(self) -> None:
        """Run database queries."""
        from nix_for_humanity.database.models import NixKnowledge
        
        session = self.Session()
        try:
            if self.operation == "read":
                for _ in range(self.query_count):
                    session.query(NixKnowledge).limit(10).all()
            elif self.operation == "write":
                for i in range(self.query_count):
                    knowledge = NixKnowledge(
                        command=f"test-{i}",
                        description=f"Test entry {i}",
                    )
                    session.add(knowledge)
                session.commit()
        finally:
            session.close()


class CacheBenchmark(PerformanceBenchmark):
    """Benchmark cache operations."""
    
    def __init__(self, operation: str, item_count: int = 1000):
        """Initialize cache benchmark.
        
        Args:
            operation: Cache operation type
            item_count: Number of items to cache
        """
        super().__init__(f"Cache: {operation}", "cache")
        self.operation = operation
        self.item_count = item_count
    
    def setup(self) -> None:
        """Setup cache."""
        from nix_for_humanity.cache.redis_cache import RedisCache
        
        self.cache = RedisCache()
        if self.operation == "read":
            # Pre-populate cache
            for i in range(self.item_count):
                self.cache.set("benchmark", f"key-{i}", f"value-{i}")
    
    def run_benchmark(self) -> None:
        """Run cache operations."""
        if self.operation == "write":
            for i in range(self.item_count):
                self.cache.set("benchmark", f"key-{i}", f"value-{i}")
        elif self.operation == "read":
            for i in range(self.item_count):
                self.cache.get("benchmark", f"key-{i}")


def run_performance_suite(verbose: bool = False) -> BenchmarkSuite:
    """Run complete performance benchmark suite.
    
    Args:
        verbose: Whether to print progress
        
    Returns:
        Benchmark suite results
    """
    benchmarks = [
        # CLI benchmarks
        CLIBenchmark("help"),
        CLIBenchmark("search", ["firefox"]),
        CLIBenchmark("install", ["--dry-run", "firefox"]),
        
        # Search benchmarks
        PackageSearchBenchmark("editor"),
        PackageSearchBenchmark("python"),
        PackageSearchBenchmark("development tools"),
        
        # Command benchmarks
        CommandExecutionBenchmark("install firefox"),
        CommandExecutionBenchmark("update my system"),
        CommandExecutionBenchmark("show installed packages"),
        
        # Database benchmarks
        DatabaseBenchmark("read", 100),
        DatabaseBenchmark("write", 50),
        
        # Cache benchmarks
        CacheBenchmark("write", 100),
        CacheBenchmark("read", 100),
    ]
    
    results = []
    
    for benchmark in benchmarks:
        if verbose:
            print(f"Running {benchmark.name}...")
        
        result = benchmark.execute(iterations=3)
        results.append(result)
        
        if verbose:
            if result.success:
                print(f"  ✓ {result.duration_seconds:.3f}s")
            else:
                print(f"  ✗ Failed: {result.error}")
    
    # Collect environment info
    environment = {
        "python_version": sys.version,
        "platform": sys.platform,
        "cpu_count": psutil.cpu_count(),
        "memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
        "nix_backend": os.getenv("NIX_HUMANITY_PYTHON_BACKEND", "false"),
    }
    
    suite = BenchmarkSuite(
        name="Nix for Humanity Performance Suite",
        version="1.2.0",
        results=results,
        environment=environment,
    )
    
    return suite


def compare_benchmarks(
    baseline: BenchmarkSuite,
    current: BenchmarkSuite,
    threshold: float = 0.1,
) -> Dict[str, Any]:
    """Compare two benchmark suites.
    
    Args:
        baseline: Baseline benchmark suite
        current: Current benchmark suite
        threshold: Performance regression threshold (10% default)
        
    Returns:
        Comparison results
    """
    comparison = {
        "baseline": baseline.name,
        "current": current.name,
        "regressions": [],
        "improvements": [],
        "unchanged": [],
    }
    
    baseline_results = {r.name: r for r in baseline.results}
    
    for current_result in current.results:
        if current_result.name not in baseline_results:
            continue
        
        baseline_result = baseline_results[current_result.name]
        
        if not (current_result.success and baseline_result.success):
            continue
        
        change = (current_result.duration_seconds - baseline_result.duration_seconds) / baseline_result.duration_seconds
        
        result_comparison = {
            "name": current_result.name,
            "baseline": baseline_result.duration_seconds,
            "current": current_result.duration_seconds,
            "change_percent": change * 100,
        }
        
        if change > threshold:
            comparison["regressions"].append(result_comparison)
        elif change < -threshold:
            comparison["improvements"].append(result_comparison)
        else:
            comparison["unchanged"].append(result_comparison)
    
    return comparison


if __name__ == "__main__":
    # Run benchmarks
    print("🚀 Running Nix for Humanity Performance Benchmarks...")
    print("=" * 60)
    
    suite = run_performance_suite(verbose=True)
    
    print("\n📊 Summary:")
    print("-" * 60)
    
    summary = suite.get_summary()
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Mean duration: {summary['duration']['mean']:.3f}s")
    print(f"Median duration: {summary['duration']['median']:.3f}s")
    print(f"Max memory: {summary['memory_mb']['max']:.1f}MB")
    
    # Save results
    results_dir = Path("benchmark_results")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = results_dir / f"benchmark_{timestamp}.json"
    
    suite.save(filepath)
    print(f"\n💾 Results saved to: {filepath}")
    
    # Check for regressions if baseline exists
    baseline_path = results_dir / "baseline.json"
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline_data = json.load(f)
            baseline = BenchmarkSuite(
                name=baseline_data["name"],
                version=baseline_data["version"],
                results=[BenchmarkResult(**r) for r in baseline_data["results"]],
                environment=baseline_data["environment"],
                timestamp=baseline_data["timestamp"],
            )
        
        comparison = compare_benchmarks(baseline, suite)
        
        if comparison["regressions"]:
            print("\n⚠️ Performance Regressions Detected:")
            for reg in comparison["regressions"]:
                print(f"  - {reg['name']}: {reg['change_percent']:+.1f}%")
            sys.exit(1)
        else:
            print("\n✅ No performance regressions detected!")
    
    print("\n🎯 All benchmarks complete!")