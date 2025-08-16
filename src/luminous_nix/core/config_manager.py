"""
Configuration Persistence Manager for Nix for Humanity.

Manages user preferences, command aliases, usage patterns, and session history.
Provides persistent storage for personalization and learning features.

Key Features:
    - User preferences management with defaults
    - Command alias system for shortcuts
    - Usage history tracking and analysis
    - Pattern learning from user behavior
    - Statistics collection for insights
    - Import/export for backup and sharing

Usage Example:
    >>> config = ConfigManager()
    >>> config.add_alias("i", "install")
    >>> expanded = config.expand_aliases("i firefox")
    >>> print(expanded)
    "install firefox"

File Locations:
    - Config: ~/.config/luminous-nix/
    - Data: ~/.local/share/luminous-nix/
    - Cache: ~/.cache/luminous-nix/

Since: v1.0.0
"""

import hashlib
import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..constants import (
    BATCH_SIZE_DEFAULT,
    HISTORY_MAX_ENTRIES,
    MAX_SUGGESTION_COUNT,
    PATTERN_DECAY_DAYS,
)
from ..types import ConfigDict
from .logging_config import get_logger

logger = get_logger(__name__)

# Configuration directories
CONFIG_DIR = Path.home() / ".config" / "nix-humanity"
DATA_DIR = Path.home() / ".local" / "share" / "nix-humanity"
CACHE_DIR = Path.home() / ".cache" / "nix-humanity"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Configuration files
CONFIG_FILE = CONFIG_DIR / "config.json"
ALIASES_FILE = CONFIG_DIR / "aliases.json"
PREFERENCES_FILE = CONFIG_DIR / "preferences.json"
HISTORY_FILE = DATA_DIR / "history.jsonl"
PATTERNS_FILE = DATA_DIR / "patterns.json"
STATS_FILE = DATA_DIR / "stats.json"


@dataclass
class UserPreferences:
    """
    User preferences and settings.

    Stores all user-configurable preferences with sensible defaults.
    Automatically persisted and loaded across sessions.

    Attributes:
        default_dry_run (bool): Safety mode - preview before execute
        default_log_level (str): Logging verbosity level
        enable_progress (bool): Show progress indicators
        enable_colors (bool): Use colored output
        enable_learning (bool): Learn from usage patterns
        enable_caching (bool): Cache results for speed
        max_history (int): Maximum history entries to keep
        preferred_output (str): Output format preference

    Example:
        >>> prefs = UserPreferences(enable_colors=False)
        >>> prefs.default_dry_run
        True

    Since: v1.0.0
    """

    default_dry_run: bool = True
    default_log_level: str = "WARNING"
    enable_progress: bool = True
    enable_colors: bool = True
    enable_learning: bool = True
    enable_caching: bool = True
    max_history: int = HISTORY_MAX_ENTRIES
    preferred_output: str = "concise"  # concise, detailed, json
    theme: str = "sacred"  # sacred, minimal, verbose

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserPreferences":
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class CommandAlias:
    """Command alias definition"""

    alias: str
    expansion: str
    description: str | None = None
    created: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alias": self.alias,
            "expansion": self.expansion,
            "description": self.description,
            "created": self.created.isoformat(),
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandAlias":
        """Create from dictionary"""
        data = data.copy()
        if "created" in data:
            data["created"] = datetime.fromisoformat(data["created"])
        return cls(**data)


@dataclass
class SessionContext:
    """Session context for continuity"""

    session_id: str
    started: datetime
    last_activity: datetime
    working_directory: str | None = None
    active_project: str | None = None
    command_count: int = 0
    success_rate: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "started": self.started.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "working_directory": self.working_directory,
            "active_project": self.active_project,
            "command_count": self.command_count,
            "success_rate": self.success_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionContext":
        """Create from dictionary"""
        data = data.copy()
        data["started"] = datetime.fromisoformat(data["started"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        return cls(**data)


class ConfigManager:
    """
    Manages configuration persistence

    Features:
    - User preferences
    - Command aliases
    - Learned patterns
    - Session history
    - Usage statistics
    """

    def __init__(self):
        """Initialize configuration manager"""
        self.preferences = self._load_preferences()
        self.aliases = self._load_aliases()
        self.patterns = self._load_patterns()
        self.stats = self._load_stats()
        self.session = self._init_session()

    def _load_preferences(self) -> UserPreferences:
        """Load user preferences"""
        if PREFERENCES_FILE.exists():
            try:
                with open(PREFERENCES_FILE) as f:
                    data = json.load(f)
                    return UserPreferences.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}")
        return UserPreferences()

    def _load_aliases(self) -> dict[str, CommandAlias]:
        """Load command aliases"""
        aliases = {}
        if ALIASES_FILE.exists():
            try:
                with open(ALIASES_FILE) as f:
                    data = json.load(f)
                    for alias_name, alias_data in data.items():
                        aliases[alias_name] = CommandAlias.from_dict(alias_data)
            except Exception as e:
                logger.warning(f"Failed to load aliases: {e}")

        # Add default aliases if none exist
        if not aliases:
            aliases = self._get_default_aliases()

        return aliases

    def _get_default_aliases(self) -> dict[str, CommandAlias]:
        """Get default command aliases"""
        return {
            "i": CommandAlias("i", "install", "Install package"),
            "s": CommandAlias("s", "search", "Search packages"),
            "u": CommandAlias("u", "update", "System update"),
            "r": CommandAlias("r", "rollback", "Rollback system"),
            "g": CommandAlias("g", "generate", "Generate config"),
        }

    def _load_patterns(self) -> dict[str, Any]:
        """Load learned patterns"""
        if PATTERNS_FILE.exists():
            try:
                with open(PATTERNS_FILE) as f:
                    patterns = json.load(f)
                    # Ensure time_patterns has all hour keys
                    if "time_patterns" in patterns:
                        time_dict = defaultdict(list)
                        # Copy existing data
                        for hour, intents in patterns["time_patterns"].items():
                            time_dict[str(hour)] = intents
                        patterns["time_patterns"] = time_dict
                    return patterns
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

        # Initialize with all hour keys (0-23) to prevent KeyError
        time_patterns = defaultdict(list)
        for hour in range(24):
            time_patterns[str(hour)] = []

        return {
            "common_packages": [],
            "frequent_queries": [],
            "success_patterns": [],
            "error_patterns": [],
            "time_patterns": time_patterns,
        }

    def _load_stats(self) -> dict[str, Any]:
        """Load usage statistics"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load stats: {e}")

        return {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "most_used_intents": Counter(),
            "daily_usage": defaultdict(int),
        }

    def _init_session(self) -> SessionContext:
        """Initialize or restore session"""
        session_file = DATA_DIR / "session.json"

        if session_file.exists():
            try:
                with open(session_file) as f:
                    data = json.load(f)
                    session = SessionContext.from_dict(data)

                    # Check if session is still valid (< 24 hours old)
                    if datetime.now() - session.last_activity < timedelta(hours=24):
                        session.last_activity = datetime.now()
                        logger.info(f"Restored session {session.session_id}")
                        return session
            except Exception as e:
                logger.warning(f"Failed to restore session: {e}")

        # Create new session
        session_id = hashlib.md5(
            f"{datetime.now().isoformat()}{os.getpid()}".encode()
        ).hexdigest()[:8]

        return SessionContext(
            session_id=session_id,
            started=datetime.now(),
            last_activity=datetime.now(),
            working_directory=os.getcwd(),
        )

    def save_preferences(self, preferences: UserPreferences | None = None) -> None:
        """Save user preferences"""
        if preferences:
            self.preferences = preferences

        try:
            with open(PREFERENCES_FILE, "w") as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
            logger.debug("Saved preferences")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def save_aliases(self) -> None:
        """Save command aliases"""
        try:
            data = {name: alias.to_dict() for name, alias in self.aliases.items()}
            with open(ALIASES_FILE, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved aliases")
        except Exception as e:
            logger.error(f"Failed to save aliases: {e}")

    def add_alias(
        self, alias: str, expansion: str, description: str | None = None
    ) -> None:
        """Add a command alias"""
        self.aliases[alias] = CommandAlias(
            alias=alias, expansion=expansion, description=description
        )
        self.save_aliases()
        logger.info(f"Added alias: {alias} -> {expansion}")

    def remove_alias(self, alias: str) -> bool:
        """Remove a command alias"""
        if alias in self.aliases:
            del self.aliases[alias]
            self.save_aliases()
            logger.info(f"Removed alias: {alias}")
            return True
        return False

    def expand_aliases(self, query: str) -> str:
        """Expand aliases in query"""
        words = query.split()
        if words and words[0] in self.aliases:
            alias = self.aliases[words[0]]
            alias.usage_count += 1
            expanded = alias.expansion + " " + " ".join(words[1:])
            logger.debug(f"Expanded alias: {query} -> {expanded}")
            return expanded.strip()
        return query

    def add_to_history(self, query: str, success: bool, execution_time: float) -> None:
        """Add query to history"""
        try:
            with open(HISTORY_FILE, "a") as f:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.session.session_id,
                    "query": query,
                    "success": success,
                    "execution_time": execution_time,
                }
                f.write(json.dumps(entry) + "\n")

            # Update session
            self.session.command_count += 1
            self.session.last_activity = datetime.now()
            if self.session.command_count > 0:
                success_count = self.session.command_count * self.session.success_rate
                if success:
                    success_count += 1
                self.session.success_rate = success_count / (
                    self.session.command_count + 1
                )

            # Update stats
            self.stats["total_queries"] += 1
            if success:
                self.stats["successful_queries"] += 1
            else:
                self.stats["failed_queries"] += 1

            # Update average response time
            avg = self.stats["average_response_time"]
            count = self.stats["total_queries"]
            self.stats["average_response_time"] = (
                avg * (count - 1) + execution_time
            ) / count

            # Save periodically
            if self.session.command_count % BATCH_SIZE_DEFAULT == 0:
                self.save_session()
                self.save_stats()

        except Exception as e:
            logger.error(f"Failed to add to history: {e}")

    def get_recent_history(
        self, limit: int = BATCH_SIZE_DEFAULT
    ) -> list[dict[str, Any]]:
        """Get recent command history"""
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE) as f:
                    # Read last N lines efficiently
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        history.append(json.loads(line))
            except Exception as e:
                logger.warning(f"Failed to read history: {e}")
        return history

    def learn_pattern(self, intent: str, query: str, success: bool) -> None:
        """Learn from user patterns"""
        if not self.preferences.enable_learning:
            return

        # Track common queries
        if success:
            queries = self.patterns.get("frequent_queries", [])
            queries.append(query)
            # Keep only last HISTORY_MAX_ENTRIES
            self.patterns["frequent_queries"] = queries[-HISTORY_MAX_ENTRIES:]

            # Track success patterns
            patterns = self.patterns.get("success_patterns", [])
            patterns.append({"intent": intent, "query": query})
            self.patterns["success_patterns"] = patterns[-50:]
        else:
            # Track error patterns
            patterns = self.patterns.get("error_patterns", [])
            patterns.append({"intent": intent, "query": query})
            self.patterns["error_patterns"] = patterns[-50:]

        # Track time patterns
        hour = datetime.now().hour
        self.patterns["time_patterns"][str(hour)].append(intent)

        # Save periodically
        if self.session.command_count % 20 == 0:
            self.save_patterns()

    def save_patterns(self) -> None:
        """Save learned patterns"""
        try:
            # Convert defaultdict to regular dict for JSON
            patterns = dict(self.patterns)
            if "time_patterns" in patterns:
                patterns["time_patterns"] = dict(patterns["time_patterns"])

            with open(PATTERNS_FILE, "w") as f:
                json.dump(patterns, f, indent=2)
            logger.debug("Saved patterns")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def save_stats(self) -> None:
        """Save usage statistics"""
        try:
            # Convert Counter to dict for JSON
            stats = dict(self.stats)
            if "most_used_intents" in stats and isinstance(
                stats["most_used_intents"], Counter
            ):
                stats["most_used_intents"] = dict(stats["most_used_intents"])
            if "daily_usage" in stats:
                stats["daily_usage"] = dict(stats["daily_usage"])

            with open(STATS_FILE, "w") as f:
                json.dump(stats, f, indent=2)
            logger.debug("Saved stats")
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def save_session(self) -> None:
        """Save current session"""
        try:
            session_file = DATA_DIR / "session.json"
            with open(session_file, "w") as f:
                json.dump(self.session.to_dict(), f, indent=2)
            logger.debug("Saved session")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def get_suggestions(self, partial_query: str) -> list[str]:
        """Get query suggestions based on history and patterns"""
        suggestions = []

        # Check aliases
        for alias, cmd in self.aliases.items():
            if alias.startswith(partial_query):
                suggestions.append(f"{alias} ({cmd.description})")

        # Check frequent queries
        for query in self.patterns.get("frequent_queries", []):
            if query.startswith(partial_query) and query not in suggestions:
                suggestions.append(query)

        # Check success patterns
        for pattern in self.patterns.get("success_patterns", []):
            query = pattern.get("query", "")
            if query.startswith(partial_query) and query not in suggestions:
                suggestions.append(query)

        return suggestions[:MAX_SUGGESTION_COUNT]  # Return top suggestions

    def get_config_dict(self) -> ConfigDict:
        """Get configuration as ConfigDict"""
        return ConfigDict(
            dry_run=self.preferences.default_dry_run,
            debug=self.preferences.default_log_level == "DEBUG",
            caching=self.preferences.enable_caching,
            learning=self.preferences.enable_learning,
            log_level=self.preferences.default_log_level,
        )

    def cleanup_old_data(self, days: int = PATTERN_DECAY_DAYS) -> None:
        """Clean up old data files"""
        cutoff = datetime.now() - timedelta(days=days)

        # Clean old history
        if HISTORY_FILE.exists():
            try:
                kept_lines = []
                with open(HISTORY_FILE) as f:
                    for line in f:
                        entry = json.loads(line)
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        if timestamp > cutoff:
                            kept_lines.append(line)

                # Rewrite file with kept lines
                with open(HISTORY_FILE, "w") as f:
                    f.writelines(kept_lines)

                logger.info(f"Cleaned history older than {days} days")
            except Exception as e:
                logger.error(f"Failed to clean history: {e}")

    def export_config(self, path: Path) -> None:
        """Export configuration to file"""
        config = {
            "preferences": self.preferences.to_dict(),
            "aliases": {name: alias.to_dict() for name, alias in self.aliases.items()},
            "patterns": dict(self.patterns),
            "stats": dict(self.stats),
        }

        with open(path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Exported configuration to {path}")

    def import_config(self, path: Path) -> None:
        """Import configuration from file"""
        with open(path) as f:
            config = json.load(f)

        if "preferences" in config:
            self.preferences = UserPreferences.from_dict(config["preferences"])
            self.save_preferences()

        if "aliases" in config:
            self.aliases = {
                name: CommandAlias.from_dict(data)
                for name, data in config["aliases"].items()
            }
            self.save_aliases()

        if "patterns" in config:
            self.patterns = config["patterns"]
            self.save_patterns()

        if "stats" in config:
            self.stats = config["stats"]
            self.save_stats()

        logger.info(f"Imported configuration from {path}")


# Singleton instance
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get singleton configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
