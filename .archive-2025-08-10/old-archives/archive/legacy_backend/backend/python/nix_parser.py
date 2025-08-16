#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Tree-sitter based Nix Parser
Advanced parsing and understanding of Nix configurations
Part of the Python AI integration roadmap
"""

import logging
import sys
from dataclasses import dataclass, field
from typing import Any

# Tree-sitter import handling
try:
    import tree_sitter_nix as tsnix
    from tree_sitter import Language, Parser

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print(
        "Warning: tree-sitter not available. Install with: pip install tree-sitter tree-sitter-nix"
    )

logger = logging.getLogger(__name__)


@dataclass
class NixPackage:
    """Represents a Nix package reference"""

    name: str
    attribute_path: str
    source_location: tuple[int, int]  # line, column
    context: str = ""  # surrounding code context


@dataclass
class NixFunction:
    """Represents a Nix function definition"""

    name: str | None
    parameters: list[str]
    body_location: tuple[int, int]
    is_lambda: bool = True


@dataclass
class NixImport:
    """Represents an import statement"""

    path: str
    location: tuple[int, int]
    is_relative: bool = True


@dataclass
class NixConfigAnalysis:
    """Complete analysis of a Nix configuration"""

    packages: list[NixPackage] = field(default_factory=list)
    functions: list[NixFunction] = field(default_factory=list)
    imports: list[NixImport] = field(default_factory=list)
    services: dict[str, dict] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class NixParser:
    """
    Advanced Nix parser using tree-sitter for deep understanding.

    This enables Nix for Humanity to:
    1. Understand existing configurations
    2. Suggest improvements
    3. Generate valid Nix code
    4. Detect common patterns and anti-patterns
    """

    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise ImportError("tree-sitter is required for NixParser")

        # Initialize tree-sitter
        NIX_LANGUAGE = Language(tsnix.language(), "nix")
        self.parser = Parser()
        self.parser.set_language(NIX_LANGUAGE)

        # Common patterns
        self.package_patterns = [
            "environment.systemPackages",
            "users.users.*.packages",
            "home.packages",
        ]

        self.service_patterns = [
            "services.*",
            "systemd.services.*",
        ]

    def parse_file(self, file_path: str) -> NixConfigAnalysis:
        """Parse a Nix file and extract meaningful information"""
        with open(file_path, "rb") as f:
            content = f.read()

        return self.parse_content(content, file_path)

    def parse_content(
        self, content: bytes, source_name: str = "<input>"
    ) -> NixConfigAnalysis:
        """Parse Nix content and analyze it"""
        tree = self.parser.parse(content)
        analysis = NixConfigAnalysis()

        # Walk the AST
        self._walk_tree(tree.root_node, content, analysis)

        return analysis

    def _walk_tree(self, node, content: bytes, analysis: NixConfigAnalysis):
        """Recursively walk the AST and extract information"""

        # Extract packages
        if self._is_package_list(node):
            packages = self._extract_packages(node, content)
            analysis.packages.extend(packages)

        # Extract function definitions
        if node.type == "function":
            func = self._extract_function(node, content)
            if func:
                analysis.functions.append(func)

        # Extract imports
        if node.type == "apply" and node.child_count >= 2:
            if (
                node.children[0].type == "identifier"
                and self._get_text(node.children[0], content) == "import"
            ):
                imp = self._extract_import(node, content)
                if imp:
                    analysis.imports.append(imp)

        # Extract service configurations
        if self._is_service_config(node):
            service_name, config = self._extract_service(node, content)
            if service_name:
                analysis.services[service_name] = config

        # Recurse into children
        for child in node.children:
            self._walk_tree(child, content, analysis)

    def _is_package_list(self, node) -> bool:
        """Check if node represents a package list"""
        if node.type != "attrset" and node.type != "list":
            return False

        # Check if parent is systemPackages or similar
        parent = node.parent
        if parent and parent.type == "binding":
            attr_path = self._get_attribute_path(parent)
            return any(pattern in attr_path for pattern in self.package_patterns)

        return False

    def _extract_packages(self, node, content: bytes) -> list[NixPackage]:
        """Extract package references from a list node"""
        packages = []

        if node.type == "list":
            for child in node.children:
                if child.type == "identifier" or child.type == "attrpath":
                    name = self._get_text(child, content)
                    if name and name not in ["[", "]", "with", "pkgs"]:
                        package = NixPackage(
                            name=name.split(".")[-1],
                            attribute_path=name,
                            source_location=(
                                child.start_point[0],
                                child.start_point[1],
                            ),
                        )
                        packages.append(package)

        return packages

    def _extract_function(self, node, content: bytes) -> NixFunction | None:
        """Extract function definition"""
        params = []
        name = None

        # Extract parameters
        if node.child_count >= 2 and node.children[0].type == "formals":
            formals = node.children[0]
            for child in formals.children:
                if child.type == "identifier":
                    params.append(self._get_text(child, content))

        return NixFunction(
            name=name,
            parameters=params,
            body_location=(node.start_point[0], node.start_point[1]),
        )

    def _extract_import(self, node, content: bytes) -> NixImport | None:
        """Extract import statement"""
        if node.child_count >= 2:
            path_node = node.children[1]
            path = self._get_text(path_node, content)

            # Clean up path
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]

            return NixImport(
                path=path,
                location=(node.start_point[0], node.start_point[1]),
                is_relative=not path.startswith("/") and not path.startswith("<"),
            )

        return None

    def _is_service_config(self, node) -> bool:
        """Check if node represents a service configuration"""
        if node.type != "attrset":
            return False

        parent = node.parent
        if parent and parent.type == "binding":
            attr_path = self._get_attribute_path(parent)
            return any(
                pattern.replace("*", "") in attr_path
                for pattern in self.service_patterns
            )

        return False

    def _extract_service(self, node, content: bytes) -> tuple[str | None, dict]:
        """Extract service configuration"""
        if node.parent and node.parent.type == "binding":
            service_path = self._get_attribute_path(node.parent)
            service_name = service_path.split(".")[-1]

            config = {}
            # Extract key-value pairs from attrset
            for child in node.children:
                if child.type == "binding":
                    key = self._get_binding_key(child, content)
                    value = self._get_binding_value(child, content)
                    if key:
                        config[key] = value

            return service_name, config

        return None, {}

    def _get_attribute_path(self, binding_node) -> str:
        """Get the full attribute path of a binding"""
        parts = []

        for child in binding_node.children:
            if child.type == "attrpath":
                for attr_child in child.children:
                    if attr_child.type == "identifier":
                        parts.append(self._get_text(attr_child, binding_node.text))

        return ".".join(parts)

    def _get_binding_key(self, binding_node, content: bytes) -> str | None:
        """Extract key from a binding node"""
        for child in binding_node.children:
            if child.type == "attrpath":
                return self._get_text(child, content)
        return None

    def _get_binding_value(self, binding_node, content: bytes) -> Any:
        """Extract value from a binding node"""
        for child in binding_node.children:
            if child.type not in ["attrpath", "="]:
                return self._get_text(child, content)
        return None

    def _get_text(self, node, content: bytes) -> str:
        """Get text content of a node"""
        return content[node.start_byte : node.end_byte].decode("utf-8")


class NixIntelligence:
    """
    High-level intelligence layer built on the parser.
    Provides insights and suggestions for Nix configurations.
    """

    def __init__(self):
        self.parser = NixParser()

        # Knowledge base of common patterns
        self.best_practices = {
            "package_management": {
                "prefer_declarative": "Use environment.systemPackages instead of nix-env",
                "use_overlays": "Consider overlays for package customization",
                "pin_versions": "Pin package versions for reproducibility",
            },
            "services": {
                "enable_explicitly": "Always set enable = true explicitly",
                "use_systemd": "Prefer systemd services over raw scripts",
                "security": "Use DynamicUser and sandboxing options",
            },
        }

    def analyze_configuration(self, config_path: str) -> dict:
        """Provide intelligent analysis of a configuration"""
        analysis = self.parser.parse_file(config_path)

        insights = {
            "summary": self._generate_summary(analysis),
            "suggestions": self._generate_suggestions(analysis),
            "security_review": self._security_review(analysis),
            "complexity_score": self._calculate_complexity(analysis),
        }

        return insights

    def suggest_package_installation(
        self, package_name: str, current_config: str
    ) -> str:
        """Suggest the best way to install a package given current config"""
        analysis = self.parser.parse_content(current_config.encode())

        # Check if systemPackages is already used
        has_system_packages = any(
            "systemPackages" in p.attribute_path for p in analysis.packages
        )

        if has_system_packages:
            return f"""
To install {package_name}, add it to your existing systemPackages:

environment.systemPackages = with pkgs; [
  # ... existing packages ...
  {package_name}
];
"""
        return f"""
To install {package_name}, add this to your configuration.nix:

environment.systemPackages = with pkgs; [
  {package_name}
];
"""

    def _generate_summary(self, analysis: NixConfigAnalysis) -> dict:
        """Generate a summary of the configuration"""
        return {
            "total_packages": len(analysis.packages),
            "total_services": len(analysis.services),
            "imports_count": len(analysis.imports),
            "functions_defined": len(analysis.functions),
            "has_errors": len(analysis.errors) > 0,
        }

    def _generate_suggestions(self, analysis: NixConfigAnalysis) -> list[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Check for common anti-patterns
        if not analysis.packages and not analysis.services:
            suggestions.append(
                "Configuration appears empty. Consider adding packages or services."
            )

        # Check for security
        for service_name, config in analysis.services.items():
            if isinstance(config, dict) and config.get("enable") == "true":
                if not config.get("DynamicUser"):
                    suggestions.append(
                        f"Consider using DynamicUser for service '{service_name}'"
                    )

        return suggestions

    def _security_review(self, analysis: NixConfigAnalysis) -> dict:
        """Review configuration for security issues"""
        issues = []
        score = 100  # Start with perfect score

        # Check services
        for service_name, config in analysis.services.items():
            if isinstance(config, dict):
                # Check for running as root
                if config.get("User") == "root":
                    issues.append(f"Service '{service_name}' runs as root")
                    score -= 10

                # Check for exposed ports without auth
                if config.get("openFirewall") == "true":
                    issues.append(f"Service '{service_name}' opens firewall")
                    score -= 5

        return {"score": max(0, score), "issues": issues, "passed": score >= 70}

    def _calculate_complexity(self, analysis: NixConfigAnalysis) -> int:
        """Calculate a complexity score for the configuration"""
        score = 0

        # Add complexity for various elements
        score += len(analysis.packages) * 1
        score += len(analysis.services) * 5
        score += len(analysis.imports) * 3
        score += len(analysis.functions) * 10

        # Normalize to 0-100 scale
        return min(100, score)


# Demo and testing
if __name__ == "__main__":
    if not TREE_SITTER_AVAILABLE:
        print("tree-sitter not available. This module requires:")
        print("  pip install tree-sitter tree-sitter-nix")
        sys.exit(1)

    # Example usage
    intelligence = NixIntelligence()

    # Sample configuration
    sample_config = """
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  environment.systemPackages = with pkgs; [
    firefox
    vim
    git
  ];

  services.openssh = {
    enable = true;
    permitRootLogin = "no";
  };
}
"""

    print("🌲 Tree-sitter Nix Parser Demo")
    print("=" * 50)

    # Parse the sample
    parser = NixParser()
    analysis = parser.parse_content(sample_config.encode())

    print(f"\n📦 Found {len(analysis.packages)} packages:")
    for pkg in analysis.packages:
        print(f"  - {pkg.name} at line {pkg.source_location[0]}")

    print(f"\n🔧 Found {len(analysis.services)} services:")
    for service, config in analysis.services.items():
        print(f"  - {service}: {config}")

    print(f"\n📥 Found {len(analysis.imports)} imports:")
    for imp in analysis.imports:
        print(f"  - {imp.path} at line {imp.location[0]}")

    # Test intelligence layer
    print("\n🧠 Configuration Intelligence:")

    suggestion = intelligence.suggest_package_installation("htop", sample_config)
    print(suggestion)
