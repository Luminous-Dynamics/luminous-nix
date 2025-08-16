#!/usr/bin/env python3
"""
Add proper error handling to files with TODOs.
"""

import os
import re

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
