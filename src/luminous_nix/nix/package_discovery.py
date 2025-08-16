#!/usr/bin/env python3
"""
Smart Package Discovery for Nix for Humanity

Helps users find packages through:
- Natural language descriptions
- Common aliases and alternative names
- Feature-based search
- Category browsing
- Similarity matching
"""

import sqlite3
import time
import json
import hashlib
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@dataclass
class PackageMatch:
    """A potential package match"""

    name: str
    description: str
    score: float
    reason: str  # Why this was matched
    alternatives: list[str] = None
    category: str | None = None


@dataclass
class PackageInfo:
    """Detailed package information"""

    name: str
    description: str
    version: str | None
    homepage: str | None
    license: str | None
    maintainers: list[str]
    platforms: list[str]
    similar_packages: list[str]
    common_commands: list[str]


class PackageDiscovery:
    """Smart package discovery with natural language understanding"""

    # Cache settings
    CACHE_TTL = 3600  # 1 hour in seconds
    MEMORY_CACHE_SIZE = 1000  # Number of queries to cache in memory
    
    def __init__(self, db_path: Path | None = None):
        self.db_path = (
            db_path or Path.home() / ".cache" / "nix-humanity" / "packages.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize caches
        self.cache_path = self.db_path.parent / "search_cache.db"
        self._init_cache_db()
        self._memory_cache: Dict[str, Tuple[float, List[PackageMatch]]] = {}
        self._last_cache_cleanup = time.time()

        # Common package aliases and mappings
        self.aliases = {
            # Browsers
            "browser": ["firefox", "chromium", "brave", "qutebrowser"],
            "chrome": ["chromium", "google-chrome"],
            "ff": ["firefox"],
            # Editors
            "editor": ["vim", "neovim", "emacs", "vscode", "sublime3", "atom"],
            "code": ["vscode", "vscodium"],
            "sublime": ["sublime3", "sublime4"],
            # Development
            "python": ["python3", "python311", "python312"],
            "node": ["nodejs", "nodejs_20", "nodejs_21"],
            "java": ["openjdk", "openjdk17", "openjdk21"],
            "c++": ["gcc", "clang", "llvm"],
            "rust": ["rustc", "cargo", "rustup"],
            # Tools
            "unzip": ["unzip", "p7zip"],
            "screenshot": ["flameshot", "spectacle", "gnome-screenshot"],
            "terminal": ["alacritty", "kitty", "wezterm", "gnome-terminal"],
            "music": ["spotify", "rhythmbox", "clementine", "mpd"],
            "video": ["vlc", "mpv", "mplayer"],
            "image": ["gimp", "inkscape", "krita"],
            # System
            "vpn": ["openvpn", "wireguard", "tailscale"],
            "backup": ["borgbackup", "restic", "duplicity"],
            "monitor": ["htop", "btop", "glances"],
            "network": ["nmap", "wireshark", "tcpdump"],
        }

        # Category mappings
        self.categories = {
            "development": {
                "keywords": ["programming", "coding", "development", "ide", "compiler"],
                "packages": [
                    "vim",
                    "neovim",
                    "emacs",
                    "vscode",
                    "gcc",
                    "clang",
                    "python3",
                    "nodejs",
                    "rustc",
                ],
            },
            "multimedia": {
                "keywords": ["music", "video", "audio", "media", "player"],
                "packages": [
                    "vlc",
                    "mpv",
                    "spotify",
                    "audacity",
                    "obs-studio",
                    "ffmpeg",
                ],
            },
            "graphics": {
                "keywords": ["image", "photo", "graphics", "drawing", "design"],
                "packages": ["gimp", "inkscape", "krita", "blender", "darktable"],
            },
            "networking": {
                "keywords": ["network", "internet", "wifi", "vpn", "security"],
                "packages": [
                    "nmap",
                    "wireshark",
                    "openvpn",
                    "wireguard",
                    "curl",
                    "wget",
                ],
            },
            "productivity": {
                "keywords": ["office", "document", "spreadsheet", "presentation"],
                "packages": ["libreoffice", "thunderbird", "zathura", "pandoc"],
            },
            "utilities": {
                "keywords": ["tool", "utility", "system", "file", "backup"],
                "packages": ["htop", "tree", "ranger", "fzf", "ripgrep", "fd", "bat"],
            },
        }

        # Feature to package mappings
        self.features = {
            "pdf": ["zathura", "evince", "okular", "mupdf"],
            "markdown": ["pandoc", "grip", "markdown"],
            "screenshot": ["flameshot", "spectacle", "scrot"],
            "clipboard": ["xclip", "xsel", "copyq"],
            "torrents": ["transmission", "qbittorrent", "deluge"],
            "encryption": ["gnupg", "veracrypt", "cryptsetup"],
            "virtualization": ["virtualbox", "qemu", "virt-manager"],
            "containers": ["docker", "podman", "lxc"],
            "databases": ["postgresql", "mysql", "sqlite", "redis"],
            "web servers": ["nginx", "apache", "caddy"],
        }

        # Initialize or update database
        self._init_db()
        
        # Pre-warm cache with common searches
        self._prewarm_cache()

    def _init_db(self):
        """Initialize the package database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS packages (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    version TEXT,
                    homepage TEXT,
                    license TEXT,
                    category TEXT,
                    keywords TEXT,
                    last_updated INTEGER
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    query TEXT,
                    selected_package TEXT,
                    timestamp INTEGER
                )
            """
            )

            # Create full-text search index
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts
                USING fts5(name, description, keywords, content=packages)
            """
            )
            
            # Create index for faster lookups
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_packages_category ON packages(category)"
            )

    def _init_cache_db(self):
        """Initialize the cache database"""
        with sqlite3.connect(self.cache_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_cache (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT,
                    results TEXT,
                    timestamp INTEGER,
                    hit_count INTEGER DEFAULT 1
                )
            """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_timestamp ON search_cache(timestamp)"
            )
    
    def _get_query_hash(self, query: str) -> str:
        """Get a hash for the query to use as cache key"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    @lru_cache(maxsize=MEMORY_CACHE_SIZE)
    def search_packages(self, query: str, limit: int = 10) -> list[PackageMatch]:
        """Search for packages using natural language with caching"""
        # Check memory cache first (fastest)
        query_hash = self._get_query_hash(query)
        
        if query_hash in self._memory_cache:
            timestamp, results = self._memory_cache[query_hash]
            if time.time() - timestamp < self.CACHE_TTL:
                logger.debug(f"Memory cache hit for query: {query}")
                return results
        
        # Check disk cache (second fastest)
        cached_results = self._get_cached_results(query_hash)
        if cached_results:
            logger.debug(f"Disk cache hit for query: {query}")
            # Update memory cache
            self._memory_cache[query_hash] = (time.time(), cached_results)
            return cached_results
        
        # Perform actual search (slowest)
        logger.debug(f"Cache miss, performing search for: {query}")
        query_lower = query.lower()
        matches = []

        # 1. Check direct aliases
        for alias, packages in self.aliases.items():
            if alias in query_lower:
                for pkg in packages:
                    matches.append(
                        PackageMatch(
                            name=pkg,
                            description=f"Common name for {alias}",
                            score=1.0,
                            reason=f"Alias match for '{alias}'",
                        )
                    )

        # 2. Check features
        for feature, packages in self.features.items():
            if feature in query_lower:
                for pkg in packages:
                    matches.append(
                        PackageMatch(
                            name=pkg,
                            description=f"Supports {feature}",
                            score=0.9,
                            reason=f"Feature match for '{feature}'",
                        )
                    )

        # 3. Check categories
        for category, data in self.categories.items():
            if any(keyword in query_lower for keyword in data["keywords"]):
                for pkg in data["packages"][:5]:  # Top 5 per category
                    matches.append(
                        PackageMatch(
                            name=pkg,
                            description=f"Popular {category} tool",
                            score=0.8,
                            reason=f"Category match for '{category}'",
                            category=category,
                        )
                    )

        # 4. Database search
        db_matches = self._search_database(query)
        matches.extend(db_matches)

        # 5. Fuzzy matching on package names
        all_packages = set()
        for packages in self.aliases.values():
            all_packages.update(packages)
        for packages in self.features.values():
            all_packages.update(packages)

        fuzzy_matches = get_close_matches(query_lower, all_packages, n=3, cutoff=0.6)
        for match in fuzzy_matches:
            if not any(m.name == match for m in matches):
                matches.append(
                    PackageMatch(
                        name=match,
                        description="Similar package name",
                        score=0.6,
                        reason="Fuzzy name match",
                    )
                )

        # Remove duplicates and sort by score
        seen = set()
        unique_matches = []
        for match in sorted(matches, key=lambda x: x.score, reverse=True):
            if match.name not in seen:
                seen.add(match.name)
                unique_matches.append(match)

        results = unique_matches[:limit]
        
        # Cache the results
        self._cache_results(query_hash, query, results)
        self._memory_cache[query_hash] = (time.time(), results)
        
        # Periodic cache cleanup
        if time.time() - self._last_cache_cleanup > 3600:  # Every hour
            self._cleanup_cache()
            self._last_cache_cleanup = time.time()
        
        return results

    def _search_database(self, query: str) -> list[PackageMatch]:
        """Search the package database"""
        matches = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Full-text search
                cursor = conn.execute(
                    """
                    SELECT p.name, p.description, p.category
                    FROM packages p
                    JOIN packages_fts ON p.rowid = packages_fts.rowid
                    WHERE packages_fts MATCH ?
                    ORDER BY rank
                    LIMIT 10
                """,
                    (query,),
                )

                for name, description, category in cursor:
                    matches.append(
                        PackageMatch(
                            name=name,
                            description=description or "Package in Nixpkgs",
                            score=0.7,
                            reason="Database search match",
                            category=category,
                        )
                    )

        except sqlite3.OperationalError:
            # Table might not exist or be populated yet
            pass

        return matches

    def find_alternatives(self, package_name: str) -> list[str]:
        """Find alternative packages for a given package"""
        alternatives = []

        # Check aliases
        for alias, packages in self.aliases.items():
            if package_name in packages:
                alternatives.extend([p for p in packages if p != package_name])

        # Check features
        for feature, packages in self.features.items():
            if package_name in packages:
                alternatives.extend([p for p in packages if p != package_name])

        # Check categories
        for category, data in self.categories.items():
            if package_name in data["packages"]:
                alternatives.extend(
                    [p for p in data["packages"][:3] if p != package_name]
                )

        return list(set(alternatives))

    def get_package_info(self, package_name: str) -> PackageInfo | None:
        """Get detailed information about a package"""
        # Try database first
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT name, description, version, homepage, license
                    FROM packages
                    WHERE name = ?
                """,
                    (package_name,),
                )

                row = cursor.fetchone()
                if row:
                    name, description, version, homepage, license = row
                    return PackageInfo(
                        name=name,
                        description=description or "No description available",
                        version=version,
                        homepage=homepage,
                        license=license,
                        maintainers=[],
                        platforms=["x86_64-linux"],
                        similar_packages=self.find_alternatives(name),
                        common_commands=self._get_common_commands(name),
                    )
        except Exception as e:
            logger.debug(f"Failed to get package info for {package_name}: {e}")

        # Fallback to basic info
        return PackageInfo(
            name=package_name,
            description=self._get_basic_description(package_name),
            version=None,
            homepage=None,
            license=None,
            maintainers=[],
            platforms=["x86_64-linux"],
            similar_packages=self.find_alternatives(package_name),
            common_commands=self._get_common_commands(package_name),
        )

    def _get_basic_description(self, package_name: str) -> str:
        """Get a basic description for known packages"""
        descriptions = {
            "firefox": "Free and open source web browser",
            "chromium": "Open source web browser",
            "vim": "Highly configurable text editor",
            "neovim": "Vim-fork focused on extensibility",
            "vscode": "Visual Studio Code - Open source code editor",
            "htop": "Interactive process viewer",
            "git": "Distributed version control system",
            "tmux": "Terminal multiplexer",
            "docker": "Container platform",
            "python3": "Python programming language",
            "nodejs": "JavaScript runtime",
            "gcc": "GNU Compiler Collection",
            "rustc": "Rust compiler",
        }

        return descriptions.get(package_name, f"{package_name} package")

    def _get_common_commands(self, package_name: str) -> list[str]:
        """Get common commands for a package"""
        commands = {
            "git": ["git status", "git add", "git commit", "git push"],
            "docker": ["docker ps", "docker run", "docker build"],
            "python3": ["python3", "pip3"],
            "nodejs": ["node", "npm", "npx"],
            "vim": ["vim", "vimdiff"],
            "htop": ["htop"],
            "tmux": ["tmux", "tmux attach", "tmux new"],
        }

        return commands.get(package_name, [package_name])

    def suggest_by_command(self, command: str) -> list[PackageMatch]:
        """Suggest packages that provide a specific command"""
        # Command to package mappings
        command_mappings = {
            "python": ["python3", "python311", "python312"],
            "pip": ["python3", "python311-pip"],
            "node": ["nodejs", "nodejs_20"],
            "npm": ["nodejs", "nodejs_20"],
            "cargo": ["rustc", "cargo", "rustup"],
            "rustc": ["rustc", "cargo"],
            "gcc": ["gcc", "gcc12", "gcc13"],
            "g++": ["gcc", "gcc12", "gcc13"],
            "make": ["gnumake", "cmake"],
            "docker": ["docker", "docker-compose"],
            "kubectl": ["kubectl", "kubernetes"],
            "aws": ["awscli", "awscli2"],
            "terraform": ["terraform"],
            "ansible": ["ansible"],
        }

        matches = []

        # Direct mapping
        if command in command_mappings:
            for pkg in command_mappings[command]:
                matches.append(
                    PackageMatch(
                        name=pkg,
                        description=f"Provides the '{command}' command",
                        score=1.0,
                        reason=f"Command provider for '{command}'",
                    )
                )

        # Fuzzy match on command
        similar_commands = get_close_matches(
            command, command_mappings.keys(), n=3, cutoff=0.6
        )
        for similar in similar_commands:
            if similar != command:
                for pkg in command_mappings[similar]:
                    matches.append(
                        PackageMatch(
                            name=pkg,
                            description=f"Provides similar command '{similar}'",
                            score=0.7,
                            reason="Similar command match",
                        )
                    )

        return matches

    def _get_cached_results(self, query_hash: str) -> List[PackageMatch] | None:
        """Get cached search results from disk"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT results, timestamp FROM search_cache
                    WHERE query_hash = ?
                    """,
                    (query_hash,)
                )
                row = cursor.fetchone()
                
                if row:
                    results_json, timestamp = row
                    # Check if cache is still valid
                    if time.time() - timestamp < self.CACHE_TTL:
                        # Update hit count
                        conn.execute(
                            "UPDATE search_cache SET hit_count = hit_count + 1 WHERE query_hash = ?",
                            (query_hash,)
                        )
                        # Deserialize results
                        results_data = json.loads(results_json)
                        return [
                            PackageMatch(
                                name=r["name"],
                                description=r["description"],
                                score=r["score"],
                                reason=r["reason"],
                                alternatives=r.get("alternatives"),
                                category=r.get("category")
                            )
                            for r in results_data
                        ]
        except Exception as e:
            logger.warning(f"Failed to get cached results: {e}")
        return None
    
    def _cache_results(self, query_hash: str, query: str, results: List[PackageMatch]):
        """Cache search results to disk"""
        try:
            # Serialize results
            results_data = [
                {
                    "name": r.name,
                    "description": r.description,
                    "score": r.score,
                    "reason": r.reason,
                    "alternatives": r.alternatives,
                    "category": r.category
                }
                for r in results
            ]
            results_json = json.dumps(results_data)
            
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO search_cache 
                    (query_hash, query, results, timestamp, hit_count)
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    (query_hash, query, results_json, int(time.time()))
                )
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        try:
            cutoff_time = int(time.time() - self.CACHE_TTL)
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute(
                    "DELETE FROM search_cache WHERE timestamp < ?",
                    (cutoff_time,)
                )
            # Also cleanup memory cache
            current_time = time.time()
            expired_keys = [
                k for k, (t, _) in self._memory_cache.items()
                if current_time - t > self.CACHE_TTL
            ]
            for key in expired_keys:
                del self._memory_cache[key]
            
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        except Exception as e:
            logger.warning(f"Failed to cleanup cache: {e}")
    
    def _prewarm_cache(self):
        """Pre-warm cache with common searches"""
        common_searches = [
            "browser", "editor", "terminal", "python", "git",
            "docker", "music player", "video player", "development tools",
            "system monitor", "file manager", "text editor"
        ]
        
        for search in common_searches:
            # This will populate the cache
            self.search_packages(search, limit=5)
        
        logger.info(f"Pre-warmed cache with {len(common_searches)} common searches")
    
    def browse_categories(self) -> dict[str, Any]:
        """Get all categories and their top packages"""
        result = {}

        for category, data in self.categories.items():
            result[category] = {
                "description": f"Packages for {category}",
                "keywords": data["keywords"],
                "top_packages": data["packages"][:10],
            }

        return result

    def learn_from_selection(self, query: str, selected_package: str):
        """Learn from user's package selection"""
        import time

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO search_history (query, selected_package, timestamp)
                VALUES (?, ?, ?)
            """,
                (query, selected_package, int(time.time())),
            )

    def clear_cache(self):
        """Clear all caches"""
        try:
            # Clear memory cache
            self._memory_cache.clear()
            self.search_packages.cache_clear()  # Clear LRU cache
            
            # Clear disk cache
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute("DELETE FROM search_cache")
            
            logger.info("Cleared all search caches")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "memory_cache_size": len(self._memory_cache),
            "memory_cache_info": self.search_packages.cache_info()._asdict(),
            "disk_cache_size": 0,
            "most_popular_searches": []
        }
        
        try:
            with sqlite3.connect(self.cache_path) as conn:
                # Get disk cache size
                cursor = conn.execute("SELECT COUNT(*) FROM search_cache")
                stats["disk_cache_size"] = cursor.fetchone()[0]
                
                # Get most popular searches
                cursor = conn.execute(
                    """
                    SELECT query, hit_count FROM search_cache
                    ORDER BY hit_count DESC
                    LIMIT 10
                    """
                )
                stats["most_popular_searches"] = cursor.fetchall()
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
        
        return stats
    
    def get_popular_packages(
        self, category: str | None = None
    ) -> list[tuple[str, str]]:
        """Get popular packages, optionally filtered by category"""
        popular = []

        if category and category in self.categories:
            packages = self.categories[category]["packages"]
            for pkg in packages[:10]:
                desc = self._get_basic_description(pkg)
                popular.append((pkg, desc))
        else:
            # General popular packages
            general_popular = [
                ("firefox", "Web browser"),
                ("vim", "Text editor"),
                ("git", "Version control"),
                ("htop", "System monitor"),
                ("tmux", "Terminal multiplexer"),
                ("docker", "Container platform"),
                ("python3", "Programming language"),
                ("nodejs", "JavaScript runtime"),
                ("vscode", "Code editor"),
                ("vlc", "Media player"),
            ]
            popular = general_popular

        return popular


def demonstrate_package_discovery():
    """Demo the package discovery functionality"""
    discovery = PackageDiscovery()

    print("🔍 Smart Package Discovery Demo")
    print("=" * 50)

    # Example 1: Natural language search
    print("\n1. Natural Language Search:")
    test_queries = [
        "i need a web browser",
        "something to edit photos",
        "tool for programming in python",
        "play music files",
        "monitor my system resources",
    ]

    for query in test_queries:
        print(f"\n💬 Query: '{query}'")
        results = discovery.search_packages(query, limit=3)
        for match in results:
            print(f"   • {match.name}: {match.description}")
            print(f"     (Score: {match.score:.1f}, Reason: {match.reason})")

    # Example 2: Command-based search
    print("\n\n2. Command-Based Search:")
    commands = ["python", "npm", "cargo", "kubectl"]

    for cmd in commands:
        print(f"\n🔧 Command '{cmd}' not found")
        suggestions = discovery.suggest_by_command(cmd)
        if suggestions:
            print("   Install one of these packages:")
            for match in suggestions:
                print(f"   • nix-env -iA nixpkgs.{match.name}")

    # Example 3: Browse categories
    print("\n\n3. Browse by Category:")
    categories = discovery.browse_categories()

    for category, info in list(categories.items())[:3]:
        print(f"\n📁 {category.title()}:")
        print(f"   Keywords: {', '.join(info['keywords'][:3])}")
        print(f"   Popular: {', '.join(info['top_packages'][:5])}")

    # Example 4: Find alternatives
    print("\n\n4. Package Alternatives:")
    test_packages = ["firefox", "vim", "docker"]

    for pkg in test_packages:
        alternatives = discovery.find_alternatives(pkg)
        if alternatives:
            print(f"\n🔄 Alternatives to {pkg}:")
            for alt in alternatives[:3]:
                print(f"   • {alt}")

    print("\n\n✨ Smart discovery helps find packages naturally!")


if __name__ == "__main__":
    demonstrate_package_discovery()
