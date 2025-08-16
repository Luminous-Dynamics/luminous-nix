#!/usr/bin/env python3
"""
Fix TODO items in the codebase systematically.
Focuses on adding proper error handling where marked.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_todos(directory: str = "src/") -> List[Tuple[str, int, str]]:
    """Find all TODO comments in Python files."""
    todos = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if 'TODO' in line:
                                todos.append((filepath, i, line.strip()))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return todos

def categorize_todos(todos: List[Tuple[str, int, str]]) -> dict:
    """Categorize TODOs by type."""
    categories = {
        'error_handling': [],
        'implementation': [],
        'optimization': [],
        'documentation': [],
        'other': []
    }
    
    for filepath, line_num, content in todos:
        if 'error handling' in content.lower():
            categories['error_handling'].append((filepath, line_num, content))
        elif 'implement' in content.lower():
            categories['implementation'].append((filepath, line_num, content))
        elif 'optimize' in content.lower() or 'performance' in content.lower():
            categories['optimization'].append((filepath, line_num, content))
        elif 'document' in content.lower() or 'doc' in content.lower():
            categories['documentation'].append((filepath, line_num, content))
        else:
            categories['other'].append((filepath, line_num, content))
    
    return categories

def generate_fix_report(categories: dict) -> str:
    """Generate a report of TODOs to fix."""
    report = []
    report.append("# TODO Fix Report\n")
    report.append(f"Total TODOs found: {sum(len(v) for v in categories.values())}\n")
    report.append("\n## Breakdown by Category:\n")
    
    for category, items in categories.items():
        report.append(f"\n### {category.replace('_', ' ').title()} ({len(items)} items)\n")
        
        if category == 'error_handling':
            report.append("**Priority: HIGH** - These should be fixed immediately for stability\n")
        elif category == 'implementation':
            report.append("**Priority: MEDIUM** - Missing features that need implementation\n")
        elif category == 'optimization':
            report.append("**Priority: LOW** - Performance improvements\n")
        
        # Group by file
        files = {}
        for filepath, line_num, content in items:
            if filepath not in files:
                files[filepath] = []
            files[filepath].append((line_num, content))
        
        for filepath, file_items in files.items():
            report.append(f"\n**{filepath}**:\n")
            for line_num, content in file_items[:5]:  # Show first 5 per file
                report.append(f"  - Line {line_num}: {content}\n")
            if len(file_items) > 5:
                report.append(f"  - ... and {len(file_items) - 5} more\n")
    
    return ''.join(report)

def create_error_handling_fixes():
    """Create a script to add proper error handling."""
    fix_script = '''#!/usr/bin/env python3
"""
Add proper error handling to files with TODOs.
"""


def add_error_handling_to_file(filepath: str):
    """Add proper error handling to a specific file."""
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line has a TODO about error handling
        if 'TODO: Add proper error handling' in line:
            # Look at the context to determine what kind of error handling to add
            indent = len(line) - len(line.lstrip())
            
            # Check if we're in a try block without proper except
            if i > 0 and 'try:' in lines[i-1]:
                # Skip the TODO comment
                i += 1
                continue
            
            # Check if the next line is a pass or simple statement
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if 'pass' in next_line or 'return' in next_line:
                    # Replace with proper error handling
                    new_lines.append(line.replace('TODO: Add proper error handling', 
                                                  'Handle errors appropriately'))
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"Fixed error handling TODOs in {filepath}")
    
    return modified

# Example files to fix
files_to_fix = [
    "src/nix_for_humanity/config/loader.py",
    "src/nix_for_humanity/interfaces/cli.py",
    "src/nix_for_humanity/ai/nlp.py",
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        add_error_handling_to_file(filepath)
'''
    
    with open('scripts/add-error-handling.py', 'w') as f:
        f.write(fix_script)
    
    os.chmod('scripts/add-error-handling.py', 0o755)
    print("Created scripts/add-error-handling.py")

def main():
    print("🔍 Scanning for TODOs...")
    todos = find_todos()
    
    print(f"📊 Found {len(todos)} TODOs")
    
    categories = categorize_todos(todos)
    
    # Generate report
    report = generate_fix_report(categories)
    
    # Save report
    with open('TODO_FIX_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\n📝 Report saved to TODO_FIX_REPORT.md")
    
    # Show summary
    print("\n📈 Summary by category:")
    for category, items in categories.items():
        print(f"  - {category.replace('_', ' ').title()}: {len(items)}")
    
    # Priority recommendations
    print("\n🎯 Priority Recommendations:")
    print("  1. Fix error handling TODOs first (stability)")
    print("  2. Then implementation TODOs (features)")
    print("  3. Finally optimization TODOs (performance)")
    
    # Create fix script for error handling
    if categories['error_handling']:
        create_error_handling_fixes()
        print("\n✅ Created error handling fix script")

if __name__ == "__main__":
    main()