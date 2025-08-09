#!/usr/bin/env python3
"""
Research documentation synthesis script for Nix for Humanity
Consolidates 201 research files into high-level synthesis documents
"""

import os
from pathlib import Path
from collections import defaultdict
import re

class ResearchSynthesizer:
    def __init__(self, research_root):
        self.research_root = Path(research_root)
        self.categories = defaultdict(list)
        self.synthesis_docs = {}
        
    def categorize_research(self):
        """Categorize research files by topic"""
        print("Categorizing research files...")
        
        category_patterns = {
            'economic': ['economic', 'economy', 'reciprocity', 'value', 'currency'],
            'technical': ['technical', 'architecture', 'engineering', 'system', 'ai'],
            'philosophical': ['kosmos', 'consciousness', 'philosophy', 'meta', 'soul'],
            'ethical': ['ethical', 'moral', 'sacred', 'responsibility'],
            'decentralized': ['decentralized', 'distributed', 'blockchain', 'dao'],
            'symbiotic': ['symbiotic', 'partnership', 'collaboration', 'human-ai'],
            'implementation': ['implementation', 'guide', 'roadmap', 'practical']
        }
        
        for md_file in self.research_root.rglob("*.md"):
            file_content = md_file.read_text(errors='ignore').lower()
            file_name = md_file.name.lower()
            
            # Determine primary category
            best_category = 'general'
            max_matches = 0
            
            for category, keywords in category_patterns.items():
                matches = sum(1 for keyword in keywords 
                            if keyword in file_name or keyword in file_content[:500])
                if matches > max_matches:
                    max_matches = matches
                    best_category = category
                    
            self.categories[best_category].append(md_file)
            
        # Print category summary
        for category, files in self.categories.items():
            print(f"  {category}: {len(files)} files")
            
    def create_synthesis(self, category, files):
        """Create a synthesis document for a category"""
        synthesis = f"# {category.title()} Research Synthesis\n\n"
        synthesis += f"*Synthesized from {len(files)} research documents*\n\n"
        synthesis += "## 🎯 Executive Summary\n\n"
        
        # Extract key themes
        themes = defaultdict(int)
        key_insights = []
        
        for file in files[:20]:  # Analyze first 20 files for themes
            content = file.read_text(errors='ignore')
            
            # Extract headers as themes
            headers = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
            for header in headers:
                cleaned = header.strip().lower()
                if len(cleaned) > 5 and len(cleaned) < 50:
                    themes[cleaned] += 1
                    
            # Extract key insights (lines starting with -)
            insights = re.findall(r'^\s*-\s+(.+)$', content, re.MULTILINE)
            key_insights.extend(insights[:3])  # Top 3 from each doc
            
        # Add top themes
        synthesis += "### Key Themes\n\n"
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]
        for theme, count in top_themes:
            synthesis += f"- **{theme.title()}** (appears in {count} documents)\n"
            
        synthesis += "\n### Core Insights\n\n"
        # Add unique insights
        unique_insights = list(set(key_insights))[:15]
        for insight in unique_insights:
            if len(insight) > 20 and len(insight) < 200:
                synthesis += f"- {insight}\n"
                
        # Add document index
        synthesis += "\n## 📚 Source Documents\n\n"
        synthesis += "### Primary Sources\n\n"
        
        # Group by subdirectory
        by_subdir = defaultdict(list)
        for file in sorted(files):
            subdir = file.parent.name
            by_subdir[subdir].append(file)
            
        for subdir, subfiles in sorted(by_subdir.items()):
            synthesis += f"\n#### {subdir}\n"
            for file in subfiles[:10]:  # Limit to 10 per subdir
                relative_path = file.relative_to(self.research_root)
                synthesis += f"- [{file.stem}]({relative_path})\n"
                
        synthesis += "\n## 🔄 Integration Points\n\n"
        synthesis += "### With Core Architecture\n"
        synthesis += "- See: [System Architecture](../../02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md)\n"
        synthesis += "- See: [Backend Architecture](../../02-ARCHITECTURE/02-BACKEND-ARCHITECTURE.md)\n\n"
        
        synthesis += "### With Implementation\n"
        synthesis += "- See: [Implementation Roadmap](../../IMPLEMENTATION_ROADMAP.md)\n"
        synthesis += "- See: [Development Guide](../../03-DEVELOPMENT/README.md)\n\n"
        
        synthesis += "---\n\n"
        from datetime import datetime
        synthesis += f"*Synthesized on: {datetime.now().strftime('%Y-%m-%d')}*\n"
        
        return synthesis
        
    def generate_synthesis_docs(self):
        """Generate all synthesis documents"""
        print("\nGenerating synthesis documents...")
        
        synthesis_dir = self.research_root / "SYNTHESIS"
        synthesis_dir.mkdir(exist_ok=True)
        
        for category, files in self.categories.items():
            if files:
                synthesis_content = self.create_synthesis(category, files)
                synthesis_path = synthesis_dir / f"{category.upper()}_SYNTHESIS.md"
                
                with open(synthesis_path, 'w') as f:
                    f.write(synthesis_content)
                    
                print(f"✅ Created {synthesis_path.name}")
                self.synthesis_docs[category] = synthesis_path
                
    def create_master_index(self):
        """Create a master research index"""
        print("\nCreating master research index...")
        
        index_content = """# Research Documentation Index

## 🎯 Quick Navigation

### 📊 Research Synthesis Documents
*High-level summaries of research categories*

"""
        
        # Add synthesis docs
        for category, path in sorted(self.synthesis_docs.items()):
            relative_path = path.relative_to(self.research_root)
            index_content += f"- **[{category.title()} Research]({relative_path})** - "
            
            # Add description based on category
            descriptions = {
                'economic': "Economic models, value systems, and reciprocity frameworks",
                'technical': "Technical architecture, AI systems, and implementation details",
                'philosophical': "Consciousness, kosmos concepts, and philosophical foundations",
                'ethical': "Ethical frameworks, moral considerations, and sacred principles",
                'decentralized': "Decentralized systems, DAOs, and distributed architectures",
                'symbiotic': "Human-AI partnership, symbiotic intelligence, and collaboration",
                'implementation': "Practical guides, roadmaps, and implementation strategies"
            }
            
            index_content += descriptions.get(category, "Research synthesis") + "\n"
            
        index_content += "\n### 📁 Research Categories\n\n"
        
        # Add detailed file listings
        for category, files in sorted(self.categories.items()):
            index_content += f"\n#### {category.title()} ({len(files)} documents)\n"
            
            # Show first 5 files as examples
            for file in sorted(files)[:5]:
                relative_path = file.relative_to(self.research_root)
                index_content += f"- [{file.stem}]({relative_path})\n"
                
            if len(files) > 5:
                index_content += f"- *...and {len(files) - 5} more documents*\n"
                
        # Add statistics
        total_files = sum(len(files) for files in self.categories.values())
        index_content += f"\n## 📈 Research Statistics\n\n"
        index_content += f"- **Total Research Documents**: {total_files}\n"
        index_content += f"- **Categories**: {len(self.categories)}\n"
        index_content += f"- **Synthesis Documents**: {len(self.synthesis_docs)}\n"
        
        # Save index
        index_path = self.research_root / "INDEX.md"
        with open(index_path, 'w') as f:
            f.write(index_content)
            
        print(f"✅ Created master index at {index_path}")

def main():
    """Run the research synthesis"""
    research_root = Path(__file__).parent.parent / "docs" / "01-VISION" / "research"
    
    print("🔬 Nix for Humanity Research Synthesis")
    print("=" * 50)
    
    synthesizer = ResearchSynthesizer(research_root)
    
    # Step 1: Categorize research
    synthesizer.categorize_research()
    
    # Step 2: Generate synthesis documents
    synthesizer.generate_synthesis_docs()
    
    # Step 3: Create master index
    synthesizer.create_master_index()
    
    print("\n✨ Research synthesis complete!")
    print("Review the SYNTHESIS directory for consolidated research documents.")

if __name__ == "__main__":
    main()