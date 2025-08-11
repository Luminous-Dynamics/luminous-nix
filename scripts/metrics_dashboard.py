#!/usr/bin/env python3
"""
Standards Compliance Metrics Dashboard Generator

Collects, analyzes, and visualizes project metrics for standards compliance.
Part of the Sacred Trinity development model.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class MetricsDashboard:
    """Comprehensive metrics collection and visualization for Nix for Humanity."""

    def __init__(self, project_root: Path | None = None):
        """Initialize dashboard with project root."""
        self.project_root = project_root or Path.cwd()
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.metrics_dir / "raw").mkdir(exist_ok=True)
        (self.metrics_dir / "aggregated").mkdir(exist_ok=True)
        (self.metrics_dir / "reports").mkdir(exist_ok=True)

        self.timestamp = datetime.now()
        self.metrics: dict[str, Any] = {}

    def collect_test_coverage(self) -> dict[str, Any]:
        """Run pytest and collect coverage metrics."""
        print("📊 Collecting test coverage...")

        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "pytest",
                    "--cov=nix_for_humanity",
                    "--cov-report=json",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)

                return {
                    "timestamp": self.timestamp.isoformat(),
                    "total_coverage": data["totals"]["percent_covered"],
                    "covered_lines": data["totals"]["covered_lines"],
                    "total_lines": data["totals"]["num_statements"],
                    "files": {
                        path: {
                            "coverage": info["summary"]["percent_covered"],
                            "lines": info["summary"]["num_statements"],
                        }
                        for path, info in data.get("files", {}).items()
                    },
                }
        except Exception as e:
            print(f"  ⚠️  Coverage collection failed: {e}")

        return {
            "timestamp": self.timestamp.isoformat(),
            "error": "Coverage collection not available",
        }

    def collect_type_coverage(self) -> dict[str, Any]:
        """Run mypy and collect type coverage."""
        print("🔍 Checking type coverage...")

        try:
            # Run mypy
            result = subprocess.run(
                ["poetry", "run", "mypy", "src/", "--strict"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Parse output for statistics
            lines = result.stdout.split("\n")
            errors = []
            for line in lines:
                if ": error:" in line or ": note:" in line:
                    errors.append(line.strip())

            success = result.returncode == 0

            return {
                "timestamp": self.timestamp.isoformat(),
                "success": success,
                "errors": len(errors),
                "error_details": errors[:10],  # First 10 errors
            }
        except Exception as e:
            print(f"  ⚠️  Type checking failed: {e}")

        return {
            "timestamp": self.timestamp.isoformat(),
            "error": "Type checking not available",
        }

    def collect_lint_metrics(self) -> dict[str, Any]:
        """Run Ruff and collect linting metrics."""
        print("🔧 Running linter checks...")

        try:
            # Run Ruff
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "ruff",
                    "check",
                    "src/",
                    "tests/",
                    "scripts/",
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []

            # Categorize issues
            by_severity = {"error": 0, "warning": 0, "info": 0}
            by_rule = {}

            for issue in issues:
                # Count by severity (Ruff doesn't have severity, so we'll estimate)
                if issue.get("code", "").startswith("E"):
                    by_severity["error"] += 1
                elif issue.get("code", "").startswith("W"):
                    by_severity["warning"] += 1
                else:
                    by_severity["info"] += 1

                # Count by rule
                rule = issue.get("code", "unknown")
                by_rule[rule] = by_rule.get(rule, 0) + 1

            return {
                "timestamp": self.timestamp.isoformat(),
                "total_issues": len(issues),
                "by_severity": by_severity,
                "by_rule": dict(
                    sorted(by_rule.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "success": len(issues) == 0,
            }
        except Exception as e:
            print(f"  ⚠️  Linting failed: {e}")

        return {
            "timestamp": self.timestamp.isoformat(),
            "error": "Linting not available",
        }

    def collect_complexity_metrics(self) -> dict[str, Any]:
        """Analyze code complexity using radon."""
        print("🧩 Analyzing code complexity...")

        try:
            # Run radon for cyclomatic complexity
            result = subprocess.run(
                ["poetry", "run", "radon", "cc", "src/", "-j", "-s"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.stdout:
                data = json.loads(result.stdout)

                # Calculate statistics
                complexities = []
                complex_functions = []

                for file_path, functions in data.items():
                    for func in functions:
                        complexity = func["complexity"]
                        complexities.append(complexity)

                        if complexity > 10:  # High complexity threshold
                            complex_functions.append(
                                {
                                    "file": file_path,
                                    "function": func["name"],
                                    "complexity": complexity,
                                    "rank": func["rank"],
                                }
                            )

                avg_complexity = (
                    sum(complexities) / len(complexities) if complexities else 0
                )

                return {
                    "timestamp": self.timestamp.isoformat(),
                    "average_complexity": round(avg_complexity, 2),
                    "max_complexity": max(complexities) if complexities else 0,
                    "functions_analyzed": len(complexities),
                    "complex_functions": sorted(
                        complex_functions, key=lambda x: x["complexity"], reverse=True
                    )[:5],
                }
        except Exception as e:
            print(f"  ⚠️  Complexity analysis failed: {e}")

        return {
            "timestamp": self.timestamp.isoformat(),
            "error": "Complexity analysis not available",
        }

    def collect_performance_metrics(self) -> dict[str, Any]:
        """Measure performance metrics."""
        print("⚡ Measuring performance...")

        metrics = {}

        # Cold start time
        try:
            import time

            start = time.perf_counter()
            subprocess.run(
                [
                    "python",
                    "-c",
                    "from nix_for_humanity import initialize; initialize()",
                ],
                capture_output=True,
                cwd=self.project_root,
                timeout=5,
            )
            cold_start = int((time.perf_counter() - start) * 1000)
            metrics["cold_start_ms"] = cold_start
            metrics["cold_start_pass"] = cold_start < 3000
        except Exception as e:
            metrics["cold_start_error"] = str(e)

        # Memory usage
        try:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    """
import psutil
import os
from nix_for_humanity import initialize

process = psutil.Process(os.getpid())
app = initialize()
mem_mb = process.memory_info().rss / 1024 / 1024
print(f'{mem_mb:.1f}')
""",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5,
            )

            if result.returncode == 0:
                mem_mb = float(result.stdout.strip())
                metrics["memory_mb"] = mem_mb
                metrics["memory_pass"] = mem_mb < 100
        except Exception as e:
            metrics["memory_error"] = str(e)

        metrics["timestamp"] = self.timestamp.isoformat()
        return metrics

    def collect_documentation_metrics(self) -> dict[str, Any]:
        """Check documentation completeness."""
        print("📚 Checking documentation...")

        required_docs = [
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "docs/README.md",
            "docs/QUICK_REFERENCE.md",
            "CLAUDE.md",
            ".github/pull_request_template.md",
        ]

        metrics = {
            "timestamp": self.timestamp.isoformat(),
            "required_files": {},
            "total_required": len(required_docs),
            "total_present": 0,
        }

        for doc in required_docs:
            doc_path = self.project_root / doc
            exists = doc_path.exists()
            metrics["required_files"][doc] = exists
            if exists:
                metrics["total_present"] += 1

        metrics["completeness_percent"] = (
            metrics["total_present"] / metrics["total_required"] * 100
        )

        return metrics

    def collect_git_metrics(self) -> dict[str, Any]:
        """Collect Git repository metrics."""
        print("📊 Analyzing Git history...")

        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20", "--format=%s"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            commits = result.stdout.strip().split("\n") if result.stdout else []

            # Check conventional commits
            conventional_pattern = re.compile(
                r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
                r"(\(.+\))?: .+"
            )

            conventional = 0
            for commit in commits:
                if conventional_pattern.match(commit):
                    conventional += 1

            return {
                "timestamp": self.timestamp.isoformat(),
                "recent_commits": len(commits),
                "conventional_commits": conventional,
                "conventional_percent": (
                    (conventional / len(commits) * 100) if commits else 0
                ),
            }
        except Exception as e:
            print(f"  ⚠️  Git metrics failed: {e}")

        return {
            "timestamp": self.timestamp.isoformat(),
            "error": "Git metrics not available",
        }

    def generate_dashboard(self) -> None:
        """Generate complete dashboard with all metrics."""
        print("\n🚀 Generating Standards Compliance Dashboard...\n")

        # Collect all metrics
        self.metrics = {
            "meta": {
                "timestamp": self.timestamp.isoformat(),
                "project": "Nix for Humanity",
                "version": self._get_version(),
            },
            "coverage": self.collect_test_coverage(),
            "types": self.collect_type_coverage(),
            "linting": self.collect_lint_metrics(),
            "complexity": self.collect_complexity_metrics(),
            "performance": self.collect_performance_metrics(),
            "documentation": self.collect_documentation_metrics(),
            "git": self.collect_git_metrics(),
        }

        # Save raw metrics
        self._save_raw_metrics()

        # Generate reports
        self._generate_text_report()
        self._generate_html_dashboard()
        self._generate_markdown_report()

        print("\n✅ Dashboard generation complete!")
        print(f"   📁 Metrics saved to: {self.metrics_dir}")
        print(f"   📊 HTML Dashboard: {self.project_root / 'dashboard.html'}")
        print(
            f"   📝 Markdown Report: {self.metrics_dir / 'reports' / f'report_{self.timestamp.strftime('%Y%m%d')}.md'}"
        )

    def _get_version(self) -> str:
        """Get project version from pyproject.toml."""
        try:
            pyproject = self.project_root / "pyproject.toml"
            if pyproject.exists():
                with open(pyproject) as f:
                    for line in f:
                        if line.startswith("version = "):
                            return line.split('"')[1]
        except:
            pass
        return "unknown"

    def _save_raw_metrics(self) -> None:
        """Save raw metrics to JSON file."""
        filename = f"metrics_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.metrics_dir / "raw" / filename

        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def _generate_text_report(self) -> None:
        """Generate text summary report."""
        lines = []
        lines.append("=" * 60)
        lines.append("   📊 Nix for Humanity - Standards Compliance Report")
        lines.append(f"   {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")

        # Coverage
        if "total_coverage" in self.metrics["coverage"]:
            cov = self.metrics["coverage"]["total_coverage"]
            status = "✅" if cov >= 90 else "⚠️" if cov >= 80 else "❌"
            lines.append(f"{status} Test Coverage: {cov:.1f}%")

        # Types
        if "success" in self.metrics["types"]:
            status = "✅" if self.metrics["types"]["success"] else "❌"
            lines.append(
                f"{status} Type Checking: {'Passed' if self.metrics['types']['success'] else 'Failed'}"
            )

        # Linting
        if "total_issues" in self.metrics["linting"]:
            issues = self.metrics["linting"]["total_issues"]
            status = "✅" if issues == 0 else "⚠️" if issues < 10 else "❌"
            lines.append(f"{status} Linting Issues: {issues}")

        # Complexity
        if "average_complexity" in self.metrics["complexity"]:
            avg = self.metrics["complexity"]["average_complexity"]
            status = "✅" if avg < 5 else "⚠️" if avg < 10 else "❌"
            lines.append(f"{status} Average Complexity: {avg:.1f}")

        # Performance
        if "cold_start_ms" in self.metrics["performance"]:
            ms = self.metrics["performance"]["cold_start_ms"]
            status = "✅" if ms < 3000 else "❌"
            lines.append(f"{status} Cold Start: {ms}ms")

        # Documentation
        if "completeness_percent" in self.metrics["documentation"]:
            pct = self.metrics["documentation"]["completeness_percent"]
            status = "✅" if pct == 100 else "⚠️" if pct >= 80 else "❌"
            lines.append(f"{status} Documentation: {pct:.0f}% complete")

        # Git
        if "conventional_percent" in self.metrics["git"]:
            pct = self.metrics["git"]["conventional_percent"]
            status = "✅" if pct >= 80 else "⚠️" if pct >= 60 else "❌"
            lines.append(f"{status} Conventional Commits: {pct:.0f}%")

        lines.append("")
        lines.append("=" * 60)

        print("\n".join(lines))

    def _generate_html_dashboard(self) -> None:
        """Generate interactive HTML dashboard."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nix for Humanity - Standards Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #718096;
            font-size: 14px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .metric-title {{
            font-size: 14px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .metric-status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-success {{
            background: #c6f6d5;
            color: #22543d;
        }}
        .status-warning {{
            background: #fed7d7;
            color: #742a2a;
        }}
        .status-info {{
            background: #bee3f8;
            color: #2c5282;
        }}
        .progress-bar {{
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #38a169);
            transition: width 0.3s ease;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Nix for Humanity - Standards Compliance Dashboard</h1>
            <div class="timestamp">Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>

        <div class="metrics-grid">
            {self._generate_metric_cards()}
        </div>

        <footer>
            <p>Sacred Trinity Development Model - $200/month achieving $4.2M quality 🕉️</p>
        </footer>
    </div>
</body>
</html>"""

        with open(self.project_root / "dashboard.html", "w") as f:
            f.write(html)

    def _generate_metric_cards(self) -> str:
        """Generate HTML for metric cards."""
        cards = []

        # Test Coverage Card
        if "total_coverage" in self.metrics["coverage"]:
            cov = self.metrics["coverage"]["total_coverage"]
            status_class = "status-success" if cov >= 90 else "status-warning"
            cards.append(
                f"""
            <div class="metric-card">
                <div class="metric-title">Test Coverage</div>
                <div class="metric-value" style="color: {'#48bb78' if cov >= 90 else '#f6ad55'};">
                    {cov:.1f}%
                </div>
                <span class="metric-status {status_class}">
                    Target: ≥90%
                </span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {cov}%"></div>
                </div>
            </div>
            """
            )

        # Type Checking Card
        if "success" in self.metrics["types"]:
            success = self.metrics["types"]["success"]
            errors = self.metrics["types"].get("errors", 0)
            cards.append(
                f"""
            <div class="metric-card">
                <div class="metric-title">Type Checking</div>
                <div class="metric-value" style="color: {'#48bb78' if success else '#e53e3e'};">
                    {'✅ Passed' if success else f'❌ {errors} errors'}
                </div>
                <span class="metric-status {'status-success' if success else 'status-warning'}">
                    mypy --strict
                </span>
            </div>
            """
            )

        # Linting Card
        if "total_issues" in self.metrics["linting"]:
            issues = self.metrics["linting"]["total_issues"]
            cards.append(
                f"""
            <div class="metric-card">
                <div class="metric-title">Linting Issues</div>
                <div class="metric-value" style="color: {'#48bb78' if issues == 0 else '#f6ad55'};">
                    {issues}
                </div>
                <span class="metric-status {'status-success' if issues == 0 else 'status-warning'}">
                    Ruff checks
                </span>
            </div>
            """
            )

        # Performance Card
        if "cold_start_ms" in self.metrics["performance"]:
            ms = self.metrics["performance"]["cold_start_ms"]
            cards.append(
                f"""
            <div class="metric-card">
                <div class="metric-title">Cold Start Time</div>
                <div class="metric-value" style="color: {'#48bb78' if ms < 3000 else '#e53e3e'};">
                    {ms}ms
                </div>
                <span class="metric-status {'status-success' if ms < 3000 else 'status-warning'}">
                    Budget: <3000ms
                </span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(100, ms/3000*100)}%"></div>
                </div>
            </div>
            """
            )

        return "\n".join(cards)

    def _generate_markdown_report(self) -> None:
        """Generate detailed markdown report."""
        lines = []
        lines.append("# 📊 Standards Compliance Report")
        lines.append(f"**Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(
            f"**Project**: Nix for Humanity v{self.metrics['meta']['version']}"
        )
        lines.append("")

        lines.append("## Executive Summary")
        lines.append("")

        # Summary table
        lines.append("| Metric | Status | Value | Target |")
        lines.append("|--------|--------|-------|--------|")

        # Add metrics rows
        if "total_coverage" in self.metrics["coverage"]:
            cov = self.metrics["coverage"]["total_coverage"]
            status = "✅" if cov >= 90 else "⚠️"
            lines.append(f"| Test Coverage | {status} | {cov:.1f}% | ≥90% |")

        if "success" in self.metrics["types"]:
            status = "✅" if self.metrics["types"]["success"] else "❌"
            lines.append(
                f"| Type Checking | {status} | {'Passed' if self.metrics['types']['success'] else 'Failed'} | Pass |"
            )

        if "total_issues" in self.metrics["linting"]:
            issues = self.metrics["linting"]["total_issues"]
            status = "✅" if issues == 0 else "⚠️"
            lines.append(f"| Linting | {status} | {issues} issues | 0 |")

        lines.append("")
        lines.append("## Detailed Metrics")
        lines.append("")

        # Add detailed sections for each metric category
        for category in [
            "coverage",
            "types",
            "linting",
            "complexity",
            "performance",
            "documentation",
            "git",
        ]:
            if category in self.metrics:
                lines.append(f"### {category.title()}")
                lines.append("```json")
                lines.append(json.dumps(self.metrics[category], indent=2))
                lines.append("```")
                lines.append("")

        # Save report
        report_file = (
            self.metrics_dir
            / "reports"
            / f"report_{self.timestamp.strftime('%Y%m%d')}.md"
        )
        with open(report_file, "w") as f:
            f.write("\n".join(lines))


def main():
    """Main entry point for dashboard generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate standards compliance dashboard"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument(
        "--output-format",
        choices=["all", "html", "markdown", "json"],
        default="all",
        help="Output format",
    )

    args = parser.parse_args()

    dashboard = MetricsDashboard(args.project_root)
    dashboard.generate_dashboard()


if __name__ == "__main__":
    main()
