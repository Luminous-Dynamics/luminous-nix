#!/usr/bin/env python3
"""
Documentation Consistency Checker for Nix for Humanity
Ensures all documentation reflects the single source of truth (PROJECT_STATUS.yaml)
"""

import yaml
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def load_project_status() -> Dict:
    """Load the single source of truth"""
    with open('PROJECT_STATUS.yaml', 'r') as f:
        return yaml.safe_load(f)

def check_file_consistency(filepath: Path, status: Dict) -> List[str]:
    """Check if a file is consistent with PROJECT_STATUS.yaml"""
    issues = []
    
    try:
        content = filepath.read_text()
        
        # Extract version and phase info from status
        current_version = status['version']['current']
        current_phase = status['development_phase']['number']
        phase_name = status['development_phase']['name']
        phase_status = status['development_phase']['status']
        
        # Check version references
        version_patterns = [
            r'[Vv]ersion:?\s*(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+\.\d+)',
            r'"version":\s*"(\d+\.\d+\.\d+)"',
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match != current_version and match not in ['0.0.0', '1.0.0', '1.0.1', '1.1.0']:
                    # Allow historical versions but flag future ones
                    if match > current_version:
                        issues.append(f"Incorrect version '{match}' (should be {current_version})")
        
        # Check phase references
        phase_patterns = [
            r'Phase\s+(\d+).*?(?:COMPLETE|complete|Complete)',
            r'Phase\s+(\d+).*?(?:CURRENT|current|Current)',
            r'Current\s+Phase:?\s*(\d+)',
        ]
        
        for pattern in phase_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                phase_num = int(match.group(1))
                if 'COMPLETE' in match.group(0) or 'complete' in match.group(0):
                    if phase_num >= current_phase:
                        issues.append(f"Phase {phase_num} marked complete but current is {current_phase}")
                elif 'CURRENT' in match.group(0) or 'current' in match.group(0):
                    if phase_num != current_phase:
                        issues.append(f"Claims Phase {phase_num} is current but it's {current_phase}")
        
        # Check for false feature claims
        if 'voice.*?working' in content.lower() or 'voice.*?complete' in content.lower():
            if not status['reality_check'].get('voice_fully_working', False):
                if 'TODO' not in content and 'planned' not in content.lower():
                    issues.append("Claims voice is complete but reality_check says unknown/false")
                    
    except Exception as e:
        issues.append(f"Error reading file: {e}")
    
    return issues

def main():
    """Check all documentation files for consistency"""
    print("🔍 Documentation Consistency Checker")
    print("=" * 50)
    
    # Load the source of truth
    try:
        status = load_project_status()
        print(f"✅ Loaded PROJECT_STATUS.yaml")
        print(f"   Version: {status['version']['current']}")
        print(f"   Phase: {status['development_phase']['number']} - {status['development_phase']['name']}")
        print(f"   Status: {status['development_phase']['status']}")
        print()
    except Exception as e:
        print(f"❌ Failed to load PROJECT_STATUS.yaml: {e}")
        sys.exit(1)
    
    # Check all markdown files
    issues_found = False
    docs_to_check = [
        'README.md',
        'docs/README.md',
        'docs/04-OPERATIONS/CURRENT_STATUS_DASHBOARD.md',
        'docs/01-VISION/02-ROADMAP.md',
        'CHANGELOG.md',
    ]
    
    # Add all markdown files in docs/
    docs_dir = Path('docs')
    if docs_dir.exists():
        docs_to_check.extend([str(f) for f in docs_dir.rglob('*.md')])
    
    # Remove duplicates
    docs_to_check = list(set(docs_to_check))
    
    for doc_path in sorted(docs_to_check):
        filepath = Path(doc_path)
        if not filepath.exists():
            continue
            
        issues = check_file_consistency(filepath, status)
        if issues:
            issues_found = True
            print(f"❌ {doc_path}")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ {doc_path}")
    
    print()
    if issues_found:
        print("⚠️  Documentation inconsistencies found!")
        print("Please update the files to match PROJECT_STATUS.yaml")
        sys.exit(1)
    else:
        print("✨ All documentation is consistent!")
        sys.exit(0)

if __name__ == '__main__':
    main()