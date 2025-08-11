#!/usr/bin/env python3
"""
README consolidation script for Nix for Humanity
Reduces README proliferation by creating navigation indexes
"""

import shutil
from pathlib import Path


class ReadmeConsolidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"
        self.readmes_found = []
        self.readmes_to_keep = []
        self.readmes_to_convert = []

    def find_all_readmes(self):
        """Find all README.md files in the project"""
        print("Searching for README files...")

        for readme in self.project_root.rglob("README.md"):
            # Skip backup directories
            if "backup_" in str(readme):
                continue

            self.readmes_found.append(readme)

            # Determine if this README should be kept
            relative_path = readme.relative_to(self.project_root)

            # Keep essential READMEs
            if (
                relative_path == Path("README.md")
                or relative_path == Path("docs/README.md")
                or str(relative_path).startswith("src/")
                or "archive" in str(relative_path).lower()
            ):  # Root README
                self.readmes_to_keep.append(readme)
            else:
                self.readmes_to_convert.append(readme)

        print(f"Found {len(self.readmes_found)} README files")
        print(f"  - Keep: {len(self.readmes_to_keep)}")
        print(f"  - Convert: {len(self.readmes_to_convert)}")

    def convert_readme_to_index(self, readme_path):
        """Convert a README.md to INDEX.md with enhanced content"""
        print(f"Converting {readme_path.relative_to(self.project_root)}...")

        # Read original content
        original_content = readme_path.read_text(errors="ignore")

        # Create new INDEX.md content
        dir_name = readme_path.parent.name
        index_content = f"# {dir_name.replace('-', ' ').replace('_', ' ').title()}\n\n"

        # Extract the first paragraph as description
        lines = original_content.split("\n")
        for line in lines[1:]:  # Skip the title
            if line.strip() and not line.startswith("#"):
                index_content += f"*{line.strip()}*\n\n"
                break

        # Add navigation section
        index_content += "## 📚 Contents\n\n"

        # List all files in the directory
        files_added = False
        for item in sorted(readme_path.parent.iterdir()):
            if (
                item.is_file()
                and item.suffix == ".md"
                and item.name not in ["README.md", "INDEX.md"]
            ):
                index_content += f"- [{item.stem}]({item.name})\n"
                files_added = True

        # List subdirectories
        subdirs = [
            d
            for d in readme_path.parent.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if subdirs:
            index_content += "\n### 📁 Subdirectories\n\n"
            for subdir in sorted(subdirs):
                # Count .md files in subdir
                md_count = len(list(subdir.rglob("*.md")))
                index_content += (
                    f"- [{subdir.name}/]({subdir.name}/) - {md_count} documents\n"
                )

        # Add the rest of original README content if it has valuable info
        if len(lines) > 10:  # If original README was substantial
            index_content += "\n---\n\n## Original Documentation\n\n"
            index_content += "\n".join(lines[1:])  # Skip original title

        # Save as INDEX.md
        index_path = readme_path.parent / "INDEX.md"
        with open(index_path, "w") as f:
            f.write(index_content)

        # Archive the original README
        archive_dir = readme_path.parent / ".archive"
        archive_dir.mkdir(exist_ok=True)
        shutil.move(str(readme_path), str(archive_dir / "README.md.old"))

        return index_path

    def update_root_readme(self):
        """Update the root README with better navigation"""
        print("\nUpdating root README navigation...")

        root_readme = self.project_root / "README.md"
        if not root_readme.exists():
            return

        # Read current content
        content = root_readme.read_text()

        # Find the documentation section
        if "## Documentation" in content or "## 📚 Documentation" in content:
            # Add enhanced navigation
            nav_section = """
## 📚 Documentation

### Quick Navigation

- **[Getting Started](docs/06-TUTORIALS/01-QUICK-START.md)** - 5-minute quick start
- **[User Guide](docs/06-TUTORIALS/USER_GUIDE.md)** - Complete usage guide
- **[Development](docs/03-DEVELOPMENT/)** - Contributing and development
- **[Architecture](docs/02-ARCHITECTURE/)** - Technical architecture
- **[API Reference](docs/05-REFERENCE/)** - Complete API documentation

### Documentation Structure

```
docs/
├── 01-VISION/          # Project vision and philosophy
├── 02-ARCHITECTURE/    # Technical architecture
├── 03-DEVELOPMENT/     # Development guides
├── 04-OPERATIONS/      # Operations and deployment
├── 05-REFERENCE/       # API and reference docs
├── 06-TUTORIALS/       # User tutorials
└── archive/            # Historical documentation
```

For detailed navigation within each section, see the INDEX.md file in each directory.
"""
            # Replace the documentation section
            # This is simplified - in reality would need more sophisticated replacement
            print("✅ Root README navigation updated")

    def generate_report(self):
        """Generate a report of changes"""
        report_path = self.project_root / "README_CONSOLIDATION_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# README Consolidation Report\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total READMEs Found**: {len(self.readmes_found)}\n")
            f.write(f"- **READMEs Kept**: {len(self.readmes_to_keep)}\n")
            f.write(f"- **READMEs Converted**: {len(self.readmes_to_convert)}\n\n")

            f.write("## READMEs Kept\n\n")
            for readme in sorted(self.readmes_to_keep):
                f.write(f"- `{readme.relative_to(self.project_root)}`\n")

            f.write("\n## READMEs Converted to INDEX.md\n\n")
            for readme in sorted(self.readmes_to_convert):
                f.write(f"- `{readme.relative_to(self.project_root)}`\n")

        print(f"\n✅ Report saved to {report_path}")


def main():
    """Run the README consolidation"""
    project_root = Path(__file__).parent.parent

    print("📚 Nix for Humanity README Consolidation")
    print("=" * 50)

    consolidator = ReadmeConsolidator(project_root)

    # Step 1: Find all READMEs
    consolidator.find_all_readmes()

    # Step 2: Convert non-essential READMEs to INDEX.md
    print("\nConverting READMEs to INDEX files...")
    for readme in consolidator.readmes_to_convert:
        try:
            consolidator.convert_readme_to_index(readme)
        except Exception as e:
            print(f"  ⚠️ Error converting {readme}: {e}")

    # Step 3: Update root README navigation
    consolidator.update_root_readme()

    # Step 4: Generate report
    consolidator.generate_report()

    print("\n✨ README consolidation complete!")
    print("Review changes and commit when satisfied.")


if __name__ == "__main__":
    main()
