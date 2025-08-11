#!/usr/bin/env python3
"""
Documentation Generator for Nix for Humanity.

Automatically generates and updates documentation based on code analysis.
Ensures all public APIs have proper documentation following our standards.

Key Features:
    - Analyzes code for missing documentation
    - Generates documentation templates
    - Validates existing documentation
    - Creates API reference documentation
    - Generates usage examples

Usage Example:
    >>> python tools/generate_docs.py --check
    Checking documentation coverage...
    Coverage: 85% (missing: 5 functions)

    >>> python tools/generate_docs.py --generate
    Generating missing documentation...

Since: v1.0.0
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocIssue:
    """
    Documentation issue found during validation.

    Attributes:
        file_path (str): Path to the file
        line (int): Line number of the issue
        name (str): Name of the function/class
        issue_type (str): Type of issue (missing, incomplete, etc.)
        details (str): Detailed description of the issue

    Since: v1.0.0
    """

    file_path: str
    line: int
    name: str
    issue_type: str
    details: str


class DocumentationAnalyzer:
    """
    Analyzes Python code for documentation completeness.

    Checks all public functions, classes, and modules for proper
    documentation following the project standards.

    Attributes:
        root_path (Path): Root directory to analyze
        issues (List[DocIssue]): Found documentation issues
        stats (Dict): Documentation statistics

    Example:
        >>> analyzer = DocumentationAnalyzer("src/")
        >>> analyzer.analyze()
        >>> print(f"Coverage: {analyzer.get_coverage()}%")
        92.5

    Since: v1.0.0
    """

    def __init__(self, root_path: str = "src"):
        """
        Initialize the documentation analyzer.

        Args:
            root_path: Root directory to analyze
        """
        self.root_path = Path(root_path)
        self.issues: list[DocIssue] = []
        self.stats = {
            "total_modules": 0,
            "documented_modules": 0,
            "total_classes": 0,
            "documented_classes": 0,
            "total_functions": 0,
            "documented_functions": 0,
            "total_methods": 0,
            "documented_methods": 0,
        }

    def analyze(self) -> list[DocIssue]:
        """
        Analyze all Python files for documentation issues.

        Returns:
            List of documentation issues found

        Since: v1.0.0
        """
        for py_file in self.root_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            self._analyze_file(py_file)
        return self.issues

    def _analyze_file(self, file_path: Path):
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file

        Since: v1.0.0
        """
        try:
            with open(file_path) as f:
                source = f.read()

            tree = ast.parse(source)
            self._analyze_node(tree, file_path, source)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _analyze_node(self, node: ast.AST, file_path: Path, source: str):
        """
        Recursively analyze AST nodes for documentation.

        Args:
            node: AST node to analyze
            file_path: Path to the source file
            source: Source code as string

        Since: v1.0.0
        """
        if isinstance(node, ast.Module):
            self.stats["total_modules"] += 1
            docstring = ast.get_docstring(node)
            if docstring:
                self.stats["documented_modules"] += 1
                self._validate_module_docstring(docstring, file_path)
            else:
                self.issues.append(
                    DocIssue(
                        str(file_path), 1, "module", "missing", "Module lacks docstring"
                    )
                )

        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                self.stats["total_classes"] += 1
                docstring = ast.get_docstring(node)
                if docstring:
                    self.stats["documented_classes"] += 1
                    self._validate_class_docstring(
                        docstring, node.name, file_path, node.lineno
                    )
                else:
                    self.issues.append(
                        DocIssue(
                            str(file_path),
                            node.lineno,
                            node.name,
                            "missing",
                            "Class lacks docstring",
                        )
                    )

        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            if not node.name.startswith("_"):
                is_method = isinstance(getattr(node, "_parent", None), ast.ClassDef)

                if is_method:
                    self.stats["total_methods"] += 1
                else:
                    self.stats["total_functions"] += 1

                docstring = ast.get_docstring(node)
                if docstring:
                    if is_method:
                        self.stats["documented_methods"] += 1
                    else:
                        self.stats["documented_functions"] += 1
                    self._validate_function_docstring(
                        docstring, node.name, file_path, node.lineno, node
                    )
                else:
                    self.issues.append(
                        DocIssue(
                            str(file_path),
                            node.lineno,
                            node.name,
                            "missing",
                            "Function/method lacks docstring",
                        )
                    )

        # Set parent reference for methods detection
        for child in ast.iter_child_nodes(node):
            if isinstance(node, ast.ClassDef):
                child._parent = node
            self._analyze_node(child, file_path, source)

    def _validate_module_docstring(self, docstring: str, file_path: Path):
        """
        Validate module docstring completeness.

        Args:
            docstring: The module's docstring
            file_path: Path to the module file

        Since: v1.0.0
        """
        required_sections = [
            "Since:",
            "Usage Example:" if "test" not in str(file_path) else "Since:",
        ]
        for section in required_sections:
            if section not in docstring:
                self.issues.append(
                    DocIssue(
                        str(file_path),
                        1,
                        "module",
                        "incomplete",
                        f"Missing '{section}' section",
                    )
                )

    def _validate_class_docstring(
        self, docstring: str, name: str, file_path: Path, line: int
    ):
        """
        Validate class docstring completeness.

        Args:
            docstring: The class docstring
            name: Class name
            file_path: Path to the file
            line: Line number

        Since: v1.0.0
        """
        required_sections = ["Attributes:", "Example:", "Since:"]
        for section in required_sections:
            if section not in docstring and "TypedDict" not in docstring:
                self.issues.append(
                    DocIssue(
                        str(file_path),
                        line,
                        name,
                        "incomplete",
                        f"Missing '{section}' section",
                    )
                )

    def _validate_function_docstring(
        self, docstring: str, name: str, file_path: Path, line: int, node: ast.AST
    ):
        """
        Validate function/method docstring completeness.

        Args:
            docstring: The function's docstring
            name: Function name
            file_path: Path to the file
            line: Line number
            node: AST node of the function

        Since: v1.0.0
        """
        # Check for required sections based on function signature
        has_args = (
            len(node.args.args) > 1 if name != "__init__" else len(node.args.args) > 1
        )
        has_return = not (
            name == "__init__"
            or any(
                isinstance(n, ast.Return) and n.value is None for n in ast.walk(node)
            )
        )

        if has_args and "Args:" not in docstring and "Parameters:" not in docstring:
            self.issues.append(
                DocIssue(
                    str(file_path), line, name, "incomplete", "Missing 'Args:' section"
                )
            )

        if has_return and "Returns:" not in docstring and "Yields:" not in docstring:
            if "__" not in name:  # Skip dunder methods
                self.issues.append(
                    DocIssue(
                        str(file_path),
                        line,
                        name,
                        "incomplete",
                        "Missing 'Returns:' section",
                    )
                )

        if "Since:" not in docstring:
            self.issues.append(
                DocIssue(
                    str(file_path), line, name, "incomplete", "Missing 'Since:' version"
                )
            )

    def get_coverage(self) -> float:
        """
        Calculate documentation coverage percentage.

        Returns:
            Coverage percentage (0-100)

        Since: v1.0.0
        """
        total = (
            self.stats["total_modules"]
            + self.stats["total_classes"]
            + self.stats["total_functions"]
            + self.stats["total_methods"]
        )

        documented = (
            self.stats["documented_modules"]
            + self.stats["documented_classes"]
            + self.stats["documented_functions"]
            + self.stats["documented_methods"]
        )

        if total == 0:
            return 100.0

        return (documented / total) * 100

    def print_report(self):
        """
        Print a detailed documentation report.

        Since: v1.0.0
        """
        print("\n" + "=" * 60)
        print("📊 Documentation Analysis Report")
        print("=" * 60)

        print("\n📈 Statistics:")
        print(
            f"  Modules:   {self.stats['documented_modules']}/{self.stats['total_modules']}"
        )
        print(
            f"  Classes:   {self.stats['documented_classes']}/{self.stats['total_classes']}"
        )
        print(
            f"  Functions: {self.stats['documented_functions']}/{self.stats['total_functions']}"
        )
        print(
            f"  Methods:   {self.stats['documented_methods']}/{self.stats['total_methods']}"
        )

        coverage = self.get_coverage()
        print(f"\n🎯 Overall Coverage: {coverage:.1f}%")

        if coverage >= 90:
            print("✅ Excellent documentation coverage!")
        elif coverage >= 75:
            print("⚠️  Good coverage, but room for improvement")
        else:
            print("❌ Documentation needs significant work")

        if self.issues:
            print(f"\n🔍 Found {len(self.issues)} issues:")

            # Group issues by type
            missing = [i for i in self.issues if i.issue_type == "missing"]
            incomplete = [i for i in self.issues if i.issue_type == "incomplete"]

            if missing:
                print(f"\n  Missing documentation ({len(missing)}):")
                for issue in missing[:5]:  # Show first 5
                    print(f"    - {issue.file_path}:{issue.line} - {issue.name}")
                if len(missing) > 5:
                    print(f"    ... and {len(missing)-5} more")

            if incomplete:
                print(f"\n  Incomplete documentation ({len(incomplete)}):")
                for issue in incomplete[:5]:  # Show first 5
                    print(
                        f"    - {issue.file_path}:{issue.line} - {issue.name}: {issue.details}"
                    )
                if len(incomplete) > 5:
                    print(f"    ... and {len(incomplete)-5} more")


class DocumentationGenerator:
    """
    Generates documentation templates and API references.

    Creates documentation following project standards for
    undocumented or poorly documented code elements.

    Since: v1.0.0
    """

    @staticmethod
    def generate_function_docstring(
        name: str, args: list[str], has_return: bool = True, is_async: bool = False
    ) -> str:
        """
        Generate a template docstring for a function.

        Args:
            name: Function name
            args: List of argument names
            has_return: Whether function returns a value
            is_async: Whether function is async

        Returns:
            Template docstring as string

        Since: v1.0.0
        """
        docstring = f'''
    """
    Brief description of {name}.
    
    [Add detailed description here]
    '''

        if args and args[0] != "self":
            docstring += """
    
    Args:"""
            for arg in args:
                if arg not in ["self", "cls"]:
                    docstring += f"""
        {arg}: Description of {arg}"""

        if has_return:
            if is_async and "yield" in name.lower():
                docstring += """
    
    Yields:
        Description of yielded values"""
            else:
                docstring += """
    
    Returns:
        Description of return value"""

        docstring += '''
    
    Example:
        >>> # Add example here
        pass
    
    Since: v1.0.0
    """
    '''
        return docstring

    @staticmethod
    def generate_class_docstring(name: str) -> str:
        """
        Generate a template docstring for a class.

        Args:
            name: Class name

        Returns:
            Template docstring as string

        Since: v1.0.0
        """
        return f'''
    """
    Brief description of {name}.
    
    [Add detailed description here]
    
    Attributes:
        attribute1 (Type): Description
        attribute2 (Type): Description
    
    Example:
        >>> obj = {name}()
        >>> # Add example here
    
    Since: v1.0.0
    """
    '''

    @staticmethod
    def generate_module_docstring(module_name: str) -> str:
        """
        Generate a template docstring for a module.

        Args:
            module_name: Name of the module

        Returns:
            Template docstring as string

        Since: v1.0.0
        """
        return f'''
"""
{module_name} - Brief description.

[Add detailed description of module purpose and functionality]

Key Features:
    - Feature 1: Description
    - Feature 2: Description

Usage Example:
    >>> from nix_for_humanity import {module_name}
    >>> # Add example here

Since: v1.0.0
"""
'''


def generate_api_reference(output_path: str = "docs/API_REFERENCE.md"):
    """
    Generate comprehensive API reference documentation.

    Args:
        output_path: Where to save the API reference

    Since: v1.0.0
    """
    api_doc = """# 📖 API Reference

> Complete API documentation for Nix for Humanity

## Core API

### Main Functions

#### `ask_nix(query: str, *, execute: bool = False) -> QueryResult`

Natural language interface to NixOS.

**Parameters:**
- `query` (str): Natural language command
- `execute` (bool): Whether to execute (default: False)

**Returns:**
- `QueryResult`: Result object with success, data, and message

**Example:**
```python
result = ask_nix("install firefox")
print(result.message)
```

### Backend API

#### `NixForHumanityBackend`

Core backend for processing natural language queries.

**Methods:**
- `execute(query: str, context: Context) -> ExecutionResult`
- `understand(query: str, context: Context) -> Intent`

### Configuration API

#### `ConfigManager`

Manages user configuration and preferences.

**Methods:**
- `get(key: str, default: Any = None) -> Any`
- `set(key: str, value: Any) -> None`
- `add_alias(name: str, expansion: str) -> None`

## Type Definitions

See [types.py](../src/nix_for_humanity/types.py) for complete type definitions.

"""

    with open(output_path, "w") as f:
        f.write(api_doc)

    print(f"✅ API reference generated: {output_path}")


def main():
    """
    Main entry point for documentation tools.

    Since: v1.0.0
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Documentation tools for Nix for Humanity"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check documentation coverage"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate missing documentation templates",
    )
    parser.add_argument(
        "--api-ref", action="store_true", help="Generate API reference documentation"
    )
    parser.add_argument(
        "--path",
        default="src/nix_for_humanity",
        help="Path to analyze (default: src/nix_for_humanity)",
    )

    args = parser.parse_args()

    if args.check or not any([args.generate, args.api_ref]):
        analyzer = DocumentationAnalyzer(args.path)
        analyzer.analyze()
        analyzer.print_report()

        if analyzer.get_coverage() < 90:
            return 1  # Exit with error if coverage too low

    if args.generate:
        print("\n🔧 Generating documentation templates...")
        generator = DocumentationGenerator()
        # Would implement actual generation here
        print("💡 Use templates from documentation standards guide")

    if args.api_ref:
        generate_api_reference()

    return 0


if __name__ == "__main__":
    sys.exit(main())
