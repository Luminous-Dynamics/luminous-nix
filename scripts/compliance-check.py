#!/usr/bin/env python3
"""
Compliance Check Script
Verifies project standards are being followed
"""

import json
import subprocess
import sys
from pathlib import Path

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, f"Command failed: {' '.join(cmd)}"


class ComplianceChecker:
    """Check compliance with project standards."""

    def __init__(self):
        self.results = {}
        self.project_root = Path(__file__).parent.parent

    def check_documentation_standards(self) -> dict[str, bool]:
        """Check documentation standards compliance."""
        print_header("📚 Documentation Standards")
        checks = {}

        # Check for required documentation files
        required_docs = [
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "docs/README.md",
            "docs/DOCUMENTATION-STANDARDS.md",
            "docs/PYTHON-PACKAGING-STANDARDS.md",
            "docs/API-VERSIONING-STANDARDS.md",
            "docs/PERFORMANCE-STANDARDS.md",
            "docs/GIT-STANDARDS.md",
        ]

        for doc in required_docs:
            filepath = self.project_root / doc
            exists = filepath.exists()
            checks[doc] = exists
            status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
            print(f"  {status} {doc}")

        return checks

    def check_python_standards(self) -> dict[str, bool]:
        """Check Python standards compliance."""
        print_header("🐍 Python Standards")
        checks = {}

        # Check for pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        checks["pyproject.toml exists"] = pyproject.exists()

        if pyproject.exists():
            content = pyproject.read_text()

            # Check for Poetry configuration
            checks["Uses Poetry"] = "[tool.poetry]" in content

            # Check for Black configuration
            checks["Black configured"] = "[tool.black]" in content
            checks["Black 88 chars"] = "line-length = 88" in content

            # Check for Ruff configuration
            checks["Ruff configured"] = "[tool.ruff]" in content

            # Check for mypy configuration
            checks["mypy configured"] = "[tool.mypy]" in content

            # Check for pytest configuration
            checks["pytest configured"] = "[tool.pytest.ini_options]" in content

        # Check for poetry.lock
        checks["poetry.lock exists"] = (self.project_root / "poetry.lock").exists()

        # Report results
        for check, passed in checks.items():
            status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
            print(f"  {status} {check}")

        return checks

    def check_git_standards(self) -> dict[str, bool]:
        """Check Git/GitHub standards compliance."""
        print_header("📝 Git/GitHub Standards")
        checks = {}

        # Check for GitHub templates
        github_files = [
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
        ]

        for filepath in github_files:
            full_path = self.project_root / filepath
            checks[filepath] = full_path.exists()
            status = f"{GREEN}✓{RESET}" if full_path.exists() else f"{RED}✗{RESET}"
            print(f"  {status} {filepath}")

        # Check for pre-commit config
        precommit = self.project_root / ".pre-commit-config.yaml"
        checks["Pre-commit config"] = precommit.exists()

        if precommit.exists():
            content = precommit.read_text()
            # Check line length consistency
            checks["Black 88 chars in pre-commit"] = (
                "'--line-length=88'" in content or "'--line-length', '88'" in content
            )
            checks["Flake8 88 chars in pre-commit"] = (
                "'--max-line-length=88'" in content
            )

        # Report additional checks
        for check, passed in [
            ("Pre-commit config", checks.get("Pre-commit config", False)),
            (
                "Black 88 chars in pre-commit",
                checks.get("Black 88 chars in pre-commit", False),
            ),
            (
                "Flake8 88 chars in pre-commit",
                checks.get("Flake8 88 chars in pre-commit", False),
            ),
        ]:
            if check not in github_files:
                status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
                print(f"  {status} {check}")

        return checks

    def check_project_structure(self) -> dict[str, bool]:
        """Check project structure compliance."""
        print_header("📂 Project Structure")
        checks = {}

        # Required directories
        required_dirs = [
            "src/nix_for_humanity",
            "tests",
            "docs",
            "bin",
            "scripts",
        ]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            checks[dir_path] = full_path.is_dir()
            status = f"{GREEN}✓{RESET}" if full_path.is_dir() else f"{RED}✗{RESET}"
            print(f"  {status} {dir_path}/")

        return checks

    def check_code_quality_tools(self) -> dict[str, bool]:
        """Check if code quality tools are available."""
        print_header("🔧 Code Quality Tools")
        checks = {}

        # Check Python version
        python_version = sys.version_info
        checks["Python 3.11+"] = python_version >= (3, 11)
        print(
            f"  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check for tools (would be via Poetry in real environment)
        tools = {
            "poetry": "poetry --version",
            "black": "black --version",
            "ruff": "ruff --version",
            "mypy": "mypy --version",
            "pytest": "pytest --version",
        }

        for tool, cmd in tools.items():
            success, _ = run_command(cmd.split())
            checks[f"{tool} available"] = success
            status = f"{GREEN}✓{RESET}" if success else f"{YELLOW}⚠{RESET}"
            print(f"  {status} {tool}")

        return checks

    def check_python_files(self) -> dict[str, int]:
        """Check Python files for basic compliance."""
        print_header("📊 Python File Analysis")
        stats = {
            "total_files": 0,
            "with_type_hints": 0,
            "with_docstrings": 0,
            "imports_future": 0,
        }

        src_dir = self.project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue

                stats["total_files"] += 1
                content = py_file.read_text()

                # Basic checks
                if "def " in content and "->" in content:
                    stats["with_type_hints"] += 1
                if '"""' in content or "'''" in content:
                    stats["with_docstrings"] += 1
                if "from __future__ import" in content:
                    stats["imports_future"] += 1

        print(f"  Total Python files: {stats['total_files']}")
        if stats["total_files"] > 0:
            print(
                f"  With type hints: {stats['with_type_hints']} ({stats['with_type_hints']*100//stats['total_files']}%)"
            )
            print(
                f"  With docstrings: {stats['with_docstrings']} ({stats['with_docstrings']*100//stats['total_files']}%)"
            )

        return stats

    def generate_report(self) -> None:
        """Generate compliance report."""
        print_header("📈 Compliance Summary")

        total_checks = 0
        passed_checks = 0

        for category, results in self.results.items():
            if isinstance(results, dict):
                for check, passed in results.items():
                    if isinstance(passed, bool):
                        total_checks += 1
                        if passed:
                            passed_checks += 1

        if total_checks > 0:
            compliance_rate = (passed_checks / total_checks) * 100

            if compliance_rate >= 90:
                color = GREEN
                status = "EXCELLENT"
            elif compliance_rate >= 70:
                color = YELLOW
                status = "GOOD"
            else:
                color = RED
                status = "NEEDS IMPROVEMENT"

            print(
                f"  Overall Compliance: {color}{compliance_rate:.1f}%{RESET} ({status})"
            )
            print(f"  Passed Checks: {passed_checks}/{total_checks}")

        # Save report
        report_file = self.project_root / "docs" / "COMPLIANCE_REPORT.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n  Report saved to: {report_file}")

    def run(self) -> None:
        """Run all compliance checks."""
        print(f"\n{GREEN}🚀 Running Compliance Checks for Nix for Humanity{RESET}")
        print(f"Project root: {self.project_root}")

        # Run all checks
        self.results["documentation"] = self.check_documentation_standards()
        self.results["python"] = self.check_python_standards()
        self.results["git"] = self.check_git_standards()
        self.results["structure"] = self.check_project_structure()
        self.results["tools"] = self.check_code_quality_tools()
        self.results["files"] = self.check_python_files()

        # Generate report
        self.generate_report()

        print(f"\n{GREEN}✅ Compliance check complete!{RESET}\n")


if __name__ == "__main__":
    checker = ComplianceChecker()
    checker.run()
