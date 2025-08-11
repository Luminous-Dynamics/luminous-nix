#!/usr/bin/env python3
"""
Weekly Standards Compliance Report Generator

Aggregates metrics from the past week and generates a comprehensive report.
Part of the Sacred Trinity development model.
"""

import json
import statistics
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class WeeklyReportGenerator:
    """Generate weekly standards compliance reports."""

    def __init__(self, project_root: Path | None = None):
        """Initialize report generator."""
        self.project_root = project_root or Path.cwd()
        self.metrics_dir = self.project_root / "metrics"
        self.today = datetime.now()
        self.week_start = self.today - timedelta(days=7)

    def collect_week_metrics(self) -> list[dict[str, Any]]:
        """Collect all metrics from the past week."""
        metrics = []
        raw_dir = self.metrics_dir / "raw"

        if not raw_dir.exists():
            return metrics

        for metric_file in raw_dir.glob("metrics_*.json"):
            try:
                # Parse timestamp from filename
                timestamp_str = metric_file.stem.replace("metrics_", "")
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                # Check if within past week
                if file_date >= self.week_start:
                    with open(metric_file) as f:
                        data = json.load(f)
                        metrics.append(data)
            except Exception as e:
                print(f"Error reading {metric_file}: {e}")

        return sorted(metrics, key=lambda x: x["meta"]["timestamp"])

    def calculate_trends(self, metrics: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate trends from weekly metrics."""
        trends = {
            "coverage": [],
            "type_errors": [],
            "lint_issues": [],
            "complexity": [],
            "cold_start": [],
            "memory": [],
            "conventional_commits": [],
        }

        for m in metrics:
            # Coverage trend
            if "coverage" in m and "total_coverage" in m["coverage"]:
                trends["coverage"].append(m["coverage"]["total_coverage"])

            # Type errors trend
            if "types" in m and "errors" in m["types"]:
                trends["type_errors"].append(m["types"]["errors"])

            # Lint issues trend
            if "linting" in m and "total_issues" in m["linting"]:
                trends["lint_issues"].append(m["linting"]["total_issues"])

            # Complexity trend
            if "complexity" in m and "average_complexity" in m["complexity"]:
                trends["complexity"].append(m["complexity"]["average_complexity"])

            # Performance trends
            if "performance" in m:
                if "cold_start_ms" in m["performance"]:
                    trends["cold_start"].append(m["performance"]["cold_start_ms"])
                if "memory_mb" in m["performance"]:
                    trends["memory"].append(m["performance"]["memory_mb"])

            # Git trends
            if "git" in m and "conventional_percent" in m["git"]:
                trends["conventional_commits"].append(m["git"]["conventional_percent"])

        return trends

    def analyze_trends(self, trends: dict[str, list[float]]) -> dict[str, Any]:
        """Analyze trends and generate insights."""
        analysis = {}

        for metric, values in trends.items():
            if not values:
                analysis[metric] = {"status": "no_data"}
                continue

            current = values[-1] if values else 0
            previous = values[0] if len(values) > 1 else current

            # Calculate statistics
            analysis[metric] = {
                "current": current,
                "previous": previous,
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "trend": (
                    "improving"
                    if current > previous
                    else "declining" if current < previous else "stable"
                ),
                "data_points": len(values),
            }

            # Add specific insights
            if metric == "coverage":
                analysis[metric]["target"] = 90
                analysis[metric]["meets_target"] = current >= 90
            elif metric == "type_errors" or metric == "lint_issues":
                analysis[metric]["target"] = 0
                analysis[metric]["meets_target"] = current == 0
            elif metric == "cold_start":
                analysis[metric]["target"] = 3000
                analysis[metric]["meets_target"] = current < 3000

        return analysis

    def get_git_activity(self) -> dict[str, Any]:
        """Get Git activity for the week."""
        try:
            # Get commits from past week
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--since",
                    "1 week ago",
                    "--oneline",
                    "--format=%H|%s|%an|%ae",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        commits.append(
                            {
                                "hash": parts[0][:7],
                                "message": parts[1],
                                "author": parts[2],
                                "email": parts[3],
                            }
                        )

            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--stat", "HEAD@{1 week ago}..HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            stats_lines = result.stdout.strip().split("\n")
            files_changed = len(stats_lines) - 1 if stats_lines else 0

            return {
                "commits": len(commits),
                "authors": len(set(c["author"] for c in commits)),
                "files_changed": files_changed,
                "commit_list": commits[:10],  # First 10 commits
            }
        except Exception as e:
            print(f"Error getting Git activity: {e}")
            return {"error": str(e)}

    def generate_action_items(self, analysis: dict[str, Any]) -> list[str]:
        """Generate action items based on analysis."""
        actions = []

        # Coverage actions
        if "coverage" in analysis and not analysis["coverage"].get(
            "meets_target", True
        ):
            actions.append(
                f"📈 Increase test coverage from {analysis['coverage']['current']:.1f}% to 90%"
            )

        # Type errors
        if "type_errors" in analysis and analysis["type_errors"].get("current", 0) > 0:
            actions.append(
                f"🔍 Fix {int(analysis['type_errors']['current'])} type errors"
            )

        # Linting
        if "lint_issues" in analysis and analysis["lint_issues"].get("current", 0) > 5:
            actions.append(
                f"🧹 Resolve {int(analysis['lint_issues']['current'])} linting issues"
            )

        # Performance
        if "cold_start" in analysis and not analysis["cold_start"].get(
            "meets_target", True
        ):
            actions.append(
                f"⚡ Optimize cold start time (currently {int(analysis['cold_start']['current'])}ms)"
            )

        # Complexity
        if "complexity" in analysis and analysis["complexity"].get("current", 0) > 10:
            actions.append(
                f"🔧 Refactor complex functions (avg complexity: {analysis['complexity']['current']:.1f})"
            )

        return actions

    def generate_report(self) -> str:
        """Generate the complete weekly report."""
        print("📊 Generating Weekly Standards Report...")

        # Collect data
        metrics = self.collect_week_metrics()
        trends = self.calculate_trends(metrics)
        analysis = self.analyze_trends(trends)
        git_activity = self.get_git_activity()
        action_items = self.generate_action_items(analysis)

        # Build report
        lines = []
        lines.append("# 📊 Weekly Standards Report")
        lines.append(
            f"**Week of**: {self.week_start.strftime('%Y-%m-%d')} to {self.today.strftime('%Y-%m-%d')}"
        )
        lines.append(f"**Generated**: {self.today.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Executive Summary
        lines.append("## 📋 Executive Summary")
        lines.append("")

        # Calculate overall compliance
        compliance_score = 100
        if analysis.get("coverage", {}).get("current", 0) < 90:
            compliance_score -= 10
        if analysis.get("type_errors", {}).get("current", 0) > 0:
            compliance_score -= 15
        if analysis.get("lint_issues", {}).get("current", 0) > 0:
            compliance_score -= 10
        if analysis.get("cold_start", {}).get("current", 0) > 3000:
            compliance_score -= 10

        status_emoji = (
            "🌟" if compliance_score >= 90 else "⚠️" if compliance_score >= 70 else "❌"
        )
        lines.append(f"**Overall Compliance**: {compliance_score}% {status_emoji}")
        lines.append(f"**Data Points Analyzed**: {len(metrics)}")
        lines.append(
            f"**Git Activity**: {git_activity.get('commits', 0)} commits by {git_activity.get('authors', 0)} authors"
        )
        lines.append("")

        # Key Metrics Table
        lines.append("## 📊 Key Metrics")
        lines.append("")
        lines.append("| Metric | Current | Previous | Trend | Target | Status |")
        lines.append("|--------|---------|----------|-------|--------|--------|")

        # Add metric rows
        if "coverage" in analysis and analysis["coverage"]["status"] != "no_data":
            a = analysis["coverage"]
            trend_arrow = (
                "↑"
                if a["trend"] == "improving"
                else "↓" if a["trend"] == "declining" else "→"
            )
            status = "✅" if a.get("meets_target", False) else "❌"
            lines.append(
                f"| Test Coverage | {a['current']:.1f}% | {a['previous']:.1f}% | {trend_arrow} | ≥90% | {status} |"
            )

        if "type_errors" in analysis and analysis["type_errors"]["status"] != "no_data":
            a = analysis["type_errors"]
            trend_arrow = (
                "↓"
                if a["trend"] == "improving"
                else "↑" if a["trend"] == "declining" else "→"
            )
            status = "✅" if a.get("meets_target", False) else "❌"
            lines.append(
                f"| Type Errors | {int(a['current'])} | {int(a['previous'])} | {trend_arrow} | 0 | {status} |"
            )

        if "lint_issues" in analysis and analysis["lint_issues"]["status"] != "no_data":
            a = analysis["lint_issues"]
            trend_arrow = (
                "↓"
                if a["trend"] == "improving"
                else "↑" if a["trend"] == "declining" else "→"
            )
            status = "✅" if a.get("meets_target", False) else "⚠️"
            lines.append(
                f"| Lint Issues | {int(a['current'])} | {int(a['previous'])} | {trend_arrow} | 0 | {status} |"
            )

        if "cold_start" in analysis and analysis["cold_start"]["status"] != "no_data":
            a = analysis["cold_start"]
            trend_arrow = (
                "↓"
                if a["trend"] == "improving"
                else "↑" if a["trend"] == "declining" else "→"
            )
            status = "✅" if a.get("meets_target", False) else "❌"
            lines.append(
                f"| Cold Start | {int(a['current'])}ms | {int(a['previous'])}ms | {trend_arrow} | <3000ms | {status} |"
            )

        lines.append("")

        # Trends and Insights
        lines.append("## 📈 Trends & Insights")
        lines.append("")

        improving = []
        declining = []
        stable = []

        for metric, a in analysis.items():
            if a.get("status") == "no_data":
                continue
            if a.get("trend") == "improving":
                improving.append(metric.replace("_", " ").title())
            elif a.get("trend") == "declining":
                declining.append(metric.replace("_", " ").title())
            else:
                stable.append(metric.replace("_", " ").title())

        if improving:
            lines.append(f"**✅ Improving**: {', '.join(improving)}")
        if declining:
            lines.append(f"**⚠️ Declining**: {', '.join(declining)}")
        if stable:
            lines.append(f"**→ Stable**: {', '.join(stable)}")

        lines.append("")

        # Git Activity
        lines.append("## 🔄 Git Activity")
        lines.append("")
        if "error" not in git_activity:
            lines.append(f"- **Commits**: {git_activity['commits']}")
            lines.append(f"- **Authors**: {git_activity['authors']}")
            lines.append(f"- **Files Changed**: {git_activity['files_changed']}")

            if git_activity.get("commit_list"):
                lines.append("")
                lines.append("### Recent Commits")
                for commit in git_activity["commit_list"][:5]:
                    lines.append(
                        f"- `{commit['hash']}` {commit['message']} ({commit['author']})"
                    )
        else:
            lines.append(f"Error collecting Git activity: {git_activity['error']}")

        lines.append("")

        # Action Items
        lines.append("## 🎯 Action Items")
        lines.append("")
        if action_items:
            for i, action in enumerate(action_items, 1):
                lines.append(f"{i}. {action}")
        else:
            lines.append("✨ All standards are being met! Keep up the great work!")

        lines.append("")

        # Recommendations
        lines.append("## 💡 Recommendations")
        lines.append("")

        if compliance_score < 70:
            lines.append("### Critical Actions Needed")
            lines.append("- Schedule team meeting to address standards violations")
            lines.append("- Consider pausing feature development to focus on quality")
            lines.append("- Review and update development workflows")
        elif compliance_score < 90:
            lines.append("### Suggested Improvements")
            lines.append("- Increase focus on test coverage")
            lines.append("- Schedule code review session for complex functions")
            lines.append("- Update pre-commit hooks to catch issues earlier")
        else:
            lines.append("### Maintain Excellence")
            lines.append("- Continue current practices")
            lines.append("- Consider documenting successful patterns")
            lines.append("- Share knowledge with team")

        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by the Sacred Trinity development model*")
        lines.append("*$200/month achieving $4.2M quality* 🕉️")

        return "\n".join(lines)

    def save_report(self, content: str) -> Path:
        """Save the report to file."""
        report_dir = self.metrics_dir / "reports"
        report_dir.mkdir(exist_ok=True)

        filename = f"weekly_report_{self.today.strftime('%Y_%W')}.md"
        filepath = report_dir / filename

        with open(filepath, "w") as f:
            f.write(content)

        return filepath


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly standards report")
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument("--output", type=Path, help="Output file path")
    parser.add_argument(
        "--email", action="store_true", help="Format for email (simplified)"
    )

    args = parser.parse_args()

    generator = WeeklyReportGenerator(args.project_root)
    report = generator.generate_report()

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"✅ Report saved to: {args.output}")
    else:
        filepath = generator.save_report(report)
        print(f"✅ Report saved to: {filepath}")

    # Also print to console
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
