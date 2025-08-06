# Knowledge Base Engine
"""
Manages NixOS knowledge and package information
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from .interface import IntentType


@dataclass
class PackageInfo:
    """Information about a NixOS package"""
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    installation_methods: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.installation_methods is None:
            self.installation_methods = []


class KnowledgeBase:
    """Centralized knowledge about NixOS operations"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to user's config directory
            db_path = Path.home() / ".config" / "nix-for-humanity" / "knowledge.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_db()
        self._init_knowledge()
        
    def _init_db(self):
        """Initialize the knowledge database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Solutions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY,
                intent TEXT NOT NULL,
                category TEXT NOT NULL,
                solution TEXT NOT NULL,
                example TEXT,
                explanation TEXT,
                related TEXT
            )
        ''')
        
        # Common problems table
        c.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                symptom TEXT NOT NULL,
                cause TEXT NOT NULL,
                solution TEXT NOT NULL,
                prevention TEXT
            )
        ''')
        
        # Package cache table
        c.execute('''
            CREATE TABLE IF NOT EXISTS package_cache (
                id INTEGER PRIMARY KEY,
                search_term TEXT NOT NULL,
                results TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(search_term)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_knowledge(self):
        """Populate with essential NixOS knowledge"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if already populated
        c.execute("SELECT COUNT(*) FROM solutions")
        if c.fetchone()[0] > 0:
            conn.close()
            return
            
        solutions = [
            # Package management
            ('install', 'package', 'Use declarative or imperative installation', 
             'nix profile install nixpkgs#firefox', 
             'Modern Nix uses profile commands for user packages', 
             'search,remove'),
            
            ('search', 'package', 'Search using nix search or online', 
             'nix search nixpkgs firefox', 
             'Use search.nixos.org for web interface', 
             'install'),
            
            ('remove', 'package', 'Remove packages from profile', 
             'nix profile remove firefox', 
             'For declarative, remove from configuration.nix', 
             'install'),
            
            # System management
            ('update', 'system', 'Update channels and rebuild', 
             'sudo nix-channel --update && sudo nixos-rebuild switch', 
             'Updates all packages and system configuration', 
             'rollback'),
            
            ('rollback', 'system', 'Boot previous generation', 
             'sudo nixos-rebuild switch --rollback', 
             'Every rebuild creates a new generation you can rollback to', 
             'update,generations'),
            
            ('generations', 'system', 'Show system generations', 
             'sudo nix-env --list-generations --profile /nix/var/nix/profiles/system', 
             'Each generation is a complete system snapshot', 
             'rollback'),
            
            # Network
            ('wifi', 'network', 'Enable NetworkManager or check hardware', 
             'networking.networkmanager.enable = true;', 
             'Most WiFi issues are solved by enabling NetworkManager', 
             'network'),
            
            # Help
            ('help', 'general', 'Show available commands and examples',
             'ask-nix help',
             'Natural language interface for NixOS',
             'install,search,update'),
        ]
        
        for solution in solutions:
            c.execute('''
                INSERT OR IGNORE INTO solutions 
                (intent, category, solution, example, explanation, related)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', solution)
            
        # Common problems
        problems = [
            ('command not found', 'Package not in PATH', 
             'Install package or use nix-shell', 
             'Use declarative installation when possible'),
             
            ('read-only file system', 'Trying to modify /etc directly', 
             'Edit configuration.nix instead', 
             'NixOS manages /etc through configuration'),
             
            ('infinite recursion', 'Circular dependency in config', 
             'Check for recursive definitions', 
             'Use mkForce or mkDefault for overrides'),
             
            ('attribute missing', 'Package or option not found',
             'Check spelling and nixpkgs version',
             'Use nix search to find correct attribute name'),
        ]
        
        for problem in problems:
            c.execute('''
                INSERT OR IGNORE INTO problems
                (symptom, cause, solution, prevention)
                VALUES (?, ?, ?, ?)
            ''', problem)
            
        conn.commit()
        conn.close()
        
    def get_solution(self, intent_type: IntentType) -> Dict:
        """Get solution for a specific intent type"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Map IntentType enum to string
        intent_map = {
            IntentType.INSTALL: 'install',
            IntentType.REMOVE: 'remove',
            IntentType.UPDATE: 'update',
            IntentType.SEARCH: 'search',
            IntentType.ROLLBACK: 'rollback',
            IntentType.INFO: 'generations',
            IntentType.HELP: 'help',
        }
        
        intent_str = intent_map.get(intent_type, 'unknown')
        
        c.execute('''
            SELECT solution, example, explanation, related
            FROM solutions
            WHERE intent = ?
        ''', (intent_str,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return {
                'found': False,
                'suggestion': "I don't understand that yet. Try 'help' to see what I can do."
            }
            
        solution, example, explanation, related = result
        
        return {
            'found': True,
            'solution': solution,
            'example': example,
            'explanation': explanation,
            'related': related.split(',') if related else []
        }
        
    def get_install_methods(self, package: str) -> List[Dict[str, str]]:
        """Get all installation methods for a package"""
        methods = []
        
        # Declarative method (recommended)
        methods.append({
            'name': 'Declarative (Recommended)',
            'description': 'Add to your system configuration for permanent installation',
            'command': 'Edit /etc/nixos/configuration.nix',
            'example': f'environment.systemPackages = with pkgs; [ {package} ];'
        })
        
        # Home Manager method
        methods.append({
            'name': 'Home Manager',
            'description': 'User-specific declarative installation',
            'command': 'Edit ~/.config/home-manager/home.nix',
            'example': f'home.packages = with pkgs; [ {package} ];'
        })
        
        # Imperative method (nix profile)
        methods.append({
            'name': 'Imperative (Quick)',
            'description': 'Install for current user immediately',
            'command': f'nix profile install nixpkgs#{package}',
            'example': f'nix profile install nixpkgs#{package}'
        })
        
        # Temporary shell method
        methods.append({
            'name': 'Temporary Shell',
            'description': 'Try without installing permanently',
            'command': f'nix-shell -p {package}',
            'example': f'nix-shell -p {package}'
        })
        
        return methods
        
    def search_packages(self, query: str) -> List[PackageInfo]:
        """Search for packages in the knowledge base"""
        # This would integrate with nix search in the real implementation
        # For now, return empty list
        return []
        
    def get_problem_solution(self, error: str) -> Optional[Dict[str, str]]:
        """Find solution for a specific error"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Search for matching problems
        c.execute('''
            SELECT symptom, cause, solution, prevention
            FROM problems
            WHERE symptom LIKE ? OR cause LIKE ?
        ''', (f'%{error}%', f'%{error}%'))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            symptom, cause, solution, prevention = result
            return {
                'symptom': symptom,
                'cause': cause,
                'solution': solution,
                'prevention': prevention
            }
        
        return None
        
    def cache_search_results(self, search_term: str, results: List[Dict]):
        """Cache package search results"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO package_cache (search_term, results)
            VALUES (?, ?)
        ''', (search_term, json.dumps(results)))
        
        conn.commit()
        conn.close()
        
    def get_cached_search(self, search_term: str) -> Optional[List[Dict]]:
        """Get cached search results if available and recent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Cache expires after 24 hours
        c.execute('''
            SELECT results FROM package_cache
            WHERE search_term = ? 
            AND datetime(timestamp) > datetime('now', '-1 day')
        ''', (search_term,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        
        return None
    
    def update_package_cache(self, package_name: str, exists: bool):
        """Update package existence in cache"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Store package existence information
        c.execute('''
            INSERT OR REPLACE INTO package_cache (search_term, results)
            VALUES (?, ?)
        ''', (f"exists:{package_name}", json.dumps({"exists": exists})))
        
        conn.commit()
        conn.close()
    
    def check_package_exists(self, package_name: str) -> bool:
        """Check if package exists in cache"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Look for package existence information
        c.execute('''
            SELECT results FROM package_cache
            WHERE search_term = ?
        ''', (f"exists:{package_name}",))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            data = json.loads(result[0])
            return data.get("exists", False)
        
        return False