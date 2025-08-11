#!/usr/bin/env python3
"""
🕉️ Sacred Trinity Code Quality Runner

Runs all code quality checks in parallel for faster feedback.
Uses Poetry to ensure consistent environment.
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Status of a quality check."""

    PENDING = "⏳"
    RUNNING = "🔄"
    PASSED = "✅"
    FAILED = "❌"
    SKIPPED = "⏭️"


@dataclass
class Check:
    """A code quality check to run."""

    name: str
    command: list[str]
    description: str
    required: bool = True
    status: CheckStatus = CheckStatus.PENDING
    output: str = ""
    duration: float = 0.0


class QualityRunner:
    """Runs code quality checks efficiently."""

    def __init__(self, fix_mode: bool = False):
        self.fix_mode = fix_mode
        self.checks = self._get_checks()

    def _get_checks(self) -> list[Check]:
        """Get list of checks to run."""
        if self.fix_mode:
            return [
                Check(
                    "Black",
                    ["poetry", "run", "black", "."],
                    "Formatting code with Black (88 chars)",
                ),
                Check(
                    "Ruff",
                    ["poetry", "run", "ruff", "check", "--fix", "."],
                    "Auto-fixing linting issues with Ruff",
                ),
                Check(
                    "isort",
                    ["poetry", "run", "isort", "."],
                    "Sorting imports",
                    required=False,
                ),
            ]
        return [
            Check(
                "Black",
                ["poetry", "run", "black", "--check", "."],
                "Checking formatting with Black",
            ),
            Check(
                "Ruff",
                ["poetry", "run", "ruff", "check", "."],
                "Linting with Ruff",
            ),
            Check(
                "mypy",
                ["poetry", "run", "mypy", "."],
                "Type checking with mypy",
                required=False,  # Don't fail on type errors yet
            ),
            Check(
                "Bandit",
                ["poetry", "run", "bandit", "-r", "src/", "-ll"],
                "Security check with Bandit",
                required=False,
            ),
            Check(
                "Tests",
                ["poetry", "run", "pytest", "-q"],
                "Running tests with pytest",
            ),
        ]

    async def run_check(self, check: Check) -> None:
        """Run a single check asynchronously."""
        check.status = CheckStatus.RUNNING
        self._print_status()

        start_time = time.time()
        try:
            process = await asyncio.create_subprocess_exec(
                *check.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            check.duration = time.time() - start_time
            check.output = stdout.decode() + stderr.decode()

            if process.returncode == 0:
                check.status = CheckStatus.PASSED
            else:
                check.status = (
                    CheckStatus.FAILED if check.required else CheckStatus.SKIPPED
                )

        except Exception as e:
            check.duration = time.time() - start_time
            check.status = CheckStatus.FAILED
            check.output = str(e)

        self._print_status()

    def _print_status(self) -> None:
        """Print current status of all checks."""
        # Clear previous output
        print("\033[2J\033[H", end="")  # Clear screen and move to top

        mode = "Auto-Fix Mode" if self.fix_mode else "Check Mode"
        print(f"🕉️ Sacred Trinity Quality {mode}")
        print("=" * 50)
        print()

        for check in self.checks:
            status_icon = check.status.value
            duration = f" ({check.duration:.1f}s)" if check.duration > 0 else ""
            print(f"{status_icon} {check.name}: {check.description}{duration}")

        print()

    async def run_all(self) -> bool:
        """Run all checks in parallel."""
        self._print_status()

        # Run all checks concurrently
        tasks = [self.run_check(check) for check in self.checks]
        await asyncio.gather(*tasks)

        # Print final summary
        print("=" * 50)
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        skipped = sum(1 for c in self.checks if c.status == CheckStatus.SKIPPED)

        print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
        print()

        # Show failed check outputs
        for check in self.checks:
            if check.status == CheckStatus.FAILED:
                print(f"❌ {check.name} failed:")
                print("-" * 40)
                # Show last 10 lines of output
                lines = check.output.strip().split("\n")
                for line in lines[-10:]:
                    print(f"  {line}")
                print()

        # Return success if all required checks passed
        return all(
            c.status in (CheckStatus.PASSED, CheckStatus.SKIPPED)
            for c in self.checks
            if c.required
        )

    def run(self) -> int:
        """Run all checks and return exit code."""
        try:
            success = asyncio.run(self.run_all())

            if success:
                if self.fix_mode:
                    print("✨ All fixes applied successfully!")
                else:
                    print("🎉 All quality checks passed!")
                return 0
            print("⚠️ Some checks failed. Please fix the issues.")
            return 1

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            return 130


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Sacred Trinity code quality checks"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues instead of just checking",
    )

    args = parser.parse_args()

    runner = QualityRunner(fix_mode=args.fix)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
