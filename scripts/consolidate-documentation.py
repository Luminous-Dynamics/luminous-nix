#!/usr/bin/env python3
"""
Documentation consolidation script for Nix for Humanity
Helps clean up and organize the documentation structure
"""

import os
import shutil
from pathlib import Path
import hashlib
from datetime import datetime
import json

class DocumentationConsolidator:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.backup_dir = self.docs_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.duplicates = []
        self.moved_files = []
        
    def create_backup(self):
        """Create a full backup of the docs directory"""
        print(f"Creating backup in {self.backup_dir}...")
        shutil.copytree(self.docs_root, self.backup_dir)
        print("✅ Backup created successfully")
        
    def find_duplicates(self):
        """Find duplicate files based on content hash"""
        print("\nSearching for duplicate files...")
        file_hashes = {}
        
        for md_file in self.docs_root.rglob("*.md"):
            if self.backup_dir.name in str(md_file):
                continue
                
            with open(md_file, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
                
            if file_hash in file_hashes:
                self.duplicates.append({
                    'original': str(file_hashes[file_hash]),
                    'duplicate': str(md_file),
                    'hash': file_hash
                })
            else:
                file_hashes[file_hash] = md_file
                
        print(f"Found {len(self.duplicates)} duplicate files")
        return self.duplicates
        
    def consolidate_archives(self):
        """Merge archive and ARCHIVE directories"""
        print("\nConsolidating archive directories...")
        
        archive_lower = self.docs_root / "archive"
        archive_upper = self.docs_root / "ARCHIVE"
        
        # Create new structure
        new_archive = self.docs_root / "archive"
        subdirs = ["historical", "completed", "legacy", "research-detailed"]
        
        for subdir in subdirs:
            (new_archive / subdir).mkdir(parents=True, exist_ok=True)
            
        # Move files from lowercase archive
        if archive_lower.exists() and archive_lower != new_archive:
            for item in archive_lower.iterdir():
                if item.is_file():
                    dest = new_archive / "historical" / item.name
                    shutil.move(str(item), str(dest))
                    self.moved_files.append((str(item), str(dest)))
                    
        # Move files from uppercase ARCHIVE
        if archive_upper.exists():
            for item in archive_upper.rglob("*"):
                if item.is_file():
                    # Determine destination based on content
                    if "completed" in str(item).lower():
                        dest_dir = new_archive / "completed"
                    elif "legacy" in str(item).lower() or "old" in str(item).lower():
                        dest_dir = new_archive / "legacy"
                    else:
                        dest_dir = new_archive / "historical"
                        
                    dest = dest_dir / item.name
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                        self.moved_files.append((str(item), str(dest)))
                        
            # Remove empty ARCHIVE directory
            shutil.rmtree(archive_upper)
            
        print(f"✅ Moved {len(self.moved_files)} files to consolidated archive")
        
    def create_navigation_indexes(self):
        """Create INDEX.md files for main directories"""
        print("\nCreating navigation indexes...")
        
        directories = {
            "01-VISION": "Vision, Philosophy, and Research",
            "02-ARCHITECTURE": "Technical Architecture Documentation",
            "03-DEVELOPMENT": "Development Guides and Standards",
            "04-OPERATIONS": "Operations and Deployment",
            "05-REFERENCE": "API and Reference Documentation",
            "06-TUTORIALS": "User Tutorials and Guides"
        }
        
        for dir_name, description in directories.items():
            dir_path = self.docs_root / dir_name
            if dir_path.exists():
                index_content = f"# {dir_name.replace('-', ' ').title()}\n\n"
                index_content += f"*{description}*\n\n"
                index_content += "## 📚 Contents\n\n"
                
                # List all .md files in the directory
                for md_file in sorted(dir_path.rglob("*.md")):
                    if md_file.name != "INDEX.md":
                        relative_path = md_file.relative_to(dir_path)
                        index_content += f"- [{md_file.stem}]({relative_path})\n"
                        
                index_path = dir_path / "INDEX.md"
                with open(index_path, 'w') as f:
                    f.write(index_content)
                    
                print(f"✅ Created {index_path}")
                
    def generate_report(self):
        """Generate a cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'backup_location': str(self.backup_dir),
            'duplicates_found': len(self.duplicates),
            'files_moved': len(self.moved_files),
            'duplicate_details': self.duplicates,
            'moved_files': self.moved_files
        }
        
        report_path = self.docs_root / "CLEANUP_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n✅ Cleanup report saved to {report_path}")
        
        # Also create a human-readable summary
        summary_path = self.docs_root / "CLEANUP_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(f"# Documentation Cleanup Summary\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"## Results\n\n")
            f.write(f"- **Backup Created**: `{self.backup_dir.name}`\n")
            f.write(f"- **Duplicates Found**: {len(self.duplicates)}\n")
            f.write(f"- **Files Consolidated**: {len(self.moved_files)}\n\n")
            
            if self.duplicates:
                f.write("## Duplicate Files\n\n")
                for dup in self.duplicates[:10]:  # Show first 10
                    f.write(f"- `{dup['duplicate']}` duplicates `{dup['original']}`\n")
                if len(self.duplicates) > 10:
                    f.write(f"\n*...and {len(self.duplicates) - 10} more duplicates*\n")
                    
        print(f"✅ Summary saved to {summary_path}")

def main():
    """Run the documentation consolidation"""
    docs_root = Path(__file__).parent.parent / "docs"
    
    print("🧹 Nix for Humanity Documentation Cleanup")
    print("=" * 50)
    
    consolidator = DocumentationConsolidator(docs_root)
    
    # Step 1: Create backup
    consolidator.create_backup()
    
    # Step 2: Find duplicates
    consolidator.find_duplicates()
    
    # Step 3: Consolidate archives
    consolidator.consolidate_archives()
    
    # Step 4: Create navigation indexes
    consolidator.create_navigation_indexes()
    
    # Step 5: Generate report
    consolidator.generate_report()
    
    print("\n✨ Documentation cleanup complete!")
    print(f"Review the changes and run 'git add -A && git commit' when satisfied.")

if __name__ == "__main__":
    main()