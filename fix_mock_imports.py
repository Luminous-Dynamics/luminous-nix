#!/usr/bin/env python3
"""Fix missing mock imports in test files."""

import os
import re

# Find all Python test files with removed mock imports
test_files = []
for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                content = f.read()
                if "# REMOVED MOCK IMPORT" in content:
                    test_files.append(filepath)

print(f"Found {len(test_files)} files to fix")

for filepath in test_files:
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace the removed import line with proper import
    content = re.sub(
        r'# REMOVED MOCK IMPORT:.*?\n',
        'from unittest.mock import Mock, MagicMock, patch, call\n',
        content
    )
    
    # Also handle cases where the mock import is missing entirely but MagicMock is used
    if "from unittest.mock import" not in content and ("MagicMock" in content or "Mock" in content or "patch" in content):
        # Add import after other imports
        lines = content.split("\n")
        import_added = False
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                # Find the last import statement
                continue
            elif not line.strip() or line.startswith("#"):
                continue
            else:
                # This is the first non-import, non-comment line
                if not import_added and i > 0:
                    lines.insert(i, "from unittest.mock import Mock, MagicMock, patch, call")
                    import_added = True
                    break
        content = "\n".join(lines)
    
    with open(filepath, "w") as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

print("Done!")