#!/usr/bin/env python3
"""Pre-commit hook to detect and prevent code sprawl patterns."""

import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime

# Forbidden naming patterns that indicate sprawl
SPRAWL_PATTERNS = [
    (r'.*_enhanced\.(py|js)$', "Enhanced variant detected"),
    (r'.*_unified\.(py|js)$', "Unified variant detected"),
    (r'.*_consolidated\.(py|js)$', "Consolidated variant detected"),
    (r'.*_v\d+\.(py|js)$', "Versioned file detected (use git branches instead)"),
    (r'.*_new\.(py|js)$', "'New' variant detected"),
    (r'.*_improved\.(py|js)$', "'Improved' variant detected"),
    (r'.*_refactored\.(py|js)$', "'Refactored' variant detected"),
    (r'.*_better\.(py|js)$', "'Better' variant detected"),
    (r'.*_alt\.(py|js)$', "Alternative implementation detected"),
    (r'.*_temp\.(py|js)$', "Temporary file detected"),
]

# Known duplicate hotspots
DUPLICATE_HOTSPOTS = {
    "backends": {
        "pattern": "*backend*.py",
        "max_allowed": 1,
        "current_violators": [
            "consolidated_backend.py",
            "unified_backend.py",
            "headless_engine.py",
        ]
    },
    "ui_apps": {
        "pattern": "*app*.py",
        "path_filter": "*/ui/*",
        "max_allowed": 2,  # app.py and main_app.py ok
        "current_violators": [
            "enhanced_main_app.py",
            "enhanced_main_app_with_demo.py",
            "enhanced_tui.py",
            "consolidated_ui.py",
        ]
    },
    "voice_interfaces": {
        "pattern": "*voice*.py",
        "max_allowed": 3,  # recognition, synthesis, pipeline
        "current_violators": [
            "consolidated_voice.py",
            "voice_interface.py",
        ]
    },
}


def check_sprawl_patterns(src_dir: Path = Path('src')) -> List[Tuple[str, str]]:
    """Check for files matching sprawl patterns."""
    violations = []
    
    for pattern, description in SPRAWL_PATTERNS:
        for path in src_dir.rglob('*'):
            if path.is_file() and re.match(pattern, path.name):
                violations.append((str(path), description))
    
    return violations


def check_duplicate_implementations(src_dir: Path = Path('src')) -> Dict[str, List[str]]:
    """Check for duplicate implementations in known hotspots."""
    duplicates = {}
    
    for category, config in DUPLICATE_HOTSPOTS.items():
        pattern = config["pattern"]
        max_allowed = config["max_allowed"]
        
        # Find all matching files
        if "path_filter" in config:
            files = [f for f in src_dir.rglob(pattern) 
                    if config["path_filter"] in str(f)]
        else:
            files = list(src_dir.rglob(pattern))
        
        if len(files) > max_allowed:
            duplicates[category] = {
                "found": [str(f) for f in files],
                "count": len(files),
                "max_allowed": max_allowed,
                "overflow": len(files) - max_allowed,
                "known_violators": config.get("current_violators", [])
            }
    
    return duplicates


def calculate_sprawl_score(violations: List, duplicates: Dict) -> int:
    """Calculate overall sprawl score (lower is better)."""
    score = 0
    
    # Each naming violation adds 2 points
    score += len(violations) * 2
    
    # Each duplicate over limit adds 3 points
    for category, info in duplicates.items():
        score += info["overflow"] * 3
    
    return score


def generate_report(violations: List, duplicates: Dict, sprawl_score: int) -> str:
    """Generate human-readable report."""
    report = []
    report.append("\n" + "="*60)
    report.append("       🔍 CODE SPRAWL DETECTION REPORT")
    report.append("="*60)
    
    # Summary
    report.append(f"\n📊 Sprawl Score: {sprawl_score}")
    if sprawl_score == 0:
        report.append("✅ EXCELLENT - No sprawl detected!")
    elif sprawl_score < 5:
        report.append("🟡 GOOD - Minor sprawl detected")
    elif sprawl_score < 10:
        report.append("🟠 WARNING - Moderate sprawl detected")
    else:
        report.append("🔴 CRITICAL - Severe sprawl detected!")
    
    # Naming violations
    if violations:
        report.append("\n🚨 NAMING VIOLATIONS:")
        for filepath, description in violations:
            report.append(f"  ❌ {filepath}")
            report.append(f"     {description}")
    
    # Duplicate implementations
    if duplicates:
        report.append("\n🔁 DUPLICATE IMPLEMENTATIONS:")
        for category, info in duplicates.items():
            report.append(f"\n  {category.upper()}:")
            report.append(f"    Found: {info['count']} files (max allowed: {info['max_allowed']})")
            report.append(f"    Overflow: {info['overflow']} files need consolidation")
            report.append("    Files:")
            for f in info['found']:
                marker = "❌" if Path(f).name in info['known_violators'] else "⚠️"
                report.append(f"      {marker} {f}")
    
    # Recommendations
    if sprawl_score > 0:
        report.append("\n💡 RECOMMENDATIONS:")
        if violations:
            report.append("  1. Rename or consolidate files with sprawl patterns")
            report.append("     Instead of '_enhanced', modify the original file")
        if duplicates:
            report.append("  2. Consolidate duplicate implementations:")
            for category in duplicates:
                report.append(f"     - Merge {category} into single file")
        report.append("  3. Use git branches for experiments, not new files")
        report.append("  4. Delete old code when replacing (trust git history)")
    
    report.append("\n" + "="*60)
    return "\n".join(report)


def save_metrics(sprawl_score: int, violations: List, duplicates: Dict):
    """Save metrics for tracking over time."""
    metrics_dir = Path('metrics/sprawl')
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "sprawl_score": sprawl_score,
        "violation_count": len(violations),
        "duplicate_categories": len(duplicates),
        "details": {
            "violations": violations,
            "duplicates": {k: v["overflow"] for k, v in duplicates.items()}
        }
    }
    
    filename = f"sprawl_{datetime.now():%Y%m%d_%H%M%S}.json"
    (metrics_dir / filename).write_text(json.dumps(metrics, indent=2))


def main():
    """Main entry point."""
    src_dir = Path('src/nix_for_humanity')
    
    if not src_dir.exists():
        print("⚠️  Source directory not found. Running from project root?")
        return 0
    
    # Run checks
    violations = check_sprawl_patterns(src_dir)
    duplicates = check_duplicate_implementations(src_dir)
    sprawl_score = calculate_sprawl_score(violations, duplicates)
    
    # Generate and print report
    report = generate_report(violations, duplicates, sprawl_score)
    print(report)
    
    # Save metrics
    save_metrics(sprawl_score, violations, duplicates)
    
    # Exit with error if sprawl is too high
    if sprawl_score > 10:
        print("\n❌ COMMIT BLOCKED: Sprawl score too high!")
        print("Please consolidate duplicate code before committing.")
        return 1
    elif sprawl_score > 5:
        print("\n⚠️  WARNING: Consider consolidating code to reduce sprawl.")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
